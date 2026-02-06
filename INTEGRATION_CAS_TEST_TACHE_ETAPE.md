# Intégration des Cas de Test avec les Tâches d'Étape

## Résumé

L'intégration des cas de test (`CasTest`) avec les tâches d'étape (`TacheEtape`) a été complétée avec succès. Les utilisateurs peuvent maintenant gérer les cas de test directement depuis l'interface de gestion des tâches d'étape.

## Modifications Effectuées

### 1. Modèle `CasTest` (core/models.py)

**Changement principal**: Le modèle `CasTest` utilise maintenant `tache_etape` au lieu de `tache_test`.

```python
class CasTest(models.Model):
    # Relations - Utilise TacheEtape directement
    tache_etape = models.ForeignKey('TacheEtape', on_delete=models.CASCADE, related_name='cas_tests')
    
    # ... autres champs ...
    
    def marquer_comme_passe(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme passé"""
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour la progression de la tâche d'étape parente
        self.tache_etape.mettre_a_jour_progression_depuis_cas_tests()
```

**Raison**: La base de données contenait déjà la colonne `tache_etape_id`, donc le modèle a été mis à jour pour correspondre à la structure existante.

### 2. Modèle `TacheEtape` (core/models.py)

**Ajout d'une méthode**: Méthode pour mettre à jour la progression basée sur les cas de test.

```python
def mettre_a_jour_progression_depuis_cas_tests(self):
    """Alias pour mettre_a_jour_statut_avec_sous_taches - utilisé par CasTest"""
    self.mettre_a_jour_statut_avec_sous_taches()
```

Cette méthode met automatiquement à jour le statut et la progression de la tâche d'étape en fonction des résultats des cas de test.

### 3. Vue `gestion_cas_tests_tache_view` (core/views_tests.py)

**Simplification**: La vue ne crée plus de pont avec `TacheTest`, elle travaille directement avec `TacheEtape`.

```python
@login_required
def gestion_cas_tests_tache_view(request, projet_id, etape_id, tache_id):
    """Vue de gestion des cas de test pour une tâche d'étape spécifique"""
    # ...
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Récupérer les cas de test pour cette tâche d'étape
    cas_tests = CasTest.objects.filter(tache_etape=tache).order_by('ordre', 'date_creation')
    # ...
```

### 4. Vue `creer_cas_test_view` (core/views_tests.py)

**Mise à jour**: Utilise maintenant `tache_etape` au lieu de `tache_test`.

```python
@login_required
@require_http_methods(["POST"])
def creer_cas_test_view(request, projet_id, etape_id, tache_id):
    """Vue de création d'un cas de test pour une tâche d'étape"""
    # ...
    tache_etape = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Créer le cas de test
    cas_test = CasTest.objects.create(
        tache_etape=tache_etape,
        # ... autres champs ...
    )
```

### 5. URLs (core/urls.py)

**Mise à jour**: Les URLs utilisent maintenant `tache_id` pour les tâches d'étape.

```python
# Gestion des cas de test (CasTest) - Hiérarchie
path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/', 
     views_tests.gestion_cas_tests_tache_view, name='gestion_cas_tests_tache'),
path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/creer/', 
     views_tests.creer_cas_test_view, name='creer_cas_test'),
```

### 6. Template (templates/core/gestion_cas_tests_tache.html)

**Mise à jour**: Le template utilise maintenant `tache.id` au lieu de `tache_test.id`.

```javascript
fetch('{% url "creer_cas_test" projet.id etape.id tache.id %}', {
    method: 'POST',
    // ...
})
```

### 7. Template (templates/core/gestion_taches_etape.html)

**Ajout du bouton**: Bouton "Gérer les cas de test" pour les tâches d'étape de type TEST.

```html
{% if etape.type_etape.nom == 'TESTS' %}
<a href="{% url 'gestion_cas_tests_tache' projet.id etape.id tache.id %}"
   class="text-purple-600 hover:text-purple-800 p-1.5 rounded transition-colors"
   title="Gérer les cas de test">
    <i class="fas fa-vial text-sm"></i>
</a>
{% endif %}
```

## Fonctionnalités

### Interface de Gestion des Cas de Test

L'interface comprend:

1. **Statistiques en temps réel**:
   - Total des cas de test
   - Cas passés
   - Cas échoués
   - Cas en cours
   - Cas en attente
   - Pourcentage de réussite

2. **Tableau des cas de test**:
   - Numéro du cas
   - Nom et description
   - Statut (avec badges colorés)
   - Priorité
   - Exécuteur
   - Actions (voir, marquer comme passé/échoué)

3. **Modal de création**:
   - Nom du cas
   - Description
   - Priorité
   - Étapes d'exécution
   - Résultats attendus
   - Données d'entrée (optionnel)
   - Préconditions (optionnel)

### Mise à Jour Automatique

Lorsqu'un cas de test est marqué comme passé ou échoué:
1. Le statut du cas de test est mis à jour
2. La date d'exécution est enregistrée
3. L'exécuteur est enregistré
4. La progression de la tâche d'étape parente est automatiquement mise à jour

## Structure de la Base de Données

La table `core_castest` contient les colonnes suivantes:
- `id` (UUID)
- `numero_cas` (VARCHAR)
- `nom` (VARCHAR)
- `description` (TEXT)
- `priorite` (VARCHAR)
- `donnees_entree` (TEXT)
- `preconditions` (TEXT)
- `etapes_execution` (TEXT)
- `resultats_attendus` (TEXT)
- `resultats_obtenus` (TEXT)
- `statut` (VARCHAR)
- `date_execution` (DATETIME)
- `date_creation` (DATETIME)
- `date_modification` (DATETIME)
- `ordre` (INT)
- `createur_id` (UUID)
- `executeur_id` (UUID)
- **`tache_etape_id` (UUID)** ← Clé étrangère vers TacheEtape

## Accès à l'Interface

Pour accéder à l'interface de gestion des cas de test:

1. Naviguer vers un projet
2. Accéder à une étape de type "TESTS"
3. Cliquer sur "Gérer les tâches"
4. Pour chaque tâche, cliquer sur l'icône de fiole (vial) pour gérer ses cas de test

URL format: `/projets/{projet_id}/etapes/{etape_id}/taches/{tache_id}/cas-tests/`

## Tests

Un script de test d'intégration a été créé: `test_cas_test_integration.py`

Ce script vérifie:
- La présence d'étapes de type TEST
- Les tâches d'étape associées
- Les cas de test existants
- L'URL d'accès à l'interface

Exécution: `python test_cas_test_integration.py`

## Notes Importantes

1. **Compatibilité**: Cette intégration remplace l'ancien système qui utilisait `TacheTest` comme intermédiaire.

2. **Migration**: Aucune migration Django n'était nécessaire car la base de données contenait déjà la bonne structure.

3. **Permissions**: Les permissions sont gérées via `ServiceTests._peut_creer_tests()` et `ServiceTests._peut_executer_tests()`.

4. **Étapes TEST uniquement**: Cette fonctionnalité n'est disponible que pour les étapes de type "TESTS".

## Prochaines Étapes Possibles

1. Ajouter la possibilité de modifier un cas de test existant
2. Ajouter la possibilité de supprimer un cas de test
3. Ajouter des filtres et tri dans le tableau des cas de test
4. Ajouter l'export des résultats de test en PDF/Excel
5. Ajouter des graphiques de progression des tests
6. Intégrer avec le système de bugs pour créer automatiquement un bug lors d'un échec

## Conclusion

L'intégration est complète et fonctionnelle. Les utilisateurs peuvent maintenant gérer les cas de test directement depuis l'interface de gestion des tâches d'étape, avec une mise à jour automatique de la progression basée sur les résultats des tests.
