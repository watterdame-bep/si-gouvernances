"""
Commande Django pour initialiser les tâches Celery Beat
Crée les tâches planifiées dans la base de données

Usage:
    python manage.py setup_celery_beat
"""

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = 'Initialise les tâches planifiées Celery Beat dans la base de données'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('  INITIALISATION DES TÂCHES CELERY BEAT'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # ====================================================================
        # PLANIFICATION: Toutes les 4 heures (0h, 4h, 8h, 12h, 16h, 20h)
        # ====================================================================
        
        # Créer le crontab pour "toutes les 4 heures"
        schedule_4h, created = CrontabSchedule.objects.get_or_create(
            minute='0',
            hour='*/4',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Planification créée: Toutes les 4 heures'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Planification existe déjà: Toutes les 4 heures'))
        
        self.stdout.write('')
        
        # ====================================================================
        # TÂCHES À CRÉER
        # ====================================================================
        
        tasks_config = [
            {
                'name': 'check-project-deadlines-every-4h',
                'task': 'core.tasks.check_project_deadlines_task',
                'description': 'Vérification des échéances de projets (J-7, J-3, J-1, retards)',
                'minute_offset': 0,
            },
            {
                'name': 'check-stage-delays-every-4h',
                'task': 'core.tasks.check_stage_delays_task',
                'description': 'Vérification des retards d\'étapes',
                'minute_offset': 5,
            },
            {
                'name': 'check-task-deadlines-every-4h',
                'task': 'core.tasks.check_task_deadlines_task',
                'description': 'Vérification des tâches en retard',
                'minute_offset': 10,
            },
            {
                'name': 'check-budget-every-4h',
                'task': 'core.tasks.check_budget_task',
                'description': 'Vérification des dépassements de budget',
                'minute_offset': 15,
            },
            {
                'name': 'check-contract-expiration-every-4h',
                'task': 'core.tasks.check_contract_expiration_task',
                'description': 'Vérification des expirations de contrats',
                'minute_offset': 20,
            },
        ]
        
        # Créer ou mettre à jour chaque tâche
        for task_config in tasks_config:
            # Créer un crontab spécifique avec l'offset de minutes
            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=str(task_config['minute_offset']),
                hour='*/4',
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )
            
            # Créer ou mettre à jour la tâche
            task, created = PeriodicTask.objects.get_or_create(
                name=task_config['name'],
                defaults={
                    'task': task_config['task'],
                    'crontab': schedule,
                    'enabled': True,
                    'description': task_config['description'],
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Tâche créée: {task_config["name"]}')
                )
                self.stdout.write(f'   Task: {task_config["task"]}')
                self.stdout.write(f'   Description: {task_config["description"]}')
                self.stdout.write(f'   Planification: Toutes les 4h à XX:{task_config["minute_offset"]:02d}')
            else:
                # Mettre à jour si nécessaire
                task.task = task_config['task']
                task.crontab = schedule
                task.description = task_config['description']
                task.enabled = True
                task.save()
                
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Tâche mise à jour: {task_config["name"]}')
                )
            
            self.stdout.write('')
        
        # ====================================================================
        # RÉSUMÉ
        # ====================================================================
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('  RÉSUMÉ'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        # Compter les tâches actives
        active_tasks = PeriodicTask.objects.filter(enabled=True).count()
        total_tasks = PeriodicTask.objects.count()
        
        self.stdout.write(f'📊 Total de tâches: {total_tasks}')
        self.stdout.write(f'✅ Tâches actives: {active_tasks}')
        self.stdout.write('')
        
        # Afficher toutes les tâches
        self.stdout.write('📋 Liste des tâches planifiées:')
        self.stdout.write('')
        
        for task in PeriodicTask.objects.all().order_by('name'):
            status = '✅' if task.enabled else '❌'
            self.stdout.write(f'  {status} {task.name}')
            self.stdout.write(f'     Task: {task.task}')
            
            if task.crontab:
                cron = task.crontab
                self.stdout.write(
                    f'     Planification: {cron.minute} {cron.hour} '
                    f'{cron.day_of_week} {cron.day_of_month} {cron.month_of_year}'
                )
            
            if task.description:
                self.stdout.write(f'     Description: {task.description}')
            
            self.stdout.write('')
        
        # ====================================================================
        # INSTRUCTIONS
        # ====================================================================
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('  PROCHAINES ÉTAPES'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        self.stdout.write('1. Démarrer Celery Worker:')
        self.stdout.write('   celery -A si_gouvernance worker --loglevel=info')
        self.stdout.write('')
        
        self.stdout.write('2. Démarrer Celery Beat:')
        self.stdout.write('   celery -A si_gouvernance beat --loglevel=info')
        self.stdout.write('')
        
        self.stdout.write('3. Vérifier les tâches actives:')
        self.stdout.write('   celery -A si_gouvernance inspect active')
        self.stdout.write('')
        
        self.stdout.write('4. Monitoring avec Flower (optionnel):')
        self.stdout.write('   celery -A si_gouvernance flower')
        self.stdout.write('   Accès: http://localhost:5555')
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('✅ Configuration terminée!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        self.stdout.write(
            self.style.WARNING(
                '⚠️  Les alertes s\'exécuteront automatiquement toutes les 4 heures:'
            )
        )
        self.stdout.write('   00:00, 04:00, 08:00, 12:00, 16:00, 20:00')
        self.stdout.write('')
