# Redirection vers "Mes tâches" globales

## Fonctionnalité implémentée

Lorsqu'un utilisateur clique sur une notification de tâche, il est maintenant redirigé vers une page "Mes tâches" globale qui affiche toutes ses tâches (tous projets confondus) avec des boutons d'action "Terminer" et "Voir détails".

## Modifications apportées

### 1. Nouvelle vue mes_taches_globales_view (core/views.py)

Création d'une vue globale qui affiche toutes les tâches de l'utilisateur:

```python
@login_required
def mes_taches_globales_view(request):
    """Vue globale pour voir toutes les tâches assignées à l'utilisateur (tous projets)"""
    # Récupère toutes les tâches d'étape et de module
    # Combine et trie les tâches
    # Affiche avec filtres et statistiques
```

**Fonctionnalités**:
- Affiche toutes les tâches (étapes + modules)
- Filtres: Projet, Statut, Priorité
- Statistiques: Total, À faire, En cours, Terminées
- Boutons d'action pour chaque tâche

### 2. Nouvelle URL (core/urls.py)

```python
path('mes-taches/', views.mes_taches_globales_view, name='mes_taches_globales'),
```

### 3. Modification de la redirection (core/views.py)

Dans `notification_redirect_view()`:

```python
# Chercher dans NotificationTache
try:
    notif = NotificationTache.objects.get(id=notification_id, destinataire=user)
    if not notif.lue:
        notif.lue = True
        notif.date_lecture = timezone.now()
        notif.save()
    
    # Rediriger vers "Mes tâches" pour que l'utilisateur voie sa tâche assignée
    redirect_url = '/mes-taches/'
    
    return redirect(redirect_url)
```

### 4. Nouveau template (templates/core/mes_taches_globales.html)

Template moderne avec:
- **Statistiques** en haut (cartes avec icônes)
- **Filtres** (Projet, Statut, Priorité)
- **Liste des tâches** avec:
  - Nom et description
  - Badges de statut et priorité
  - Informations (projet, contexte, échéance, progression)
  - **Boutons d'action**:
    - ✅ **Terminer** (si pas déjà terminée)
    - 👁️ **Voir détails** (lien vers la page de gestion)

## Interface "Mes tâches"

### Statistiques (en haut)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Total     │   À faire   │  En cours   │  Terminées  │
│     15      │      5      │      7      │      3      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Filtres
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Projet    │   Statut    │  Priorité   │  [Filtrer]  │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Liste des tâches
```
┌────────────────────────────────────────────────────────┐
│ Nom de la tâche          [À faire] [Haute]             │
│ Description de la tâche...                             │
│ 📊 Projet X  │  📁 Module Y  │  📅 15/02/2026         │
│                                    [Terminer] [Détails] │
├────────────────────────────────────────────────────────┤
│ Autre tâche              [En cours] [Moyenne]          │
│ ...                                                     │
└────────────────────────────────────────────────────────┘
```

## Boutons d'action

### Bouton "Terminer"
- **Visible**: Seulement si la tâche n'est pas terminée
- **Action**: Marque la tâche comme terminée
- **Confirmation**: Demande confirmation avant de terminer
- **Couleur**: Vert (bg-green-600)
- **Icône**: ✓ (fas fa-check)

### Bouton "Voir détails"
- **Visible**: Toujours
- **Action**: Redirige vers la page de gestion de la tâche
- **Destination**:
  - Tâche d'étape → `/projets/{projet_id}/etapes/{etape_id}/taches/`
  - Tâche de module → `/projets/{projet_id}/modules/{module_id}/taches/`
- **Couleur**: Bleu (bg-blue-600)
- **Icône**: 👁️ (fas fa-eye)

## Flux utilisateur

### Scénario: Notification d'assignation de tâche

1. **Utilisateur reçoit une notification**
   - "La tâche 'Créer API' vous a été assignée"
   - Badge de notification affiche "1"

2. **Utilisateur clique sur la notification**
   - Notification marquée comme lue
   - Redirection vers `/mes-taches/`

3. **Page "Mes tâches" s'affiche**
   - Statistiques en haut
   - Liste de toutes ses tâches
   - La nouvelle tâche est visible

4. **Utilisateur voit sa tâche**
   - Nom: "Créer API"
   - Statut: "À faire"
   - Projet: "Système de gestion"
   - Contexte: "Module: Backend"

5. **Utilisateur a deux options**:
   - **Option A**: Cliquer sur "Terminer"
     - Confirmation demandée
     - Tâche marquée comme terminée
     - Page rechargée
   
   - **Option B**: Cliquer sur "Voir détails"
     - Redirection vers la page de gestion des tâches du module
     - Peut voir tous les détails, commentaires, historique, etc.

## Types de tâches supportées

### 1. Tâches d'étape (TacheEtape)
- Contexte affiché: "Étape: [Nom de l'étape]"
- Lien détails: `/projets/{projet_id}/etapes/{etape_id}/taches/`

### 2. Tâches de module (TacheModule)
- Contexte affiché: "Module: [Nom du module]"
- Lien détails: `/projets/{projet_id}/modules/{module_id}/taches/`

## Filtres disponibles

### Filtre par projet
- Liste déroulante avec tous les projets où l'utilisateur a des tâches
- Option "Tous les projets" par défaut

### Filtre par statut
- À faire
- En cours
- Terminée
- Bloquée
- Option "Tous les statuts" par défaut

### Filtre par priorité
- Critique
- Haute
- Moyenne
- Basse
- Option "Toutes les priorités" par défaut

## Fichiers créés/modifiés

### Créés:
- `templates/core/mes_taches_globales.html` - Template de la page

### Modifiés:
- `core/views.py`:
  - Nouvelle fonction `mes_taches_globales_view()` (ligne ~4145)
  - Modification de `notification_redirect_view()` (ligne ~3720)
- `core/urls.py`:
  - Ajout de la route `/mes-taches/`

## Statut

✅ **Implémenté**  
✅ **Prêt pour test**  
⏳ **Nécessite redémarrage du serveur**

## Action requise

Redémarrer le serveur Django:
```bash
python manage.py runserver
```

## Test de la fonctionnalité

### Étapes pour tester:

1. **Assigner une tâche à un utilisateur**
   - Se connecter en tant qu'admin/responsable
   - Assigner une tâche à un membre

2. **Se connecter avec le membre**
   - Vérifier la notification

3. **Cliquer sur la notification**
   - Devrait rediriger vers `/mes-taches/`
   - Voir toutes les tâches assignées

4. **Tester les boutons**:
   - Cliquer sur "Terminer" → Tâche marquée comme terminée
   - Cliquer sur "Voir détails" → Redirection vers la page de gestion

5. **Tester les filtres**:
   - Filtrer par projet
   - Filtrer par statut
   - Filtrer par priorité

---

**Date**: 2026-02-10  
**Fonctionnalité**: Page "Mes tâches" globale avec boutons d'action  
**Type**: Amélioration UX
