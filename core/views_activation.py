# -*- coding: utf-8 -*-
"""
Vues pour le système d'activation sécurisé des comptes utilisateurs.

Ce module gère le flux complet d'activation :
1. Génération et envoi du lien d'activation
2. Validation du token et affichage du formulaire
3. Activation du compte avec définition du mot de passe
4. Renvoi du lien d'activation si nécessaire
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Utilisateur
from .models_activation import AccountActivationToken, AccountActivationLog
from .utils import enregistrer_audit, require_super_admin


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Récupère le User-Agent du client"""
    return request.META.get('HTTP_USER_AGENT', '')


def envoyer_email_activation(user, token_plain, request):
    """
    Envoie l'email d'activation avec le lien sécurisé.
    
    Args:
        user: Instance de Utilisateur
        token_plain: Token en clair (non hashé)
        request: Requête HTTP pour construire l'URL absolue
    
    Returns:
        bool: True si l'email a été envoyé avec succès
    """
    # Encoder l'ID utilisateur en base64
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Construire le lien d'activation
    activation_url = request.build_absolute_uri(
        f'/activate-account/{uidb64}/{token_plain}/'
    )
    
    # Préparer le contenu de l'email
    subject = 'Activation de votre compte - SI Gouvernance'
    
    message = f"""
Bonjour {user.get_full_name()},

Un compte utilisateur a été créé pour vous sur la plateforme SI Gouvernance.

Pour activer votre compte et définir votre mot de passe, veuillez cliquer sur le lien ci-dessous :

{activation_url}

⚠️ IMPORTANT :
- Ce lien est valide pendant 24 heures
- Vous devrez définir un mot de passe fort lors de l'activation
- Ce lien ne peut être utilisé qu'une seule fois

Si vous n'avez pas demandé la création de ce compte, veuillez ignorer cet email.

Cordialement,
L'équipe SI Gouvernance
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {str(e)}")
        return False


def activate_account_view(request, uidb64, token):
    """
    Affiche le formulaire de création de mot de passe pour l'activation.
    
    Cette vue :
    1. Vérifie la validité du token
    2. Affiche le formulaire de création de mot de passe
    3. Gère les erreurs (token expiré, invalide, etc.)
    """
    # Décoder l'ID utilisateur
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        messages.error(request, 'Lien d\'activation invalide.')
        return render(request, 'core/activation_error.html', {
            'error_type': 'invalid_link',
            'error_message': 'Le lien d\'activation est invalide.'
        })
    
    # Vérifier si le compte est déjà actif
    if user.is_active:
        messages.info(request, 'Votre compte est déjà activé. Vous pouvez vous connecter.')
        return redirect('login')
    
    # Récupérer l'IP du client
    ip_address = get_client_ip(request)
    
    # Vérifier le token
    token_instance = AccountActivationToken.verify_token(user, token, ip_address)
    
    if not token_instance:
        # Token invalide ou expiré
        AccountActivationLog.objects.create(
            user=user,
            action='ACTIVATION_FAILED',
            ip_address=ip_address,
            user_agent=get_user_agent(request),
            details='Token invalide ou expiré'
        )
        
        messages.error(request, 'Le lien d\'activation est invalide ou a expiré.')
        return render(request, 'core/activation_error.html', {
            'error_type': 'expired_token',
            'error_message': 'Le lien d\'activation a expiré ou est invalide.',
            'user': user,
            'can_resend': True
        })
    
    # Vérifier le nombre de tentatives
    if token_instance.attempts >= 5:
        AccountActivationLog.objects.create(
            user=user,
            token=token_instance,
            action='TOO_MANY_ATTEMPTS',
            ip_address=ip_address,
            user_agent=get_user_agent(request),
            details='Trop de tentatives d\'activation'
        )
        
        messages.error(request, 'Trop de tentatives. Veuillez demander un nouveau lien.')
        return render(request, 'core/activation_error.html', {
            'error_type': 'too_many_attempts',
            'error_message': 'Trop de tentatives d\'activation.',
            'user': user,
            'can_resend': True
        })
    
    # Logger la tentative d'activation
    AccountActivationLog.objects.create(
        user=user,
        token=token_instance,
        action='ACTIVATION_ATTEMPT',
        ip_address=ip_address,
        user_agent=get_user_agent(request),
        details='Affichage du formulaire d\'activation'
    )
    
    # Afficher le formulaire
    context = {
        'user': user,
        'uidb64': uidb64,
        'token': token,
        'expires_at': token_instance.expires_at,
    }
    
    return render(request, 'core/activate_account.html', context)


@require_http_methods(["POST"])
def activate_account_submit(request, uidb64, token):
    """
    Traite la soumission du formulaire d'activation.
    
    Cette vue :
    1. Valide le mot de passe
    2. Active le compte
    3. Invalide le token
    4. Enregistre l'audit
    """
    # Décoder l'ID utilisateur
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Utilisateur.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Utilisateur.DoesNotExist):
        return JsonResponse({
            'success': False,
            'error': 'Lien d\'activation invalide.'
        })
    
    # Vérifier si le compte est déjà actif
    if user.is_active:
        return JsonResponse({
            'success': False,
            'error': 'Votre compte est déjà activé.'
        })
    
    # Récupérer l'IP du client
    ip_address = get_client_ip(request)
    
    # Vérifier le token
    token_instance = AccountActivationToken.verify_token(user, token, ip_address)
    
    if not token_instance:
        return JsonResponse({
            'success': False,
            'error': 'Le lien d\'activation est invalide ou a expiré.'
        })
    
    # Récupérer les mots de passe
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')
    
    # Validation
    if not password1 or not password2:
        return JsonResponse({
            'success': False,
            'error': 'Veuillez remplir tous les champs.'
        })
    
    if password1 != password2:
        return JsonResponse({
            'success': False,
            'error': 'Les mots de passe ne correspondent pas.'
        })
    
    # Valider la force du mot de passe
    try:
        validate_password(password1, user)
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': ' '.join(e.messages)
        })
    
    # Tout est OK, activer le compte
    try:
        with transaction.atomic():
            # Définir le mot de passe
            user.set_password(password1)
            user.is_active = True
            user.statut_actif = True
            user.save()
            
            # Marquer le token comme utilisé
            token_instance.mark_as_used()
            
            # Logger le succès
            AccountActivationLog.objects.create(
                user=user,
                token=token_instance,
                action='ACTIVATION_SUCCESS',
                ip_address=ip_address,
                user_agent=get_user_agent(request),
                details='Compte activé avec succès'
            )
            
            # Audit système
            enregistrer_audit(
                utilisateur=user,
                type_action='ACTIVATION_COMPTE',
                description=f'Activation du compte {user.username}',
                request=request,
                donnees_apres={
                    'username': user.username,
                    'email': user.email,
                    'ip_address': ip_address
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Votre compte a été activé avec succès !',
            'redirect_url': '/login/'
        })
        
    except Exception as e:
        AccountActivationLog.objects.create(
            user=user,
            token=token_instance,
            action='ACTIVATION_FAILED',
            ip_address=ip_address,
            user_agent=get_user_agent(request),
            details=f'Erreur lors de l\'activation : {str(e)}'
        )
        
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'activation : {str(e)}'
        })


@require_super_admin
@require_http_methods(["POST"])
def resend_activation_link(request, user_id):
    """
    Renvoie un nouveau lien d'activation pour un utilisateur.
    
    Cette vue :
    1. Invalide l'ancien token
    2. Génère un nouveau token
    3. Envoie un nouvel email
    4. Enregistre l'audit
    """
    user = get_object_or_404(Utilisateur, id=user_id)
    
    # Vérifier que le compte n'est pas déjà actif
    if user.is_active:
        return JsonResponse({
            'success': False,
            'error': 'Ce compte est déjà activé.'
        })
    
    try:
        # Récupérer l'IP
        ip_address = get_client_ip(request)
        
        # Créer un nouveau token (invalide automatiquement les anciens)
        token_instance, token_plain = AccountActivationToken.create_for_user(user, ip_address)
        
        # Envoyer l'email
        email_sent = envoyer_email_activation(user, token_plain, request)
        
        if not email_sent:
            return JsonResponse({
                'success': False,
                'error': 'Erreur lors de l\'envoi de l\'email.'
            })
        
        # Logger l'action
        AccountActivationLog.objects.create(
            user=user,
            token=token_instance,
            action='TOKEN_RESENT',
            ip_address=ip_address,
            user_agent=get_user_agent(request),
            details=f'Lien renvoyé par {request.user.username}'
        )
        
        # Audit système
        enregistrer_audit(
            utilisateur=request.user,
            type_action='RENVOI_LIEN_ACTIVATION',
            description=f'Renvoi du lien d\'activation pour {user.username}',
            request=request,
            donnees_apres={
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email
            }
        )
        
        messages.success(request, f'Un nouveau lien d\'activation a été envoyé à {user.email}')
        return JsonResponse({
            'success': True,
            'message': 'Lien d\'activation renvoyé avec succès.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur : {str(e)}'
        })
