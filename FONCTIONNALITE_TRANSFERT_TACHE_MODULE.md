# Fonctionnalité de Transfert de Tâche de Module

**Date**: 11 février 2026  
**Statut**: ✅ IMPLÉMENTÉ

## Objectif

Permettre au responsable du module de transférer une tâche d'un membre à un autre membre de l'équipe du module.

## Règles Métier

### Qui peut transférer une tâche ?

- ✅ Responsable du module
- ✅ Super admin
- ✅ Créateur du projet
- ❌ Responsable de la tâche (ne peut pas transférer sa propre tâche)
- ❌ Contributeurs du module

### Conditions de Transfert

1. La tâche ne doit PAS être terminée
2. Le nouveau responsable doit faire partie de l'équipe du module
3. Le nouveau responsable doit être différent du responsable actuel
4. Le nouveau responsable doit avoir une affectation active au module

## Implémentation

### 1. Backend - Vue de Transfert

**Fichier**: `core/views_taches_module.py`  
**Fonction**: `transferer_tache_module_view()`

```python
@login_required
@require_http_methods(["POST"])
def transferer_tache_module_view(request, projet_id, tache_id):
    """Transférer une tâche de module à un autre membre de l'équipe"""
    # Vérifications:
    # 1. Accès au projet
    # 2. Permission de transfert (responsable module)
    # 3. Nouveau responsable valide
    # 4. Nouveau responsable fait partie de l'équipe
    # 5. Pas de transfert à la même personne
    
    # Actions:
    # 1. Mettre à jour le responsable de la tâche
    # 2. Notifier le nouveau responsable
    # 3. Notifier l'ancien responsable
    # 4. Enregistrer l'audit
```

### 2. URL

**Fichier**: `core/urls.py`

```python
path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/transferer/', 
     views_taches_module.transferer_tache_module_view, 
     name='transferer_tache_module'),
```

### 3. Frontend - Bouton de Transfert

**Fichier**: `templates/core/gestion_taches_module.html`

**Emplacement**: Colonne Actions du tableau

**Condition d'affichage**:
```django
{% if peut_creer_taches and tache.responsable and tache.statut != 'TERMINEE' %}
<button onclick="ouvrirModalTransfererTache('{{ tache.id }}', '{{ tache.nom|escapejs }}', '{{ tache.responsable.get_full_name|escapejs }}')"
        class="text-purple-600 hover:text-purple-800" title="Transférer">
    <i class="fas fa-exchange-alt text-lg"></i>
</button>
{% endif %}
```

**Icône**: `fa-exchange-alt` (flèches d'échange)  
**Couleur**: Violet (`purple-600`)

### 4. Modale de Transfert

**Éléments de la modale**:

1. **En-tête** (violet)
   - Titre: "Transférer la Tâche"
   - Nom de la tâche

2. **Corps**
   - Encadré bleu: Affiche le responsable actuel
   - Select: Liste des membres de l'équipe du module
   - Encadré jaune: Avertissement sur les notifications

3. **Pied**
   - Bouton Annuler
   - Bouton Transférer (violet)

### 5. Fonctions JavaScript

```javascript
// Ouvrir la modale
function ouvrirModalTransfererTache(tacheId, nomTache, responsableActuel)

// Fermer la modale
function fermerModalTransfererTache()

// Confirmer le transfert
function confirmerTransfererTache()
```

## Notifications

### Notification au Nouveau Responsable

**Type**: `NOUVELLE_TACHE`  
**Titre**: "📋 Tâche transférée: {nom_tache}"  
**Message**: "{utilisateur} vous a transféré la tâche '{nom_tache}' dans le module '{nom_module}'"

**Données contexte**:
- `tache_id`
- `type_tache`: "module"
- `projet_id`
- `module_id`
- `ancien_responsable`

### Notification à l'Ancien Responsable

**Type**: `TACHE_TERMINEE`  
**Titre**: "🔄 Tâche retirée: {nom_tache}"  
**Message**: "{utilisateur} a transféré votre tâche '{nom_tache}' à {nouveau_responsable}"

**Données contexte**:
- `tache_id`
- `type_tache`: "module"
- `projet_id`
- `module_id`
- `nouveau_responsable`

**Conditions de notification**:
- Ancien responsable existe
- Ancien responsable ≠ utilisateur qui transfère
- Ancien responsable ≠ nouveau responsable

## Audit

**Type d'action**: `TRANSFERT_TACHE_MODULE`

**Description**: "Transfert de la tâche "{nom}" de {ancien} vers {nouveau}"

**Données après**:
- `tache_id`
- `tache_nom`
- `ancien_responsable`
- `nouveau_responsable`
- `module_id`
- `module_nom`

## Workflow de Transfert

```
1. Responsable du module clique sur le bouton Transférer (icône échange)
   ↓
2. Modale s'ouvre avec:
   - Nom de la tâche
   - Responsable actuel
   - Liste des membres disponibles
   ↓
3. Sélection du nouveau responsable
   ↓
4. Clic sur "Transférer"
   ↓
5. Validation backend:
   - Permission vérifiée
   - Nouveau responsable valide
   - Membre de l'équipe
   ↓
6. Mise à jour de la tâche
   ↓
7. Notifications envoyées:
   - Nouveau responsable (tâche transférée)
   - Ancien responsable (tâche retirée)
   ↓
8. Audit enregistré
   ↓
9. Message de succès + Rechargement de la page
```

## Cas d'Usage

### Cas 1: Redistribution de Charge

**Contexte**: Un membre est surchargé

**Action**: Le responsable du module transfère une de ses tâches à un autre membre moins occupé

**Résultat**: 
- Tâche réassignée
- Nouveau responsable notifié
- Ancien responsable informé

### Cas 2: Changement de Compétences

**Contexte**: Une tâche nécessite des compétences spécifiques

**Action**: Le responsable du module transfère la tâche à un membre avec les bonnes compétences

**Résultat**:
- Tâche confiée au bon expert
- Notifications envoyées

### Cas 3: Absence d'un Membre

**Contexte**: Un membre part en congé

**Action**: Le responsable du module transfère toutes ses tâches en cours à d'autres membres

**Résultat**:
- Continuité du travail assurée
- Tous les membres concernés notifiés

## Restrictions

### Tâches Non Transférables

- ❌ Tâches terminées (statut `TERMINEE`)
- ❌ Tâches sans responsable (utiliser "Assigner" à la place)

### Utilisateurs Non Autorisés

- ❌ Contributeurs du module
- ❌ Consultants du module
- ❌ Membres non affectés au module
- ❌ Responsable de la tâche lui-même

## Interface Utilisateur

### Visibilité du Bouton

Le bouton "Transférer" est visible dans la colonne Actions si:
1. L'utilisateur peut créer des tâches (`peut_creer_taches = True`)
2. La tâche a un responsable assigné
3. La tâche n'est PAS terminée

### Position du Bouton

**Ordre des boutons dans la colonne Actions**:
1. Assigner (si pas de responsable)
2. **Transférer** (si responsable et pas terminée) ← NOUVEAU
3. Démarrer / Pause / Reprendre / Terminer (pour le responsable)
4. Détails (pour tous)

### Design

- **Icône**: `fa-exchange-alt` (flèches bidirectionnelles)
- **Couleur**: Violet (`text-purple-600`)
- **Hover**: Violet foncé (`hover:text-purple-800`)
- **Tooltip**: "Transférer"

## Tests à Effectuer

### Test 1: Transfert Réussi
- [ ] Se connecter en tant que responsable du module
- [ ] Cliquer sur le bouton Transférer d'une tâche
- [ ] Sélectionner un nouveau responsable
- [ ] Confirmer le transfert
- [ ] Vérifier que la tâche est réassignée
- [ ] Vérifier les notifications

### Test 2: Permissions
- [ ] Se connecter en tant que contributeur
- [ ] Vérifier que le bouton Transférer n'est PAS visible

### Test 3: Tâche Terminée
- [ ] Vérifier qu'une tâche terminée n'a PAS de bouton Transférer

### Test 4: Notifications
- [ ] Transférer une tâche
- [ ] Vérifier que le nouveau responsable reçoit une notification
- [ ] Vérifier que l'ancien responsable reçoit une notification

### Test 5: Validation
- [ ] Essayer de transférer à la même personne → Erreur
- [ ] Essayer de transférer à quelqu'un hors de l'équipe → Erreur
- [ ] Essayer de transférer sans sélectionner de responsable → Erreur

## Fichiers Modifiés

1. **core/urls.py**
   - Ajout de la route `transferer_tache_module`

2. **core/views_taches_module.py**
   - Nouvelle fonction `transferer_tache_module_view()`

3. **templates/core/gestion_taches_module.html**
   - Ajout du bouton Transférer dans la colonne Actions
   - Ajout de la modale de transfert
   - Ajout des fonctions JavaScript

## Améliorations Futures

1. **Transfert en masse**: Transférer plusieurs tâches en une fois
2. **Historique de transfert**: Voir l'historique des transferts d'une tâche
3. **Raison du transfert**: Ajouter un champ commentaire pour expliquer le transfert
4. **Validation du nouveau responsable**: Vérifier sa disponibilité avant le transfert
5. **Transfert avec progression**: Permettre le transfert même si la tâche est en cours

## Conclusion

La fonctionnalité de transfert de tâche permet au responsable du module de gérer efficacement la répartition du travail au sein de son équipe. Les notifications automatiques assurent que tous les membres concernés sont informés des changements.
