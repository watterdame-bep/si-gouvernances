"""
Modèle pour la gestion des déploiements
Architecture hiérarchique: TacheEtape → Deploiement
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid


class Deploiement(models.Model):
    """
    Déploiement spécifique lié à une tâche de déploiement
    Similaire à CasTest pour les tests
    """
    STATUT_CHOICES = [
        ('PREVU', 'Prévu'),
        ('EN_COURS', 'En cours'),
        ('REUSSI', 'Réussi'),
        ('ECHEC', 'Échec'),
        ('ANNULE', 'Annulé'),
    ]
    
    ENVIRONNEMENT_CHOICES = [
        ('DEV', 'Développement'),
        ('TEST', 'Test'),
        ('PREPROD', 'Pré-production'),
        ('PROD', 'Production'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers la tâche de déploiement parente
    tache_deploiement = models.ForeignKey(
        'TacheEtape',
        on_delete=models.CASCADE,
        related_name='deploiements',
        verbose_name='Tâche de déploiement',
        help_text='Tâche parente contenant ce déploiement'
    )
    
    # Informations du déploiement
    version = models.CharField(
        max_length=50,
        verbose_name='Version',
        help_text='Ex: v1.2.0, 2024.02.06'
    )
    environnement = models.CharField(
        max_length=20,
        choices=ENVIRONNEMENT_CHOICES,
        verbose_name='Environnement cible'
    )
    description = models.TextField(
        verbose_name='Description',
        help_text='Description détaillée du déploiement'
    )
    
    # Statut et priorité
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='PREVU',
        verbose_name='Statut'
    )
    priorite = models.CharField(
        max_length=20,
        choices=PRIORITE_CHOICES,
        default='NORMALE',
        verbose_name='Priorité'
    )
    
    # Responsable et exécutant
    responsable = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deploiements_responsable',
        verbose_name='Responsable'
    )
    executant = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deploiements_executes',
        verbose_name='Exécuté par',
        help_text='Personne qui a effectué le déploiement'
    )
    
    # Gouvernance - Autorisation
    autorise_par = models.ForeignKey(
        'Utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deploiements_autorises',
        verbose_name='Autorisé par'
    )
    date_autorisation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date d\'autorisation'
    )
    
    # Dates
    date_prevue = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date prévue'
    )
    date_debut = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de début'
    )
    date_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de fin'
    )
    
    # Logs et résultats
    logs_deploiement = models.TextField(
        blank=True,
        verbose_name='Logs de déploiement',
        help_text='Détails techniques du déploiement'
    )
    commentaires = models.TextField(
        blank=True,
        verbose_name='Commentaires'
    )
    
    # Incident lié en cas d'échec
    incident_cree = models.ForeignKey(
        'TacheEtape',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deploiement_origine_incident',
        verbose_name='Incident créé',
        help_text='Incident créé automatiquement en cas d\'échec'
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.PROTECT,
        related_name='deploiements_crees',
        verbose_name='Créé par'
    )
    
    class Meta:
        verbose_name = "Déploiement"
        verbose_name_plural = "Déploiements"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['tache_deploiement', 'statut']),
            models.Index(fields=['environnement', 'statut']),
            models.Index(fields=['version']),
        ]
    
    def __str__(self):
        return f"{self.version} sur {self.get_environnement_display()} - {self.get_statut_display()}"
    
    def clean(self):
        """Validation métier"""
        # Vérifier que la tâche parente est bien dans l'étape DEPLOIEMENT
        if self.tache_deploiement and self.tache_deploiement.etape.type_etape.nom != 'DEPLOIEMENT':
            raise ValidationError({
                'tache_deploiement': 'La tâche parente doit être dans l\'étape DEPLOIEMENT.'
            })
        
        # Vérifier que le responsable fait partie de l'équipe du projet
        if self.responsable:
            projet = self.tache_deploiement.etape.projet
            if not projet.affectations.filter(
                utilisateur=self.responsable,
                date_fin__isnull=True
            ).exists():
                raise ValidationError({
                    'responsable': 'Le responsable doit faire partie de l\'équipe du projet.'
                })
    
    def peut_etre_autorise(self):
        """Vérifie si le déploiement peut être autorisé"""
        return self.statut == 'PREVU' and not self.autorise_par
    
    def peut_etre_execute(self):
        """Vérifie si le déploiement peut être exécuté"""
        return self.statut == 'PREVU' and self.autorise_par is not None
    
    def autoriser(self, utilisateur):
        """Autorise le déploiement"""
        if not self.peut_etre_autorise():
            raise ValidationError('Ce déploiement ne peut pas être autorisé.')
        
        self.autorise_par = utilisateur
        self.date_autorisation = timezone.now()
        self.save()
    
    def demarrer(self, executant):
        """Démarre l'exécution du déploiement"""
        if not self.peut_etre_execute():
            raise ValidationError('Ce déploiement ne peut pas être exécuté.')
        
        self.statut = 'EN_COURS'
        self.executant = executant
        self.date_debut = timezone.now()
        self.save()
    
    def marquer_reussi(self, logs=''):
        """Marque le déploiement comme réussi"""
        self.statut = 'REUSSI'
        self.date_fin = timezone.now()
        if logs:
            self.logs_deploiement = logs
        self.save()
    
    def marquer_echec(self, logs='', creer_incident=True):
        """Marque le déploiement comme échoué et crée un incident si demandé"""
        from .models import TacheEtape
        
        self.statut = 'ECHEC'
        self.date_fin = timezone.now()
        if logs:
            self.logs_deploiement = logs
        self.save()
        
        # Créer un incident automatiquement
        if creer_incident and not self.incident_cree:
            incident = TacheEtape.objects.create(
                etape=self.tache_deploiement.etape,
                nom=f"INCIDENT - Échec déploiement {self.version}",
                description=f"Le déploiement de la version {self.version} "
                            f"sur {self.get_environnement_display()} a échoué.\n\n"
                            f"**Tâche parente:** {self.tache_deploiement.nom}\n"
                            f"**Logs du déploiement:**\n{self.logs_deploiement}\n\n"
                            f"**Action requise:** Analyser la cause de l'échec et corriger avant nouvelle tentative.",
                responsable=self.responsable,
                statut='A_FAIRE',
                priorite='CRITIQUE',
                createur=self.executant or self.createur
            )
            self.incident_cree = incident
            self.save()
            return incident
        return None
    
    def annuler(self, raison=''):
        """Annule le déploiement"""
        self.statut = 'ANNULE'
        if raison:
            self.commentaires = f"Annulé: {raison}\n{self.commentaires}"
        self.save()
    
    def get_duree(self):
        """Retourne la durée du déploiement"""
        if self.date_debut and self.date_fin:
            return self.date_fin - self.date_debut
        return None
    
    def est_termine(self):
        """Vérifie si le déploiement est terminé"""
        return self.statut in ['REUSSI', 'ECHEC', 'ANNULE']
