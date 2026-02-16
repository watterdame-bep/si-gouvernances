"""
Commande Django pour vérifier les dépassements de budget des projets et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_budget
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from core.models import Projet, AlerteProjet, StatutProjet


class Command(BaseCommand):
    help = 'Vérifie les dépassements de budget des projets et envoie des alertes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des budgets des projets...'))
        
        # Compteurs
        alertes_creees = 0
        alertes_ignorees = 0
        
        # Récupérer tous les projets EN_COURS avec un budget défini
        try:
            statut_en_cours = StatutProjet.objects.get(nom='EN_COURS')
        except StatutProjet.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Statut EN_COURS non trouvé'))
            return
        
        projets_actifs = Projet.objects.filter(
            statut=statut_en_cours
        ).exclude(
            budget_previsionnel__isnull=True
        ).select_related('createur')
        
        self.stdout.write(f'📊 {projets_actifs.count()} projet(s) actif(s) à vérifier')
        
        for projet in projets_actifs:
            if not projet.budget_previsionnel or projet.budget_previsionnel <= 0:
                continue
            
            # Calculer le budget consommé (somme des coûts des tâches, modules, etc.)
            # Note: Cette logique dépend de votre modèle de données
            # Pour l'instant, on utilise un champ hypothétique ou on calcule depuis les tâches
            budget_consomme = self._calculer_budget_consomme(projet)
            
            # Vérifier si le budget est dépassé
            if budget_consomme > projet.budget_previsionnel:
                depassement = budget_consomme - projet.budget_previsionnel
                pourcentage_depassement = (depassement / projet.budget_previsionnel) * 100
                
                nb_alertes = self._creer_alerte_budget_depasse(
                    projet, 
                    budget_consomme, 
                    depassement, 
                    pourcentage_depassement
                )
                
                if nb_alertes > 0:
                    alertes_creees += nb_alertes
                    self.stdout.write(f'  🔴 {nb_alertes} alerte(s) BUDGET_DEPASSE créée(s) pour {projet.nom} (dépassement: {depassement:.2f} {projet.devise}, +{pourcentage_depassement:.1f}%)')
                else:
                    alertes_ignorees += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'🔴 Alertes BUDGET_DEPASSE : {alertes_creees}')
        self.stdout.write(f'⚪ Alertes ignorées (doublons) : {alertes_ignorees}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_creees}')

    def _calculer_budget_consomme(self, projet):
        """
        Calcule le budget consommé d'un projet
        
        Args:
            projet: Le projet concerné
        
        Returns:
            Decimal: Budget consommé
        """
        from decimal import Decimal
        from core.models_budget import ResumeBudget
        
        # Utiliser la classe ResumeBudget pour calculer le budget consommé
        resume = ResumeBudget(projet)
        return resume.total_depenses

    def _creer_alerte_budget_depasse(self, projet, budget_consomme, depassement, pourcentage_depassement):
        """
        Crée des alertes pour un projet dont le budget est dépassé
        
        Args:
            projet: Le projet concerné
            budget_consomme: Budget consommé
            depassement: Montant du dépassement
            pourcentage_depassement: Pourcentage de dépassement
        
        Destinataires :
        - Administrateur (créateur du projet)
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        from core.utils_notifications_email import envoyer_email_alerte_projet
        
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
            if self._alerte_budget_depasse_existe_aujourd_hui(projet, destinataire):
                continue
            
            titre = f"🔴 Budget dépassé - {projet.nom}"
            message = (
                f"Le budget du projet '{projet.nom}' a été dépassé. "
                f"Budget prévu : {projet.budget_previsionnel:.2f} {projet.devise}, "
                f"Budget consommé : {budget_consomme:.2f} {projet.devise}, "
                f"Dépassement : {depassement:.2f} {projet.devise} (+{pourcentage_depassement:.1f}%). "
            )
            
            if destinataire == responsable:
                message += "En tant que responsable, veuillez prendre des mesures pour contrôler les dépenses."
            elif destinataire == projet.createur:
                message += "En tant qu'administrateur, une révision budgétaire est nécessaire."
            
            alerte = AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=projet,
                type_alerte='BUDGET_DEPASSE',
                niveau='DANGER',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'budget_previsionnel': float(projet.budget_previsionnel),
                    'budget_consomme': float(budget_consomme),
                    'depassement': float(depassement),
                    'pourcentage_depassement': float(pourcentage_depassement),
                    'devise': projet.devise,
                    'type_alerte': 'BUDGET_DEPASSE'
                }
            )
            
            # Envoyer email
            try:
                envoyer_email_alerte_projet(alerte)
                self.stdout.write(f'    📧 Email envoyé à {destinataire.get_full_name()}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'    ⚠️ Erreur envoi email à {destinataire.get_full_name()}: {e}'))
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte BUDGET_DEPASSE créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_budget_depasse_existe_aujourd_hui(self, projet, utilisateur):
        """
        Vérifie si une alerte de budget dépassé existe déjà aujourd'hui pour éviter les doublons
        
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
            type_alerte='BUDGET_DEPASSE',
            date_creation__date=aujourd_hui
        ).exists()
