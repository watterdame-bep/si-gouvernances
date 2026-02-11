# Correction du Calcul des Tâches Restantes

**Date**: 11 février 2026  
**Statut**: ✅ Résolu

## Problème Identifié

Dans la section "Progression Globale" de l'interface de détail d'étape, les tâches restantes n'affichaient aucun chiffre.

### Cause Racine

Le template utilisait un calcul avec les filtres Django qui ne fonctionnait pas :
```django
{{ stats.total_taches|add:"-"|add:stats.taches_terminees }}
```

Cette syntaxe ne permet pas de faire une soustraction correctement dans Django templates.

## Solution Implémentée

### 1. Calcul Backend (Python)

Ajout du calcul des tâches restantes directement dans `core/views.py` :

```python
# Calculer les tâches restantes
stats['taches_restantes'] = stats['total_taches'] - stats['taches_terminees']
```

**Emplacement** : Fonction `detail_etape_view()` après le calcul de la progression globale (ligne ~2495)

### 2. Mise à Jour du Template

Remplacement du calcul par la variable calculée dans le backend :

```django
<span class="font-medium">{{ stats.taches_restantes }}</span>
```

**Emplacement** : `templates/core/detail_etape.html` section "Progression Globale"

## Résultat

La section "Progression Globale" affiche maintenant correctement :
- **Terminées** : Nombre de tâches terminées (ex: 18)
- **Restantes** : Nombre de tâches restantes (ex: 7)

## Principe Appliqué

✅ **Bonne pratique** : Effectuer les calculs complexes dans le backend (Python) plutôt que dans les templates Django.

Les templates Django sont conçus pour l'affichage, pas pour la logique métier complexe. Les calculs arithmétiques doivent être faits en Python pour :
- Meilleure lisibilité
- Facilité de débogage
- Performance optimale
- Éviter les erreurs de syntaxe

## Fichiers Modifiés

1. `core/views.py` - Fonction `detail_etape_view()`
2. `templates/core/detail_etape.html` - Section Progression Globale

## Tests Recommandés

1. Accéder à l'interface de détail de l'étape Développement
2. Vérifier que la section "Progression Globale" affiche :
   - Le nombre de tâches terminées
   - Le nombre de tâches restantes (avec un chiffre visible)
3. Vérifier que le calcul est correct : `Terminées + Restantes = Total`
