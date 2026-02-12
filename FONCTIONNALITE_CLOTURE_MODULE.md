# Fonctionnalité de Clôture de Module

**Date**: 11 février 2026  
**Statut**: ✅ Implémenté

## Objectif

Permettre aux responsables de projet et aux responsables de module de clôturer un module une fois terminé, avec les restrictions suivantes :
- Impossible d'ajouter de nouvelles tâches
- Impossible de supprimer le module
- Impossible d'affecter de nouveaux membres
- Consultation des tâches existantes toujours possible

## Modifications du Modèle

### Nouveaux Champs - ModuleProjet

```python
# Clôture du module
est_cloture = models.BooleanField(default=False)
date_cloture = models.DateTimeField(blank=True, null=True)
cloture_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)
```

### Migration

**Fichier** : `core/migrations/0032_add_module_cloture.py`

Ajoute les 3 champs nécessaires pour gérer la clôture des modules.

## Permissions de Clôture

Peuvent clôturer un module :
1. ✅ **Super Admin**
2. ✅ **Créateur du projet**
3. ✅ **Responsable principal du projet**
4. ✅ **Responsable du module**

❌ Les contributeurs simples ne peuvent PAS clôturer un module.

## Vue Backend

### Fonction `cloturer_module_view()`

**Fichier** : `core/views.py`

```python
@login_required
def cloturer_module_view(request, projet_id, module_id):
    """Vue de clôture d'un module"""
    # Vérifications :
    # 1. Méthode POST uniquement
    # 2. Module pas déjà clôturé
    # 3. Permissions (responsables projet ou module)
    
    # Clôture :
    module.est_cloture = True
    module.date_cloture = timezone.now()
    module.cloture_par = user
    module.save()
    
    # Audit
    ActionAudit.objects.create(
        type_action='CLOTURE_MODULE',
        description=f'Clôture du module "{module.nom}"'
    )
```

### Route URL

```python
path('projets/<uuid:projet_id>/modules/<int:module_id>/cloturer/', 
     views.cloturer_module_view, 
     name='cloturer_module'),
```

## Interface Utilisateur

### 1. Badge "Clôturé" dans le Tableau

**Emplacement** : Colonne "Module"

```html
<div class="flex items-center space-x-2">
    <p>{{ module.nom }}</p>
    {% if module.est_cloture %}
        <span class="bg-green-100 text-green-800 rounded text-xs">
            <i class="fas fa-check-circle"></i>Clôturé
        </span>
    {% endif %}
</div>
```

### 2. Bouton de Clôture

**Emplacement** : Colonne "Actions"  
**Couleur** : Bleu (bg-blue-600)  
**Icône** : `fa-check-circle`  
**Taille** : 6x6 (24px)

**Affichage conditionnel** :
- Visible uniquement si le module n'est PAS clôturé
- Visible uniquement pour les responsables (projet ou module)

### 3. Modale de Confirmation

**Design** : Modale bleue avec informations détaillées

```html
<div id="modalConfirmerCloture">
    <!-- Header bleu -->
    <div class="bg-blue-600">
        <i class="fas fa-check-circle"></i>
        <h3>Confirmer la clôture</h3>
        <p>Action définitive</p>
    </div>
    
    <!-- Corps -->
    <div>
        <h4>Êtes-vous sûr de vouloir clôturer ce module ?</h4>
        <p>Module : <strong id="nomModuleCloture"></strong></p>
        
        <!-- Avertissement -->
        <div class="bg-yellow-50">
            <strong>Important :</strong> Une fois clôturé, vous ne pourrez plus :
            <ul>
                <li>Ajouter de nouvelles tâches</li>
                <li>Supprimer le module</li>
                <li>Affecter de nouveaux membres</li>
            </ul>
        </div>
        
        <!-- Info positive -->
        <div class="bg-green-50">
            <i class="fas fa-check"></i>
            Vous pourrez toujours consulter les tâches existantes.
        </div>
    </div>
    
    <!-- Footer -->
    <button onclick="fermerModalConfirmerCloture()">Annuler</button>
    <button onclick="executerClotureModule()">Clôturer</button>
</div>
```

### 4. Fonctions JavaScript

```javascript
// Variables globales
let moduleIdCloture = null;
let nomModuleCloture = null;

function confirmerClotureModule(moduleId, nomModule) {
    moduleIdCloture = moduleId;
    nomModuleCloture = nomModule;
    document.getElementById('nomModuleCloture').textContent = nomModule;
    document.getElementById('modalConfirmerCloture').classList.remove('hidden');
}

function fermerModalConfirmerCloture() {
    document.getElementById('modalConfirmerCloture').classList.add('hidden');
    moduleIdCloture = null;
    nomModuleCloture = null;
}

function executerClotureModule() {
    // Appel AJAX vers /projets/{id}/modules/{id}/cloturer/
    // Message de succès + rechargement
}
```

## Restrictions Appliquées

### 1. Suppression Bloquée

**Vue** : `supprimer_module_view()`

```python
if module.est_cloture:
    return JsonResponse({
        'success': False,
        'error': 'Impossible de supprimer un module clôturé.'
    })
```

**Template** : Bouton de suppression masqué si `module.est_cloture`

### 2. Création de Tâches Bloquée

**Vue** : `creer_tache_module_nouvelle_view()`

```python
if module.est_cloture:
    return JsonResponse({
        'success': False,
        'error': 'Impossible de créer une tâche dans un module clôturé.'
    })
```

**Template** : Bouton "Nouvelle Tâche" remplacé par badge "Module clôturé"

```html
{% if peut_creer_taches and not module.est_cloture %}
    <button>Nouvelle Tâche</button>
{% elif module.est_cloture %}
    <span class="bg-green-100 text-green-800">
        <i class="fas fa-check-circle"></i>Module clôturé
    </span>
{% endif %}
```

### 3. Affectation Bloquée

**Template** : Bouton "Affecter" masqué si `module.est_cloture`

```html
{% if not module.est_cloture %}
    <button onclick="ouvrirModalAffecterModuleNouveau()">
        <i class="fas fa-user-plus"></i>
    </button>
{% endif %}
```

### 4. Consultation Autorisée

✅ Le bouton "Tâches" reste visible  
✅ Les tâches existantes peuvent être consultées  
✅ Le bouton "Détails" reste visible

## Boutons d'Action - État Final

### Module Non Clôturé

| Bouton | Icône | Couleur | Permissions |
|--------|-------|---------|-------------|
| Détails | info-circle | Gris | Tous |
| Tâches | tasks | Vert | Responsables |
| Affecter | user-plus | Indigo | Tous |
| Clôturer | check-circle | Bleu | Responsables |
| Supprimer | trash | Rouge | Responsables projet |

### Module Clôturé

| Bouton | Icône | Couleur | Permissions |
|--------|-------|---------|-------------|
| Détails | info-circle | Gris | Tous |
| Tâches | tasks | Vert | Responsables (lecture seule) |
| ~~Affecter~~ | - | - | Masqué |
| ~~Clôturer~~ | - | - | Masqué |
| ~~Supprimer~~ | - | - | Masqué |

## Audit

Chaque clôture de module crée une entrée d'audit :

```python
ActionAudit.objects.create(
    utilisateur=user,
    projet=projet,
    type_action='CLOTURE_MODULE',
    description=f'Clôture du module "{module.nom}"'
)
```

## Fichiers Modifiés

1. `core/models.py` - Ajout des champs de clôture
2. `core/migrations/0032_add_module_cloture.py` - Migration
3. `core/views.py` - Vue `cloturer_module_view()` + modification `supprimer_module_view()`
4. `core/views_taches_module.py` - Vérification clôture dans `creer_tache_module_nouvelle_view()`
5. `core/urls.py` - Route de clôture
6. `templates/core/gestion_modules.html` - Badge, bouton, modale, fonctions JS
7. `templates/core/gestion_taches_module.html` - Badge "Module clôturé"

## Tests Recommandés

### Test 1 : Clôture par responsable projet
1. Se connecter en tant que responsable projet
2. Cliquer sur le bouton bleu "Clôturer"
3. Confirmer dans la modale
4. Vérifier le badge "Clôturé" ✅
5. Vérifier que les boutons Affecter, Clôturer et Supprimer ont disparu ✅

### Test 2 : Clôture par responsable module
1. Se connecter en tant que responsable du module
2. Vérifier que le bouton "Clôturer" est visible
3. Clôturer le module
4. Vérifier la clôture ✅

### Test 3 : Restrictions après clôture
1. Clôturer un module
2. Essayer d'accéder aux tâches → Bouton "Nouvelle Tâche" masqué ✅
3. Badge "Module clôturé" affiché ✅
4. Tâches existantes consultables ✅

### Test 4 : Tentative de suppression
1. Clôturer un module
2. Vérifier que le bouton "Supprimer" a disparu ✅

### Test 5 : Permissions
1. Se connecter en tant que contributeur simple
2. Vérifier que le bouton "Clôturer" n'est PAS visible ✅
