# Correction du Statut par Défaut des Tâches de Module

**Date**: 11 février 2026  
**Statut**: ✅ CORRIGÉ

## Problème Identifié

Lors de la création d'une tâche de module, le statut était défini à `EN_ATTENTE` au lieu de `A_FAIRE`, ce qui causait un problème d'affichage des boutons d'action.

### Symptômes

- DON DIEU ne voyait pas le bouton "Démarrer" pour la tâche qui lui était assignée
- Le template ne reconnaissait pas le statut `EN_ATTENTE` (statut invalide)
- Aucun bouton d'action n'était affiché dans la colonne Actions

### Diagnostic

```
Tâche: "Tache pour tester coté admin"
Statut actuel: EN_ATTENTE ❌
Responsable: DON DIEU ✅

⚠️ PROBLÈME: Le statut EN_ATTENTE n'existe pas dans le modèle TacheModule
Statuts valides: A_FAIRE, EN_COURS, EN_PAUSE, TERMINEE
```

## Cause Racine

Dans la fonction `creer_tache_module_nouvelle_view()` (ligne ~240), le statut était forcé à `EN_ATTENTE` :

```python
# ❌ AVANT (incorrect)
tache = TacheModule.objects.create(
    module=module,
    nom=nom,
    description=description,
    responsable=responsable,
    createur=user,
    statut='EN_ATTENTE'  # ❌ Statut invalide
)
```

## Solution Appliquée

### 1. Correction de la Vue

**Fichier**: `core/views_taches_module.py`  
**Fonction**: `creer_tache_module_nouvelle_view()`  
**Ligne**: ~240

```python
# ✅ APRÈS (correct)
tache = TacheModule.objects.create(
    module=module,
    nom=nom,
    description=description,
    responsable=responsable,
    createur=user,
    statut='A_FAIRE'  # ✅ Statut valide
)
```

### 2. Vérification du Modèle

Le modèle `TacheModule` a déjà le bon statut par défaut :

```python
# core/models.py - ligne 1281
statut = models.CharField(
    max_length=20, 
    choices=STATUT_CHOICES, 
    default='A_FAIRE'  # ✅ Correct
)
```

### 3. Correction des Tâches Existantes

Script exécuté : `corriger_statut_tache_26.py`

```
✅ Tâche 26: "Tache pour tester coté admin" → A_FAIRE
✅ Tâche 25: "Tache des notiifcation" → A_FAIRE
```

## Statuts Valides du Modèle TacheModule

```python
STATUT_CHOICES = [
    ('A_FAIRE', 'À faire'),      # ✅ Statut initial
    ('EN_COURS', 'En cours'),    # ✅ Tâche démarrée
    ('EN_PAUSE', 'En pause'),    # ✅ Tâche mise en pause
    ('TERMINEE', 'Terminée'),    # ✅ Tâche terminée
]
```

## Workflow des Statuts

```
A_FAIRE → EN_COURS → TERMINEE
            ↓  ↑
         EN_PAUSE
```

### Actions Disponibles par Statut

| Statut | Bouton Visible | Action |
|--------|---------------|--------|
| A_FAIRE | 🟠 Démarrer | Passe à EN_COURS |
| EN_COURS | 🟡 Pause + 🟢 Terminer | Passe à EN_PAUSE ou TERMINEE |
| EN_PAUSE | 🟠 Reprendre | Passe à EN_COURS |
| TERMINEE | ✅ (grisé) | Aucune action |

## Conditions d'Affichage des Boutons

Le template vérifie :

```django
{% if tache.responsable and tache.responsable.id == user.id %}
    {% if tache.statut == 'A_FAIRE' %}
        <!-- Bouton Démarrer -->
    {% elif tache.statut == 'EN_COURS' %}
        <!-- Boutons Pause + Terminer -->
    {% elif tache.statut == 'EN_PAUSE' %}
        <!-- Bouton Reprendre -->
    {% elif tache.statut == 'TERMINEE' %}
        <!-- Icône check grisée -->
    {% endif %}
{% endif %}
```

## Tests Effectués

### Test 1: Création de Tâche
- [x] Créer une nouvelle tâche
- [x] Vérifier que le statut est `A_FAIRE`
- [x] Vérifier que le bouton "Démarrer" est visible pour le responsable

### Test 2: Correction des Tâches Existantes
- [x] Identifier les tâches avec statut `EN_ATTENTE`
- [x] Corriger automatiquement vers `A_FAIRE`
- [x] Vérifier l'affichage des boutons après correction

### Test 3: Workflow Complet
- [x] A_FAIRE → Démarrer → EN_COURS
- [x] EN_COURS → Pause → EN_PAUSE
- [x] EN_PAUSE → Reprendre → EN_COURS
- [x] EN_COURS → Terminer → TERMINEE

## Fichiers Modifiés

1. **core/views_taches_module.py**
   - Fonction: `creer_tache_module_nouvelle_view()`
   - Changement: `statut='EN_ATTENTE'` → `statut='A_FAIRE'`

2. **Scripts de correction**
   - `corriger_statut_tache_26.py` - Correction des tâches existantes
   - `debug_bouton_demarrer_don_dieu.py` - Diagnostic du problème

## Impact

### Avant la Correction
- ❌ Tâches créées avec statut invalide `EN_ATTENTE`
- ❌ Aucun bouton d'action visible
- ❌ Impossible de démarrer les tâches

### Après la Correction
- ✅ Tâches créées avec statut valide `A_FAIRE`
- ✅ Bouton "Démarrer" visible pour le responsable
- ✅ Workflow complet fonctionnel

## Recommandations

1. **Validation Backend**: Ajouter une validation dans le modèle pour rejeter les statuts invalides
2. **Tests Unitaires**: Créer des tests pour vérifier le statut par défaut
3. **Migration**: Créer une migration pour corriger toutes les tâches existantes avec statut invalide

## Conclusion

Le problème est maintenant résolu. Toutes les nouvelles tâches de module seront créées avec le statut `A_FAIRE`, et les boutons d'action s'afficheront correctement pour les responsables des tâches.

DON DIEU peut maintenant voir et utiliser le bouton "Démarrer" pour la tâche qui lui est assignée.
