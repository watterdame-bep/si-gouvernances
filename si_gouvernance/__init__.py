"""
Initialisation de l'application SI-Gouvernance
Configure Celery pour qu'il soit chargé au démarrage de Django
"""

# Import de l'application Celery pour qu'elle soit disponible
from .celery import app as celery_app

__all__ = ('celery_app',)
