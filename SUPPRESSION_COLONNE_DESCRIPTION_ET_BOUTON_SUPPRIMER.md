# Suppression Colonne Description et Ajout Bouton Supprimer Module

**Date**: 11 février 2026  
**Statut**: ✅ Implémenté

## Objectif

1. Supprimer la colonne "Description" du tableau des modules (trop longue et peu utile)
2. Ajouter un bouton de suppression pour permettre aux responsables du projet de supprimer un module

## Modifications Apportées

### 1. Suppression de la Colonne Description

**Avant** : 6 colonnes
- Module
- Description ❌ (supprimée)
- Responsable
- Équipe
- Tâches
- Actions

**Après** : 5 colonnes
- Module
- Responsable
- Équipe
- Tâches
- Actions

**Raison** : La description peut être très longue et prend beaucoup d'espace. Elle reste accessible via le bouton "Détails".

### 2. Ajout du Bouton Supprimer

#### Emplacement
Colonne "Actions", après les boutons Détails, Tâches et Affecter

#### Design
```html
<button onclick="confirmerSuppressionModule('{{ module.id }}', '{{ module.nom }}')"
        class="w-6 h-6 bg-red-600 hover:bg-red-700 text-white rounded"
        title="Supprimer le module">
    <i class="fas fa-trash text-xs"></i>
</button>
```

- Couleur : Rouge (bg-red-600)
- Icône : `fa-trash`
- Taille : 6x6 (24px)
- Tooltip : "Supprimer le module"

#### Permissions

Le bouton de suppression s'affiche uniquement pour :
1. ✅ **Super Admin**
2. ✅ **Créateur du projet**
3. ✅ **Responsable principal du projet**

❌ Les responsables de module NE PEUVENT PAS supprimer leur module (seuls les responsables du projet)

### 3. Fonction JavaScript

```javascript
function confirmerSuppressionModule(moduleId, nomModule) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer le module "${nomModule}" ?
    
Cette action est irréversible et supprimera également toutes les tâches associées.`)) {
        // Appel AJAX vers le backend
        fetch(`/projets/${projetId}/modules/${moduleId}/supprimer/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                afficherMessage('success', data.message);
                setTimeout(() => window.location.reload(), 1500);
            } else {
                afficherMessage('error', data.error);
            }
        });
    }
}
```

**Sécurité** :
- Confirmation obligatoire avec `confirm()`
- Message d'avertissement sur l'irréversibilité
- Vérification des permissions côté backend

### 4. Vue Backend

**Fichier** : `core/views.py`

```python
@login_required
def supprimer_module_view(request, projet_id, module_id):
    """Vue de suppression d'un module"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, etape__projet=projet)
    
    # Vérifier les permissions
    can_delete = user.est_super_admin() or projet.createur == user
    
    if not can_delete:
        affectation_user = projet.affectations.filter(
            utilisateur=user,
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_delete = affectation_user is not None
    
    if not can_delete:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas les permissions pour supprimer ce module.'
        }, status=403)
    
    try:
        nom_module = module.nom
        module.delete()  # Suppression en cascade des tâches
        
        # Audit
        ActionAudit.objects.create(
            utilisateur=user,
            projet=projet,
            type_action='SUPPRESSION_MODULE',
            description=f'Suppression du module "{nom_module}"'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Le module "{nom_module}" a été supprimé avec succès.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la suppression : {str(e)}'
        }, status=500)
```

**Sécurités** :
- Vérification de la méthode POST
- Vérification des permissions
- Gestion des erreurs avec try/except
- Création d'une entrée d'audit
- Suppression en cascade des tâches associées

### 5. Route URL

**Fichier** : `core/urls.py`

```python
path('projets/<uuid:projet_id>/modules/<int:module_id>/supprimer/', 
     views.supprimer_module_view, 
     name='supprimer_module'),
```

## Comportement de la Suppression

### Cascade
Lors de la suppression d'un module, sont également supprimés :
- ✅ Toutes les tâches du module (`TacheModule`)
- ✅ Toutes les affectations au module (`AffectationModule`)
- ✅ Toutes les notifications liées au module

### Audit
Une entrée d'audit est créée avec :
- Type : `SUPPRESSION_MODULE`
- Description : `Suppression du module "{nom}"`
- Utilisateur : Celui qui a effectué la suppression
- Projet : Le projet concerné

## Interface Utilisateur

### Tableau Simplifié

| Module | Responsable | Équipe | Tâches | Actions |
|--------|-------------|--------|--------|---------|
| 🟦 Dashboard<br>11/02/2026 | Jean Dupont | 👥 3 | 5 | ℹ️ ✓ ➕ 🗑️ |

### Boutons d'Action (4 boutons)

1. **Détails** (gris) : `fa-info-circle` - Tout le monde
2. **Tâches** (vert) : `fa-tasks` - Responsables projet + responsables module
3. **Affecter** (indigo) : `fa-user-plus` - Tout le monde
4. **Supprimer** (rouge) : `fa-trash` - Responsables projet uniquement

## Avantages

✅ **Tableau plus compact** : Suppression de la colonne description  
✅ **Gestion complète** : Possibilité de supprimer un module  
✅ **Sécurisé** : Permissions strictes + confirmation  
✅ **Traçable** : Entrée d'audit créée  
✅ **Propre** : Suppression en cascade  

## Fichiers Modifiés

1. `templates/core/gestion_modules.html` - Suppression colonne + bouton supprimer + fonction JS
2. `core/views.py` - Vue `supprimer_module_view()`
3. `core/urls.py` - Route de suppression

## Test Recommandé

### Test 1 : Affichage du bouton
1. Se connecter en tant que créateur du projet
2. Accéder à "Gestion des Modules"
3. Vérifier que le bouton rouge "Supprimer" est visible ✅

### Test 2 : Permissions
1. Se connecter en tant que contributeur simple
2. Accéder à "Gestion des Modules"
3. Vérifier que le bouton "Supprimer" n'est PAS visible ✅

### Test 3 : Suppression
1. Cliquer sur le bouton "Supprimer" d'un module
2. Confirmer la suppression
3. Vérifier que le module est supprimé
4. Vérifier que les tâches associées sont supprimées
5. Vérifier l'entrée d'audit ✅

### Test 4 : Annulation
1. Cliquer sur "Supprimer"
2. Cliquer sur "Annuler" dans la confirmation
3. Vérifier que le module n'est PAS supprimé ✅
