# -*- coding: utf-8 -*-
"""
Vues personnalisées pour la réinitialisation de mot de passe
Avec audit, sécurité renforcée et notifications email
"""

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView
)
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.urls import reverse_lazy
from django.conf import settings
from .utils import enregistrer_audit
import logging

logger = logging.getLogger(__name__)

Utilisateur = get_user_model()


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CustomPasswordResetView(PasswordResetView):
    """
    Vue personnalisée pour la demande de réinitialisation
    - Audit de la demande
    - Email HTML professionnel
    - Logging de l'IP
    """
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        """Traitement après validation du formulaire"""
        email = form.cleaned_data.get('email')
        ip_address = get_client_ip(self.request)
        
        # Vérifier si l'utilisateur existe
        try:
            user = Utilisateur.objects.get(email=email, is_active=True)
            
            # Audit de la demande
            enregistrer_audit(
                utilisateur=user,
                type_action='DEMANDE_RESET_PASSWORD',
                description=f'Demande de réinitialisation de mot de passe depuis {ip_address}',
                request=self.request,
                donnees_apres={'email': email, 'ip': ip_address}
            )
            
            logger.info(f"Demande de réinitialisation de mot de passe pour {email} depuis {ip_address}")
            
        except Utilisateur.DoesNotExist:
            # Ne pas révéler que l'email n'existe pas (sécurité)
            logger.warning(f"Tentative de réinitialisation pour email inexistant: {email} depuis {ip_address}")
        
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Ajouter des données au contexte de l'email"""
        context = super().get_context_data(**kwargs)
        context['timestamp'] = timezone.now()
        context['ip_address'] = get_client_ip(self.request)
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vue personnalisée pour la confirmation de réinitialisation
    - Audit du changement
    - Invalidation des sessions
    - Email de confirmation
    """
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        """Traitement après validation du nouveau mot de passe"""
        user = form.user
        ip_address = get_client_ip(self.request)
        
        # Audit du changement
        enregistrer_audit(
            utilisateur=user,
            type_action='RESET_PASSWORD_SUCCESS',
            description=f'Mot de passe réinitialisé avec succès depuis {ip_address}',
            request=self.request,
            donnees_apres={'ip': ip_address}
        )
        
        logger.info(f"Mot de passe réinitialisé pour {user.email} depuis {ip_address}")
        
        # Invalider toutes les sessions actives de l'utilisateur
        self.invalidate_user_sessions(user)
        
        # Envoyer email de confirmation
        self.send_password_changed_email(user, ip_address)
        
        return super().form_valid(form)
    
    def invalidate_user_sessions(self, user):
        """Invalide toutes les sessions actives de l'utilisateur"""
        try:
            # Récupérer toutes les sessions actives
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            
            for session in sessions:
                session_data = session.get_decoded()
                if session_data.get('_auth_user_id') == str(user.id):
                    session.delete()
            
            logger.info(f"Sessions invalidées pour l'utilisateur {user.email}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'invalidation des sessions: {str(e)}")
    
    def send_password_changed_email(self, user, ip_address):
        """Envoie un email de confirmation de changement de mot de passe"""
        try:
            # Contexte pour le template
            context = {
                'user': user,
                'protocol': 'https' if self.request.is_secure() else 'http',
                'domain': self.request.get_host(),
                'timestamp': timezone.now(),
                'ip_address': ip_address,
            }
            
            # Rendu du template HTML
            html_message = render_to_string('emails/password_changed_confirmation.html', context)
            plain_message = strip_tags(html_message)
            
            # Envoi de l'email
            send_mail(
                subject='[SI-Gouvernance] Votre mot de passe a été modifié',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Email de confirmation envoyé à {user.email}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email de confirmation: {str(e)}")


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Vue personnalisée pour la page de confirmation d'envoi"""
    template_name = 'registration/password_reset_done.html'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Vue personnalisée pour la page de succès final"""
    template_name = 'registration/password_reset_complete.html'
