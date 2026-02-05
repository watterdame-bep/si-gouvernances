# Architecture Hiérarchique des Tests - Version 2

## 🎯 Objectif

Implémenter une structure hiérarchique pour les tests où :
- **TâcheTest** = Sujet de test (ex: Authentification)
- **CasTest** = Cas de test individuel (ex: Connexion avec email valide)
- **BugTest** = Bug lié à un cas de test qui échoue

## 🏗️ Structure Hiérarchique

```
Étape TEST
└── TâcheTest (Sujet de test - ex: "Authentification")
    ├── CasTest 1 (ex: "Connexion avec email valide")
    │   ├── Données de test
    │   ├── Résultats attendus
    │   ├── Résultats obtenus
    │   ├── Statut (PASSE/ECHEC/EN_ATTENTE)
    │   └── Bug lié (si échec)
    ├── CasTest 2 (ex: "Connexion avec mot de passe incorrect")
    └── CasTest 3 (ex: "Connexion avec compte bloqué")
```

## 📊 Logique Métier

### Statut Global de TâcheTest
Le statut de la TâcheTest est calculé automatiquement basé sur ses cas :

- ✅ **PASSE** : Tous les cas passent
- ❌ **ECHEC** : Au moins un cas échoue
- ⏳ **EN_COURS** : Certains cas exécutés, d'autres non
- 🔄 **EN_ATTENTE** : Aucun cas exécuté

### Workflow
1. QA crée une **TâcheTest** "Authentification"
2. QA ajoute plusieurs **CasTest** dans cette tâche
3. QA exécute chaque cas individuellement
4. Si un cas échoue → création automatique d'un **Bug**
5. Statut global mis à jour automatiquement

## 🔧 Implémentation Technique

### Modèle CasTest

```python
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
    tache_test = models.ForeignKey(TacheTest, on_delete=models.CASCADE, related_name='cas_tests')
    
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
        Utilisateur, 
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
        Utilisateur, 
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
            prefix = self.tache_test.nom[:4].upper().replace(' ', '')
            existing_count = CasTest.objects.filter(tache_test=self.tache_test).count()
            self.numero_cas = f"{prefix}-{existing_count + 1:03d}"
        
        super().save(*args, **kwargs)
    
    def marquer_comme_passe(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme passé"""
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        self.tache_test.mettre_a_jour_statut()
    
    def marquer_comme_echec(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme échoué"""
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        self.tache_test.mettre_a_jour_statut()
```

### Méthodes TâcheTest

```python
def mettre_a_jour_statut(self):
    """Mettre à jour le statut de la tâche basé sur ses cas de test"""
    cas_tests = self.cas_tests.all()
    
    if not cas_tests.exists():
        return
    
    total_cas = cas_tests.count()
    cas_passes = cas_tests.filter(statut='PASSE').count()
    cas_echecs = cas_tests.filter(statut='ECHEC').count()
    cas_en_cours = cas_tests.filter(statut='EN_COURS').count()
    
    if cas_echecs > 0:
        self.statut = 'ECHEC'
    elif cas_passes == total_cas:
        self.statut = 'PASSE'
    elif cas_en_cours > 0 or cas_passes > 0:
        self.statut = 'EN_COURS'
    else:
        self.statut = 'EN_ATTENTE'
    
    self.save()

@property
def statistiques_cas(self):
    """Retourne les statistiques des cas de test"""
    cas_tests = self.cas_tests.all()
    return {
        'total': cas_tests.count(),
        'passes': cas_tests.filter(statut='PASSE').count(),
        'echecs': cas_tests.filter(statut='ECHEC').count(),
        'en_cours': cas_tests.filter(statut='EN_COURS').count(),
        'en_attente': cas_tests.filter(statut='EN_ATTENTE').count(),
    }

@property
def progression_pourcentage(self):
    """Calcule le pourcentage de progression"""
    stats = self.statistiques_cas
    if stats['total'] == 0:
        return 0
    return round((stats['passes'] / stats['total']) * 100, 1)
```

## 🎨 Interface Utilisateur

### Vue Principale - TâcheTest
- Liste des tâches de test avec progression
- Statut global calculé automatiquement
- Bouton "Voir les cas" pour chaque tâche

### Vue Détail - CasTest
- Liste des cas de test dans une tâche
- Statut individuel de chaque cas
- Boutons d'exécution pour chaque cas
- Création automatique de bugs en cas d'échec

### Workflow QA
1. **Créer une TâcheTest** : "Authentification"
2. **Ajouter des CasTest** :
   - "Connexion avec email valide"
   - "Connexion avec mot de passe incorrect"
   - "Connexion avec compte bloqué"
3. **Exécuter chaque cas** individuellement
4. **Voir le statut global** mis à jour automatiquement

## 📋 URLs Nécessaires

```python
# Gestion des tâches de test (niveau supérieur)
path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/', views.gestion_tests_view, name='gestion_tests'),
path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/creer/', views.creer_tache_test_view, name='creer_tache_test'),

# Gestion des cas de test (niveau détail)
path('projets/<uuid:projet_id>/tests/<uuid:tache_id>/cas/', views.gestion_cas_tests_view, name='gestion_cas_tests'),
path('projets/<uuid:projet_id>/tests/<uuid:tache_id>/cas/creer/', views.creer_cas_test_view, name='creer_cas_test'),
path('projets/<uuid:projet_id>/cas/<uuid:cas_id>/executer/', views.executer_cas_test_view, name='executer_cas_test'),
```

## 🚀 Prochaines Étapes

1. **Corriger models.py** et créer la migration
2. **Créer les vues hiérarchiques** :
   - Vue liste des TâcheTest
   - Vue détail avec CasTest
   - Vue d'exécution des cas
3. **Créer les templates** :
   - Liste des tâches de test
   - Détail d'une tâche avec ses cas
   - Formulaires de création
4. **Implémenter la logique métier** :
   - Calcul automatique des statuts
   - Création automatique de bugs
   - Notifications

## ✅ Avantages de cette Architecture

- **Granularité** : Tests détaillés au niveau des cas
- **Traçabilité** : Chaque cas a son historique
- **Automatisation** : Statuts calculés automatiquement
- **Flexibilité** : Ajout facile de nouveaux cas
- **Reporting** : Statistiques précises par tâche et cas

Cette architecture respecte les pratiques QA professionnelles et offre une gestion complète des tests hiérarchiques.