"""
Commande Django pour vérifier les échéances des tâches et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_task_deadlines
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import TacheEtape, NotificationTache


class Command(BaseCommand):
    help = 'Vérifie les échéances des tâches et envoie des alertes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des échéances des tâches...'))
        
        aujourd_hui = timezone.now().date()
        
        # Compteurs
        alertes_2_jours = 0
        alertes_1_jour = 0
        alertes_jour_j = 0
        alertes_retard = 0
        
        # Récupérer toutes les tâches non terminées avec une date de fin
        taches_actives = TacheEtape.objects.filter(
            statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']
        ).exclude(date_fin__isnull=True).select_related('responsable', 'etape__projet')
        
        self.stdout.write(f'📊 {taches_actives.count()} tâches actives à vérifier')
        
        for tache in taches_actives:
            if not tache.date_fin:
                continue
                
            jours_restants = (tache.date_fin - aujourd_hui).days
            
            # 🟡 ALERTE : 2 jours avant échéance
            if jours_restants == 2:
                self._creer_alerte_2_jours(tache)
                alertes_2_jours += 1
                
            # 🟠 ALERTE : 1 jour avant échéance (demain)
            elif jours_restants == 1:
                self._creer_alerte_1_jour(tache)
                alertes_1_jour += 1
                
            # 🔴 ALERTE : Jour J (aujourd'hui)
            elif jours_restants == 0:
                self._creer_alerte_jour_j(tache)
                alertes_jour_j += 1
                
            # 🔴 ALERTE : En retard
            elif jours_restants < 0:
                self._creer_alerte_retard(tache, abs(jours_restants))
                alertes_retard += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'🟡 Alertes 2 jours : {alertes_2_jours}')
        self.stdout.write(f'🟠 Alertes 1 jour : {alertes_1_jour}')
        self.stdout.write(f'🔴 Alertes jour J : {alertes_jour_j}')
        self.stdout.write(f'🔴 Alertes retard : {alertes_retard}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_2_jours + alertes_1_jour + alertes_jour_j + alertes_retard}')

    def _creer_alerte_2_jours(self, tache):
        """Alerte 2 jours avant échéance - Destinataire : Responsable de la tâche"""
        if not tache.responsable:
            return
        
        # Vérifier que le responsable a accès au projet
        if not tache.responsable.a_acces_projet(tache.etape.projet):
            self.stdout.write(f'  ⚠️ Alerte ignorée : {tache.responsable.get_full_name()} n\'a pas accès au projet {tache.etape.projet.nom}')
            return
            
        # Vérifier si une alerte similaire n'existe pas déjà aujourd'hui
        if self._alerte_existe_aujourd_hui(tache, tache.responsable, '2_jours'):
            return
        
        titre = "⚠️ Échéance dans 2 jours"
        message = f"La tâche '{tache.nom}' arrive à échéance dans 2 jours ({tache.date_fin.strftime('%d/%m/%Y')})"
        
        NotificationTache.objects.create(
            destinataire=tache.responsable,
            tache=tache,
            type_notification='ALERTE_ECHEANCE',
            titre=titre,
            message=message,
            lue=False
        )
        
        self.stdout.write(f'  🟡 Alerte 2 jours créée pour {tache.responsable.get_full_name()} - {tache.nom}')

    def _creer_alerte_1_jour(self, tache):
        """Alerte 1 jour avant échéance - Destinataire : Responsable de la tâche"""
        if not tache.responsable:
            return
        
        # Vérifier que le responsable a accès au projet
        if not tache.responsable.a_acces_projet(tache.etape.projet):
            self.stdout.write(f'  ⚠️ Alerte ignorée : {tache.responsable.get_full_name()} n\'a pas accès au projet {tache.etape.projet.nom}')
            return
            
        if self._alerte_existe_aujourd_hui(tache, tache.responsable, '1_jour'):
            return
        
        titre = "🔔 Échéance demain"
        message = f"Urgent : La tâche '{tache.nom}' arrive à échéance demain !"
        
        NotificationTache.objects.create(
            destinataire=tache.responsable,
            tache=tache,
            type_notification='ALERTE_ECHEANCE',
            titre=titre,
            message=message,
            lue=False
        )
        
        self.stdout.write(f'  🟠 Alerte 1 jour créée pour {tache.responsable.get_full_name()} - {tache.nom}')

    def _creer_alerte_jour_j(self, tache):
        """Alerte jour J - Destinataires : Responsable tâche + Responsable projet"""
        destinataires = []
        
        # Responsable de la tâche (si a accès au projet)
        if tache.responsable and tache.responsable.a_acces_projet(tache.etape.projet):
            destinataires.append(tache.responsable)
        elif tache.responsable:
            self.stdout.write(f'  ⚠️ Alerte ignorée : {tache.responsable.get_full_name()} n\'a pas accès au projet {tache.etape.projet.nom}')
        
        # Responsable du projet (toujours inclus car c'est son projet)
        if tache.etape.projet.createur and tache.etape.projet.createur not in destinataires:
            destinataires.append(tache.etape.projet.createur)
        
        for destinataire in destinataires:
            if self._alerte_existe_aujourd_hui(tache, destinataire, 'jour_j'):
                continue
            
            titre = "🚨 Échéance aujourd'hui"
            if destinataire == tache.responsable:
                message = f"Critique : La tâche '{tache.nom}' doit être terminée aujourd'hui"
            else:
                message = f"La tâche '{tache.nom}' (assignée à {tache.responsable.get_full_name() if tache.responsable else 'Non assignée'}) doit être terminée aujourd'hui"
            
            NotificationTache.objects.create(
                destinataire=destinataire,
                tache=tache,
                type_notification='ALERTE_CRITIQUE',
                titre=titre,
                message=message,
                lue=False
            )
            
            self.stdout.write(f'  🔴 Alerte jour J créée pour {destinataire.get_full_name()} - {tache.nom}')

    def _creer_alerte_retard(self, tache, jours_retard):
        """Alerte de retard - Destinataires : Responsable tâche + Responsable projet"""
        destinataires = []
        
        # Responsable de la tâche (si a accès au projet)
        if tache.responsable and tache.responsable.a_acces_projet(tache.etape.projet):
            destinataires.append(tache.responsable)
        elif tache.responsable:
            self.stdout.write(f'  ⚠️ Alerte ignorée : {tache.responsable.get_full_name()} n\'a pas accès au projet {tache.etape.projet.nom}')
        
        # Responsable du projet (toujours inclus car c'est son projet)
        if tache.etape.projet.createur and tache.etape.projet.createur not in destinataires:
            destinataires.append(tache.etape.projet.createur)
        
        for destinataire in destinataires:
            if self._alerte_existe_aujourd_hui(tache, destinataire, 'retard'):
                continue
            
            titre = f"❌ Retard de {jours_retard} jour{'s' if jours_retard > 1 else ''}"
            if destinataire == tache.responsable:
                message = f"La tâche '{tache.nom}' est en retard de {jours_retard} jour{'s' if jours_retard > 1 else ''}"
            else:
                message = f"La tâche '{tache.nom}' (assignée à {tache.responsable.get_full_name() if tache.responsable else 'Non assignée'}) est en retard de {jours_retard} jour{'s' if jours_retard > 1 else ''}"
            
            NotificationTache.objects.create(
                destinataire=destinataire,
                tache=tache,
                type_notification='ALERTE_RETARD',
                titre=titre,
                message=message,
                lue=False
            )
            
            self.stdout.write(f'  🔴 Alerte retard créée pour {destinataire.get_full_name()} - {tache.nom} ({jours_retard}j)')

    def _alerte_existe_aujourd_hui(self, tache, utilisateur, type_alerte):
        """Vérifie si une alerte du même type existe déjà aujourd'hui pour éviter les doublons"""
        aujourd_hui = timezone.now().date()
        
        # Mapper les types d'alertes aux types de notifications
        type_mapping = {
            '2_jours': 'ALERTE_ECHEANCE',
            '1_jour': 'ALERTE_ECHEANCE',
            'jour_j': 'ALERTE_CRITIQUE',
            'retard': 'ALERTE_RETARD'
        }
        
        type_notification = type_mapping.get(type_alerte)
        
        return NotificationTache.objects.filter(
            destinataire=utilisateur,
            tache=tache,
            type_notification=type_notification,
            date_creation__date=aujourd_hui
        ).exists()
