# Redirection Cas de Test depuis Mes Tests

## Contexte
Lorsqu'un utilisateur a la responsabilité d'une tâche dans l'étape TESTS, il peut accéder à ses tâches via l'interface "Mes Tests". Il doit pouvoir accéder aux cas de test de ces tâches, et le bouton "Retour" doit le ramener à "Mes Tests" plutôt qu'à la gestion des tâches de l'étape.

## Solution Implémentée

### 1. Ajout du Bouton "Cas de Test" dans Mes Tests

**Fichier**: `templates/core/mes_taches_simple.html`

- Ajout d'un bouton "Cas de Test" pour chaque tâche d'étape de type TESTS
- Le bouton inclut le paramètre `?from=mes_tests` dans l'URL
- Style : bouton compact violet avec icône de fiole

```django
{% if tache.etape.type_etape.nom == 'TESTS' %}
<div class="ml-4">
    <a href="{% url 'gestion_cas_tests_tache' projet.id tache.etape.id tache.id %}?from=mes_tests" 
       class="inline-flex items-center px-3 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-medium rounded transition-colors"
       title="Accéder aux cas de test">
        <i class="fas fa-vial mr-1"></i>Cas de Test
    </a>
</div>
{% endif %}
```

### 2. Redirection Conditionnelle du Bouton Retour

**Fichier**: `templates/core/gestion_cas_tests_tache.html`

- Le bouton "Retour" vérifie le paramètre `from` dans l'URL
- Si `from=mes_tests` : redirige vers "Mes Tests" (`mes_taches`)
- Sinon : redirige vers "Gestion des Tâches" (`gestion_taches_etape`)

```django
{% if request.GET.from == 'mes_tests' %}
<a href="{% url 'mes_taches' projet.id %}" 
   class="inline-flex items-center px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium text-sm transition-colors">
    <i class="fas fa-arrow-left mr-2"></i>Retour à Mes Tests
</a>
{% else %}
<a href="{% url 'gestion_taches_etape' projet.id etape.id %}" 
   class="inline-flex items-center px-3 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md font-medium text-sm transition-colors">
    <i class="fas fa-arrow-left mr-2"></i>Retour
</a>
{% endif %}
```

## Flux Utilisateur

### Scénario 1 : Depuis "Mes Tests"
1. Utilisateur va dans "Mes Tests" (`/projets/{id}/mes-taches/`)
2. Voit ses tâches de l'étape TESTS avec un bouton "Cas de Test"
3. Clique sur "Cas de Test" → redirigé vers `/projets/{id}/etapes/{etape_id}/taches/{tache_id}/cas-tests/?from=mes_tests`
4. Clique sur "Retour à Mes Tests" → retour à "Mes Tests"

### Scénario 2 : Depuis "Gestion des Tâches"
1. Admin/Responsable va dans "Gestion des Tâches" de l'étape TESTS
2. Clique sur un lien vers les cas de test (sans paramètre `from`)
3. Clique sur "Retour" → retour à "Gestion des Tâches"

## Avantages

1. **Navigation intuitive** : L'utilisateur revient toujours à son point de départ
2. **Cohérence** : Même pattern que "Mes Modules" avec `?from=mes_modules`
3. **Flexibilité** : Fonctionne pour les deux contextes (Mes Tests et Gestion)
4. **Simplicité** : Pas de modification backend nécessaire, tout est géré dans les templates

## Pattern Réutilisable

Ce pattern peut être appliqué à d'autres interfaces :
- Paramètre URL : `?from=source`
- Vérification dans le template : `{% if request.GET.from == 'source' %}`
- Redirection conditionnelle basée sur la source

## Fichiers Modifiés

1. `templates/core/mes_taches_simple.html` - Ajout du bouton "Cas de Test"
2. `templates/core/gestion_cas_tests_tache.html` - Redirection conditionnelle du bouton "Retour"

## Test

### Test 1 : Accès depuis Mes Tests
1. Se connecter avec un utilisateur ayant une tâche dans l'étape TESTS
2. Aller dans "Mes Tests"
3. Vérifier la présence du bouton "Cas de Test" pour les tâches TESTS
4. Cliquer sur "Cas de Test"
5. Vérifier que le bouton affiche "Retour à Mes Tests"
6. Cliquer sur "Retour à Mes Tests"
7. Vérifier le retour à l'interface "Mes Tests"

### Test 2 : Accès depuis Gestion des Tâches
1. Se connecter en tant qu'admin/responsable
2. Aller dans la gestion des tâches d'une étape TESTS
3. Accéder aux cas de test d'une tâche
4. Vérifier que le bouton affiche "Retour" (sans "à Mes Tests")
5. Cliquer sur "Retour"
6. Vérifier le retour à "Gestion des Tâches"

## Statut
✅ Implémenté et prêt pour les tests
