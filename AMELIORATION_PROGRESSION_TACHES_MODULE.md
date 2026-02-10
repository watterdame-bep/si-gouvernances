# Amélioration Progression Tâches de Module

## Objectif
Permettre au **responsable du module** ET au **responsable de la tâche** de modifier la progression des tâches du module, comme c'est le cas pour les tâches d'étape.

## Problème Initial
- Seul le responsable de la tâche pouvait modifier la progression
- Le responsable du module ne pouvait pas suivre/modifier la progression des tâches de son module
- Les URLs pour les actions sur les tâches de module étaient manquantes

## Solution Implémentée

### 1. Nouvelles URLs (core/urls.py)

Ajout de 3 nouvelles URLs pour les tâches de module :

```python
path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/progression/', 
     views_taches_module.mettre_a_jour_progression_tache_module_view, 
     name='mettre_a_jour_progression_tache_module'),

path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/demarrer/', 
     views_taches_module.demarrer_tache_module_view, 
     name='demarrer_tache_module'),

path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/terminer/', 
     views_taches_module.terminer_tache_module_view, 
     name='terminer_tache_module'),
```

### 2. Nouvelles Vues (core/views_taches_module.py)

#### A. `mettre_a_jour_progression_tache_module_view`

**Permissions** :
- ✅ Super admin
- ✅ Créateur du projet
- ✅ Responsable principal du projet
- ✅ **Responsable du module** (NOUVEAU)
- ✅ Responsable de la tâche

**Fonctionnalités** :
- Mise à jour du pourcentage de completion (0-100%)
- Contrainte : Tâche doit être EN_COURS
- Si progression = 100% → Statut devient TERMINEE automatiquement
- Notifications aux paliers de 25%, 50%, 75%, 100%
- Notification différenciée à 100% (message "Tâche terminée")
- Audit complet

#### B. `demarrer_tache_module_view`

**Permissions** : Identiques à la progression

**Fonctionnalités** :
- Passe le statut de A_FAIRE à EN_COURS
- Enregistre la date de début réelle
- Audit de l'action

#### C. `terminer_tache_module_view`

**Permissions** : Identiques à la progression

**Fonctionnalités** :
- Passe le statut à TERMINEE
- Met la progression à 100%
- Enregistre la date de fin réelle
- Notification au responsable du projet
- Audit de l'action

### 3. Modifications Vue `gestion_taches_module_view`

Ajout d'une nouvelle variable de contexte :

```python
peut_modifier_taches = False  # Permission de modification des tâches
```

**Logique** :
- Super admin, créateur projet, responsable projet → `peut_modifier_taches = True`
- **Responsable du module** → `peut_modifier_taches = True`
- Contributeur simple → `peut_modifier_taches = False` (mais peut modifier ses propres tâches)

### 4. Modifications Template (gestion_taches_module.html)

**Colonne Progression** :
- Reste cliquable pour toutes les tâches EN_COURS
- La vue backend vérifie les permissions

**Boutons d'Action** :
```django
{% if peut_modifier_taches or tache.responsable.id == user.id %}
    <!-- Actions de modification -->
{% endif %}
```

Cette condition permet :
- Au responsable du module de modifier toutes les tâches
- Au responsable de la tâche de modifier sa propre tâche

## Comportement Final

### Responsable du Module
✅ Peut voir toutes les tâches du module
✅ Peut créer de nouvelles tâches
✅ Peut assigner des tâches
✅ **Peut modifier la progression de TOUTES les tâches**
✅ **Peut démarrer/terminer TOUTES les tâches**
✅ Reçoit des notifications de progression

### Responsable d'une Tâche (Contributeur)
✅ Voit ses propres tâches
✅ **Peut modifier la progression de SA tâche**
✅ **Peut démarrer/terminer SA tâche**
✅ Peut créer des tâches (si `peut_creer_taches = True`)

### Contributeur Simple (sans tâche assignée)
✅ Voit ses tâches créées
✅ Peut créer des tâches (si `peut_creer_taches = True`)
❌ Ne peut pas modifier les tâches des autres

## Notifications

### Progression (25%, 50%, 75%)
```
Titre: 📊 Progression: [Nom Tâche] (X%)
Message: [Utilisateur] a mis à jour la progression de '[Nom Tâche]' du module '[Nom Module]' à X%
```

### Progression à 100%
```
Titre: ✅ Tâche terminée: [Nom Tâche]
Message: [Utilisateur] a terminé la tâche '[Nom Tâche]' du module '[Nom Module]'
```

## Cohérence avec Tâches d'Étape

Le système est maintenant cohérent avec les tâches d'étape :
- ✅ Responsable de l'entité (étape/module) peut tout modifier
- ✅ Responsable de la tâche peut modifier sa tâche
- ✅ Slider de progression accessible selon les permissions
- ✅ Notifications aux paliers significatifs
- ✅ Passage automatique à TERMINEE à 100%

## Fichiers Modifiés

1. **core/urls.py** - Ajout de 3 nouvelles URLs
2. **core/views_taches_module.py** - Ajout de 3 nouvelles vues + modification de `gestion_taches_module_view`
3. **templates/core/gestion_taches_module.html** - Modification de la condition d'affichage des actions

## Test Recommandé

1. **En tant que Responsable de Module** :
   - Créer une tâche et l'assigner à un contributeur
   - Vérifier qu'on peut modifier la progression de cette tâche
   - Tester le slider de progression
   - Vérifier la notification à 100%

2. **En tant que Contributeur (responsable de tâche)** :
   - Vérifier qu'on peut modifier la progression de sa propre tâche
   - Vérifier qu'on ne peut pas modifier les tâches des autres

3. **En tant que Contributeur Simple** :
   - Vérifier qu'on ne voit que ses tâches créées
   - Vérifier qu'on ne peut pas modifier les tâches des autres

## Date
10 février 2026
