# Correction Accès Contributeurs aux Modules

## Problème Identifié
Les contributeurs (membres simples) affectés à un module ne voyaient pas le bouton d'action pour accéder à leurs tâches dans l'interface "Mes Modules".

## Cause
1. Le template `mes_modules.html` affichait le bouton uniquement si `affectation.peut_creer_taches = True`
2. La vue `gestion_taches_module_view` refusait l'accès aux membres qui n'avaient pas `peut_creer_taches = True`

## Solution Implémentée

### 1. Template `mes_modules.html`
**Avant** : Le bouton s'affichait uniquement si `peut_creer_taches = True`
```html
{% if affectation.peut_creer_taches %}
    <a href="...">Gérer mes tâches</a>
{% else %}
    <span>Aucune action</span>
{% endif %}
```

**Après** : Le bouton s'affiche pour tous les membres affectés
```html
<a href="{% url 'gestion_taches_module' projet.id affectation.module.id %}?from=mes_modules"
   title="{% if affectation.peut_creer_taches %}Gérer mes tâches{% else %}Voir mes tâches{% endif %}">
    <i class="fas fa-tasks"></i>
</a>
```

### 2. Vue `gestion_taches_module_view` (core/views_taches_module.py)

**Modifications** :
1. **Accès élargi** : Tous les membres affectés au module peuvent accéder à l'interface
2. **Nouvelle variable** : `peut_creer_taches` pour distinguer les permissions de création
3. **Logique adaptée** :
   - Super admin, créateur projet, responsable projet → Accès complet + création
   - Responsable module → Accès complet + création
   - Contributeur/Consultant → Accès à leurs tâches + création selon `peut_creer_taches`

**Code** :
```python
# Tout membre affecté au module peut voir ses tâches
affectation_membre = module.affectations.filter(
    utilisateur=user,
    date_fin_affectation__isnull=True
).first()
if affectation_membre:
    peut_gerer_taches = True  # Peut accéder à l'interface
    est_membre_simple = affectation_membre.role_module != 'RESPONSABLE'
    peut_creer_taches = affectation_membre.peut_creer_taches  # Permission de création
```

### 3. Template `gestion_taches_module.html`

**Modifications** :
- Bouton "Nouvelle Tâche" : Utilise `peut_creer_taches` au lieu de `peut_gerer_taches`
- Bouton "Assigner" : Utilise `peut_creer_taches`
- Actions de modification : Utilise `peut_creer_taches`

**Résultat** :
- Les contributeurs sans `peut_creer_taches` peuvent voir leurs tâches mais pas en créer
- Les contributeurs avec `peut_creer_taches` peuvent créer et gérer leurs tâches

## Comportement Final

### Contributeur SANS `peut_creer_taches = True`
✅ Voit le bouton d'action dans "Mes Modules"
✅ Accède à l'interface des tâches du module
✅ Voit uniquement ses tâches créées
❌ Ne peut pas créer de nouvelles tâches
❌ Ne voit pas le bouton "Nouvelle Tâche"
✅ Peut modifier la progression de ses tâches
✅ Peut changer le statut de ses tâches

### Contributeur AVEC `peut_creer_taches = True`
✅ Voit le bouton d'action dans "Mes Modules"
✅ Accède à l'interface des tâches du module
✅ Voit uniquement ses tâches créées
✅ Peut créer de nouvelles tâches
✅ Voit le bouton "Nouvelle Tâche"
✅ Peut assigner des tâches
✅ Peut modifier la progression de ses tâches
✅ Peut changer le statut de ses tâches

### Responsable de Module
✅ Voit toutes les tâches du module
✅ Peut créer, assigner, modifier toutes les tâches
✅ Accès complet à la gestion

## Fichiers Modifiés
1. `templates/core/mes_modules.html` - Affichage du bouton pour tous
2. `core/views_taches_module.py` - Logique d'accès élargie + nouvelle variable
3. `templates/core/gestion_taches_module.html` - Utilisation de `peut_creer_taches`

## Test Recommandé
1. Créer un contributeur avec `peut_creer_taches = False`
2. L'affecter à un module
3. Vérifier qu'il voit le bouton dans "Mes Modules"
4. Vérifier qu'il accède à l'interface mais ne voit pas "Nouvelle Tâche"
5. Modifier `peut_creer_taches = True`
6. Vérifier qu'il voit maintenant "Nouvelle Tâche"

## Date
10 février 2026
