"""
Utilitaires pour l'envoi d'emails de notifications
Centralise l'envoi d'emails pour tous les types de notifications
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone


def envoyer_email_notification(notification, type_model='tache'):
    """
    Envoie un email pour une notification donnée
    
    Args:
        notification: Instance de NotificationTache, NotificationEtape, NotificationModule, NotificationProjet ou AlerteProjet
        type_model: Type de modèle ('tache', 'etape', 'module', 'projet', 'alerte')
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    try:
        # Vérifier que le destinataire a un email
        if not notification.destinataire.email:
            print(f"Pas d'email pour {notification.destinataire.get_full_name()}")
            return False
        
        # Préparer le contexte selon le type
        context = {
            'notification': notification,
            'destinataire': notification.destinataire,
            'titre': notification.titre,
            'message': notification.message,
            'date_creation': notification.date_creation,
            'site_name': 'SI-Gouvernance JCM',
        }
        
        # Ajouter des informations spécifiques selon le type
        if type_model == 'tache':
            context.update({
                'tache': notification.tache,
                'projet': notification.tache.etape.projet if hasattr(notification.tache, 'etape') else notification.tache.module.projet,
                'type_notification': notification.get_type_notification_display(),
                'emetteur': notification.emetteur,
            })
            sujet_prefix = "Tâche"
            
        elif type_model == 'etape':
            context.update({
                'etape': notification.etape,
                'projet': notification.etape.projet,
                'type_notification': notification.get_type_notification_display(),
                'emetteur': notification.emetteur,
            })
            sujet_prefix = "Étape"
            
        elif type_model == 'module':
            context.update({
                'module': notification.module,
                'projet': notification.module.projet,
                'type_notification': notification.get_type_notification_display(),
                'emetteur': notification.emetteur,
            })
            sujet_prefix = "Module"
            
        elif type_model == 'projet':
            context.update({
                'projet': notification.projet,
                'type_notification': notification.get_type_notification_display(),
                'emetteur': notification.emetteur,
            })
            sujet_prefix = "Projet"
            
        elif type_model == 'alerte':
            context.update({
                'projet': notification.projet,
                'type_alerte': notification.get_type_alerte_display(),
                'niveau': notification.get_niveau_display(),
            })
            sujet_prefix = "Alerte"
        
        # Sujet de l'email
        sujet = f"[SI-Gouvernance] {sujet_prefix}: {notification.titre}"
        
        # Corps de l'email en texte brut
        message_text = generer_message_texte(notification, type_model, context)
        
        # Essayer d'utiliser un template HTML si disponible
        message_html = None
        try:
            template_name = f'emails/notification_{type_model}.html'
            message_html = render_to_string(template_name, context)
        except Exception:
            # Si le template n'existe pas, on utilise seulement le texte brut
            pass
        
        # Envoyer l'email
        send_mail(
            subject=sujet,
            message=message_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@si-gouvernance.com'),
            recipient_list=[notification.destinataire.email],
            html_message=message_html,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email de notification: {str(e)}")
        return False


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
