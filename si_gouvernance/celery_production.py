"""
Configuration Celery Production pour SI-Gouvernance
Architecture production-ready avec fréquence configurable

Ce module configure:
- Celery worker pour tâches asynchrones
- Celery Beat pour tâches planifiées (fréquence configurable)
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
# Fréquence configurable via variable d'environnement CELERY_ALERTS_FREQUENCY_HOURS
# Par défaut: toutes les 4 heures (0h, 4h, 8h, 12h, 16h, 20h)
# ============================================================================

def get_alerts_frequency():
    """Récupère la fréquence des alertes depuis les settings"""
    try:
        from django.conf import settings
        return int(getattr(settings, 'CELERY_ALERTS_FREQUENCY_HOURS', 4))
    except:
        return 4

ALERTS_FREQUENCY_HOURS = get_alerts_frequency()

app.conf.beat_schedule = {
    # ========================================================================
    # VÉRIFICATION DES ÉCHÉANCES DE PROJETS
    # ========================================================================
    'check-project-deadlines': {
        'task': 'core.tasks.check_project_deadlines_task',
        'schedule': crontab(minute=0, hour=f'*/{ALERTS_FREQUENCY_HOURS}'),
        'options': {
            'expires': 3600 * (ALERTS_FREQUENCY_HOURS - 1),
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
    # VÉRIFICATION DES RETARDS D'ÉTAPES
    # ========================================================================
    'check-stage-delays': {
        'task': 'core.tasks.check_stage_delays_task',
        'schedule': crontab(minute=5, hour=f'*/{ALERTS_FREQUENCY_HOURS}'),
        'options': {
            'expires': 3600 * (ALERTS_FREQUENCY_HOURS - 1),
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
    'check-task-deadlines': {
        'task': 'core.tasks.check_task_deadlines_task',
        'schedule': crontab(minute=10, hour=f'*/{ALERTS_FREQUENCY_HOURS}'),
        'options': {
            'expires': 3600 * (ALERTS_FREQUENCY_HOURS - 1),
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
    'check-budget': {
        'task': 'core.tasks.check_budget_task',
        'schedule': crontab(minute=15, hour=f'*/{ALERTS_FREQUENCY_HOURS}'),
        'options': {
            'expires': 3600 * (ALERTS_FREQUENCY_HOURS - 1),
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
    'check-contract-expiration': {
        'task': 'core.tasks.check_contract_expiration_task',
        'schedule': crontab(minute=20, hour=f'*/{ALERTS_FREQUENCY_HOURS}'),
        'options': {
            'expires': 3600 * (ALERTS_FREQUENCY_HOURS - 1),
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
    result_expires=3600 * 24,
    result_extended=True,
    
    # Worker
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Tâches
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    
    # Logs
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    
    # Beat
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    beat_sync_every=1,
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de debug pour tester Celery"""
    print(f'Request: {self.request!r}')
