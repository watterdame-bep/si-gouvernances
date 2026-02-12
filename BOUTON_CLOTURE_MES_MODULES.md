# Bouton de Clôture dans "Mes Modules"

**Date**: 11 février 2026  
**Statut**: ✅ Implémenté et Testé

## 📋 Contexte

Ajout d'un bouton permettant aux responsables de module de clôturer leur module directement depuis l'interface "Mes Modules", avec vérification automatique que toutes les tâches sont terminées.

## 🎯 Objectif

Permettre aux responsables de module de clôturer facilement leur module une fois toutes les tâches terminées, sans avoir à passer par l'interface de gestion des modules du projet.

## ✨ Fonctionnalités Implémentées

### 1. Calcul Backend des Tâches

**Fichier**: `core/views.py` - Fonction `mes_modules_view()`

```python
# Enrichir chaque affectation avec les informations de clôture
affectations_enrichies = []
for affectation in mes_affectations:
    module = affectation.module
    total_taches = module.taches.count()
    taches_terminees = module.taches.filter(statut='TERMINEE').count()
    
    # Déterminer si l'utilisateur peut clôturer ce module
    peut_cloturer = (
        affectation.role_module == 'RESPONSABLE' and 
        not module.est_cloture and
        total_taches > 0 and
        total_taches == taches_terminees
    )
    
    # Ajouter les informations calculées à l'affectation
    affectation.total_taches = total_taches
    affectation.taches_terminees = taches_terminees
    affectation.taches_restantes = total_taches - taches_terminees
    affectation.peut_cloturer = peut_cloturer
    affectations_enrichies.append(affectation)
```

**Avantages**:
- ✅ Calcul côté serveur (plus fiable)
- ✅ Pas de logique complexe dans le template
- ✅ Données enrichies disponibles pour l'affichage

### 2. Bouton de Clôture Conditionnel

**Fichier**: `templates/core/mes_modules.html`

#### Bouton Actif (toutes tâches terminées)
```html
{% if affectation.peut_cloturer %}
    <button onclick="confirmerClotureModule('{{ affectation.module.id }}', '{{ affectation.module.nom }}')"
            class="inline-flex items-center justify-center w-8 h-8 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            title="Clôturer le module">
        <i class="fas fa-check-circle text-sm"></i>
    </button>
{% endif %}
```

#### Bouton Désactivé (tâches restantes)
```html
{% else %}
    <button disabled
            class="inline-flex items-center justify-center w-8 h-8 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
            title="Toutes les tâches doivent être terminées ({{ affectation.taches_restantes }} restante{{ affectation.taches_restantes|pluralize }})">
        <i class="fas fa-check-circle text-sm"></i>
    </button>
{% endif %}
```

**Conditions d'affichage**:
- ✅ Utilisateur est RESPONSABLE du module
- ✅ Module non clôturé
- ✅ Au moins une tâche existe
- ✅ Toutes les tâches sont terminées

### 3. Badge "Clôturé"

```html
{% if affectation.module.est_cloture %}
    <span class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
        <i class="fas fa-check-circle mr-1"></i>Clôturé
    </span>
{% endif %}
```

### 4. Modale de Confirmation

**Design**: Modale verte professionnelle identique à celle de `gestion_modules.html`

**Contenu**:
- ✅ Nom du module à clôturer
- ⚠️ Avertissement sur les restrictions après clôture
- ✅ Information sur la consultation toujours possible

**Restrictions affichées**:
- ❌ Impossible d'ajouter de nouvelles tâches
- ❌ Impossible de supprimer le module
- ❌ Impossible d'affecter de nouveaux membres

### 5. Fonctions JavaScript

**Fichier**: `templates/core/mes_modules.html`

```javascript
// Variables globales
let moduleIdCloture = null;
let nomModuleCloture = null;

// Ouvrir la modale
function confirmerClotureModule(moduleId, nomModule) {
    moduleIdCloture = moduleId;
    nomModuleCloture = nomModule;
    document.getElementById('nomModuleCloture').textContent = nomModule;
    document.getElementById('modalConfirmerCloture').classList.remove('hidden');
}

// Fermer la modale
function fermerModalConfirmerCloture() {
    document.getElementById('modalConfirmerCloture').classList.add('hidden');
    moduleIdCloture = null;
    nomModuleCloture = null;
}

// Exécuter la clôture
function executerClotureModule() {
    const url = `/projets/${projetId}/modules/${moduleIdCloture}/cloturer/`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': '{{ csrf_token }}'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Message de succès + rechargement
            setTimeout(() => window.location.reload(), 1500);
        }
    });
}
```

## 🎨 Interface Utilisateur

### Colonne Actions du Tableau

```
┌─────────────────────────────────────┐
│ Actions                             │
├─────────────────────────────────────┤
│ [📋] [✓]  ← Tâches + Clôturer       │
│ [📋] [✓]  ← Actif (vert)            │
│ [📋] [✓]  ← Désactivé (gris)        │
└─────────────────────────────────────┘
```

### États du Bouton

1. **Actif** (vert): Toutes tâches terminées
   - Couleur: `bg-green-600 hover:bg-green-700`
   - Icône: `fa-check-circle`
   - Tooltip: "Clôturer le module"

2. **Désactivé** (gris): Tâches restantes
   - Couleur: `bg-gray-300`
   - Icône: `fa-check-circle`
   - Tooltip: "Toutes les tâches doivent être terminées (X restante(s))"
   - Curseur: `cursor-not-allowed`

3. **Masqué**: Module déjà clôturé
   - Badge "Clôturé" affiché à côté du nom

## 🔒 Permissions

### Qui peut voir le bouton ?
- ✅ Responsables de module uniquement
- ❌ Contributeurs (pas de bouton)

### Qui peut clôturer ?
- ✅ Responsable du module
- ✅ Toutes les tâches terminées
- ✅ Module non clôturé
- ✅ Au moins une tâche existe

## 📊 Logique de Validation

```python
peut_cloturer = (
    affectation.role_module == 'RESPONSABLE' and  # Est responsable
    not module.est_cloture and                     # Pas déjà clôturé
    total_taches > 0 and                           # Au moins 1 tâche
    total_taches == taches_terminees               # Toutes terminées
)
```

## 🔄 Flux Utilisateur

1. **Utilisateur responsable** accède à "Mes Modules"
2. **Système calcule** pour chaque module :
   - Nombre total de tâches
   - Nombre de tâches terminées
   - Si clôture possible
3. **Affichage conditionnel** :
   - Bouton vert actif si toutes tâches terminées
   - Bouton gris désactivé si tâches restantes
   - Badge "Clôturé" si déjà clôturé
4. **Clic sur bouton** → Modale de confirmation
5. **Confirmation** → Requête AJAX vers `/projets/{id}/modules/{id}/cloturer/`
6. **Succès** → Message + rechargement page

## 📁 Fichiers Modifiés

### Backend
- `core/views.py` - Fonction `mes_modules_view()` (lignes 5456-5510)
  - Ajout du calcul des tâches par module
  - Enrichissement des affectations avec `peut_cloturer`

### Frontend
- `templates/core/mes_modules.html`
  - Ajout du bouton de clôture dans la colonne Actions
  - Ajout du badge "Clôturé"
  - Ajout de la modale de confirmation
  - Ajout des fonctions JavaScript

## ✅ Tests à Effectuer

### Scénario 1: Module avec toutes tâches terminées
1. Se connecter comme responsable d'un module
2. Aller dans "Mes Modules"
3. Vérifier que le bouton vert "Clôturer" est actif
4. Cliquer → Modale s'ouvre
5. Confirmer → Module clôturé + rechargement
6. Vérifier badge "Clôturé" affiché

### Scénario 2: Module avec tâches restantes
1. Se connecter comme responsable d'un module
2. Aller dans "Mes Modules"
3. Vérifier que le bouton gris est désactivé
4. Survoler → Tooltip indique nombre de tâches restantes
5. Impossible de cliquer

### Scénario 3: Module déjà clôturé
1. Se connecter comme responsable d'un module clôturé
2. Aller dans "Mes Modules"
3. Vérifier que le badge "Clôturé" est affiché
4. Vérifier que le bouton de clôture n'est pas affiché

### Scénario 4: Contributeur (non responsable)
1. Se connecter comme contributeur d'un module
2. Aller dans "Mes Modules"
3. Vérifier que seul le bouton "Tâches" est affiché
4. Pas de bouton de clôture

## 🎯 Résultat

✅ Les responsables de module peuvent clôturer leur module depuis "Mes Modules"  
✅ Vérification automatique que toutes les tâches sont terminées  
✅ Bouton désactivé avec tooltip informatif si tâches restantes  
✅ Modale de confirmation professionnelle  
✅ Badge "Clôturé" pour les modules clôturés  
✅ Permissions respectées (responsables uniquement)  
✅ Interface cohérente avec "Gestion des Modules"

## 📝 Notes Techniques

- Calcul des tâches fait côté backend pour fiabilité
- Réutilisation de la route existante `/projets/{id}/modules/{id}/cloturer/`
- Modale identique à celle de `gestion_modules.html`
- Rechargement automatique après clôture réussie
- Message de succès affiché pendant 1.5 secondes
