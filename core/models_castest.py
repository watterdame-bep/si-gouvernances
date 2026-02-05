"""
Modèle CasTest pour la structure hiérarchique des tests
"""

import uuid
from django.db import models
from django.utils import timezone


class CasTest(models.Model):
    """Cas de test individuel dans une tâche de test"""
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('PASSE', 'Passé'),
        ('ECHEC', 'Échec'),
        ('BLOQUE', 'Bloqué'),
    ]
    
    PRIORITE_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_cas = models.CharField(max_length=30, help_text="Auto-généré: AUTH-001, AUTH-002, etc.")
    
    # Relations
    tache_test = models.ForeignKey('TacheTest', on_delete=models.CASCADE, related_name='cas_tests')
    
    # Informations du cas
    nom = models.CharField(max_length=200, help_text="Ex: Connexion avec email valide")
    description = models.TextField(help_text="Description détaillée du cas de test")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Données de test
    donnees_entree = models.TextField(blank=True, help_text="Données d'entrée du test")
    preconditions = models.TextField(blank=True, help_text="Conditions préalables à remplir")
    
    # Étapes d'exécution
    etapes_execution = models.TextField(help_text="Étapes détaillées pour exécuter ce cas")
    
    # Résultats
    resultats_attendus = models.TextField(help_text="Résultats attendus pour ce cas spécifique")
    resultats_obtenus = models.TextField(blank=True, help_text="Résultats obtenus lors de l'exécution")
    
    # Statut et exécution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_execution = models.DateTimeField(null=True, blank=True)
    
    # Assignation et exécution
    executeur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cas_tests_executes',
        help_text="QA qui a exécuté ce cas"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cas_tests_crees'
    )
    
    # Ordre dans la tâche
    ordre = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['ordre', 'date_creation']
        unique_together = ['tache_test', 'numero_cas']
        verbose_name = "Cas de test"
        verbose_name_plural = "Cas de tests"
    
    def __str__(self):
        return f"{self.numero_cas} - {self.nom}"
    
    def save(self, *args, **kwargs):
        # Auto-générer le numéro de cas si pas défini
        if not self.numero_cas:
            # Prendre le préfixe de la tâche parent et ajouter un numéro séquentiel
            prefix = self.tache_test.nom[:4].upper().replace(' ', '')
            existing_count = CasTest.objects.filter(tache_test=self.tache_test).count()
            self.numero_cas = f"{prefix}-{existing_count + 1:03d}"
        
        super().save(*args, **kwargs)
    
    @property
    def est_critique(self):
        """Vérifie si ce cas est critique"""
        return self.priorite == 'CRITIQUE'
    
    @property
    def peut_etre_execute(self):
        """Vérifie si ce cas peut être exécuté"""
        return self.statut in ['EN_ATTENTE', 'ECHEC']
    
    @property
    def est_termine(self):
        """Vérifie si ce cas est terminé (passé ou échoué)"""
        return self.statut in ['PASSE', 'ECHEC']
    
    def marquer_comme_passe(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme passé"""
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()
    
    def marquer_comme_echec(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme échoué"""
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()