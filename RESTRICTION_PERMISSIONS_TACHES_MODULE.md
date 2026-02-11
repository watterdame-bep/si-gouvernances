# Restriction des Permissions - Tâches de Module

**Date**: 11 février 2026  
**Statut**: ✅ Implémenté

## Modifications Demandées

### 1. Supprimer le Bouton Progression de la Colonne Actions
La progression se gère via la colonne "Progression" (cliquable), pas via un bouton dans la colonne "Actions".

### 2. Seul le Responsable Peut Gérer sa Tâche
Seul le responsable assigné à une tâche peut :
- Démarrer la tâche
- Mettre en pause la tâche
- Reprendre la tâche
- Terminer la tâche
- Mettre à jour la progression

Le créateur de la tâche et le responsable du module ne peuvent PAS gérer les tâches des autres.

### 3. Filtrage des Tâches dans "Mes Modules"
Quand un utilisateur accède aux tâches d'un module depuis "Mes Modules", il ne voit que les tâches qui lui sont assignées.

## Implémentation

### 1. Template - Suppression du Bouton Progression

**Fichier** : `templates/core/gestion_taches_module.html`

**Avant** (statut EN_COURS) :
```django
{% elif tache.statut == 'EN_COURS' %}
    <button onclick="ouvrirModalProgression(...)">Progression</button>
    <button onclick="mettreEnPause(...)">Pause</button>
    <button onclick="terminerTache(...)">Terminer</button>
```

**Après** (statut EN_COURS) :
```django
{% elif tache.statut == 'EN_COURS' %}
    <button onclick="mettreEnPause(...)">Pause</button>
    <button onclick="terminerTache(...)">Terminer</button>
```

La progression se gère maintenant uniquement via la colonne "Progression" qui est cliquable.

### 2. Template - Restriction aux Responsables Uniquement

**Avant** :
```django
{% if peut_modifier_taches or tache.createur.id == user.id or tache.responsable and tache.responsable.id == user.id %}
    <!-- Actions -->
{% endif %}
```

**Après** :
```django
{% if tache.responsable and tache.responsable.id == user.id %}
    <!-- Actions -->
{% endif %}
```

Seul le responsable de la tâche voit les boutons d'action.

### 3. Vue - Filtrage des Tâches

**Fichier** : `core/views_taches_module.py`

**Fonction** : `gestion_taches_module_view()`

**Avant** :
```python
# Tous les membres voient toutes les tâches
taches = module.taches.all().select_related('responsable', 'createur').order_by('-date_creation')
```

**Après** :
```python
# Si on vient de "Mes Modules", filtrer pour ne montrer que les tâches assignées
if from_mes_modules and est_membre_simple:
    taches = module.taches.filter(responsable=user).select_related('responsable', 'createur').order_by('-date_creation')
else:
    # Sinon, tous les membres voient toutes les tâches
    taches = module.taches.all().select_related('responsable', 'createur').order_by('-date_creation')
```

### 4. Vues Backend - Restriction des Permissions

Toutes les fonctions de gestion des tâches ont été modifiées pour vérifier que l'utilisateur est le responsable de la tâche.

#### Fonction `demarrer_tache_module_view()`

**Avant** : Vérification complexe avec plusieurs rôles
```python
peut_modifier = False
if user.est_super_admin(): peut_modifier = True
elif projet.createur == user: peut_modifier = True
elif responsable_principal: peut_modifier = True
elif responsable_module: peut_modifier = True
elif tache.createur == user: peut_modifier = True
elif tache.responsable == user: peut_modifier = True
```

**Après** : Vérification simple
```python
# RÈGLE: Seul le responsable de la tâche peut la démarrer
if not tache.responsable:
    return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})

if tache.responsable != user:
    return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la démarrer'})
```

#### Fonction `mettre_en_pause_tache_module_view()`

Même logique appliquée :
```python
# RÈGLE: Seul le responsable de la tâche peut la mettre en pause
if not tache.responsable:
    return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})

if tache.responsable != user:
    return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la mettre en pause'})
```

#### Fonction `terminer_tache_module_view()`

Même logique appliquée :
```python
# RÈGLE: Seul le responsable de la tâche peut la terminer
if not tache.responsable:
    return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})

if tache.responsable != user:
    return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la terminer'})
```

#### Fonction `mettre_a_jour_progression_tache_module_view()`

Même logique appliquée :
```python
# RÈGLE: Seul le responsable de la tâche peut mettre à jour la progression
if not tache.responsable:
    return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})

if tache.responsable != user:
    return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut mettre à jour la progression'})
```

### 5. Message Informatif Mis à Jour

**Avant** :
```
Vue contributeur
Vous voyez toutes les tâches du module. Vous pouvez modifier vos propres tâches.
```

**Après** :
```
Mes Tâches
Vous voyez uniquement les tâches qui vous sont assignées. Seul le responsable d'une tâche peut la démarrer et la gérer.
```

## Workflow Utilisateur

### Responsable du Module
1. Accède à "Gestion des modules" → "Tâches du module"
2. Voit TOUTES les tâches du module
3. Peut créer de nouvelles tâches
4. Peut assigner des tâches aux membres
5. Ne peut PAS démarrer/modifier les tâches des autres

### Contributeur (via "Mes Modules")
1. Accède à "Mes Modules" → Clique sur l'icône "Gérer mes tâches"
2. Voit UNIQUEMENT ses tâches assignées
3. Ne peut PAS créer de tâches
4. Peut gérer ses propres tâches (démarrer, pause, progression, terminer)

### Responsable d'une Tâche
1. Voit le bouton "Démarrer" si la tâche est à faire
2. Peut mettre en pause une tâche en cours
3. Peut reprendre une tâche en pause
4. Peut terminer une tâche en cours
5. Peut mettre à jour la progression via la colonne "Progression" (cliquable)

## Colonne Progression

La colonne "Progression" reste cliquable pour le responsable de la tâche :
- Tâche EN_COURS : Bouton bleu cliquable avec pourcentage
- Tâche TERMINEE : Badge vert "100%"
- Autres statuts : Texte gris avec cadenas (non modifiable)

## Colonne Actions

Les boutons affichés selon le statut (uniquement pour le responsable) :

| Statut | Boutons Disponibles |
|--------|---------------------|
| A_FAIRE | Démarrer (orange) |
| EN_COURS | Pause (jaune) + Terminer (vert) |
| EN_PAUSE | Reprendre (orange) |
| TERMINEE | Icône check grise (pas d'action) |

## Messages d'Erreur

Si un utilisateur non-responsable tente une action :
- "Seul le responsable de la tâche peut la démarrer"
- "Seul le responsable de la tâche peut la mettre en pause"
- "Seul le responsable de la tâche peut la terminer"
- "Seul le responsable de la tâche peut mettre à jour la progression"

Si une tâche n'a pas de responsable :
- "Cette tâche n'a pas de responsable assigné"

## Avantages

1. **Clarté des responsabilités** : Chaque tâche a un responsable unique
2. **Autonomie** : Les contributeurs gèrent leurs propres tâches
3. **Simplicité** : Interface épurée avec seulement les actions pertinentes
4. **Sécurité** : Impossible de modifier les tâches des autres
5. **Traçabilité** : Chaque action est liée au responsable de la tâche

## Fichiers Modifiés

1. **templates/core/gestion_taches_module.html**
   - Suppression du bouton Progression de la colonne Actions
   - Restriction de l'affichage des boutons au responsable uniquement
   - Mise à jour du message informatif

2. **core/views_taches_module.py**
   - `gestion_taches_module_view()` - Filtrage des tâches pour "Mes Modules"
   - `demarrer_tache_module_view()` - Restriction au responsable
   - `mettre_en_pause_tache_module_view()` - Restriction au responsable
   - `terminer_tache_module_view()` - Restriction au responsable
   - `mettre_a_jour_progression_tache_module_view()` - Restriction au responsable

## Tests Recommandés

### Test 1 : Responsable du Module
1. ✅ Créer une tâche et l'assigner à un contributeur
2. ✅ Vérifier qu'on ne voit PAS les boutons d'action sur cette tâche
3. ✅ Vérifier qu'on voit toutes les tâches du module

### Test 2 : Contributeur via "Mes Modules"
1. ✅ Accéder aux tâches via "Mes Modules"
2. ✅ Vérifier qu'on ne voit QUE ses tâches assignées
3. ✅ Vérifier qu'on peut démarrer sa tâche
4. ✅ Vérifier qu'on peut mettre à jour la progression
5. ✅ Vérifier qu'on peut terminer sa tâche

### Test 3 : Tentative d'Action Non Autorisée
1. ✅ Essayer de démarrer la tâche d'un autre (via API)
2. ✅ Vérifier le message d'erreur approprié

## Action Requise

⚠️ **Redémarrer le serveur Django** pour que les changements prennent effet :

```bash
# Arrêter avec Ctrl+C puis relancer
python manage.py runserver
```

## Résultat Final

✅ Bouton Progression supprimé de la colonne Actions  
✅ Seul le responsable peut gérer sa tâche  
✅ Filtrage des tâches dans "Mes Modules"  
✅ Messages d'erreur clairs et explicites  
✅ Interface simplifiée et intuitive

---

**Note** : Cette restriction renforce la responsabilité individuelle et évite les conflits de gestion des tâches. Chaque membre est autonome sur ses propres tâches.
