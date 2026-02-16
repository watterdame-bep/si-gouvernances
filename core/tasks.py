"""
Tâches Celery pour SI-Gouvernance
Toutes les tâches d'alertes automatiques sont définies ici

Architecture:
- Chaque tâche appelle une commande Django management
- Retry automatique en cas d'échec
- Logs détaillés pour monitoring
- Protection contre exécutions multiples (task_id unique)
- Gestion robuste des exceptions

Planification: Toutes les 4 heures (0h, 4h, 8h, 12h, 16h, 20h)
"""

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

# Configuration du logger
logger = logging.getLogger('celery.tasks')


# ============================================================================
# DÉCORATEUR COMMUN POUR TOUTES LES TÂCHES
# ============================================================================
# Configuration:
# - bind=True: Accès à self (task instance)
# - autoretry_for: Retry automatique sur ces exceptions
# - retry_kwargs: Configuration du retry
# - max_retries: Nombre maximum de tentatives
# - default_retry_delay: Délai entre les tentatives
# ============================================================================

TASK_CONFIG = {
    'bind': True,
    'autoretry_for': (Exception,),
    'retry_kwargs': {'max_retries': 3, 'countdown': 60},
    'max_retries': 3,
    'default_retry_delay': 60,
    'acks_late': True,  # Acknowledge après exécution
    'reject_on_worker_lost': True,  # Rejeter si worker crash
}


# ============================================================================
# TÂCHE 1: VÉRIFICATION DES ÉCHÉANCES DE PROJETS
# ============================================================================
@shared_task(**TASK_CONFIG, name='core.tasks.check_project_deadlines_task')
def check_project_deadlines_task(self):
    """
    Vérifie les échéances de projets et envoie des alertes
    
    Vérifie:
    - Projets à J-7 de l'échéance
    - Projets à J-3 de l'échéance
    - Projets à J-1 de l'échéance
    - Projets en retard (échéance dépassée)
    
    Envoie des AlerteProjet avec notification email automatique
    aux responsables de projets concernés.
    
    Planification: Toutes les 4 heures
    """
    task_id = self.request.id
    start_time = timezone.now()
    
    logger.info(f"[{task_id}] 🚀 Démarrage: Vérification des échéances de projets")
    logger.info(f"[{task_id}] ⏰ Heure de démarrage: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Exécution de la commande Django
        call_command('check_project_deadlines')
        
        # Calcul du temps d'exécution
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{task_id}] ✅ Succès: Vérification des échéances de projets terminée")
        logger.info(f"[{task_id}] ⏱️  Durée d'exécution: {duration:.2f} secondes")
        
        return {
            'status': 'success',
            'task': 'check_project_deadlines',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
        }
        
    except Exception as e:
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"[{task_id}] ❌ Erreur: {str(e)}")
        logger.error(f"[{task_id}] ⏱️  Durée avant échec: {duration:.2f} secondes")
        logger.error(f"[{task_id}] 🔄 Tentative {self.request.retries + 1}/{self.max_retries}")
        
        # Le retry est automatique grâce à autoretry_for
        raise


# ============================================================================
# TÂCHE 2: VÉRIFICATION DES RETARDS D'ÉTAPES
# ============================================================================
@shared_task(**TASK_CONFIG, name='core.tasks.check_stage_delays_task')
def check_stage_delays_task(self):
    """
    Vérifie les retards d'étapes et envoie des alertes
    
    Vérifie:
    - Étapes dont la date de fin prévue est dépassée
    - Étapes en cours avec retard
    
    Envoie des NotificationEtape avec notification email automatique
    aux responsables de projets concernés.
    
    Planification: Toutes les 4 heures (+ 5 minutes)
    """
    task_id = self.request.id
    start_time = timezone.now()
    
    logger.info(f"[{task_id}] 🚀 Démarrage: Vérification des retards d'étapes")
    logger.info(f"[{task_id}] ⏰ Heure de démarrage: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        call_command('check_stage_delays')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{task_id}] ✅ Succès: Vérification des retards d'étapes terminée")
        logger.info(f"[{task_id}] ⏱️  Durée d'exécution: {duration:.2f} secondes")
        
        return {
            'status': 'success',
            'task': 'check_stage_delays',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
        }
        
    except Exception as e:
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"[{task_id}] ❌ Erreur: {str(e)}")
        logger.error(f"[{task_id}] ⏱️  Durée avant échec: {duration:.2f} secondes")
        logger.error(f"[{task_id}] 🔄 Tentative {self.request.retries + 1}/{self.max_retries}")
        
        raise


# ============================================================================
# TÂCHE 3: VÉRIFICATION DES TÂCHES EN RETARD
# ============================================================================
@shared_task(**TASK_CONFIG, name='core.tasks.check_task_deadlines_task')
def check_task_deadlines_task(self):
    """
    Vérifie les tâches en retard et envoie des alertes
    
    Vérifie:
    - Tâches dont la date d'échéance est dépassée
    - Tâches non terminées en retard
    
    Envoie des AlerteProjet avec notification email automatique
    aux responsables de projets concernés.
    
    Planification: Toutes les 4 heures (+ 10 minutes)
    """
    task_id = self.request.id
    start_time = timezone.now()
    
    logger.info(f"[{task_id}] 🚀 Démarrage: Vérification des tâches en retard")
    logger.info(f"[{task_id}] ⏰ Heure de démarrage: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        call_command('check_task_deadlines')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{task_id}] ✅ Succès: Vérification des tâches en retard terminée")
        logger.info(f"[{task_id}] ⏱️  Durée d'exécution: {duration:.2f} secondes")
        
        return {
            'status': 'success',
            'task': 'check_task_deadlines',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
        }
        
    except Exception as e:
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"[{task_id}] ❌ Erreur: {str(e)}")
        logger.error(f"[{task_id}] ⏱️  Durée avant échec: {duration:.2f} secondes")
        logger.error(f"[{task_id}] 🔄 Tentative {self.request.retries + 1}/{self.max_retries}")
        
        raise


# ============================================================================
# TÂCHE 4: VÉRIFICATION DES DÉPASSEMENTS DE BUDGET
# ============================================================================
@shared_task(**TASK_CONFIG, name='core.tasks.check_budget_task')
def check_budget_task(self):
    """
    Vérifie les dépassements de budget et envoie des alertes
    
    Vérifie:
    - Projets dont le budget consommé dépasse le budget prévu
    
    Envoie des AlerteProjet avec notification email automatique
    aux responsables de projets concernés.
    
    Planification: Toutes les 4 heures (+ 15 minutes)
    """
    task_id = self.request.id
    start_time = timezone.now()
    
    logger.info(f"[{task_id}] 🚀 Démarrage: Vérification des dépassements de budget")
    logger.info(f"[{task_id}] ⏰ Heure de démarrage: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        call_command('check_budget')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{task_id}] ✅ Succès: Vérification des budgets terminée")
        logger.info(f"[{task_id}] ⏱️  Durée d'exécution: {duration:.2f} secondes")
        
        return {
            'status': 'success',
            'task': 'check_budget',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
        }
        
    except Exception as e:
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"[{task_id}] ❌ Erreur: {str(e)}")
        logger.error(f"[{task_id}] ⏱️  Durée avant échec: {duration:.2f} secondes")
        logger.error(f"[{task_id}] 🔄 Tentative {self.request.retries + 1}/{self.max_retries}")
        
        raise


# ============================================================================
# TÂCHE 5: VÉRIFICATION DES EXPIRATIONS DE CONTRATS
# ============================================================================
@shared_task(**TASK_CONFIG, name='core.tasks.check_contract_expiration_task')
def check_contract_expiration_task(self):
    """
    Vérifie les expirations de contrats et envoie des alertes
    
    Vérifie:
    - Contrats expirant dans 30 jours
    - Contrats déjà expirés
    
    Envoie des AlerteProjet avec notification email automatique
    aux responsables de projets concernés.
    
    Planification: Toutes les 4 heures (+ 20 minutes)
    """
    task_id = self.request.id
    start_time = timezone.now()
    
    logger.info(f"[{task_id}] 🚀 Démarrage: Vérification des expirations de contrats")
    logger.info(f"[{task_id}] ⏰ Heure de démarrage: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        call_command('check_contract_expiration')
        
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"[{task_id}] ✅ Succès: Vérification des contrats terminée")
        logger.info(f"[{task_id}] ⏱️  Durée d'exécution: {duration:.2f} secondes")
        
        return {
            'status': 'success',
            'task': 'check_contract_expiration',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
        }
        
    except Exception as e:
        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.error(f"[{task_id}] ❌ Erreur: {str(e)}")
        logger.error(f"[{task_id}] ⏱️  Durée avant échec: {duration:.2f} secondes")
        logger.error(f"[{task_id}] 🔄 Tentative {self.request.retries + 1}/{self.max_retries}")
        
        raise


# ============================================================================
# TÂCHE DE TEST
# ============================================================================
@shared_task(name='core.tasks.test_celery_task')
def test_celery_task():
    """
    Tâche de test pour vérifier que Celery fonctionne
    
    Usage:
        from core.tasks import test_celery_task
        result = test_celery_task.delay()
        print(result.get())
    """
    logger.info("🧪 Test Celery: Tâche exécutée avec succès!")
    return {
        'status': 'success',
        'message': 'Celery fonctionne correctement!',
        'timestamp': timezone.now().isoformat(),
    }
