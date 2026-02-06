"""
Modèles pour le système de MAINTENANCE
Architecture métier conforme aux pratiques d'entreprise
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
import uuid


class ContratGarantie(models.Model):
    """
    Contrat de garantie lié à un projet
    Définit les conditions de maintenance gratuite
    """
    TYPE_GARANTIE_CHOICES = [
        ('CORRECTIVE', 'Maintenance Corrective'),
        ('EVOLUTIVE', 'Maintenance Évolutive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='contrats_garantie')
    
    # Type et période
    type_garantie = models.CharField(max_length=20, choices=TYPE_GARANTIE_CHOICES)
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    
    # SLA (Service Level Agreement)
    sla_heures = models.IntegerField(
        verbose_name="SLA en heures",
        help_text="Temps de réponse maximum en heures"
    )
    
    # Conditions
    description_couverture = models.TextField(
        verbose_name="Description de la couverture",
        help_text="Détails sur ce qui est couvert par la garantie"
    )
    exclusions = models.TextField(
        blank=True,
        verbose_name="Exclusions",
        help_text="Ce qui n'est PAS couvert par la garantie"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey('Utilisateur', on_delete=models.SET_NULL, null=True, related_name='contrats_crees')
    
    class Meta:
        verbose_name = "Contrat de Garantie"
        verbose_name_plural = "Contrats de Garantie"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.get_type_garantie_display()} - {self.projet.nom} ({self.date_debut} → {self.date_fin})"
    
    @property
    def est_actif(self):
        """Vérifie si le contrat est actuellement actif"""
        aujourd_hui = timezone.now().date()
        return self.date_debut <= aujourd_hui <= self.date_fin
    
    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants"""
        if not self.est_actif:
            return 0
        return (self.date_fin - timezone.now().date()).days
    
    def clean(self):
        """Validation métier"""
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError("La date de fin doit être après la date de début")
        
        # Vérifier qu'il n'y a pas de chevauchement pour le même type
        if self.projet_id:
            chevauchements = ContratGarantie.objects.filter(
                projet=self.projet,
                type_garantie=self.type_garantie
            ).filter(
                Q(date_debut__lte=self.date_fin, date_fin__gte=self.date_debut)
            ).exclude(id=self.id)
            
            if chevauchements.exists():
                raise ValidationError(
                    f"Un contrat {self.get_type_garantie_display()} existe déjà pour cette période"
                )


class TicketMaintenance(models.Model):
    """
    Ticket de maintenance (incident)
    Point d'entrée pour toute demande de maintenance
    """
    GRAVITE_CHOICES = [
        ('MINEUR', 'Mineur'),
        ('MAJEUR', 'Majeur'),
        ('CRITIQUE', 'Critique'),
    ]
    
    ORIGINE_CHOICES = [
        ('CLIENT', 'Client'),
        ('MONITORING', 'Monitoring'),
        ('INTERNE', 'Interne'),
    ]
    
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('FERME', 'Fermé'),
        ('REJETE', 'Rejeté'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_ticket = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='tickets_maintenance')
    contrat_garantie = models.ForeignKey(
        ContratGarantie, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tickets'
    )
    
    # Description du problème
    titre = models.CharField(max_length=200, verbose_name="Titre du problème")
    description_probleme = models.TextField(verbose_name="Description détaillée")
    gravite = models.CharField(max_length=20, choices=GRAVITE_CHOICES)
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES)
    
    # Statut et suivi
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    est_payant = models.BooleanField(
        default=False,
        verbose_name="Intervention payante",
        help_text="True si hors garantie ou garantie inactive"
    )
    raison_rejet = models.TextField(
        blank=True,
        verbose_name="Raison du rejet",
        help_text="Pourquoi le ticket a été rejeté"
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True)
    date_resolution = models.DateTimeField(null=True, blank=True)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    
    # Acteurs
    cree_par = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='tickets_crees'
    )
    assigne_a = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_assignes'
    )
    
    class Meta:
        verbose_name = "Ticket de Maintenance"
        verbose_name_plural = "Tickets de Maintenance"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.titre}"
    
    def save(self, *args, **kwargs):
        # Générer le numéro de ticket
        if not self.numero_ticket:
            from django.db.models import Max
            dernier = TicketMaintenance.objects.aggregate(Max('id'))
            count = TicketMaintenance.objects.count() + 1
            self.numero_ticket = f"MAINT-{count:05d}"
        
        # Vérifier la garantie à la création
        if not self.pk:  # Nouveau ticket
            self._verifier_garantie()
        
        super().save(*args, **kwargs)
    
    def _verifier_garantie(self):
        """
        RÈGLE MÉTIER CRITIQUE:
        Vérifier si le ticket peut être traité gratuitement
        """
        if not self.contrat_garantie:
            # Pas de contrat → payant
            self.est_payant = True
            return
        
        if not self.contrat_garantie.est_actif:
            # Contrat inactif → payant
            self.est_payant = True
            self.raison_rejet = "Contrat de garantie expiré"
            return
        
        # Contrat actif → gratuit
        self.est_payant = False
    
    @property
    def peut_etre_traite(self):
        """Vérifie si le ticket peut être traité"""
        if self.statut == 'REJETE':
            return False
        
        if self.est_payant:
            # Logique future: vérifier si paiement accepté
            return False
        
        return True
    
    @property
    def temps_ecoule(self):
        """Temps écoulé depuis la création (en heures)"""
        delta = timezone.now() - self.date_creation
        return delta.total_seconds() / 3600
    
    @property
    def sla_depasse(self):
        """Vérifie si le SLA est dépassé"""
        if not self.contrat_garantie:
            return False
        
        if self.statut in ['RESOLU', 'FERME']:
            return False
        
        return self.temps_ecoule > self.contrat_garantie.sla_heures
    
    def resoudre(self):
        """Marquer le ticket comme résolu"""
        self.statut = 'RESOLU'
        self.date_resolution = timezone.now()
        self.save()
    
    def fermer(self):
        """Fermer le ticket (après validation client)"""
        if self.statut != 'RESOLU':
            raise ValidationError("Le ticket doit être résolu avant d'être fermé")
        
        self.statut = 'FERME'
        self.date_fermeture = timezone.now()
        self.save()
    
    def rejeter(self, raison):
        """Rejeter le ticket"""
        self.statut = 'REJETE'
        self.raison_rejet = raison
        self.save()


class BilletIntervention(models.Model):
    """
    Billet de sortie - Autorisation d'intervention
    RÈGLE CRITIQUE: Aucune intervention sans billet validé
    """
    TYPE_INTERVENTION_CHOICES = [
        ('ANALYSE', 'Analyse du problème'),
        ('CORRECTION', 'Correction'),
        ('DEPLOIEMENT_CORRECTIF', 'Déploiement correctif'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_billet = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='billets_intervention'
    )
    developpeur_autorise = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name='billets_autorises'
    )
    
    # Type et durée
    type_intervention = models.CharField(max_length=30, choices=TYPE_INTERVENTION_CHOICES)
    duree_estimee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Durée estimée (heures)"
    )
    
    # Autorisation
    autorise_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        related_name='billets_autorises_par'
    )
    date_autorisation = models.DateTimeField(auto_now_add=True)
    
    # Instructions
    instructions = models.TextField(
        blank=True,
        verbose_name="Instructions spécifiques",
        help_text="Consignes pour le développeur"
    )
    
    class Meta:
        verbose_name = "Billet d'Intervention"
        verbose_name_plural = "Billets d'Intervention"
        ordering = ['-date_autorisation']
    
    def __str__(self):
        return f"{self.numero_billet} - {self.ticket.numero_ticket}"
    
    def save(self, *args, **kwargs):
        if not self.numero_billet:
            count = BilletIntervention.objects.count() + 1
            self.numero_billet = f"BILLET-{count:05d}"
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation métier"""
        # Vérifier que le ticket peut être traité
        if self.ticket and not self.ticket.peut_etre_traite:
            raise ValidationError("Ce ticket ne peut pas être traité (rejeté ou payant non accepté)")
        
        # Vérifier que le développeur a les permissions
        if self.developpeur_autorise:
            if not self.developpeur_autorise.role_systeme:
                raise ValidationError("Le développeur doit avoir un rôle système")
            
            if self.developpeur_autorise.role_systeme.nom not in ['DEVELOPPEUR', 'CHEF_PROJET']:
                raise ValidationError("Seuls les développeurs et chefs de projet peuvent intervenir")


class InterventionMaintenance(models.Model):
    """
    Intervention technique réelle
    Enregistre les actions effectuées
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation
    billet = models.ForeignKey(
        BilletIntervention,
        on_delete=models.CASCADE,
        related_name='interventions'
    )
    
    # Description des actions
    description_actions = models.TextField(
        verbose_name="Description des actions effectuées"
    )
    
    # Temps
    date_debut = models.DateTimeField(verbose_name="Date de début")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    temps_passe = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Temps passé (heures)",
        help_text="Temps réel passé sur l'intervention"
    )
    
    # Résultats
    correctif_applique = models.TextField(
        blank=True,
        verbose_name="Correctif appliqué",
        help_text="Détails techniques du correctif"
    )
    fichiers_modifies = models.TextField(
        blank=True,
        verbose_name="Fichiers modifiés",
        help_text="Liste des fichiers modifiés"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Intervention de Maintenance"
        verbose_name_plural = "Interventions de Maintenance"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"Intervention {self.billet.numero_billet} - {self.date_debut.strftime('%d/%m/%Y')}"
    
    def clean(self):
        """Validation métier"""
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError("La date de fin doit être après la date de début")
        
        # Vérifier que le temps passé est cohérent
        if self.temps_passe and self.billet:
            if self.temps_passe > self.billet.duree_estimee * 2:
                # Avertissement si dépassement de 200%
                pass  # On pourrait lever un warning


class StatutTechnique(models.Model):
    """
    Rapport technique final (obligatoire)
    RÈGLE: Un ticket ne peut être clôturé sans statut technique
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation (OneToOne car un seul statut par intervention)
    intervention = models.OneToOneField(
        InterventionMaintenance,
        on_delete=models.CASCADE,
        related_name='statut_technique'
    )
    
    # Analyse
    probleme_initial = models.TextField(
        verbose_name="Problème initial",
        help_text="Description du problème tel que rapporté"
    )
    cause_reelle = models.TextField(
        verbose_name="Cause réelle (Root Cause)",
        help_text="Analyse de la cause racine du problème"
    )
    solution_apportee = models.TextField(
        verbose_name="Solution apportée",
        help_text="Description détaillée de la solution"
    )
    
    # Impact et risques
    impact_systeme = models.TextField(
        verbose_name="Impact sur le système",
        help_text="Quels composants sont affectés"
    )
    risques_futurs = models.TextField(
        blank=True,
        verbose_name="Risques futurs",
        help_text="Risques identifiés pour l'avenir"
    )
    recommandations = models.TextField(
        blank=True,
        verbose_name="Recommandations",
        help_text="Actions préventives recommandées"
    )
    
    # Validation
    valide_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='statuts_valides'
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    redige_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        related_name='statuts_rediges'
    )
    
    class Meta:
        verbose_name = "Statut Technique"
        verbose_name_plural = "Statuts Techniques"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Statut - {self.intervention.billet.ticket.numero_ticket}"
    
    def valider(self, validateur):
        """Valider le statut technique"""
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()
        
        # Marquer le ticket comme résolu
        self.intervention.billet.ticket.resoudre()
