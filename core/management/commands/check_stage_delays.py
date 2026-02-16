"""
Commande Django pour vérifier les retards des étapes et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_stage_delays
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import EtapeProjet, NotificationEtape


class Command(BaseCommand):
    help = 'Vérifie les retards des étapes et envoie des alertes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des retards d\'étapes...'))
        
        aujourd_hui = timezone.now().date()
        
        # Compteurs
        alertes_creees = 0
        alertes_ignorees = 0
        
        # Récupérer toutes les étapes EN_COURS avec une date de fin dépassée
        etapes_en_retard = EtapeProjet.objects.filter(
            statut='EN_COURS',
            date_fin_reelle__isnull=True  # Pas encore terminée
        ).exclude(
            date_fin_prevue__isnull=True  # Doit avoir une date de fin prévue
        ).select_related('projet', 'projet__createur')
        
        self.stdout.write(f'📊 {etapes_en_retard.count()} étape(s) en cours à vérifier')
        
        for etape in etapes_en_retard:
            if not etape.date_fin_prevue:
                continue
            
            jours_retard = (aujourd_hui - etape.date_fin_prevue).days
            
            # Alerte seulement si en retard (date dépassée)
            if jours_retard > 0:
                nb_alertes = self._creer_alerte_retard_etape(etape, jours_retard)
                if nb_alertes > 0:
                    alertes_creees += nb_alertes
                    self.stdout.write(f'  🔴 {nb_alertes} alerte(s) RETARD créée(s) pour étape {etape.type_etape.nom} du projet {etape.projet.nom} ({jours_retard} jours)')
                else:
                    alertes_ignorees += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'🔴 Alertes RETARD_ETAPE : {alertes_creees}')
        self.stdout.write(f'⚪ Alertes ignorées (doublons) : {alertes_ignorees}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_creees}')

    def _creer_alerte_retard_etape(self, etape, jours_retard):
        """
        Crée des alertes pour une étape en retard
        
        Args:
            etape: L'étape en retard
            jours_retard: Nombre de jours de retard
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        projet = etape.projet
        
        # 1. Administrateur (créateur du projet)
        if projet.createur:
            destinataires.add(projet.createur)
        
        # 2. Responsable du projet
        responsable = projet.get_responsable_principal()
        if responsable:
            destinataires.add(responsable)
        
        # Créer les alertes
        alertes_creees = 0
        aujourd_hui = timezone.now().date()
        
        for destinataire in destinataires:
            # Vérifier si une alerte similaire n'existe pas déjà aujourd'hui
            if self._alerte_retard_etape_existe_aujourd_hui(etape, destinataire):
                continue
            
            # Message personnalisé selon le nombre de jours
            if jours_retard == 1:
                jours_text = "1 jour"
            else:
                jours_text = f"{jours_retard} jours"
            
            titre = f"🔴 Étape {etape.type_etape.nom} - EN RETARD"
            message = f"L'étape '{etape.type_etape.nom}' du projet '{projet.nom}' est en retard de {jours_text} (date de fin prévue : {etape.date_fin_prevue.strftime('%d/%m/%Y')}). "
            
            if destinataire == responsable:
                message += "En tant que responsable, une action urgente est requise pour rattraper le retard."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, veuillez prendre les mesures nécessaires pour résoudre cette situation."
            
            NotificationEtape.objects.create(
                destinataire=destinataire,
                etape=etape,
                type_notification='RETARD_ETAPE',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_retard': jours_retard,
                    'date_fin_prevue': etape.date_fin_prevue.isoformat(),
                    'type_alerte': 'RETARD_ETAPE',
                    'projet_id': str(projet.id),
                    'projet_nom': projet.nom,
                    'etape_nom': etape.type_etape.nom
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte RETARD_ETAPE créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_retard_etape_existe_aujourd_hui(self, etape, utilisateur):
        """
        Vérifie si une alerte de retard d'étape existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            etape: L'étape concernée
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return NotificationEtape.objects.filter(
            destinataire=utilisateur,
            etape=etape,
            type_notification='RETARD_ETAPE',
            date_creation__date=aujourd_hui
        ).exists()
