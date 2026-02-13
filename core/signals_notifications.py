"""
Signaux Django pour l'envoi automatique d'emails lors de la création de notifications
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NotificationTache, NotificationEtape, NotificationModule, NotificationProjet, AlerteProjet
from .utils_notifications_email import (
    envoyer_email_notification_tache,
    envoyer_email_notification_etape,
    envoyer_email_notification_module,
    envoyer_email_notification_projet,
    envoyer_email_alerte_projet
)


@receiver(post_save, sender=NotificationTache)
def envoyer_email_notification_tache_signal(sender, instance, created, **kwargs):
    """
    Envoie automatiquement un email lors de la création d'une NotificationTache
    """
    if created:  # Seulement pour les nouvelles notifications
        try:
            envoyer_email_notification_tache(instance)
        except Exception as e:
            # Ne pas faire échouer la création de la notification si l'email échoue
            print(f"Erreur lors de l'envoi de l'email pour NotificationTache {instance.id}: {e}")


@receiver(post_save, sender=NotificationEtape)
def envoyer_email_notification_etape_signal(sender, instance, created, **kwargs):
    """
    Envoie automatiquement un email lors de la création d'une NotificationEtape
    """
    if created:
        try:
            envoyer_email_notification_etape(instance)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email pour NotificationEtape {instance.id}: {e}")


@receiver(post_save, sender=NotificationModule)
def envoyer_email_notification_module_signal(sender, instance, created, **kwargs):
    """
    Envoie automatiquement un email lors de la création d'une NotificationModule
    """
    if created:
        try:
            envoyer_email_notification_module(instance)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email pour NotificationModule {instance.id}: {e}")


@receiver(post_save, sender=NotificationProjet)
def envoyer_email_notification_projet_signal(sender, instance, created, **kwargs):
    """
    Envoie automatiquement un email lors de la création d'une NotificationProjet
    """
    if created:
        try:
            envoyer_email_notification_projet(instance)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email pour NotificationProjet {instance.id}: {e}")


@receiver(post_save, sender=AlerteProjet)
def envoyer_email_alerte_projet_signal(sender, instance, created, **kwargs):
    """
    Envoie automatiquement un email lors de la création d'une AlerteProjet
    """
    if created:
        try:
            envoyer_email_alerte_projet(instance)
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email pour AlerteProjet {instance.id}: {e}")
