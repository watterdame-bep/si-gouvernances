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
    Ticket de maintenance SIMPLIFIÉ
    Unité unique de travail - Inspiré de Jira/GitHub Issues
    """
    
    # Types de demande
    TYPE_DEMANDE_CHOICES = [
        ('BUG', '🐛 Bug / Anomalie'),
        ('AMELIORATION', '✨ Amélioration'),
        ('QUESTION', '❓ Question / Support'),
        ('AUTRE', '📋 Autre'),
    ]
    
    # Priorités
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    # Gravité (impact)
    GRAVITE_CHOICES = [
        ('MINEUR', 'Mineur - Impact faible'),
        ('MAJEUR', 'Majeur - Impact modéré'),
        ('CRITIQUE', 'Critique - Impact sévère'),
        ('BLOQUANT', 'Bloquant - Système inutilisable'),
    ]
    
    # Origine
    ORIGINE_CHOICES = [
        ('CLIENT', 'Client'),
        ('MONITORING', 'Monitoring'),
        ('INTERNE', 'Interne'),
    ]
    
    # Statuts
    STATUT_CHOICES = [
        ('OUVERT', '🆕 Ouvert'),
        ('EN_COURS', '🔵 En cours'),
        ('RESOLU', '✅ Résolu'),
        ('FERME', '🔒 Fermé'),
        ('REJETE', '❌ Rejeté'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_ticket = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='tickets_maintenance')
    contrat_garantie = models.ForeignKey(
        ContratGarantie, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='tickets',
        verbose_name="Contrat de garantie"
    )
    
    # Description
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description_probleme = models.TextField(verbose_name="Description détaillée")
    
    # Classification
    type_demande = models.CharField(
        max_length=20, 
        choices=TYPE_DEMANDE_CHOICES,
        default='BUG',
        verbose_name="Type de demande"
    )
    priorite = models.CharField(
        max_length=20, 
        choices=PRIORITE_CHOICES,
        default='NORMALE',
        verbose_name="Priorité"
    )
    gravite = models.CharField(
        max_length=20, 
        choices=GRAVITE_CHOICES,
        default='MAJEUR',
        verbose_name="Gravité"
    )
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='CLIENT')
    
    # Statut et workflow
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='OUVERT',
        verbose_name="Statut"
    )
    
    # Assignation (ManyToMany pour permettre plusieurs développeurs)
    assignes_a = models.ManyToManyField(
        'Utilisateur',
        blank=True,
        related_name='tickets_assignes',
        verbose_name="Assigné à"
    )
    
    # Suivi temporel
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_debut_travail = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de début du travail"
    )
    date_resolution = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de résolution"
    )
    date_fermeture = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de fermeture"
    )
    
    # Estimation et suivi du temps
    temps_estime = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Temps estimé (heures)",
        help_text="Estimation initiale du temps nécessaire"
    )
    temps_passe = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Temps passé (heures)",
        help_text="Temps réel passé sur le ticket"
    )
    
    # Résolution
    solution = models.TextField(
        blank=True,
        verbose_name="Solution apportée",
        help_text="Description de la solution et des actions effectuées"
    )
    fichiers_modifies = models.TextField(
        blank=True,
        verbose_name="Fichiers modifiés",
        help_text="Liste des fichiers modifiés (un par ligne)"
    )
    
    # Garantie
    est_sous_garantie = models.BooleanField(
        default=True,
        verbose_name="Sous garantie",
        help_text="True si couvert par un contrat actif"
    )
    raison_rejet = models.TextField(
        blank=True,
        verbose_name="Raison hors garantie",
        help_text="Pourquoi le ticket n'est pas couvert"
    )
    
    # Métadonnées
    cree_par = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='tickets_crees',
        verbose_name="Créé par"
    )
    modifie_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_modifies',
        verbose_name="Modifié par"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Ticket de Maintenance"
        verbose_name_plural = "Tickets de Maintenance"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['statut']),
            models.Index(fields=['priorite']),
            models.Index(fields=['-date_creation']),
        ]
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.titre}"
    
    def save(self, *args, **kwargs):
        # Générer le numéro de ticket
        if not self.numero_ticket:
            count = TicketMaintenance.objects.count() + 1
            self.numero_ticket = f"MAINT-{count:05d}"
        
        # Vérifier la garantie à la création
        if not self.pk:  # Nouveau ticket
            self._verifier_garantie()
        
        super().save(*args, **kwargs)
    
    def _verifier_garantie(self):
        """
        RÈGLE MÉTIER CRITIQUE:
        Vérifier si le ticket est couvert par la garantie
        """
        if not self.contrat_garantie:
            self.est_sous_garantie = False
            self.raison_rejet = "Aucun contrat de garantie associé"
            return
        
        if not self.contrat_garantie.est_actif:
            self.est_sous_garantie = False
            self.raison_rejet = f"Contrat de garantie expiré (fin: {self.contrat_garantie.date_fin})"
            return
        
        # Contrat actif → sous garantie
        self.est_sous_garantie = True
        self.raison_rejet = ""
    
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
    
    @property
    def temps_restant_estime(self):
        """Calcule le temps restant estimé"""
        if not self.temps_estime:
            return None
        return max(0, float(self.temps_estime) - float(self.temps_passe))
    
    @property
    def pourcentage_avancement(self):
        """Calcule le pourcentage d'avancement basé sur le temps"""
        if not self.temps_estime or self.temps_estime == 0:
            return 0
        return min(100, int((float(self.temps_passe) / float(self.temps_estime)) * 100))
    
    def demarrer_travail(self, utilisateur):
        """Démarrer le travail sur le ticket"""
        if self.statut == 'OUVERT':
            self.statut = 'EN_COURS'
            self.date_debut_travail = timezone.now()
            self.modifie_par = utilisateur
            self.save()
            
            # Créer un commentaire automatique
            CommentaireTicket.objects.create(
                ticket=self,
                auteur=utilisateur,
                contenu=f"🔵 Travail démarré sur le ticket",
                est_interne=False
            )
    
    def resoudre(self, utilisateur, solution, fichiers_modifies=""):
        """Marquer le ticket comme résolu"""
        if not solution:
            raise ValidationError("Une solution doit être fournie pour résoudre le ticket")
        
        self.statut = 'RESOLU'
        self.date_resolution = timezone.now()
        self.solution = solution
        self.fichiers_modifies = fichiers_modifies
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"✅ Ticket résolu\n\nSolution: {solution[:200]}...",
            est_interne=False
        )
    
    def fermer(self, utilisateur):
        """Fermer le ticket (après validation client)"""
        if self.statut != 'RESOLU':
            raise ValidationError("Le ticket doit être résolu avant d'être fermé")
        
        self.statut = 'FERME'
        self.date_fermeture = timezone.now()
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"🔒 Ticket fermé et validé",
            est_interne=False
        )
    
    def rejeter(self, utilisateur, raison):
        """Rejeter le ticket"""
        if not raison:
            raise ValidationError("Une raison doit être fournie pour rejeter le ticket")
        
        self.statut = 'REJETE'
        self.raison_rejet = raison
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"❌ Ticket rejeté\n\nRaison: {raison}",
            est_interne=False
        )
    
    def assigner(self, utilisateurs, assigne_par):
        """Assigner le ticket à un ou plusieurs développeurs"""
        self.assignes_a.set(utilisateurs)
        self.modifie_par = assigne_par
        self.save()
        
        # Créer un commentaire automatique
        noms = ", ".join([u.get_full_name() for u in utilisateurs])
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=assigne_par,
            contenu=f"👤 Ticket assigné à: {noms}",
            est_interne=False
        )
    
    def ajouter_temps(self, heures, utilisateur):
        """Ajouter du temps passé sur le ticket"""
        self.temps_passe += heures
        self.modifie_par = utilisateur
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


class CommentaireTicket(models.Model):
    """
    Commentaires et historique du ticket
    Permet le suivi des échanges et des actions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name="Ticket"
    )
    auteur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentaires_tickets',
        verbose_name="Auteur"
    )
    
    # Contenu
    contenu = models.TextField(verbose_name="Commentaire")
    
    # Visibilité
    est_interne = models.BooleanField(
        default=False,
        verbose_name="Commentaire interne",
        help_text="Si True, visible seulement par l'équipe technique"
    )
    
    # Pièce jointe (optionnel)
    fichier = models.FileField(
        upload_to='tickets/commentaires/',
        null=True,
        blank=True,
        verbose_name="Pièce jointe"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    modifie = models.BooleanField(default=False, verbose_name="Modifié")
    date_modification = models.DateTimeField(null=True, blank=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Commentaire de Ticket"
        verbose_name_plural = "Commentaires de Tickets"
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Commentaire sur {self.ticket.numero_ticket} par {self.auteur}"
    
    def modifier(self, nouveau_contenu):
        """Modifier le commentaire"""
        self.contenu = nouveau_contenu
        self.modifie = True
        self.date_modification = timezone.now()
        self.save()


class PieceJointeTicket(models.Model):
    """
    Pièces jointes liées à un ticket
    Captures d'écran, logs, fichiers de configuration, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='pieces_jointes',
        verbose_name="Ticket"
    )
    uploade_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        related_name='pieces_jointes_uploadees',
        verbose_name="Uploadé par"
    )
    
    # Fichier
    fichier = models.FileField(
        upload_to='tickets/pieces_jointes/',
        verbose_name="Fichier"
    )
    nom_fichier = models.CharField(max_length=255, verbose_name="Nom du fichier")
    taille_fichier = models.IntegerField(verbose_name="Taille (octets)")
    type_mime = models.CharField(max_length=100, blank=True, verbose_name="Type MIME")
    
    # Description
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description optionnelle de la pièce jointe"
    )
    
    # Métadonnées
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    
    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"
        ordering = ['-date_upload']
    
    def __str__(self):
        return f"{self.nom_fichier} - {self.ticket.numero_ticket}"
    
    def save(self, *args, **kwargs):
        if self.fichier:
            self.nom_fichier = self.fichier.name
            self.taille_fichier = self.fichier.size
        super().save(*args, **kwargs)


# ============================================================================
# ANCIENS MODÈLES - CONSERVÉS POUR COMPATIBILITÉ (À SUPPRIMER APRÈS MIGRATION)
# ============================================================================

class StatutTechnique(models.Model):
    """
    Rapport technique final (obligatoire)
    RÈGLE: Un ticket ne peut être clôturé sans statut technique
    ⚠️ ANCIEN MODÈLE - À SUPPRIMER APRÈS MIGRATION
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation (OneToOne car un seul statut par intervention)
    intervention = models.OneToOneField(
        'InterventionMaintenance',
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
        ticket = self.intervention.billet.ticket
        ticket.statut = 'RESOLU'
        ticket.date_resolution = timezone.now()
        ticket.save()
