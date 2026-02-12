"""
Commande Django pour vérifier les expirations de contrats de maintenance et envoyer des alertes.
À exécuter quotidiennement via un scheduler (Task Scheduler Windows, cron, etc.)

Usage: python manage.py check_contract_expiration
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import ContratGarantie, AlerteProjet, Utilisateur


class Command(BaseCommand):
    help = 'Vérifie les expirations de contrats de maintenance et envoie des alertes (30 jours avant expiration)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Vérification des expirations de contrats...'))
        
        aujourd_hui = timezone.now().date()
        
        # Compteurs
        alertes_expiration = 0
        alertes_expire = 0
        alertes_ignorees = 0
        
        # Récupérer tous les contrats actifs
        contrats_actifs = ContratGarantie.objects.filter(
            date_debut__lte=aujourd_hui,
            date_fin__gte=aujourd_hui
        ).select_related('projet', 'cree_par')
        
        # Récupérer les contrats expirés (date_fin < aujourd'hui)
        contrats_expires = ContratGarantie.objects.filter(
            date_fin__lt=aujourd_hui
        ).select_related('projet', 'cree_par')
        
        self.stdout.write(f'📊 {contrats_actifs.count()} contrat(s) actif(s) à vérifier')
        self.stdout.write(f'📊 {contrats_expires.count()} contrat(s) expiré(s) à vérifier')
        
        # Vérifier les contrats actifs (expiration dans 30 jours)
        for contrat in contrats_actifs:
            jours_restants = (contrat.date_fin - aujourd_hui).days
            
            # ⚠️ ALERTE : Contrat expire dans 30 jours
            if jours_restants == 30:
                nb_alertes = self._creer_alerte_expiration(contrat)
                if nb_alertes > 0:
                    alertes_expiration += nb_alertes
                    self.stdout.write(f'  ⚠️  {nb_alertes} alerte(s) EXPIRATION créée(s) pour contrat {contrat.id} (expire dans 30 jours)')
                else:
                    alertes_ignorees += 1
        
        # Vérifier les contrats expirés
        for contrat in contrats_expires:
            jours_retard = (aujourd_hui - contrat.date_fin).days
            
            # 🔴 ALERTE : Contrat expiré
            nb_alertes = self._creer_alerte_expire(contrat, jours_retard)
            if nb_alertes > 0:
                alertes_expire += nb_alertes
                self.stdout.write(f'  🔴 {nb_alertes} alerte(s) EXPIRÉ créée(s) pour contrat {contrat.id} (expiré depuis {jours_retard} jours)')
            else:
                alertes_ignorees += 1
        
        # Résumé
        self.stdout.write(self.style.SUCCESS('\n✅ Vérification terminée !'))
        self.stdout.write(f'⚠️  Alertes EXPIRATION (30 jours) : {alertes_expiration}')
        self.stdout.write(f'🔴 Alertes EXPIRÉ : {alertes_expire}')
        self.stdout.write(f'⚪ Alertes ignorées (doublons) : {alertes_ignorees}')
        self.stdout.write(f'📧 Total alertes créées : {alertes_expiration + alertes_expire}')

    def _creer_alerte_expiration(self, contrat):
        """
        Crée des alertes pour un contrat proche de l'expiration
        
        Args:
            contrat: Le contrat qui expire dans 30 jours
        
        Destinataires :
        - Administrateur
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
        # 1. Administrateur
        admins = Utilisateur.objects.filter(is_superuser=True)
        for admin in admins:
            destinataires.add(admin)
        
        # 2. Responsable du projet
        responsable_projet = contrat.projet.get_responsable_principal()
        if responsable_projet:
            destinataires.add(responsable_projet)
        
        # Créer les alertes
        alertes_creees = 0
        
        for destinataire in destinataires:
            # Vérifier si une alerte similaire n'existe pas déjà
            if self._alerte_expiration_existe(contrat, destinataire):
                continue
            
            # Message
            titre = f"⚠️ Contrat de maintenance proche de l'expiration"
            message = f"Le contrat de maintenance {contrat.get_type_garantie_display()} du projet '{contrat.projet.nom}' expire dans 30 jours (date d'expiration : {contrat.date_fin.strftime('%d/%m/%Y')}). Veuillez prévoir le renouvellement ou la clôture du contrat."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=contrat.projet,
                type_alerte='CONTRAT_EXPIRATION',
                niveau='WARNING',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'contrat_id': str(contrat.id),
                    'type_garantie': contrat.type_garantie,
                    'date_fin': contrat.date_fin.isoformat(),
                    'jours_restants': 30,
                    'type_alerte': 'CONTRAT_EXPIRATION'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte EXPIRATION créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_expiration_existe(self, contrat, utilisateur):
        """
        Vérifie si une alerte d'expiration existe déjà pour ce contrat
        
        Args:
            contrat: Le contrat concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=contrat.projet,
            type_alerte='CONTRAT_EXPIRATION',
            donnees_contexte__contrat_id=str(contrat.id)
        ).exists()

    def _creer_alerte_expire(self, contrat, jours_retard):
        """
        Crée des alertes pour un contrat expiré
        
        Args:
            contrat: Le contrat expiré
            jours_retard: Nombre de jours depuis l'expiration
        
        Destinataires :
        - Administrateur
        - Responsable du projet
        
        Returns:
            int: Nombre d'alertes créées
        """
        destinataires = set()
        
        # 1. Administrateur
        admins = Utilisateur.objects.filter(is_superuser=True)
        for admin in admins:
            destinataires.add(admin)
        
        # 2. Responsable du projet
        responsable_projet = contrat.projet.get_responsable_principal()
        if responsable_projet:
            destinataires.add(responsable_projet)
        
        # Créer les alertes
        alertes_creees = 0
        
        for destinataire in destinataires:
            # Vérifier si une alerte similaire n'existe pas déjà
            if self._alerte_expire_existe(contrat, destinataire):
                continue
            
            # Message selon le nombre de jours
            if jours_retard == 1:
                jours_text = "1 jour"
            else:
                jours_text = f"{jours_retard} jours"
            
            # Message
            titre = f"🔴 Contrat de maintenance expiré"
            message = f"Le contrat de maintenance {contrat.get_type_garantie_display()} du projet '{contrat.projet.nom}' a expiré depuis {jours_text} (date d'expiration : {contrat.date_fin.strftime('%d/%m/%Y')}). Action urgente requise : renouvellement ou clôture du contrat."
            
            AlerteProjet.objects.create(
                destinataire=destinataire,
                projet=contrat.projet,
                type_alerte='CONTRAT_EXPIRE',
                niveau='DANGER',
                titre=titre,
                message=message,
                lue=False,
                donnees_contexte={
                    'contrat_id': str(contrat.id),
                    'type_garantie': contrat.type_garantie,
                    'date_fin': contrat.date_fin.isoformat(),
                    'jours_retard': jours_retard,
                    'type_alerte': 'CONTRAT_EXPIRE'
                }
            )
            
            alertes_creees += 1
            self.stdout.write(f'    📧 Alerte EXPIRÉ créée pour {destinataire.get_full_name()}')
        
        return alertes_creees

    def _alerte_expire_existe(self, contrat, utilisateur):
        """
        Vérifie si une alerte d'expiration existe déjà pour ce contrat expiré
        
        Args:
            contrat: Le contrat concerné
            utilisateur: L'utilisateur destinataire
        
        Returns:
            bool: True si une alerte existe déjà
        """
        return AlerteProjet.objects.filter(
            destinataire=utilisateur,
            projet=contrat.projet,
            type_alerte='CONTRAT_EXPIRE',
            donnees_contexte__contrat_id=str(contrat.id)
        ).exists()
