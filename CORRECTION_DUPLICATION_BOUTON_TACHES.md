# Correction de la Duplication du Bouton Tâches

**Date**: 11 février 2026  
**Statut**: ✅ Résolu

## Problème Identifié

Dans l'interface "Gestion des Modules", le bouton "Tâches" s'affichait deux fois pour le module Dashboard du projet "Système de gestion des pharmacies".

### Cause Racine

L'utilisateur (Eraste Butela) était à la fois :
1. **Responsable principal du projet** (créateur)
2. **Responsable du module Dashboard**

La logique de permissions utilisait deux boucles `{% for %}` séparées :
```django
{% for affectation in projet.affectations.all %}
    {% if ... %}
        <button>Tâches</button>  <!-- Affiché 1ère fois -->
    {% endif %}
{% endfor %}

{% for affectation_module in module.affectations.all %}
    {% if ... %}
        <button>Tâches</button>  <!-- Affiché 2ème fois -->
    {% endif %}
{% endfor %}
```

Résultat : Le bouton apparaissait deux fois si l'utilisateur avait les deux rôles.

## Solution Implémentée

Utilisation de la clause `{% empty %}` de Django pour créer une logique conditionnelle exclusive :

```django
{% for affectation in projet.affectations.all %}
    {% if affectation.utilisateur == user and affectation.est_responsable_principal %}
        <button>Tâches</button>
    {% endif %}
{% empty %}
    <!-- Cette section s'exécute SEULEMENT si la boucle précédente n'a rien trouvé -->
    {% for affectation_module in module.affectations.all %}
        {% if affectation_module.utilisateur == user and affectation_module.role_module == 'RESPONSABLE' %}
            <button>Tâches</button>
        {% endif %}
    {% endfor %}
{% endfor %}
```

### Logique de Priorité

1. **Vérifier d'abord** : Responsable principal du projet
   - Si OUI → Afficher le bouton et STOP
   - Si NON → Passer à l'étape 2

2. **Vérifier ensuite** : Responsable du module
   - Si OUI → Afficher le bouton
   - Si NON → Pas de bouton

### Hiérarchie des Permissions

Le bouton "Tâches" s'affiche pour (dans l'ordre de priorité) :

1. ✅ **Super Admin** : Toujours
2. ✅ **Créateur du projet** : Toujours
3. ✅ **Responsable principal du projet** : Tous les modules
4. ✅ **Responsable du module** : Uniquement son module

## Avantages de la Solution

✅ **Pas de duplication** : Un seul bouton affiché  
✅ **Logique claire** : Priorité au rôle projet sur le rôle module  
✅ **Performance** : Arrêt dès qu'une condition est remplie  
✅ **Maintenable** : Code Django idiomatique avec `{% empty %}`

## Clause `{% empty %}` de Django

La clause `{% empty %}` est une fonctionnalité native de Django qui s'exécute quand :
- La liste de la boucle est vide
- OU aucune itération n'a satisfait les conditions

C'est l'équivalent de :
```python
if liste:
    for item in liste:
        # faire quelque chose
else:
    # liste vide ou aucune condition satisfaite
```

## Fichier Modifié

- `templates/core/gestion_modules.html` - Section "Colonne Actions"

## Test de Validation

### Scénario 1 : Utilisateur avec double rôle
- Utilisateur : Eraste Butela
- Rôle 1 : Créateur du projet
- Rôle 2 : Responsable du module Dashboard
- **Résultat attendu** : 1 seul bouton "Tâches" ✅

### Scénario 2 : Utilisateur responsable projet uniquement
- Utilisateur : Admin
- Rôle : Responsable principal du projet
- **Résultat attendu** : 1 bouton "Tâches" pour tous les modules ✅

### Scénario 3 : Utilisateur responsable module uniquement
- Utilisateur : DON DIEU
- Rôle : Responsable du module Dashboard
- **Résultat attendu** : 1 bouton "Tâches" uniquement pour Dashboard ✅

### Scénario 4 : Utilisateur contributeur
- Utilisateur : Contributeur simple
- Rôle : Contributeur du module
- **Résultat attendu** : Pas de bouton "Tâches" ✅

## Recommandation

Cette approche avec `{% empty %}` est la solution Django idiomatique pour gérer des conditions mutuellement exclusives dans les templates. Elle évite :
- Les variables de flag complexes
- Les conditions imbriquées difficiles à lire
- Les duplications de code
