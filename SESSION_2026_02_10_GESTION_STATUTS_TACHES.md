# Session 10 Février 2026 - Gestion des Statuts de Tâches

**Date**: 10 février 2026  
**Statut**: ✅ En cours d'implémentation

---

## 🎯 Objectifs

Implémenter un système simple et professionnel de gestion des statuts de tâches avec :
- Statut "En pause" pour suspendre temporairement une tâche
- Contrainte : Progression modifiable uniquement si tâche "En cours"
- Boutons d'action dynamiques selon le statut
- Interface simple et compréhensible

---

## ✅ Modifications Backend Effectuées

### 1. **Nouveau Statut "EN_PAUSE"**
- Migration créée : `0031_add_statut_en_pause.py`
- Statuts disponibles : `A_FAIRE`, `EN_COURS`, `EN_PAUSE`, `TERMINEE`
- Statut "BLOQUEE" retiré (trop complexe)

### 2. **Nouvelles Fonctions de Gestion**

**`demarrer_tache_view()`** :
- Transition : `A_FAIRE` → `EN_COURS`
- Définit `date_debut_reelle`
- Audit automatique

**`mettre_en_pause_tache_view()`** :
- Transition : `EN_COURS` → `EN_PAUSE`
- Audit automatique

**`reprendre_tache_view()`** :
- Transition : `EN_PAUSE` → `EN_COURS`
- Audit automatique

### 3. **Contrainte sur la Progression**

Dans `mettre_a_jour_progression_tache()` :
```python
if tache.statut != 'EN_COURS':
    return JsonResponse({'success': False, 'error': 'Vous devez d\'abord démarrer la tâche'})
```

### 4. **Routes Ajoutées**
- `/projets/<projet_id>/taches/<tache_id>/demarrer/<type_tache>/`
- `/projets/<projet_id>/taches/<tache_id>/mettre-en-pause/<type_tache>/`
- `/projets/<uuid:projet_id>/taches/<uuid:tache_id>/reprendre/<str:type_tache>/`

---

## 🎨 Interface Utilisateur (À Finaliser)

### Logique des Boutons par Statut

**À FAIRE** :
- ▶️ Bouton "Démarrer" (vert)
- 📊 Progression grisée (0%, non cliquable)

**EN_COURS** :
- ⏸️ Bouton "Pause" (jaune)
- ✅ Bouton "Terminer" (vert)
- 📊 Progression active (cliquable)

**EN_PAUSE** :
- ▶️ Bouton "Reprendre" (vert)
- 📊 Progression grisée (affiche %, non cliquable)

**TERMINEE** :
- Aucun bouton
- 📊 Affiche "✓ 100%" en vert

### Badges de Statut
- 🔵 "À faire" (gris)
- 🟠 "En cours" (orange)
- 🟡 "En pause" (jaune)
- 🟢 "Terminée" (vert)

---

## 📋 Prochaines Étapes

1. ✅ Backend : Fonctions créées
2. ✅ Backend : Routes ajoutées
3. ✅ Backend : Contrainte progression
4. ⏳ Frontend : Mise à jour template avec logique conditionnelle
5. ⏳ Frontend : JavaScript pour les nouveaux boutons
6. ⏳ Test : Vérifier tous les scénarios

---

## 🔄 Workflow Utilisateur

1. Tâche créée → Statut "À faire"
2. Utilisateur clique "Démarrer" → Statut "En cours"
3. Utilisateur peut mettre à jour la progression
4. Si besoin, clique "Pause" → Statut "En pause"
5. Plus tard, clique "Reprendre" → Retour "En cours"
6. Quand terminé, clique "Terminer" → Statut "Terminée"

---

## 📝 Fichiers Modifiés

**Backend** :
- `core/models.py` - STATUT_CHOICES mis à jour
- `core/views.py` - 3 nouvelles fonctions + contrainte
- `core/urls.py` - 3 nouvelles routes
- `core/migrations/0031_add_statut_en_pause.py` - Migration

**Frontend** (à finaliser) :
- `templates/core/mes_taches_simple_tableau.html` - Logique conditionnelle

---

**Principe** : Garder l'interface simple et intuitive !
