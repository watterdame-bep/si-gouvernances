"""
Configuration Celery pour SI-Gouvernance
Architecture production-ready avec support Docker

Ce module configure:
- Celery worker pour tâches asynchrones
- Celery Beat pour tâches planifiées (toutes les 4 heures)
- Redis comme broker et backend de résultats
- Retry automatique en cas d'échec
- Protection contre exécutions multiples
- Logs détaillés
"""

import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')

# Initialisation de l'application Celery
app = Celery('si_gouvernance')

# Configuration depuis Django settings avec namespace CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-découverte des tâches dans les apps Django
app.autodiscover_tasks()


# ============================================================================
# CONFIGURATION DES TÂCHES PLANIFIÉES (CELERY BEAT)
# ============================================================================
# Toutes les tâches s'exécutent toutes les 4 heures (0h, 4h, 8h, 12h, 16h, 20h)
# ============================================================================

app.conf.beat_schedule = {
    # ========================================================================
    # VÉRIFICATION DES ÉCHÉANCES DE PROJETS
    # ========================================================================
    # Vérifie: J-7, J-3, J-1, et projets en retard
    # Envoie des alertes aux responsables de projets
    'check-project-deadlines-every-4h': {
        'task': 'core.tasks.check_project_deadlines_task',
        'schedule': crontab(minute=0, hour='*/4'),  # Toutes les 4 heures
        'options': {
            'expires': 3600 * 3,  # Expire après 3h (avant la prochaine exécution)
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 60,  # 1 minute
                'interval_step': 60,   # +1 minute à chaque retry
                'interval_max': 300,   # Max 5 minutes
            }
        }
    },
    
    # ========================================================================
    # VÉRIFICATION DES RETARDS D'ÉTAPES
    # ========================================================================
    # Vérifie les étapes dont la date de fin prévue est dépassée
    # Envoie des alertes aux responsables de projets
    'check-stage-delays-every-4h': {
        'task': 'core.tasks.check_stage_delays_task',
        'schedule': crontab(minute=5, hour='*/4'),  # Toutes les 4h + 5min
        'options': {
            'expires': 3600 * 3,
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 60,
                'interval_step': 60,
                'interval_max': 300,
            }
        }
    },
    
    # ========================================================================
    # VÉRIFICATION DES TÂCHES EN RETARD
    # ========================================================================
    # Vérifie les tâches dont la date d'échéance est dépassée
    # Envoie des alertes aux responsables de projets
    'check-task-deadlines-every-4h': {
        'task': 'core.tasks.check_task_deadlines_task',
        'schedule': crontab(minute=10, hour='*/4'),  # Toutes les 4h + 10min
        'options': {
            'expires': 3600 * 3,
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 60,
                'interval_step': 60,
                'interval_max': 300,
            }
        }
    },
    
    # ========================================================================
    # VÉRIFICATION DES DÉPASSEMENTS DE BUDGET
    # ========================================================================
    # Vérifie si le budget consommé dépasse le budget prévu
    # Envoie des alertes aux responsables de projets
    'check-budget-every-4h': {
        'task': 'core.tasks.check_budget_task',
        'schedule': crontab(minute=15, hour='*/4'),  # Toutes les 4h + 15min
        'options': {
            'expires': 3600 * 3,
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 60,
                'interval_step': 60,
                'interval_max': 300,
            }
        }
    },
    
    # ========================================================================
    # VÉRIFICATION DES EXPIRATIONS DE CONTRATS
    # ========================================================================
    # Vérifie les contrats expirant dans 30 jours ou déjà expirés
    # Envoie des alertes aux responsables de projets
    'check-contract-expiration-every-4h': {
        'task': 'core.tasks.check_contract_expiration_task',
        'schedule': crontab(minute=20, hour='*/4'),  # Toutes les 4h + 20min
        'options': {
            'expires': 3600 * 3,
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 60,
                'interval_step': 60,
                'interval_max': 300,
            }
        }
    },
}


# ============================================================================
# CONFIGURATION GLOBALE DE CELERY
# ============================================================================

app.conf.update(
    # Timezone
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    
    # Sérialisation
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Résultats
    result_expires=3600 * 24,  # Les résultats expirent après 24h
    result_extended=True,
    
    # Worker
    worker_prefetch_multiplier=1,  # Une tâche à la fois pour éviter surcharge
    worker_max_tasks_per_child=1000,  # Redémarre le worker après 1000 tâches
    
    # Tâches
    task_acks_late=True,  # Acknowledge après exécution (pas avant)
    task_reject_on_worker_lost=True,  # Rejeter si worker crash
    task_track_started=True,  # Tracker le début d'exécution
    
    # Logs
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Beat
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    beat_sync_every=1,  # Sync avec la DB toutes les 1 seconde
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
