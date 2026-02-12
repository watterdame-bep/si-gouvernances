"""
Commande Django pour vérifier les échéances des tâches et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_task_deadlines
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import TacheEtape, AlerteProjet


class Command(BaseCommand):
    help = 'Vérifie les échéances des tâches et envoie des alertes (tâches en retard)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des échéances des tâches...'))
        
        aujourd_hui = timezone.now().date()
        
        # Compteurs
        alertes_retard = 0
        alertes_ignorees = 0
        
        # Récupérer toutes les tâches non terminées avec une date de fin
        taches_actives = TacheEtape.objects.filter(
            statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']
        ).exclude(date_fin__isnull=True).select_related('responsable', 'etape__projet')
        
        self.stdout.write(f'📊 {taches_actives.count()} tâche(s) active(s) à vérifier')
        
        for tache in taches_actives:
            if not tache.date_fin:
                continue
                
            jours_restants = (tache.date_fin - aujourd_hui).days
            
            # 🔴 ALERTE : Tâche en retard
            if jours_restants < 0:
                nb_alertes = self._creer_alerte_retard(tache, abs(jours_restants))
                if nb_alertes > 0:
                    alertes_retard += nb_alertes
                    self.stdout.write(f'  🔴 {nb_alertes} alerte(s) RETARD créée(s) pour {tache.nom} ({abs(jours_restants)} jours)')
                else:
                    alertes_ignorees += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'🔴 Alertes RETARD : {alertes_retard}')
        self.stdout.write(f'⚪ Alertes ignorées (doublons) : {alertes_ignorees}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_retard}')

    def _creer_alerte_retard(self, tache, jours_retard):
        """
        Crée des alertes pour une tâche en retard
        
        Args:
            tache: La tâche en retard
            jours_retard: Nombre de jours de retard
        
        Destinataires :
        - Responsable de la tâche (utilisateur assigné)
        - Responsable du projet
        
        PAS l'administrateur (selon spécification)
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
        # 1. Responsable de la tâche (utilisateur assigné)
        if tache.responsable:
            # Vérifier que le responsable a accès au projet
            if tache.responsable.a_acces_projet(tache.etape.projet):
                destinataires.add(tache.responsable)
            else:
                self.stdout.write(f'  ⚠️  Alerte ignorée : {tache.responsable.get_full_name()} n\'a pas accès au projet')
        
        # 2. Responsable du projet
        responsable_projet = tache.etape.projet.get_responsable_principal()
        if responsable_projet:
            destinataires.add(responsable_projet)
        
        # Créer les alertes
        alertes_creees = 0
        aujourd_hui = timezone.now().date()
        
        for destinataire in destinataires:
            # Vérifier si une alerte similaire n'existe pas déjà aujourd'hui
            if self._alerte_retard_existe_aujourd_hui(tache, destinataire):
                continue
            
            # Message personnalisé selon le nombre de jours
            if jours_retard == 1:
                jours_text = "1 jour"
            else:
                jours_text = f"{jours_retard} jours"
            
            # Titre et message selon le destinataire
            if destinataire == tache.responsable:
                titre = f"🔴 Tâche en retard - {tache.nom}"
                message = f"La tâche '{tache.nom}' du projet '{tache.etape.projet.nom}' est en retard de {jours_text} (date limite : {tache.date_fin.strftime('%d/%m/%Y')}). Une action urgente est requise."
            else:
                # Responsable du projet
                titre = f"🔴 Tâche en retard - {tache.nom}"
                assignee_name = tache.responsable.get_full_name() if tache.responsable else "Non assignée"
                message = f"La tâche '{tache.nom}' du projet '{tache.etape.projet.nom}' (assignée à {assignee_name}) est en retard de {jours_text} (date limite : {tache.date_fin.strftime('%d/%m/%Y')})."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=tache.etape.projet,
                type_alerte='TACHES_EN_RETARD',
                niveau='DANGER',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_retard': jours_retard,
                    'tache_id': str(tache.id),
                    'tache_nom': tache.nom,
                    'date_fin': tache.date_fin.isoformat(),
                    'type_alerte': 'TACHE_RETARD'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte RETARD créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_retard_existe_aujourd_hui(self, tache, utilisateur):
        """
        Vérifie si une alerte de retard existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            tache: La tâche concernée
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=tache.etape.projet,
            type_alerte='TACHES_EN_RETARD',
            date_creation__date=aujourd_hui,
            donnees_contexte__tache_id=str(tache.id)
        ).exists()

