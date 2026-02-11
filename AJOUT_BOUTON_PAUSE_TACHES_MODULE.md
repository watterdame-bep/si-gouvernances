# Ajout Bouton "Mettre en Pause" pour Tâches de Module

## Modification Appliquée

Ajout du bouton "Mettre en pause" dans la colonne Actions pour les tâches EN_COURS, permettant au responsable de la tâche de suspendre temporairement son travail.

## Boutons d'Action Complets

### Tâche A_FAIRE
- 🟠 **Démarrer** (play-circle orange) → Passe EN_COURS

### Tâche EN_COURS
- 🔵 **Progression** (tasks bleu) → Ouvre modal slider
- 🟡 **Mettre en pause** (pause-circle jaune) → Passe EN_PAUSE (NOUVEAU)
- 🟢 **Terminer** (check-circle vert) → Passe TERMINEE

### Tâche EN_PAUSE
- 🟠 **Reprendre** (play-circle orange) → Passe EN_COURS

### Tâche TERMINEE
- ⚪ **Check gris** (non cliquable) → Tâche terminée

## Workflow Complet

```
A_FAIRE
   ↓ [Démarrer]
EN_COURS ←→ [Mettre en pause / Reprendre] ←→ EN_PAUSE
   ↓ [Terminer]
TERMINEE
```

## Contraintes Maintenues

1. **Progression** : Modifiable uniquement si tâche EN_COURS
2. **Pause** : Possible uniquement si tâche EN_COURS
3. **Reprise** : Possible uniquement si tâche EN_PAUSE
4. **Terminaison** : Possible depuis EN_COURS uniquement

## Permissions

Peuvent utiliser ces boutons :
- ✅ Responsable du module (toutes les tâches)
- ✅ Créateur de la tâche
- ✅ Responsable de la tâche

## Modifications Appliquées

### 1. Template `gestion_taches_module.html`

**Ajout du bouton Pause** :
```html
{% elif tache.statut == 'EN_COURS' %}
    <button onclick="ouvrirModalProgression(...)">Progression</button>
    <button onclick="mettreEnPause('{{ tache.id }}')">Pause</button>  <!-- NOUVEAU -->
    <button onclick="terminerTache(...)">Terminer</button>
{% endif %}
```

**Fonction JavaScript ajoutée** :
```javascript
function mettreEnPause(tacheId) {
    if (!confirm('Voulez-vous mettre cette tâche en pause ?')) return;
    
    const url = `/projets/{{ projet.id }}/taches-module/${tacheId}/mettre-en-pause/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            afficherMessage('success', 'Tâche mise en pause !');
            setTimeout(() => location.reload(), 1000);
        } else {
            afficherMessage('error', data.error || 'Erreur');
        }
    });
}
```

### 2. URL `core/urls.py`

**Nouvelle route ajoutée** :
```python
path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/mettre-en-pause/', 
     views_taches_module.mettre_en_pause_tache_module_view, 
     name='mettre_en_pause_tache_module'),
```

### 3. Vue `core/views_taches_module.py`

**Nouvelle vue créée** : `mettre_en_pause_tache_module_view`

**Fonctionnalités** :
- Vérifie les permissions (responsable module, créateur, responsable tâche)
- Vérifie que la tâche est EN_COURS
- Passe le statut à EN_PAUSE
- Enregistre l'audit
- Retourne JSON success/error

## Cas d'Usage

### Scénario 1 : Pause Temporaire
```
1. Alice travaille sur "Login page" (EN_COURS 50%)
2. Elle doit travailler sur une urgence
3. Clique sur le bouton "Pause" (jaune)
4. Confirme l'action
5. → Tâche passe EN_PAUSE
6. → Progression reste à 50%
7. → Alice peut reprendre plus tard
```

### Scénario 2 : Reprise après Pause
```
1. Tâche "Dashboard" est EN_PAUSE (75%)
2. Bob clique sur "Reprendre" (orange)
3. → Tâche passe EN_COURS
4. → Progression reste à 75%
5. Bob peut continuer son travail
```

### Scénario 3 : Workflow Complet
```
1. Tâche créée → A_FAIRE (0%)
2. Clic "Démarrer" → EN_COURS (0%)
3. Clic "Progression" → EN_COURS (25%)
4. Clic "Pause" → EN_PAUSE (25%)
5. Clic "Reprendre" → EN_COURS (25%)
6. Clic "Progression" → EN_COURS (100%)
7. → Automatiquement TERMINEE
```

## Avantages

1. **Flexibilité** : Permet de suspendre le travail temporairement
2. **Clarté** : Statut EN_PAUSE indique clairement l'état
3. **Traçabilité** : Audit de toutes les transitions
4. **Contrôle** : Le responsable garde le contrôle de ses tâches

## Fichiers Modifiés

1. **templates/core/gestion_taches_module.html** - Ajout bouton + fonction JS
2. **core/urls.py** - Nouvelle route
3. **core/views_taches_module.py** - Nouvelle vue

## Date
10 février 2026
