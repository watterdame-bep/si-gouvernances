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