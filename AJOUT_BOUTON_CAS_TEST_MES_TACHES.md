# Ajout Bouton Cas de Test dans Mes Tâches

## Contexte

L'interface "Mes Tâches" (`mes_taches_simple_tableau.html`) affiche toutes les tâches assignées à un utilisateur (tâches d'étapes et tâches de modules). Pour les tâches de l'étape TESTS, un bouton d'action "Cas de Test" a été ajouté pour permettre un accès direct aux cas de test.

## Modification Apportée

### 1. Ajout du Bouton dans la Colonne Actions

**Fichier** : `templates/core/mes_taches_simple_tableau.html`

**Changement** : Ajout d'un bouton violet avec icône de fiole pour les tâches TESTS

```django
<td class="px-4 py-3 text-right">
    <div class="flex items-center justify-end space-x-2">
        {% if tache.etape.type_etape.nom == 'TESTS' %}
            <a href="{% url 'gestion_cas_tests_tache' projet.id tache.etape.id tache.id %}?from=mes_taches" 
               class="text-purple-600 hover:text-purple-800" title="Cas de Test">
                <i class="fas fa-vial text-lg"></i>
            </a>
        {% endif %}
        
        <!-- Boutons d'action existants (Démarrer, Pause, Terminer) -->
    </div>
</td>
```

### 2. Gestion de la Redirection Retour

**Fichier** : `templates/core/gestion_cas_tests_tache.html`

**Changement** : Ajout de la gestion du paramètre `?from=mes_taches`

```django
{% if request.GET.from == 'mes_tests' %}
    <a href="{% url 'mes_taches' projet.id %}">
        <i class="fas fa-arrow-left mr-2"></i>Retour à Mes Tests
    </a>
{% elif request.GET.from == 'mes_taches' %}
    <a href="{% url 'mes_taches' projet.id %}">
        <i class="fas fa-arrow-left mr-2"></i>Retour à Mes Tâches
    </a>
{% else %}
    <a href="{% url 'gestion_taches_etape' projet.id etape.id %}">
        <i class="fas fa-arrow-left mr-2"></i>Retour
    </a>
{% endif %}
```

## Caractéristiques du Bouton

### Apparence
- **Icône** : Fiole (`fa-vial`)
- **Couleur** : Violet (`text-purple-600`)
- **Hover** : Violet foncé (`hover:text-purple-800`)
- **Taille** : Grande (`text-lg`)
- **Tooltip** : "Cas de Test"

### Position
- Dans la colonne "Actions" du tableau
- À gauche des boutons d'action (Démarrer, Pause, Terminer)
- Aligné avec les autres boutons d'action

### Condition d'Affichage
- Visible uniquement si `tache.etape.type_etape.nom == 'TESTS'`
- Visible pour tous les statuts de tâche (À faire, En cours, En pause, Terminée)

## Flux de Navigation

```
Interface "Mes Tâches"
    ↓
Tâche de l'étape TESTS visible
    ↓
Bouton "Cas de Test" (icône fiole violette)
    ↓
Clic sur le bouton
    ↓
Redirection vers Cas de Test (?from=mes_taches)
    ↓
Bouton "Retour à Mes Tâches"
    ↓
Retour à "Mes Tâches"
```

## Différences avec "Mes Tests"

| Aspect | Mes Tests | Mes Tâches |
|--------|-----------|------------|
| Interface | `mes_taches_simple.html` | `mes_taches_simple_tableau.html` |
| Paramètre URL | `?from=mes_tests` | `?from=mes_taches` |
| Bouton Retour | "Retour à Mes Tests" | "Retour à Mes Tâches" |
| Type de bouton | Bouton plein violet | Icône violette |
| Position | À droite de la tâche | Dans colonne Actions |

## Avantages

1. **Accès rapide** : Bouton directement dans le tableau
2. **Visibilité** : Icône distinctive pour les tâches TESTS
3. **Cohérence** : Même pattern de navigation que "Mes Tests"
4. **Flexibilité** : Fonctionne quel que soit le statut de la tâche
5. **Navigation intelligente** : Retour contextuel à "Mes Tâches"

## Cas d'Usage

### Scénario 1 : Tester une Tâche
1. Utilisateur ouvre "Mes Tâches"
2. Voit une tâche de l'étape TESTS
3. Clique sur l'icône fiole violette
4. Accède aux cas de test
5. Exécute les tests
6. Clique sur "Retour à Mes Tâches"
7. Revient à la liste de ses tâches

### Scénario 2 : Tâche Terminée
1. Utilisateur a terminé une tâche TESTS
2. Le bouton "Cas de Test" reste visible
3. Peut consulter les résultats des tests
4. Peut vérifier que tous les cas sont passés

## Compatibilité

### Avec "Mes Tests"
- Les deux interfaces coexistent
- "Mes Tests" : interface simplifiée pour les tests uniquement
- "Mes Tâches" : interface complète pour toutes les tâches

### Avec "Gestion des Tâches"
- L'admin peut toujours accéder aux cas de test depuis "Gestion des Tâches"
- Le bouton "Retour" s'adapte selon la source

## Structure du Tableau

```
┌──────────┬──────────┬────────┬────────────┬─────────┬──────────┬─────────────────┐
│  Tâche   │ Contexte │ Statut │ Progression│ Priorité│ Échéance │    Actions      │
├──────────┼──────────┼────────┼────────────┼─────────┼──────────┼─────────────────┤
│ Test API │  TESTS   │   🟠   │    50%     │    ⬆️   │ 15/02/26 │ 🧪 ⏸️ ✅        │
│          │          │        │            │         │          │ ↑ Nouveau       │
└──────────┴──────────┴────────┴────────────┴─────────┴──────────┴─────────────────┘
```

## Fichiers Modifiés

1. `templates/core/mes_taches_simple_tableau.html` - Ajout du bouton Cas de Test
2. `templates/core/gestion_cas_tests_tache.html` - Gestion du paramètre `from=mes_taches`

## Tests Recommandés

### Test 1 : Affichage du Bouton
- [ ] Le bouton apparaît pour les tâches TESTS
- [ ] Le bouton n'apparaît pas pour les autres étapes
- [ ] L'icône est violette et en forme de fiole
- [ ] Le tooltip affiche "Cas de Test"

### Test 2 : Navigation
- [ ] Clic sur le bouton redirige vers les cas de test
- [ ] L'URL contient `?from=mes_taches`
- [ ] Le bouton "Retour" affiche "Retour à Mes Tâches"
- [ ] Le retour fonctionne correctement

### Test 3 : Tous les Statuts
- [ ] Bouton visible pour tâche À FAIRE
- [ ] Bouton visible pour tâche EN COURS
- [ ] Bouton visible pour tâche EN PAUSE
- [ ] Bouton visible pour tâche TERMINÉE

### Test 4 : Responsive
- [ ] Bouton visible sur desktop
- [ ] Bouton visible sur tablette
- [ ] Bouton visible sur mobile

## Notes Techniques

- Le bouton utilise un lien `<a>` et non un `<button>` pour la navigation
- La condition `tache.etape.type_etape.nom == 'TESTS'` est évaluée côté serveur
- Le paramètre `from=mes_taches` est automatiquement disponible via `request.GET`
- Aucune modification JavaScript nécessaire

## Prochaines Améliorations Possibles

1. Ajouter un badge avec le nombre de cas de test
2. Afficher le statut des tests (ex: "3/5 passés")
3. Colorer le bouton selon le résultat des tests
4. Ajouter un indicateur de progression des tests

## Statut

✅ **Implémenté**
⏳ **Tests en attente**

## Conclusion

Cette amélioration rend l'accès aux cas de test plus intuitif et rapide depuis l'interface "Mes Tâches", tout en maintenant une navigation cohérente avec le reste de l'application.
