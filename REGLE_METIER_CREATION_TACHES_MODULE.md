# Règle Métier : Création de Tâches de Module

## Règle Appliquée

**SEUL le responsable du module peut créer des tâches dans ce module.**

Les contributeurs et consultants peuvent :
- ✅ Voir leurs tâches assignées
- ✅ Modifier leurs propres tâches (progression, statut)
- ❌ Créer de nouvelles tâches

## Justification

Cette règle garantit que :
1. Le responsable du module garde le contrôle sur la planification
2. Les tâches sont créées de manière cohérente
3. Il n'y a pas de prolifération anarchique de tâches

## Hiérarchie des Permissions de Création

### Peuvent créer des tâches :
1. ✅ **Super admin**
2. ✅ **Créateur du projet**
3. ✅ **Responsable principal du projet**
4. ✅ **Responsable du module**

### Ne peuvent PAS créer de tâches :
1. ❌ **Contributeur** (même avec `peut_creer_taches = True`)
2. ❌ **Consultant**

## Permissions des Contributeurs

### Ce qu'un contributeur PEUT faire :
- ✅ Accéder à l'interface des tâches du module
- ✅ Voir ses tâches assignées
- ✅ Démarrer ses tâches (A_FAIRE → EN_COURS)
- ✅ Modifier la progression de ses tâches (slider 0-100%)
- ✅ Terminer ses tâches
- ✅ Voir les détails de ses tâches

### Ce qu'un contributeur NE PEUT PAS faire :
- ❌ Créer de nouvelles tâches
- ❌ Voir le bouton "Nouvelle Tâche"
- ❌ Assigner des tâches à d'autres membres
- ❌ Modifier les tâches des autres

## Workflow Typique

### 1. Responsable du Module
```
1. Crée les tâches du module
2. Assigne chaque tâche à un contributeur
3. Suit la progression de toutes les tâches
4. Peut modifier n'importe quelle tâche
```

### 2. Contributeur
```
1. Accède à "Mes Modules"
2. Clique sur l'icône "Gérer mes tâches"
3. Voit uniquement ses tâches assignées
4. Démarre une tâche
5. Met à jour la progression
6. Termine la tâche
```

## Modification Appliquée

### Fichier : `core/views_taches_module.py`

**Avant** :
```python
# Permission de créer des tâches selon l'affectation
peut_creer_taches = affectation_membre.peut_creer_taches
```

**Après** :
```python
# Les contributeurs NE PEUVENT PAS créer de tâches
peut_creer_taches = False
```

## Impact sur l'Interface

### Interface "Gestion des Tâches du Module"

**Pour le Responsable du Module** :
- ✅ Bouton "Nouvelle Tâche" visible
- ✅ Peut assigner des tâches
- ✅ Voit toutes les tâches du module

**Pour le Contributeur** :
- ❌ Bouton "Nouvelle Tâche" caché
- ❌ Ne peut pas assigner de tâches
- ✅ Voit uniquement ses tâches

## Champ `peut_creer_taches` dans AffectationModule

Le champ `peut_creer_taches` dans le modèle `AffectationModule` est maintenant **ignoré** pour les contributeurs. Seul le rôle `RESPONSABLE` permet la création de tâches.

Ce champ pourrait être utilisé dans le futur pour des cas spéciaux, mais actuellement la règle est stricte : **seul le responsable crée des tâches**.

## Test Recommandé

1. **En tant que Responsable de Module** :
   - Accéder à l'interface des tâches du module
   - Vérifier que le bouton "Nouvelle Tâche" s'affiche
   - Créer une tâche et l'assigner à un contributeur

2. **En tant que Contributeur** :
   - Accéder à "Mes Modules"
   - Cliquer sur "Gérer mes tâches"
   - Vérifier que le bouton "Nouvelle Tâche" ne s'affiche PAS
   - Vérifier qu'on peut modifier ses propres tâches

## Date
10 février 2026
