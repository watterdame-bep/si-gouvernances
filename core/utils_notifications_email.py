"""
Utilitaires pour l'envoi d'emails de notifications
Centralise l'envoi d'emails pour tous les types de notifications
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site


def get_base_url(request=None):
    """Retourne l'URL de base de l'application"""
    if request:
        return f"{request.scheme}://{request.get_host()}"
    return getattr(settings, 'BASE_URL', 'http://localhost:8000')


def get_logo_url(request=None):
    """Retourne l'URL complète du logo"""
    base_url = get_base_url(request)
    # Le logo est dans media/logos/jconsult_logo.png
    return f"{base_url}/media/logos/jconsult_logo.png"


def envoyer_email_notification(notification, type_model='tache', request=None):
    """
    Envoie un email pour une notification donnée avec template HTML professionnel
    
    Args:
        notification: Instance de NotificationTache, NotificationEtape, NotificationModule, NotificationProjet ou AlerteProjet
        type_model: Type de modèle ('tache', 'etape', 'module', 'projet', 'alerte')
        request: Objet request Django (optionnel, pour générer les URLs)
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    try:
        # Vérifier que le destinataire a un email
        if not notification.destinataire.email:
            print(f"Pas d'email pour {notification.destinataire.get_full_name()}")
            return False
        
        base_url = get_base_url(request)
        logo_url = get_logo_url(request)
        
        # Contexte de base commun à tous les emails
        context = {
            'notification': notification,
            'destinataire': notification.destinataire,
            'destinataire_nom': notification.destinataire.get_full_name(),
            'titre': notification.titre,
            'message': notification.message,
            'date_creation': notification.date_creation,
            'date_notification': notification.date_creation.strftime('%d/%m/%Y à %H:%M'),
            'site_name': 'SI-Gouvernance',
            'base_url': base_url,
            'logo_url': logo_url,
        }
        
        # Préparer le sujet et le template selon le type
        sujet, template_name = preparer_email_context(notification, type_model, context, base_url)
        
        # Corps de l'email en texte brut (fallback)
        message_text = generer_message_texte(notification, type_model, context)
        
        # Générer le HTML avec le template professionnel
        try:
            message_html = render_to_string(template_name, context)
        except Exception as e:
            print(f"Erreur lors du rendu du template {template_name}: {e}")
            # Utiliser le template de base si le template spécifique n'existe pas
            message_html = None
        
        # Créer et envoyer l'email
        email = EmailMultiAlternatives(
            subject=sujet,
            body=message_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'SI-Gouvernance <noreply@si-gouvernance.com>'),
            to=[notification.destinataire.email],
        )
        
        if message_html:
            email.attach_alternative(message_html, "text/html")
        
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def preparer_email_context(notification, type_model, context, base_url):
    """
    Prépare le contexte spécifique selon le type de notification
    
    Returns:
        tuple: (sujet, template_name)
    """
    if type_model == 'tache':
        tache = notification.tache
        if hasattr(tache, 'etape'):
            projet = tache.etape.projet
            etape_nom = tache.etape.type_etape.get_nom_display()
        else:
            projet = tache.module.projet
            etape_nom = tache.module.nom
        
        context.update({
            'tache': tache,
            'tache_titre': tache.nom,
            'tache_description': tache.description if hasattr(tache, 'description') else '',
            'projet': projet,
            'projet_nom': projet.nom,
            'etape_nom': etape_nom,
            'date_echeance': tache.date_fin.strftime('%d/%m/%Y') if tache.date_fin else None,
            'assigne_par': notification.emetteur.get_full_name() if notification.emetteur else 'Système',
            'tache_url': f"{base_url}/projets/{projet.id}/",
        })
        
        sujet = f"[SI-Gouvernance] Nouvelle Tâche: {tache.nom}"
        template_name = 'emails/notification_assignation_tache.html'
        
    elif type_model == 'etape':
        etape = notification.etape
        projet = etape.projet
        
        context.update({
            'etape': etape,
            'etape_nom': etape.type_etape.get_nom_display(),
            'projet': projet,
            'projet_nom': projet.nom,
            'projet_client': projet.client,
            'emetteur': notification.emetteur.get_full_name() if notification.emetteur else 'Système',
            'projet_url': f"{base_url}/projets/{projet.id}/",
        })
        
        sujet = f"[SI-Gouvernance] Étape: {notification.titre}"
        template_name = 'emails/notification_etape.html'
        
    elif type_model == 'module':
        module = notification.module
        projet = module.projet
        
        context.update({
            'module': module,
            'module_nom': module.nom,
            'projet': projet,
            'projet_nom': projet.nom,
            'projet_client': projet.client,
            'emetteur': notification.emetteur.get_full_name() if notification.emetteur else 'Système',
            'module_url': f"{base_url}/projets/{projet.id}/modules/",
        })
        
        sujet = f"[SI-Gouvernance] Module: {notification.titre}"
        template_name = 'emails/notification_module.html'
        
    elif type_model == 'projet':
        projet = notification.projet
        
        # Déterminer le template selon le type de notification
        if notification.type_notification == 'RESPONSABLE_PRINCIPAL':
            template_name = 'emails/notification_responsable_projet.html'
            sujet = f"[SI-Gouvernance] Nouveau Responsable: {projet.nom}"
        else:
            template_name = 'emails/notification_projet.html'
            sujet = f"[SI-Gouvernance] Projet: {notification.titre}"
        
        context.update({
            'projet': projet,
            'projet_nom': projet.nom,
            'projet_client': projet.client,
            'projet_statut': projet.statut.get_nom_display(),
            'projet_budget': f"{projet.budget_previsionnel:,.2f}",
            'projet_devise': projet.devise,
            'affecte_par': notification.emetteur.get_full_name() if notification.emetteur else 'Système',
            'projet_url': f"{base_url}/projets/{projet.id}/",
        })
        
    elif type_model == 'alerte':
        projet = notification.projet
        
        context.update({
            'projet': projet,
            'projet_nom': projet.nom,
            'projet_client': projet.client,
            'projet_statut': projet.statut.get_nom_display(),
            'alerte_titre': notification.get_type_alerte_display(),
            'alerte_message': notification.message,
            'niveau': notification.get_niveau_display(),
            'projet_url': f"{base_url}/projets/{projet.id}/",
        })
        
        # Ajouter les données contextuelles
        if notification.donnees_contexte:
            context.update({
                'jours_restants': notification.donnees_contexte.get('jours_restants'),
                'date_echeance': notification.donnees_contexte.get('date_echeance'),
            })
        
        sujet = f"[SI-Gouvernance] ⚠️ Alerte: {notification.titre}"
        template_name = 'emails/notification_alerte_projet.html'
    
    else:
        sujet = f"[SI-Gouvernance] {notification.titre}"
        template_name = 'emails/base_email.html'
    
    return sujet, template_name


def generer_message_texte(notification, type_model, context):
    """
    Génère le message texte de l'email selon le type de notification
    
    Args:
        notification: Instance de notification
        type_model: Type de modèle
        context: Contexte avec les données
    
    Returns:
        str: Message texte formaté
    """
    destinataire_nom = notification.destinataire.get_full_name()
    date_str = notification.date_creation.strftime('%d/%m/%Y à %H:%M')
    
    # En-tête commun
    message = f"Bonjour {destinataire_nom},\n\n"
    message += f"{notification.message}\n\n"
    
    # Détails spécifiques selon le type
    if type_model == 'tache':
        tache = notification.tache
        if hasattr(tache, 'etape'):
            projet = tache.etape.projet
            contexte_tache = f"Étape: {tache.etape.type_etape.get_nom_display()}"
        else:
            projet = tache.module.projet
            contexte_tache = f"Module: {tache.module.nom}"
        
        message += "Détails de la tâche:\n"
        message += f"- Tâche: {tache.nom}\n"
        message += f"- {contexte_tache}\n"
        message += f"- Projet: {projet.nom}\n"
        message += f"- Client: {projet.client}\n"
        
        if tache.responsable:
            message += f"- Responsable: {tache.responsable.get_full_name()}\n"
        
        if tache.date_fin:
            message += f"- Date limite: {tache.date_fin.strftime('%d/%m/%Y')}\n"
        
        if notification.emetteur:
            message += f"- Action effectuée par: {notification.emetteur.get_full_name()}\n"
    
    elif type_model == 'etape':
        etape = notification.etape
        projet = etape.projet
        
        message += "Détails de l'étape:\n"
        message += f"- Étape: {etape.type_etape.get_nom_display()}\n"
        message += f"- Projet: {projet.nom}\n"
        message += f"- Client: {projet.client}\n"
        message += f"- Ordre: Étape {etape.ordre}\n"
        
        if etape.date_fin_reelle:
            message += f"- Date de completion: {etape.date_fin_reelle.strftime('%d/%m/%Y')}\n"
        
        if notification.emetteur:
            message += f"- Action effectuée par: {notification.emetteur.get_full_name()}\n"
    
    elif type_model == 'module':
        module = notification.module
        projet = module.projet
        
        message += "Détails du module:\n"
        message += f"- Module: {module.nom}\n"
        message += f"- Projet: {projet.nom}\n"
        message += f"- Client: {projet.client}\n"
        
        if module.description:
            message += f"- Description: {module.description}\n"
        
        # Informations sur l'affectation si c'est une notification d'affectation
        if notification.type_notification == 'AFFECTATION_MODULE':
            affectation = module.affectations.filter(
                utilisateur=notification.destinataire,
                date_fin_affectation__isnull=True
            ).first()
            if affectation:
                message += f"- Votre rôle: {affectation.get_role_module_display()}\n"
        
        if notification.emetteur:
            message += f"- Action effectuée par: {notification.emetteur.get_full_name()}\n"
    
    elif type_model == 'projet':
        projet = notification.projet
        
        message += "Détails du projet:\n"
        message += f"- Projet: {projet.nom}\n"
        message += f"- Client: {projet.client}\n"
        message += f"- Statut: {projet.statut.get_nom_display()}\n"
        
        if projet.date_debut:
            message += f"- Date de début: {projet.date_debut.strftime('%d/%m/%Y')}\n"
        
        if projet.date_fin:
            message += f"- Date de fin prévue: {projet.date_fin.strftime('%d/%m/%Y')}\n"
        
        if notification.emetteur:
            message += f"- Action effectuée par: {notification.emetteur.get_full_name()}\n"
    
    elif type_model == 'alerte':
        projet = notification.projet
        
        message += "Détails de l'alerte:\n"
        message += f"- Type: {notification.get_type_alerte_display()}\n"
        message += f"- Niveau: {notification.get_niveau_display()}\n"
        message += f"- Projet: {projet.nom}\n"
        message += f"- Client: {projet.client}\n"
        
        # Informations contextuelles si disponibles
        if notification.donnees_contexte:
            if 'jours_restants' in notification.donnees_contexte:
                message += f"- Jours restants: {notification.donnees_contexte['jours_restants']}\n"
            if 'jours_retard' in notification.donnees_contexte:
                message += f"- Jours de retard: {notification.donnees_contexte['jours_retard']}\n"
    
    # Pied de page commun
    message += f"\nDate de notification: {date_str}\n"
    message += "\nConnectez-vous à SI-Gouvernance pour plus de détails.\n\n"
    message += "Cordialement,\n"
    message += "L'équipe SI-Gouvernance JCM\n\n"
    message += "---\n"
    message += "Ceci est un email automatique, merci de ne pas y répondre."
    
    return message


def envoyer_email_notification_tache(notification):
    """Envoie un email pour une NotificationTache"""
    return envoyer_email_notification(notification, 'tache')


def envoyer_email_notification_etape(notification):
    """Envoie un email pour une NotificationEtape"""
    return envoyer_email_notification(notification, 'etape')


def envoyer_email_notification_module(notification):
    """Envoie un email pour une NotificationModule"""
    return envoyer_email_notification(notification, 'module')


def envoyer_email_notification_projet(notification):
    """Envoie un email pour une NotificationProjet"""
    return envoyer_email_notification(notification, 'projet')


def envoyer_email_alerte_projet(alerte):
    """Envoie un email pour une AlerteProjet"""
    return envoyer_email_notification(alerte, 'alerte')


def envoyer_emails_batch_notifications(notifications, type_model='tache'):
    """
    Envoie des emails pour un lot de notifications
    
    Args:
        notifications: QuerySet ou liste de notifications
        type_model: Type de modèle
    
    Returns:
        dict: Résultat avec nombre d'emails envoyés
    """
    emails_envoyes = 0
    emails_echoues = 0
    
    for notification in notifications:
        try:
            if envoyer_email_notification(notification, type_model):
                emails_envoyes += 1
            else:
                emails_echoues += 1
        except Exception as e:
            print(f"Erreur lors de l'envoi pour notification {notification.id}: {e}")
            emails_echoues += 1
    
    return {
        'success': True,
        'emails_envoyes': emails_envoyes,
        'emails_echoues': emails_echoues,
        'total': emails_envoyes + emails_echoues
    }
