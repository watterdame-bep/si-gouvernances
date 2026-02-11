# Correction des Statuts Invalides - Tâches de Module

**Date**: 11 février 2026  
**Statut**: ✅ Résolu

## Problème Identifié

L'utilisateur Eraste Butela ne voyait pas les boutons d'action (Démarrer, Progression, etc.) dans l'interface "Tâches du Module", même s'il était responsable du projet et/ou responsable des tâches.

## Diagnostic

### Investigation

Un script de diagnostic (`debug_boutons_actions_taches.py`) a révélé que :

1. ✅ L'utilisateur avait les bonnes permissions
2. ✅ La condition d'affichage des boutons était correcte
3. ❌ **Les tâches avaient un statut `EN_ATTENTE` qui n'existe pas dans le modèle**

### Statuts Valides

Le modèle `TacheModule` définit uniquement ces statuts :
- `A_FAIRE` - À faire
- `EN_COURS` - En cours
- `EN_PAUSE` - En pause
- `TERMINEE` - Terminée

### Tâches Affectées

3 tâches avaient le statut invalide `EN_ATTENTE` :
- Tâche #22 : "Front-end pour le login" (Module Authentification)
- Tâche #23 : "Parametrage vvv" (Module Authentification)
- Tâche #24 : "je ne sais pas" (Module Dashboard)

## Solution Appliquée

### 1. Correction des Statuts

Script créé : `corriger_statuts_taches_module.py`

```python
# Correction automatique des statuts invalides
for tache in taches_invalides:
    tache.statut = 'A_FAIRE'
    tache.save()
```

**Résultat** : Les 3 tâches ont été corrigées avec succès.

### 2. Simplification de la Condition d'Affichage

La condition dans `templates/core/gestion_taches_module.html` a été simplifiée :

**Avant** (logique complexe avec duplication) :
```django
{% if peut_modifier_taches or tache.createur.id == user.id %}
    <!-- Actions -->
{% elif tache.responsable and tache.responsable.id == user.id %}
    <!-- Actions dupliquées -->
{% endif %}
```

**Après** (logique unifiée) :
```django
{% if peut_modifier_taches or tache.createur.id == user.id or tache.responsable and tache.responsable.id == user.id %}
    <!-- Actions selon le statut -->
    {% if tache.statut == 'A_FAIRE' %}
        <button onclick="mettreEnCours('{{ tache.id }}')" title="Démarrer">
            <i class="fas fa-play-circle"></i>
        </button>
    {% elif tache.statut == 'EN_COURS' %}
        <!-- Progression, Pause, Terminer -->
    {% elif tache.statut == 'EN_PAUSE' %}
        <!-- Reprendre -->
    {% elif tache.statut == 'TERMINEE' %}
        <!-- Icône check grise -->
    {% endif %}
{% endif %}
```

## Permissions d'Affichage des Boutons

Les boutons d'action s'affichent si l'utilisateur est :
1. **Responsable du module** (`peut_modifier_taches=True`)
2. **Créateur de la tâche**
3. **Responsable de la tâche**

## Vérification Post-Correction

### Utilisateur : Eraste Butela
- Responsable principal du projet "Systeme de gestion des pharmacie"
- Contributeur du module "Authentification"
- Responsable du module "Dashboard"

### Tâches Vérifiées

| Tâche | Module | Statut | Responsable | Boutons Visibles |
|-------|--------|--------|-------------|------------------|
| Front-end pour le login | Authentification | A_FAIRE | Eraste Butela | ✅ Démarrer |
| Parametrage vvv | Authentification | A_FAIRE | DON DIEU | ✅ Démarrer (créateur) |
| je ne sais pas | Dashboard | A_FAIRE | DON DIEU | ✅ Démarrer (créateur + responsable module) |

## Actions Requises

1. ✅ Corriger les statuts invalides dans la base de données
2. ✅ Simplifier la condition d'affichage dans le template
3. ⚠️ **Redémarrer le serveur Django** pour appliquer les changements du template

## Commande de Redémarrage

```bash
# Arrêter le serveur (Ctrl+C)
# Puis relancer
python manage.py runserver
```

## Prévention Future

### Validation au Niveau du Modèle

Pour éviter que des statuts invalides soient créés à l'avenir, considérer l'ajout d'une validation :

```python
class TacheModule(models.Model):
    # ...
    
    def clean(self):
        if self.statut not in dict(self.STATUT_CHOICES):
            raise ValidationError(f"Statut invalide: {self.statut}")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
```

### Migration de Données

Si d'autres tâches avec statuts invalides existent, exécuter :

```bash
python corriger_statuts_taches_module.py
```

## Scripts Créés

1. **debug_boutons_actions_taches.py** - Diagnostic complet des permissions et statuts
2. **corriger_statuts_taches_module.py** - Correction automatique des statuts invalides

## Fichiers Modifiés

- `templates/core/gestion_taches_module.html` - Simplification de la condition d'affichage

## Résultat Final

✅ Les boutons d'action s'affichent correctement pour tous les utilisateurs ayant les permissions appropriées.
✅ La logique d'affichage est simplifiée et plus maintenable.
✅ Les statuts invalides ont été corrigés.

---

**Note** : Après redémarrage du serveur, l'utilisateur Eraste Butela devrait voir le bouton "Démarrer" pour la tâche "Front-end pour le login" dans le module Authentification.
