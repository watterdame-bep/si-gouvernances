# 🚀 Migration vers Celery - Fichiers prêts à l'emploi

## 📋 Vue d'ensemble

Ce document contient tous les fichiers nécessaires pour migrer vers Celery quand vous serez prêt. La logique métier reste dans `check_task_deadlines.py`, seul le déclencheur change.

## 📦 Installation

```bash
pip install celery redis
pip freeze > requirements.txt
```

## 📄 Fichiers à créer

### 1. `si_gouvernance/celery.py`

```python
"""
Configuration Celery pour SI-Gouvernance
"""
import os
from celery import Celery
from celery.schedules import crontab

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')

# Créer l'application Celery
app = Celery('si_gouvernance')

# Charger la configuration depuis Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les apps Django
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    # Vérification des échéances quotidienne à 8h00
    'check-task-deadlines-daily': {
        'task': 'core.tasks.check_task_deadlines',
        'schedule': crontab(hour=8, minute=0),
        'options': {
            'expires': 3600,  # Expire après 1h si pas exécutée
        }
    },
    
    # Exemple : Nettoyage des anciennes notifications (optionnel)
    # 'cleanup-old-notifications': {
    #     'task': 'core.tasks.cleanup_old_notifications',
    #     'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Lundi à 2h
    # },
}

# Configuration du timezone
app.conf.timezone = 'Europe/Paris'

# Configuration des résultats
app.conf.result_expires = 3600  # Les résultats expirent après 1h

# Configuration de la sérialisation
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']

# Configuration du retry
app.conf.task_acks_late = True  # Acknowledge après exécution
app.conf.task_reject_on_worker_lost = True  # Rejeter si worker crash

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
```

### 2. `core/tasks.py`

```python
"""
Tâches Celery pour l'application core
"""
from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='core.tasks.check_task_deadlines',
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def check_task_deadlines(self):
    """
    Tâche Celery pour vérifier les échéances des tâches
    
    Cette tâche appelle simplement le management command Django existant,
    ce qui permet de garder toute la logique métier au même endroit.
    
    En cas d'erreur, la tâche sera réessayée 3 fois avec un délai de 5 minutes.
    """
    try:
        logger.info("🔍 Démarrage de la vérification des échéances")
        
        # Appeler le management command existant
        call_command('check_task_deadlines')
        
        logger.info("✅ Vérification des échéances terminée avec succès")
        return {
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'message': 'Vérification des échéances terminée'
        }
        
    except Exception as exc:
        logger.error(f"❌ Erreur lors de la vérification des échéances: {exc}")
        
        # Réessayer la tâche
        raise self.retry(exc=exc)


@shared_task(name='core.tasks.cleanup_old_notifications')
def cleanup_old_notifications(days=30):
    """
    Tâche optionnelle pour nettoyer les anciennes notifications
    
    Args:
        days: Nombre de jours à conserver (par défaut 30)
    """
    try:
        from core.models import NotificationTache
        from datetime import timedelta
        
        date_limite = timezone.now() - timedelta(days=days)
        
        # Supprimer les notifications lues de plus de X jours
        deleted = NotificationTache.objects.filter(
            lue=True,
            date_creation__lt=date_limite
        ).delete()
        
        logger.info(f"🗑️ {deleted[0]} notifications supprimées (plus de {days} jours)")
        
        return {
            'status': 'success',
            'deleted': deleted[0],
            'days': days
        }
        
    except Exception as exc:
        logger.error(f"❌ Erreur lors du nettoyage: {exc}")
        raise


@shared_task(name='core.tasks.send_daily_summary')
def send_daily_summary():
    """
    Tâche optionnelle pour envoyer un résumé quotidien aux chefs de projet
    
    Cette tâche peut être ajoutée plus tard pour envoyer un email
    avec le résumé des tâches en cours, en retard, etc.
    """
    # TODO: Implémenter l'envoi de résumé quotidien
    logger.info("📧 Envoi du résumé quotidien (à implémenter)")
    pass
```

### 3. Modifier `si_gouvernance/__init__.py`

```python
"""
Configuration de l'application SI-Gouvernance
"""

# Importer Celery pour que Django le découvre
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 4. Ajouter dans `settings.py`

```python
# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# URL du broker (Redis)
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# URL du backend de résultats
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Formats acceptés
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Timezone
CELERY_TIMEZONE = 'Europe/Paris'
CELERY_ENABLE_UTC = False

# Configuration des résultats
CELERY_RESULT_EXPIRES = 3600  # 1 heure

# Configuration du worker
CELERY_WORKER_PREFETCH_MULTIPLIER = 4
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Configuration des logs
CELERY_WORKER_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
CELERY_WORKER_TASK_LOG_FORMAT = '[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s'

# Configuration du monitoring
CELERY_SEND_TASK_SENT_EVENT = True
CELERY_TRACK_STARTED = True

# ============================================================================
# LOGGING CONFIGURATION (ajouter Celery)
# ============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/celery.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'celery': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'core.tasks': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
```

### 5. `.env` (variables d'environnement)

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Redis Configuration (si nécessaire)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## 🚀 Démarrage

### Installation de Redis

**Windows** :
```bash
# Télécharger Redis depuis https://github.com/microsoftarchive/redis/releases
# Ou utiliser WSL2 avec Ubuntu
wsl --install
wsl
sudo apt update
sudo apt install redis-server
redis-server
```

**Linux** :
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker** :
```bash
docker run -d -p 6379:6379 redis:alpine
```

### Démarrage des services

**Terminal 1 : Redis**
```bash
redis-server
```

**Terminal 2 : Celery Worker**
```bash
cd E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
celery -A si_gouvernance worker -l info --pool=solo
```

**Terminal 3 : Celery Beat (Planificateur)**
```bash
cd E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
celery -A si_gouvernance beat -l info
```

**Terminal 4 : Django (optionnel)**
```bash
python manage.py runserver
```

### Monitoring avec Flower

```bash
# Installation
pip install flower

# Démarrage
celery -A si_gouvernance flower

# Accès : http://localhost:5555
```

## ✅ Tests

### Test 1 : Vérifier que Celery fonctionne

```bash
# Dans Django shell
python manage.py shell

>>> from si_gouvernance.celery import debug_task
>>> result = debug_task.delay()
>>> result.ready()  # True si terminé
>>> result.get()    # Résultat
```

### Test 2 : Tester la tâche de vérification

```bash
# Dans Django shell
python manage.py shell

>>> from core.tasks import check_task_deadlines
>>> result = check_task_deadlines.delay()
>>> result.ready()
>>> result.get()
```

### Test 3 : Vérifier le planning

```bash
# Dans Django shell
python manage.py shell

>>> from si_gouvernance.celery import app
>>> app.conf.beat_schedule
# Doit afficher les tâches planifiées
```

## 📊 Monitoring

### Logs Celery

```bash
# Voir les logs en temps réel
tail -f logs/celery.log
```

### Interface Flower

Accéder à http://localhost:5555 pour voir :
- Tâches en cours
- Tâches terminées
- Workers actifs
- Statistiques

### Django Admin (optionnel)

Installer django-celery-results pour voir les résultats dans l'admin :

```bash
pip install django-celery-results

# settings.py
INSTALLED_APPS += ['django_celery_results']
CELERY_RESULT_BACKEND = 'django-db'

# Migrations
python manage.py migrate django_celery_results
```

## 🔄 Migration depuis Planificateur Windows

1. **Installer Redis et Celery**
2. **Créer les fichiers ci-dessus**
3. **Tester en développement**
4. **Désactiver le Planificateur Windows**
5. **Démarrer Celery en production**

## 🎯 Avantages de Celery

- ✅ **Asynchrone** : Les tâches ne bloquent pas Django
- ✅ **Distribué** : Peut tourner sur plusieurs serveurs
- ✅ **Retry automatique** : Réessaye en cas d'erreur
- ✅ **Monitoring** : Interface Flower pour voir l'état
- ✅ **Scalable** : Ajouter des workers facilement
- ✅ **Multi-plateforme** : Windows, Linux, Mac

## 📝 Checklist de migration

- [ ] Redis installé et démarré
- [ ] Celery installé (`pip install celery redis`)
- [ ] Fichiers créés (celery.py, tasks.py, __init__.py)
- [ ] Settings.py mis à jour
- [ ] Test du worker : `celery -A si_gouvernance worker -l info`
- [ ] Test du beat : `celery -A si_gouvernance beat -l info`
- [ ] Test de la tâche : `check_task_deadlines.delay()`
- [ ] Flower installé et testé (optionnel)
- [ ] Planificateur Windows désactivé
- [ ] Documentation mise à jour

---

**Date** : 09/02/2026  
**Statut** : Prêt pour migration  
**Note** : Tous les fichiers sont prêts, il suffit de les créer quand vous serez prêt à migrer
