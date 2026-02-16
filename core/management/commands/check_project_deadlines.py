"""
Commande Django pour vérifier les échéances des projets et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_project_deadlines
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Projet, AlerteProjet, StatutProjet


class Command(BaseCommand):
    help = 'Vérifie les échéances des projets et envoie des alertes (J-7 et projets en retard)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des échéances des projets...'))
        
        aujourd_hui = timezone.now().date()
        
        # Compteurs
        alertes_j7 = 0
        alertes_j3 = 0
        alertes_j1 = 0
        alertes_retard = 0
        alertes_ignorees = 0
        
        # Récupérer tous les projets EN_COURS avec une date de fin
        try:
            statut_en_cours = StatutProjet.objects.get(nom='EN_COURS')
        except StatutProjet.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Statut EN_COURS non trouvé'))
            return
        
        projets_actifs = Projet.objects.filter(
            statut=statut_en_cours
        ).exclude(date_fin__isnull=True).select_related('createur')
        
        self.stdout.write(f'📊 {projets_actifs.count()} projet(s) actif(s) à vérifier')
        
        for projet in projets_actifs:
            if not projet.date_fin:
                continue
            
            jours_restants = (projet.date_fin - aujourd_hui).days
            
            # 🔴 ALERTE : Projet en retard (date dépassée)
            if jours_restants < 0:
                nb_alertes = self._creer_alerte_retard(projet, abs(jours_restants))
                if nb_alertes > 0:
                    alertes_retard += nb_alertes
                    self.stdout.write(f'  🔴 {nb_alertes} alerte(s) RETARD créée(s) pour {projet.nom} ({abs(jours_restants)} jours)')
                else:
                    alertes_ignorees += 1
            
            # 🟡 ALERTE : J-7 (7 jours avant la fin)
            elif jours_restants == 7:
                nb_alertes = self._creer_alerte_j7(projet)
                if nb_alertes > 0:
                    alertes_j7 += nb_alertes
                    self.stdout.write(f'  🟡 {nb_alertes} alerte(s) J-7 créée(s) pour {projet.nom}')
                else:
                    alertes_ignorees += 1
            
            # 🟠 ALERTE : J-3 (3 jours avant la fin)
            elif jours_restants == 3:
                nb_alertes = self._creer_alerte_j3(projet)
                if nb_alertes > 0:
                    alertes_j3 += nb_alertes
                    self.stdout.write(f'  🟠 {nb_alertes} alerte(s) J-3 créée(s) pour {projet.nom}')
                else:
                    alertes_ignorees += 1
            
            # 🔴 ALERTE : J-1 (1 jour avant la fin)
            elif jours_restants == 1:
                nb_alertes = self._creer_alerte_j1(projet)
                if nb_alertes > 0:
                    alertes_j1 += nb_alertes
                    self.stdout.write(f'  🔴 {nb_alertes} alerte(s) J-1 créée(s) pour {projet.nom}')
                else:
                    alertes_ignorees += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'🟡 Alertes J-7 : {alertes_j7}')
        self.stdout.write(f'🟠 Alertes J-3 : {alertes_j3}')
        self.stdout.write(f'🔴 Alertes J-1 : {alertes_j1}')
        self.stdout.write(f'🔴 Alertes RETARD : {alertes_retard}')
        self.stdout.write(f'⚪ Alertes ignorées (doublons) : {alertes_ignorees}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_j7 + alertes_j3 + alertes_j1 + alertes_retard}')

    def _creer_alerte_retard(self, projet, jours_retard):
        """
        Crée des alertes pour un projet en retard
        
        Args:
            projet: Le projet en retard
            jours_retard: Nombre de jours de retard
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
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
            if self._alerte_retard_existe_aujourd_hui(projet, destinataire):
                continue
            
            # Message personnalisé selon le nombre de jours
            if jours_retard == 1:
                jours_text = "1 jour"
            else:
                jours_text = f"{jours_retard} jours"
            
            titre = f"🔴 Projet {projet.nom} - EN RETARD"
            message = f"Le projet '{projet.nom}' est en retard de {jours_text} (date de fin prévue : {projet.date_fin.strftime('%d/%m/%Y')}). "
            
            if destinataire == responsable:
                message += "En tant que responsable, une action urgente est requise pour rattraper le retard."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, veuillez prendre les mesures nécessaires pour résoudre cette situation."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=projet,
                type_alerte='ECHEANCE_DEPASSEE',
                niveau='DANGER',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_retard': jours_retard,
                    'date_fin': projet.date_fin.isoformat(),
                    'type_alerte': 'RETARD'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte RETARD créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _creer_alerte_j7(self, projet):
        """
        Crée des alertes J-7 pour un projet
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        - Équipe du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
        # 1. Administrateur (créateur du projet)
        if projet.createur:
            destinataires.add(projet.createur)
        
        # 2. Responsable du projet
        responsable = projet.get_responsable_principal()
        if responsable:
            destinataires.add(responsable)
        
        # 3. Équipe du projet
        equipe = projet.get_equipe()
        for membre in equipe:
            destinataires.add(membre)
        
        # Créer les alertes
        alertes_creees = 0
        aujourd_hui = timezone.now().date()
        
        for destinataire in destinataires:
            # Vérifier si une alerte similaire n'existe pas déjà aujourd'hui
            if self._alerte_existe_aujourd_hui(projet, destinataire):
                continue
            
            titre = f"⚠️ Projet {projet.nom} - Fin dans 7 jours"
            message = f"Le projet '{projet.nom}' se termine dans 7 jours ({projet.date_fin.strftime('%d/%m/%Y')}). "
            
            if destinataire == responsable:
                message += "En tant que responsable, assurez-vous que toutes les tâches seront terminées à temps."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, surveillez l'avancement du projet."
            else:
                message += "Assurez-vous de terminer vos tâches assignées avant la date limite."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=projet,
                type_alerte='ECHEANCE_J7',
                niveau='WARNING',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_restants': 7,
                    'date_fin': projet.date_fin.isoformat(),
                    'type_alerte': 'J-7'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_retard_existe_aujourd_hui(self, projet, utilisateur):
        """
        Vérifie si une alerte de retard existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            projet: Le projet concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=projet,
            type_alerte='ECHEANCE_DEPASSEE',
            date_creation__date=aujourd_hui
        ).exists()

    def _alerte_existe_aujourd_hui(self, projet, utilisateur):
        """
        Vérifie si une alerte J-7 existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            projet: Le projet concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=projet,
            type_alerte='ECHEANCE_J7',
            date_creation__date=aujourd_hui
        ).exists()

    def _creer_alerte_j3(self, projet):
        """
        Crée des alertes J-3 pour un projet
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
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
            if self._alerte_j3_existe_aujourd_hui(projet, destinataire):
                continue
            
            titre = f"🟠 Projet {projet.nom} - Fin dans 3 jours"
            message = f"Le projet '{projet.nom}' se termine dans 3 jours ({projet.date_fin.strftime('%d/%m/%Y')}). "
            
            if destinataire == responsable:
                message += "En tant que responsable, assurez-vous que toutes les tâches critiques seront terminées à temps."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, surveillez de près l'avancement du projet."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=projet,
                type_alerte='ECHEANCE_J3',
                niveau='WARNING',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_restants': 3,
                    'date_fin': projet.date_fin.isoformat(),
                    'type_alerte': 'J-3'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte J-3 créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _creer_alerte_j1(self, projet):
        """
        Crée des alertes J-1 pour un projet
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
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
            if self._alerte_j1_existe_aujourd_hui(projet, destinataire):
                continue
            
            titre = f"🔴 Projet {projet.nom} - Fin DEMAIN"
            message = f"Le projet '{projet.nom}' se termine DEMAIN ({projet.date_fin.strftime('%d/%m/%Y')})! "
            
            if destinataire == responsable:
                message += "En tant que responsable, action urgente requise pour finaliser toutes les tâches restantes."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, intervention urgente nécessaire pour assurer la livraison."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=projet,
                type_alerte='ECHEANCE_J1',
                niveau='DANGER',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'jours_restants': 1,
                    'date_fin': projet.date_fin.isoformat(),
                    'type_alerte': 'J-1'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte J-1 créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_j3_existe_aujourd_hui(self, projet, utilisateur):
        """
        Vérifie si une alerte J-3 existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            projet: Le projet concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=projet,
            type_alerte='ECHEANCE_J3',
            date_creation__date=aujourd_hui
        ).exists()

    def _alerte_j1_existe_aujourd_hui(self, projet, utilisateur):
        """
        Vérifie si une alerte J-1 existe déjà aujourd'hui pour éviter les doublons
        
        Args:
            projet: Le projet concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        aujourd_hui = timezone.now().date()
        
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=projet,
            type_alerte='ECHEANCE_J1',
            date_creation__date=aujourd_hui
        ).exists()
