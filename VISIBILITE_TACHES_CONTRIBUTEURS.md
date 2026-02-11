# Visibilité des Tâches pour les Contributeurs

## Modification Appliquée

Les contributeurs d'un module peuvent maintenant voir **TOUTES les tâches du module**, pas seulement celles qu'ils ont créées ou qui leur sont assignées.

## Justification

Cette modification permet aux contributeurs de :
1. ✅ Avoir une vue d'ensemble du travail du module
2. ✅ Comprendre le contexte de leurs tâches
3. ✅ Voir la progression globale du module
4. ✅ Mieux coordonner leur travail avec les autres membres

## Règles de Visibilité

### Responsable du Module
- ✅ Voit **toutes les tâches** du module
- ✅ Peut créer de nouvelles tâches
- ✅ Peut modifier toutes les tâches
- ✅ Peut assigner des tâches

### Contributeur du Module
- ✅ Voit **toutes les tâches** du module (NOUVEAU)
- ❌ Ne peut pas créer de nouvelles tâches
- ✅ Peut modifier **ses propres tâches** (créées par lui ou assignées à lui)
- ❌ Ne peut pas modifier les tâches des autres
- ❌ Ne peut pas assigner de tâches

### Consultant du Module
- ✅ Voit **toutes les tâches** du module
- ❌ Ne peut pas créer de tâches
- ✅ Peut modifier ses propres tâches
- ❌ Ne peut pas modifier les tâches des autres

## Permissions par Action

| Action | Responsable | Contributeur | Consultant |
|--------|-------------|--------------|------------|
| Voir toutes les tâches | ✅ | ✅ | ✅ |
| Créer une tâche | ✅ | ❌ | ❌ |
| Modifier sa tâche | ✅ | ✅ | ✅ |
| Modifier tâche d'un autre | ✅ | ❌ | ❌ |
| Assigner une tâche | ✅ | ❌ | ❌ |
| Voir la progression | ✅ | ✅ | ✅ |

## Modification du Code

### Fichier : `core/views_taches_module.py`

**Avant** :
```python
# Si membre simple venant de "Mes Modules", ne montrer que ses tâches
if est_membre_simple and from_mes_modules:
    taches = module.taches.filter(createur=user).select_related('responsable').order_by('-date_creation')
else:
    taches = module.taches.all().select_related('responsable').order_by('-date_creation')
```

**Après** :
```python
# Tous les membres (responsable et contributeurs) voient toutes les tâches du module
taches = module.taches.all().select_related('responsable', 'createur').order_by('-date_creation')
```

### Fichier : `templates/core/gestion_taches_module.html`

**Message informatif mis à jour** :
```html
<p class="font-medium">Vue contributeur</p>
<p class="text-blue-700">Vous voyez toutes les tâches du module. Vous pouvez modifier vos propres tâches.</p>
```

## Comportement dans l'Interface

### Pour un Contributeur

1. **Accès via "Mes Modules"** :
   - Clique sur l'icône "Gérer mes tâches"
   - Arrive sur l'interface des tâches du module

2. **Vue des tâches** :
   - ✅ Voit TOUTES les tâches du module
   - ✅ Voit qui est responsable de chaque tâche
   - ✅ Voit la progression de chaque tâche
   - ✅ Voit le statut de chaque tâche

3. **Actions disponibles** :
   - Pour **ses propres tâches** (créées par lui ou assignées à lui) :
     - ✅ Bouton "Démarrer" (si A_FAIRE)
     - ✅ Bouton "Progression" (si EN_COURS)
     - ✅ Bouton "Terminer" (si EN_COURS)
   
   - Pour **les tâches des autres** :
     - ✅ Bouton "Voir" (détails)
     - ❌ Pas de boutons d'action

4. **Boutons cachés** :
   - ❌ "Nouvelle Tâche" (seul le responsable le voit)
   - ❌ "Assigner" (seul le responsable le voit)

## Avantages de cette Approche

1. **Transparence** : Tout le monde voit l'état du module
2. **Coordination** : Les contributeurs peuvent mieux s'organiser
3. **Motivation** : Voir la progression globale motive l'équipe
4. **Contrôle** : Le responsable garde le contrôle sur la création et l'assignation

## Cas d'Usage

### Scénario 1 : Contributeur vérifie l'avancement
```
1. Alice (contributeur) accède à "Mes Modules"
2. Clique sur "Gérer mes tâches" pour le module "Frontend"
3. Voit toutes les tâches :
   - "Login page" (assignée à elle) - EN_COURS 50%
   - "Dashboard" (assignée à Bob) - A_FAIRE
   - "Settings" (assignée à Claire) - TERMINEE
4. Alice comprend que Bob n'a pas encore commencé
5. Alice peut se concentrer sur sa tâche
```

### Scénario 2 : Contributeur modifie sa tâche
```
1. Alice voit sa tâche "Login page" EN_COURS
2. Clique sur "Progression" (50%)
3. Met à jour à 75%
4. La notification est envoyée au responsable du module
```

### Scénario 3 : Contributeur ne peut pas modifier les autres
```
1. Alice voit la tâche "Dashboard" de Bob
2. Seul le bouton "Voir" est disponible
3. Pas de boutons "Démarrer" ou "Progression"
4. Alice ne peut pas modifier la tâche de Bob
```

## Date
10 février 2026
