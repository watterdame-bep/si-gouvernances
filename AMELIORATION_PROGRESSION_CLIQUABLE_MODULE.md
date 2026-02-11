# Amélioration : Progression Cliquable pour Tâches de Module

## Modification Appliquée

Le responsable d'une tâche de module peut maintenant définir la progression **à tout moment**, pas seulement quand la tâche est EN_COURS.

## Avant

- ❌ Progression cliquable uniquement si tâche EN_COURS
- ❌ Tâches A_FAIRE : progression bloquée (cadenas)
- ❌ Fallait d'abord "Démarrer" la tâche avant de définir la progression

## Après

- ✅ Progression cliquable pour toutes les tâches (sauf TERMINEE)
- ✅ Tâches A_FAIRE : progression cliquable
- ✅ Définir une progression > 0% démarre automatiquement la tâche
- ✅ Workflow plus fluide et naturel

## Logique Implémentée

### 1. Affichage de la Colonne Progression

**Qui peut cliquer** :
- ✅ Responsable du module (toutes les tâches)
- ✅ Créateur de la tâche
- ✅ Responsable de la tâche

**Affichage selon le statut** :
- **TERMINEE** : Badge vert "100%" (non cliquable)
- **Autres statuts** : Bouton bleu cliquable avec pourcentage

**Autres utilisateurs** :
- Voient le pourcentage en lecture seule (gris)

### 2. Comportement du Modal de Progression

**Slider** : 0% à 100% (pas de 5%)

**Actions automatiques** :
1. Si tâche A_FAIRE + progression > 0% → Passe EN_COURS automatiquement
2. Si progression = 100% → Passe TERMINEE automatiquement

### 3. Workflow Simplifié

#### Ancien Workflow (3 étapes)
```
1. Cliquer "Démarrer" → Tâche passe EN_COURS
2. Cliquer "Progression" → Ouvrir modal
3. Définir progression → Enregistrer
```

#### Nouveau Workflow (2 étapes)
```
1. Cliquer sur la progression → Ouvrir modal
2. Définir progression → Enregistrer (démarre automatiquement si > 0%)
```

## Modifications du Code

### 1. Template `gestion_taches_module.html`

**Colonne Progression** :
```django
{% if peut_modifier_taches or tache.createur.id == user.id %}
    {% if tache.statut == 'TERMINEE' %}
        <span>100%</span>
    {% else %}
        <button onclick="ouvrirModalProgression(...)">
            {{ tache.pourcentage_completion }}%
        </button>
    {% endif %}
{% elif tache.responsable and tache.responsable.id == user.id %}
    {% if tache.statut == 'TERMINEE' %}
        <span>100%</span>
    {% else %}
        <button onclick="ouvrirModalProgression(...)">
            {{ tache.pourcentage_completion }}%
        </button>
    {% endif %}
{% else %}
    <span>{{ tache.pourcentage_completion }}%</span>
{% endif %}
```

### 2. Vue `mettre_a_jour_progression_tache_module_view`

**Avant** :
```python
# CONTRAINTE: La tâche doit être EN_COURS
if tache.statut != 'EN_COURS':
    return JsonResponse({'success': False, 'error': '...'})
```

**Après** :
```python
# Vérifier que la tâche n'est pas déjà terminée
if tache.statut == 'TERMINEE':
    return JsonResponse({'success': False, 'error': 'Cette tâche est déjà terminée'})

# Si A_FAIRE et progression > 0, passer EN_COURS automatiquement
if tache.statut == 'A_FAIRE' and pourcentage > 0:
    tache.statut = 'EN_COURS'
    tache.date_debut_reelle = timezone.now()
```

## Cas d'Usage

### Scénario 1 : Démarrage Rapide
```
1. Tâche "Login page" est A_FAIRE (0%)
2. Alice clique sur "0%" dans la colonne progression
3. Modal s'ouvre avec slider à 0%
4. Alice met le slider à 25%
5. Enregistre
6. → Tâche passe automatiquement EN_COURS (25%)
7. → Date de début enregistrée
8. → Notification envoyée au responsable du module
```

### Scénario 2 : Mise à Jour Continue
```
1. Tâche "Dashboard" est EN_COURS (50%)
2. Bob clique sur "50%"
3. Modal s'ouvre avec slider à 50%
4. Bob met le slider à 75%
5. Enregistre
6. → Tâche reste EN_COURS (75%)
7. → Notification envoyée au responsable du module
```

### Scénario 3 : Terminaison Directe
```
1. Tâche "Settings" est EN_COURS (90%)
2. Claire clique sur "90%"
3. Modal s'ouvre avec slider à 90%
4. Claire met le slider à 100%
5. Enregistre
6. → Tâche passe automatiquement TERMINEE
7. → Date de fin enregistrée
8. → Notification "Tâche terminée" envoyée
```

### Scénario 4 : Utilisateur Sans Permission
```
1. David (autre contributeur) voit la tâche de Alice
2. Colonne progression affiche "25%" en gris
3. Pas de bouton cliquable
4. David ne peut pas modifier la progression
```

## Avantages

1. **Simplicité** : Un seul clic pour définir la progression
2. **Rapidité** : Pas besoin de démarrer explicitement la tâche
3. **Fluidité** : Workflow naturel et intuitif
4. **Flexibilité** : Peut définir n'importe quel pourcentage directement
5. **Automatisation** : Transitions de statut automatiques

## Contraintes Maintenues

- ❌ Tâches TERMINEE : progression non modifiable
- ❌ Utilisateurs sans permission : progression en lecture seule
- ✅ Notifications aux paliers de 25%, 50%, 75%, 100%
- ✅ Audit de toutes les modifications

## Fichiers Modifiés

1. **templates/core/gestion_taches_module.html** - Colonne progression cliquable
2. **core/views_taches_module.py** - Logique de démarrage automatique

## Date
10 février 2026
