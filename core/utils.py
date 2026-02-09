from .models import ActionAudit
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import hashlib
import secrets
import string


def generer_mot_de_passe_temporaire(longueur=8):
    """
    Génère un mot de passe temporaire sécurisé
    
    Args:
        longueur: Longueur du mot de passe (défaut: 8)
    
    Returns:
        str: Mot de passe temporaire
    """
    # Caractères autorisés (éviter les caractères ambigus)
    lettres = string.ascii_letters.replace('l', '').replace('I', '').replace('O', '').replace('o', '')
    chiffres = string.digits.replace('0', '').replace('1', '')
    symboles = '@#$%&*+'
    
    # Assurer au moins un de chaque type
    password = [
        secrets.choice(lettres.upper()),  # Une majuscule
        secrets.choice(lettres.lower()),  # Une minuscule
        secrets.choice(chiffres),         # Un chiffre
        secrets.choice(symboles)          # Un symbole
    ]
    
    # Compléter avec des caractères aléatoires
    tous_caracteres = lettres + chiffres + symboles
    for _ in range(longueur - 4):
        password.append(secrets.choice(tous_caracteres))
    
    # Mélanger la liste
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def generer_username(prenom, nom):
    """
    Génère un nom d'utilisateur unique basé sur prénom.nom
    
    Args:
        prenom: Prénom de l'utilisateur
        nom: Nom de l'utilisateur
    
    Returns:
        str: Username unique
    """
    from .models import Utilisateur
    import unicodedata
    
    # Normaliser et nettoyer les caractères
    prenom_clean = unicodedata.normalize('NFD', prenom.lower()).encode('ascii', 'ignore').decode('ascii')
    nom_clean = unicodedata.normalize('NFD', nom.lower()).encode('ascii', 'ignore').decode('ascii')
    
    # Supprimer les espaces et caractères spéciaux
    prenom_clean = ''.join(c for c in prenom_clean if c.isalnum())
    nom_clean = ''.join(c for c in nom_clean if c.isalnum())
    
    base_username = f"{prenom_clean}.{nom_clean}"
    
    # Vérifier l'unicité
    username = base_username
    counter = 1
    
    while Utilisateur.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip


def enregistrer_audit(utilisateur, type_action, description, request=None, projet=None, donnees_avant=None, donnees_apres=None):
    """
    Enregistre automatiquement une action dans le journal d'audit
    
    Args:
        utilisateur: Instance Utilisateur qui effectue l'action
        type_action: Type d'action (voir ActionAudit.TYPE_ACTIONS)
        description: Description de l'action
        request: Objet request Django (optionnel)
        projet: Projet concerné (optionnel)
        donnees_avant: État avant modification (optionnel)
        donnees_apres: État après modification (optionnel)
    """
    
    # Récupérer les informations de la requête
    adresse_ip = '127.0.0.1'
    user_agent = 'Unknown'
    
    if request:
        adresse_ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')[:500]  # Limiter la taille
    
    # Créer l'entrée d'audit
    action_audit = ActionAudit(
        utilisateur=utilisateur,
        type_action=type_action,
        projet=projet,
        description=description,
        donnees_avant=donnees_avant,
        donnees_apres=donnees_apres,
        adresse_ip=adresse_ip,
        user_agent=user_agent,
        timestamp=timezone.now()
    )
    
    # Générer le hash d'intégrité
    data_to_hash = f"{utilisateur.id}{type_action}{action_audit.timestamp}{description}"
    action_audit.hash_integrite = hashlib.sha256(data_to_hash.encode()).hexdigest()
    
    # Sauvegarder
    action_audit.save()
    
    return action_audit


def verifier_permissions_projet(utilisateur, projet, action='consulter'):
    """
    Vérifie si un utilisateur a les permissions pour une action sur un projet
    
    Args:
        utilisateur: Instance Utilisateur
        projet: Instance Projet
        action: Type d'action ('consulter', 'modifier', 'supprimer')
    
    Returns:
        bool: True si autorisé, False sinon
    """
    from .models import Role
    
    # Super Admin a tous les droits
    if utilisateur.est_super_admin():
        return True
    
    # Créateur du projet
    if projet.createur == utilisateur:
        return True
    
    # Membre de l'équipe
    if projet.affectations.filter(utilisateur=utilisateur, date_fin__isnull=True).exists():
        if action == 'consulter':
            return True
        
        # Responsable principal peut modifier
        if action == 'modifier':
            return projet.affectations.filter(
                utilisateur=utilisateur, 
                est_responsable_principal=True,
                date_fin__isnull=True
            ).exists()
    
    return False


def calculer_statistiques_projet(projet):
    """
    Calcule les statistiques d'un projet
    
    Args:
        projet: Instance Projet
    
    Returns:
        dict: Statistiques du projet
    """
    equipe = projet.affectations.filter(date_fin__isnull=True)
    
    return {
        'nombre_membres': equipe.count(),
        'responsable': projet.get_responsable_principal(),
        'budget_formate': f"{projet.budget_previsionnel:,.2f} {projet.devise}",
        'jours_depuis_creation': (timezone.now().date() - projet.date_creation.date()).days,
        'derniere_modification': projet.date_modification,
    }


def valider_coherence_donnees():
    """
    Valide la cohérence des données du système
    
    Returns:
        dict: Résultats de validation
    """
    from .models import Projet, Utilisateur, Affectation
    from django.db import models
    
    resultats = {
        'erreurs': [],
        'avertissements': [],
        'statistiques': {}
    }
    
    # Vérifier les projets sans responsable
    projets_sans_responsable = Projet.objects.exclude(
        affectations__est_responsable_principal=True,
        affectations__date_fin__isnull=True
    ).exclude(statut__nom__in=['TERMINE', 'ARCHIVE'])
    
    if projets_sans_responsable.exists():
        resultats['erreurs'].append(
            f"{projets_sans_responsable.count()} projet(s) actif(s) sans responsable principal"
        )
    
    # Vérifier les utilisateurs inactifs avec affectations
    utilisateurs_inactifs_affectes = Utilisateur.objects.filter(
        statut_actif=False,
        affectations__date_fin__isnull=True
    ).distinct()
    
    if utilisateurs_inactifs_affectes.exists():
        resultats['avertissements'].append(
            f"{utilisateurs_inactifs_affectes.count()} utilisateur(s) inactif(s) avec des affectations actives"
        )
    
    # Vérifier les doublons d'affectation
    affectations_doublons = Affectation.objects.filter(
        date_fin__isnull=True
    ).values('utilisateur', 'projet').annotate(
        count=models.Count('id')
    ).filter(count__gt=1)
    
    if affectations_doublons.exists():
        resultats['erreurs'].append(
            f"{affectations_doublons.count()} affectation(s) en doublon détectée(s)"
        )
    
    # Statistiques générales
    resultats['statistiques'] = {
        'total_projets': Projet.objects.count(),
        'projets_actifs': Projet.objects.exclude(statut__nom__in=['TERMINE', 'ARCHIVE']).count(),
        'utilisateurs_actifs': Utilisateur.objects.filter(statut_actif=True).count(),
        'total_affectations': Affectation.objects.filter(date_fin__isnull=True).count(),
    }
    
    return resultats


def require_super_admin(view_func):
    """
    Décorateur pour restreindre l'accès aux Super Admins uniquement
    """
    from functools import wraps
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.est_super_admin():
            messages.error(request, 'Accès refusé. Seuls les Super Admins peuvent accéder à cette fonctionnalité.')
            enregistrer_audit(
                utilisateur=request.user,
                type_action='ACCES_REFUSE',
                description=f'Tentative d\'accès non autorisé à {view_func.__name__}',
                request=request
            )
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def require_project_access(view_func):
    """
    Décorateur pour vérifier l'accès à un projet
    """
    from functools import wraps
    from django.shortcuts import redirect
    from django.contrib import messages
    from django.contrib.auth.decorators import login_required
    
    @wraps(view_func)
    @login_required
    def wrapper(request, projet_id=None, *args, **kwargs):
        if request.user.est_super_admin():
            return view_func(request, projet_id=projet_id, *args, **kwargs)
        
        from .models import Projet
        try:
            projet = Projet.objects.get(id=projet_id)
            if not request.user.a_acces_projet(projet):
                messages.error(request, 'Vous n\'avez pas accès à ce projet.')
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='ACCES_REFUSE',
                    description=f'Tentative d\'accès non autorisé au projet {projet.nom}',
                    projet=projet,
                    request=request
                )
                return redirect('dashboard')
        except Projet.DoesNotExist:
            messages.error(request, 'Projet introuvable.')
            return redirect('dashboard')
        
        return view_func(request, projet_id=projet_id, *args, **kwargs)
    
    return wrapper

def peut_creer_taches(user, projet):
    """
    Vérifie si l'utilisateur peut créer des tâches pour ce projet.
    Seuls les responsables du projet, administrateurs ou chefs de projet peuvent créer des tâches.
    """
    # Super admin peut toujours créer
    if user.est_super_admin():
        return True
    
    # Créateur du projet peut toujours créer
    if projet.createur == user:
        return True
    
    # Responsable principal du projet peut créer
    if projet.affectations.filter(
        utilisateur=user, 
        est_responsable_principal=True,
        date_fin__isnull=True
    ).exists():
        return True
    
    # Chef de projet (rôle système) peut créer
    if user.role_systeme and user.role_systeme.nom == 'CHEF_PROJET':
        return True
    
    return False


def peut_creer_taches_module(user, module):
    """
    Vérifie si l'utilisateur peut créer des tâches dans un module spécifique.
    Seuls les responsables du module peuvent créer des tâches.
    """
    # Super admin peut toujours créer
    if user.est_super_admin():
        return True
    
    # Créateur du projet peut toujours créer
    if module.projet.createur == user:
        return True
    
    # Responsable principal du projet peut créer
    if module.projet.affectations.filter(
        utilisateur=user, 
        est_responsable_principal=True,
        date_fin__isnull=True
    ).exists():
        return True
    
    # Responsable du module peut créer
    if module.affectations.filter(
        utilisateur=user,
        role_module='RESPONSABLE',
        date_fin_affectation__isnull=True
    ).exists():
        return True
    
    return False


def peut_assigner_taches_module(user, module, utilisateur_cible):
    """
    Vérifie si l'utilisateur peut assigner des tâches à un utilisateur cible dans un module.
    Seuls les responsables du module peuvent assigner des tâches aux contributeurs.
    """
    # Vérifier d'abord si l'utilisateur peut créer des tâches dans le module
    if not peut_creer_taches_module(user, module):
        return False
    
    # Vérifier que l'utilisateur cible fait partie de l'équipe du projet
    if not module.projet.affectations.filter(
        utilisateur=utilisateur_cible,
        date_fin__isnull=True
    ).exists():
        return False
    
    # Vérifier que l'utilisateur cible a une affectation sur le module
    affectation_cible = module.affectations.filter(
        utilisateur=utilisateur_cible,
        date_fin_affectation__isnull=True
    ).first()
    
    if not affectation_cible:
        return False
    
    # Le responsable peut s'assigner des tâches à lui-même
    if user == utilisateur_cible:
        return True
    
    # Le responsable peut assigner des tâches aux contributeurs
    if affectation_cible.role_module == 'CONTRIBUTEUR':
        return True
    
    return False


def peut_terminer_tache_module(user, tache):
    """
    Vérifie si l'utilisateur peut terminer une tâche de module.
    - Le responsable peut terminer toutes les tâches du module
    - Le contributeur peut terminer seulement les tâches qui lui sont assignées
    """
    # Super admin peut toujours terminer
    if user.est_super_admin():
        return True
    
    # Créateur du projet peut toujours terminer
    if tache.module.projet.createur == user:
        return True
    
    # Responsable principal du projet peut terminer
    if tache.module.projet.affectations.filter(
        utilisateur=user, 
        est_responsable_principal=True,
        date_fin__isnull=True
    ).exists():
        return True
    
    # Vérifier l'affectation sur le module
    affectation_module = tache.module.affectations.filter(
        utilisateur=user,
        date_fin_affectation__isnull=True
    ).first()
    
    if not affectation_module:
        return False
    
    # Le responsable du module peut terminer toutes les tâches
    if affectation_module.role_module == 'RESPONSABLE':
        return True
    
    # Le contributeur peut terminer seulement les tâches qui lui sont assignées
    if affectation_module.role_module == 'CONTRIBUTEUR':
        return tache.responsable == user
    
    return False


def envoyer_notification_changement_mot_de_passe(utilisateur, request=None):
    """
    Envoie une notification par email lors du changement de mot de passe
    
    Args:
        utilisateur: Instance Utilisateur qui a changé son mot de passe
        request: Objet request Django (optionnel)
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    try:
        # Récupérer les informations de contexte
        adresse_ip = '127.0.0.1'
        user_agent = 'Unknown'
        
        if request:
            adresse_ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Contexte pour le template email
        context = {
            'utilisateur': utilisateur,
            'nom_complet': utilisateur.get_full_name(),
            'email': utilisateur.email,
            'date_changement': timezone.now(),
            'adresse_ip': adresse_ip,
            'navigateur': user_agent,
            'site_name': 'SI-Gouvernance JCM',
        }
        
        # Sujet de l'email
        sujet = f"{getattr(settings, 'SECURITY_EMAIL_SUBJECT_PREFIX', '[Sécurité] ')}Changement de mot de passe confirmé"
        
        # Corps de l'email en texte brut (version simple pour éviter les erreurs de template)
        message_text = f"""
Bonjour {utilisateur.get_full_name()},

Votre mot de passe a été modifié avec succès sur SI-Gouvernance JCM.

Détails de la modification :
- Date et heure : {timezone.now().strftime('%d/%m/%Y à %H:%M')}
- Adresse IP : {adresse_ip}
- Navigateur : {user_agent[:100]}...

Si vous n'êtes pas à l'origine de cette modification, contactez immédiatement votre administrateur système.

Pour votre sécurité :
- Ne partagez jamais votre mot de passe
- Utilisez un mot de passe unique et complexe
- Déconnectez-vous après chaque session

Cordialement,
L'équipe SI-Gouvernance JCM

---
Ceci est un email automatique, merci de ne pas y répondre.
        """.strip()
        
        # Essayer d'abord avec le template HTML
        message_html = None
        try:
            message_html = render_to_string('emails/changement_mot_de_passe.html', context)
        except Exception as template_error:
            # Si le template HTML échoue, on continue avec le texte brut seulement
            print(f"Erreur template HTML: {template_error}")
        
        # Envoyer l'email
        send_mail(
            subject=sujet,
            message=message_text,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@si-gouvernance.com'),
            recipient_list=[utilisateur.email],
            html_message=message_html,
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        # Log l'erreur pour le débogage
        print(f"Erreur lors de l'envoi de l'email de notification : {str(e)}")
        return False


def creer_notification_etape(etape, type_notification, utilisateur_emetteur, titre_personnalise=None, message_personnalise=None):
    """
    Crée des notifications d'étape pour les administrateurs et chefs de projet
    
    Args:
        etape: Instance EtapeProjet
        type_notification: Type de notification (ETAPE_TERMINEE, ETAPE_ACTIVEE, etc.)
        utilisateur_emetteur: Utilisateur qui a déclenché l'action
        titre_personnalise: Titre personnalisé (optionnel)
        message_personnalise: Message personnalisé (optionnel)
    
    Returns:
        int: Nombre de notifications créées
    """
    try:
        from .models import Utilisateur, RoleSysteme, NotificationEtape
        
        # Récupérer les destinataires
        destinataires = []
        
        # 1. Tous les super admins actifs
        super_admins = Utilisateur.objects.filter(
            is_superuser=True,
            statut_actif=True
        )
        destinataires.extend(super_admins)
        
        # 2. Tous les chefs de projet système actifs
        try:
            role_chef_projet = RoleSysteme.objects.get(nom='CHEF_PROJET')
            chefs_projet = Utilisateur.objects.filter(
                role_systeme=role_chef_projet,
                statut_actif=True
            )
            destinataires.extend(chefs_projet)
        except RoleSysteme.DoesNotExist:
            pass
        
        # 3. Le responsable principal du projet (s'il n'est pas déjà dans la liste)
        responsable = etape.projet.get_responsable_principal()
        if responsable and responsable not in destinataires:
            destinataires.append(responsable)
        
        # Éviter les doublons
        destinataires = list(set(destinataires))
        
        # Exclure l'utilisateur émetteur des notifications
        if utilisateur_emetteur in destinataires:
            destinataires.remove(utilisateur_emetteur)
        
        if not destinataires:
            return 0
        
        # Préparer le titre et message par défaut
        if not titre_personnalise:
            if type_notification == 'ETAPE_TERMINEE':
                titre_personnalise = f"Étape terminée : {etape.type_etape.get_nom_display()}"
            elif type_notification == 'ETAPE_ACTIVEE':
                titre_personnalise = f"Étape activée : {etape.type_etape.get_nom_display()}"
            elif type_notification == 'MODULES_DISPONIBLES':
                titre_personnalise = f"Modules disponibles : {etape.type_etape.get_nom_display()}"
            else:
                titre_personnalise = f"Notification étape : {etape.type_etape.get_nom_display()}"
        
        if not message_personnalise:
            if type_notification == 'ETAPE_TERMINEE':
                etape_suivante_info = ""
                etape_suivante = etape.get_etape_suivante()
                if etape_suivante:
                    etape_suivante_info = f" L'étape suivante '{etape_suivante.type_etape.get_nom_display()}' a été automatiquement activée."
                
                message_personnalise = f"L'étape '{etape.type_etape.get_nom_display()}' du projet '{etape.projet.nom}' a été terminée par {utilisateur_emetteur.get_full_name()}.{etape_suivante_info}"
            
            elif type_notification == 'MODULES_DISPONIBLES':
                message_personnalise = f"L'étape de développement a été activée pour le projet '{etape.projet.nom}'. Vous pouvez maintenant créer des modules pour ce projet."
            
            else:
                message_personnalise = f"Notification concernant l'étape '{etape.type_etape.get_nom_display()}' du projet '{etape.projet.nom}'."
        
        # Créer les notifications
        notifications_creees = 0
        for destinataire in destinataires:
            try:
                NotificationEtape.objects.create(
                    destinataire=destinataire,
                    etape=etape,
                    type_notification=type_notification,
                    titre=titre_personnalise,
                    message=message_personnalise,
                    emetteur=utilisateur_emetteur,
                    donnees_contexte={
                        'projet_id': str(etape.projet.id),
                        'projet_nom': etape.projet.nom,
                        'etape_id': str(etape.id),
                        'etape_nom': etape.type_etape.get_nom_display(),
                        'etape_ordre': etape.ordre,
                        'date_action': timezone.now().isoformat(),
                        'emetteur_nom': utilisateur_emetteur.get_full_name(),
                    }
                )
                notifications_creees += 1
            except Exception as e:
                print(f"Erreur lors de la création de notification pour {destinataire.get_full_name()}: {e}")
                continue
        
        return notifications_creees
        
    except Exception as e:
        print(f"Erreur lors de la création des notifications d'étape : {e}")
        return 0


def envoyer_notification_etape_terminee(etape, utilisateur_terminant, request=None):
    """
    Envoie une notification par email aux administrateurs et chefs de projet
    lorsqu'une étape est terminée
    
    Args:
        etape: Instance EtapeProjet qui a été terminée
        utilisateur_terminant: Utilisateur qui a terminé l'étape
        request: Objet request Django (optionnel)
    
    Returns:
        dict: Résultat de l'envoi avec le nombre d'emails envoyés
    """
    try:
        from .models import Utilisateur, RoleSysteme, NotificationEtape
        
        # Récupérer les destinataires
        destinataires = []
        
        # 1. TOUJOURS notifier le responsable principal du projet
        responsable_projet = etape.projet.get_responsable_principal()
        if responsable_projet and responsable_projet != utilisateur_terminant:
            destinataires.append({
                'email': responsable_projet.email,
                'nom': responsable_projet.get_full_name(),
                'role': 'Responsable Projet',
                'utilisateur': responsable_projet
            })
            
            # Créer notification dans l'app pour le responsable
            NotificationEtape.objects.create(
                destinataire=responsable_projet,
                etape=etape,
                type_notification='ETAPE_TERMINEE',
                titre=f'Étape terminée: {etape.type_etape.get_nom_display()}',
                message=f'L\'étape "{etape.type_etape.get_nom_display()}" du projet "{etape.projet.nom}" a été terminée par {utilisateur_terminant.get_full_name()}.',
                emetteur=utilisateur_terminant,
                donnees_contexte={
                    'projet_id': str(etape.projet.id),
                    'projet_nom': etape.projet.nom,
                    'etape_id': str(etape.id),
                    'etape_nom': etape.type_etape.get_nom_display(),
                }
            )
        
        # 2. Notifier les admins SEULEMENT si activé dans les paramètres du projet
        if etape.projet.notifications_admin_activees:
            # Tous les super admins
            super_admins = Utilisateur.objects.filter(
                is_superuser=True,
                statut_actif=True,
                email__isnull=False
            ).exclude(email='').exclude(id=utilisateur_terminant.id)
            
            if responsable_projet:
                super_admins = super_admins.exclude(id=responsable_projet.id)
            
            for admin in super_admins:
                destinataires.append({
                    'email': admin.email,
                    'nom': admin.get_full_name(),
                    'role': 'Administrateur',
                    'utilisateur': admin
                })
                
                # Créer notification dans l'app
                NotificationEtape.objects.create(
                    destinataire=admin,
                    etape=etape,
                    type_notification='ETAPE_TERMINEE',
                    titre=f'Étape terminée: {etape.type_etape.get_nom_display()}',
                    message=f'L\'étape "{etape.type_etape.get_nom_display()}" du projet "{etape.projet.nom}" a été terminée par {utilisateur_terminant.get_full_name()}.',
                    emetteur=utilisateur_terminant,
                    donnees_contexte={
                        'projet_id': str(etape.projet.id),
                        'projet_nom': etape.projet.nom,
                        'etape_id': str(etape.id),
                        'etape_nom': etape.type_etape.get_nom_display(),
                    }
                )
            
            # Tous les chefs de projet système
            try:
                role_chef_projet = RoleSysteme.objects.get(nom='CHEF_PROJET')
                chefs_projet = Utilisateur.objects.filter(
                    role_systeme=role_chef_projet,
                    statut_actif=True,
                    email__isnull=False
                ).exclude(email='').exclude(id=utilisateur_terminant.id)
                
                if responsable_projet:
                    chefs_projet = chefs_projet.exclude(id=responsable_projet.id)
                
                for chef in chefs_projet:
                    destinataires.append({
                        'email': chef.email,
                        'nom': chef.get_full_name(),
                        'role': 'Chef de Projet',
                        'utilisateur': chef
                    })
                    
                    # Créer notification dans l'app
                    NotificationEtape.objects.create(
                        destinataire=chef,
                        etape=etape,
                        type_notification='ETAPE_TERMINEE',
                        titre=f'Étape terminée: {etape.type_etape.get_nom_display()}',
                        message=f'L\'étape "{etape.type_etape.get_nom_display()}" du projet "{etape.projet.nom}" a été terminée par {utilisateur_terminant.get_full_name()}.',
                        emetteur=utilisateur_terminant,
                        donnees_contexte={
                            'projet_id': str(etape.projet.id),
                            'projet_nom': etape.projet.nom,
                            'etape_id': str(etape.id),
                            'etape_nom': etape.type_etape.get_nom_display(),
                        }
                    )
            except RoleSysteme.DoesNotExist:
                pass
        
        # 3. Le responsable principal du projet (s'il n'est pas déjà dans la liste)
        responsable = etape.projet.get_responsable_principal()
        if responsable and responsable.email:
            emails_existants = [d['email'] for d in destinataires]
            if responsable.email not in emails_existants:
                destinataires.append({
                    'email': responsable.email,
                    'nom': responsable.get_full_name(),
                    'role': 'Responsable Principal'
                })
        
        if not destinataires:
            return {'success': False, 'error': 'Aucun destinataire trouvé'}
        
        # Récupérer les informations de contexte
        adresse_ip = '127.0.0.1'
        if request:
            adresse_ip = get_client_ip(request)
        
        # Préparer le contexte pour l'email
        context = {
            'etape': etape,
            'projet': etape.projet,
            'utilisateur_terminant': utilisateur_terminant,
            'date_completion': etape.date_fin_reelle,
            'etape_suivante': etape.get_etape_suivante(),
            'site_name': 'SI-Gouvernance JCM',
            'adresse_ip': adresse_ip,
        }
        
        # Sujet de l'email
        sujet = f"[SI-Gouvernance] Étape terminée : {etape.type_etape.get_nom_display()} - {etape.projet.nom}"
        
        # Corps de l'email en texte brut
        etape_suivante_info = ""
        if etape.get_etape_suivante():
            etape_suivante_info = f"\n\nÉtape suivante activée : {etape.get_etape_suivante().type_etape.get_nom_display()}"
        
        emails_envoyes = 0
        
        for destinataire in destinataires:
            message_text = f"""
Bonjour {destinataire['nom']},

Une étape du projet "{etape.projet.nom}" vient d'être terminée.

Détails de l'étape :
- Étape : {etape.type_etape.get_nom_display()}
- Projet : {etape.projet.nom}
- Client : {etape.projet.client}
- Terminée par : {utilisateur_terminant.get_full_name()}
- Date de completion : {etape.date_fin_reelle.strftime('%d/%m/%Y à %H:%M')}
- Statut du projet : {etape.projet.statut.get_nom_display()}{etape_suivante_info}

Vous recevez cette notification en tant que {destinataire['role']}.

Connectez-vous à SI-Gouvernance pour consulter les détails du projet.

Cordialement,
L'équipe SI-Gouvernance JCM

---
Ceci est un email automatique, merci de ne pas y répondre.
            """.strip()
            
            try:
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@si-gouvernance.com'),
                    recipient_list=[destinataire['email']],
                    fail_silently=False,
                )
                emails_envoyes += 1
                
            except Exception as e:
                print(f"Erreur lors de l'envoi à {destinataire['email']}: {e}")
                continue
        
        return {
            'success': True,
            'emails_envoyes': emails_envoyes,
            'total_destinataires': len(destinataires)
        }
        
    except Exception as e:
        print(f"Erreur lors de l'envoi des notifications d'étape terminée : {e}")
        return {'success': False, 'error': str(e)}


def envoyer_notification_affectation_module(module, affectations_creees, utilisateur_assigneur, request=None):
    """
    Envoie une notification par email aux utilisateurs affectés à un module
    
    Args:
        module: Instance ModuleProjet
        affectations_creees: Liste des AffectationModule créées
        utilisateur_assigneur: Utilisateur qui a fait l'affectation
        request: Objet request Django (optionnel)
    
    Returns:
        dict: Résultat de l'envoi avec le nombre d'emails envoyés
    """
    try:
        if not affectations_creees:
            return {'success': False, 'error': 'Aucune affectation à notifier'}
        
        # Récupérer les informations de contexte
        adresse_ip = '127.0.0.1'
        if request:
            adresse_ip = get_client_ip(request)
        
        emails_envoyes = 0
        total_destinataires = len(affectations_creees)
        
        for affectation in affectations_creees:
            if not affectation.utilisateur.email:
                continue
            
            # Préparer le contexte pour l'email
            context = {
                'affectation': affectation,
                'module': module,
                'projet': module.projet,
                'utilisateur_assigneur': utilisateur_assigneur,
                'utilisateur_affecte': affectation.utilisateur,
                'role_module': affectation.get_role_module_display(),
                'date_affectation': affectation.date_affectation,
                'site_name': 'SI-Gouvernance JCM',
                'adresse_ip': adresse_ip,
            }
            
            # Sujet de l'email
            sujet = f"[SI-Gouvernance] Affectation au module : {module.nom} - {module.projet.nom}"
            
            # Corps de l'email en texte brut
            permissions_info = ""
            if affectation.role_module == 'RESPONSABLE':
                permissions_info = """
Vos permissions en tant que Responsable :
- Créer des tâches dans ce module
- Assigner des tâches aux contributeurs
- Voir toutes les tâches du module
- Terminer toutes les tâches du module"""
            elif affectation.role_module == 'CONTRIBUTEUR':
                permissions_info = """
Vos permissions en tant que Contributeur :
- Voir les tâches qui vous sont assignées
- Terminer les tâches qui vous sont assignées
- Collaborer avec le responsable du module"""
            
            message_text = f"""
Bonjour {affectation.utilisateur.get_full_name()},

Vous avez été affecté(e) au module "{module.nom}" du projet "{module.projet.nom}".

Détails de l'affectation :
- Module : {module.nom}
- Projet : {module.projet.nom}
- Client : {module.projet.client}
- Votre rôle : {affectation.get_role_module_display()}
- Affecté par : {utilisateur_assigneur.get_full_name()}
- Date d'affectation : {affectation.date_affectation.strftime('%d/%m/%Y à %H:%M')}

Description du module :
{module.description}
{permissions_info}

Connectez-vous à SI-Gouvernance pour consulter les détails du module et commencer à travailler.

Cordialement,
L'équipe SI-Gouvernance JCM

---
Ceci est un email automatique, merci de ne pas y répondre.
            """.strip()
            
            try:
                send_mail(
                    subject=sujet,
                    message=message_text,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@si-gouvernance.com'),
                    recipient_list=[affectation.utilisateur.email],
                    fail_silently=False,
                )
                emails_envoyes += 1
                
            except Exception as e:
                print(f"Erreur lors de l'envoi à {affectation.utilisateur.email}: {e}")
                continue
        
        return {
            'success': True,
            'emails_envoyes': emails_envoyes,
            'total_destinataires': total_destinataires
        }
        
    except Exception as e:
        print(f"Erreur lors de l'envoi des notifications d'affectation de module : {e}")
        return {'success': False, 'error': str(e)}


def creer_notification_affectation_module(module, affectations_creees, utilisateur_assigneur):
    """
    Crée des notifications in-app pour les affectations de module
    
    Args:
        module: Instance ModuleProjet
        affectations_creees: Liste des AffectationModule créées
        utilisateur_assigneur: Utilisateur qui a fait l'affectation
    
    Returns:
        int: Nombre de notifications créées
    """
    try:
        from .models import NotificationModule
        
        notifications_creees = 0
        
        for affectation in affectations_creees:
            # Ne pas notifier l'utilisateur qui fait l'affectation
            if affectation.utilisateur == utilisateur_assigneur:
                continue
            
            # Préparer le titre et message selon le rôle
            if affectation.role_module == 'RESPONSABLE':
                titre = f"Vous êtes responsable du module : {module.nom}"
                message = f"Vous avez été désigné(e) responsable du module '{module.nom}' du projet '{module.projet.nom}'. Vous pouvez maintenant créer des tâches et les assigner aux contributeurs."
            else:
                titre = f"Vous êtes contributeur du module : {module.nom}"
                message = f"Vous avez été ajouté(e) comme contributeur au module '{module.nom}' du projet '{module.projet.nom}'. Vous recevrez des tâches à réaliser de la part du responsable."
            
            # Créer la notification
            NotificationModule.objects.create(
                destinataire=affectation.utilisateur,
                module=module,
                type_notification='AFFECTATION_MODULE',
                titre=titre,
                message=message,
                emetteur=utilisateur_assigneur,
                donnees_contexte={
                    'module_id': str(module.id),
                    'module_nom': module.nom,
                    'projet_id': str(module.projet.id),
                    'projet_nom': module.projet.nom,
                    'role_module': affectation.role_module,
                    'date_affectation': affectation.date_affectation.isoformat(),
                    'assigneur_nom': utilisateur_assigneur.get_full_name(),
                }
            )
            notifications_creees += 1
        
        return notifications_creees
        
    except Exception as e:
        print(f"Erreur lors de la création des notifications de module : {e}")
        return 0
def creer_notification_retrait_module(module, affectation, retire_par):
    """Créer une notification pour le retrait d'un module"""
    try:
        from django.apps import apps
        NotificationModule = apps.get_model('core', 'NotificationModule')
        
        # Créer la notification pour l'utilisateur retiré
        NotificationModule.objects.create(
            destinataire=affectation.utilisateur,
            module=module,
            type_notification='RETRAIT_MODULE',
            titre=f'Retrait du module {module.nom}',
            message=f'Vous avez été retiré du module "{module.nom}" par {retire_par.get_full_name()}.',
            emetteur=retire_par,
            donnees_contexte={
                'module_id': str(module.id),
                'module_nom': module.nom,
                'ancien_role': affectation.role_module,
                'retire_par': retire_par.get_full_name(),
                'date_retrait': timezone.now().isoformat()
            }
        )
        
    except Exception as e:
        # Ne pas faire échouer l'opération principale
        pass