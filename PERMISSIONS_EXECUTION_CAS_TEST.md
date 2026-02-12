# Permissions d'Exécution des Cas de Test

## Contexte

Auparavant, seuls les utilisateurs avec des rôles spécifiques (QA, Admin) pouvaient exécuter les cas de test (marquer comme passé/échoué). Le responsable du projet et le responsable de la tâche ne pouvaient pas exécuter les cas de test, même s'ils pouvaient les créer.

## Problème

Un responsable de tâche ou un responsable de projet pouvait créer des cas de test mais ne pouvait pas les exécuter, créant une incohérence dans les permissions.

## Solution Implémentée

### Nouvelle Logique de Permissions d'Exécution

Les utilisateurs suivants peuvent maintenant exécuter les cas de test (marquer comme passé/échoué) :

1. **Super Admin** - Accès complet au système
2. **QA** - Rôle système QA
3. **Créateur du projet** - L'utilisateur qui a créé le projet
4. **Responsable principal du projet** ✨ **NOUVEAU**
5. **Responsable de la tâche** ✨ **NOUVEAU**

### Modifications Apportées

**Fichier** : `core/views_tests.py`

#### 1. Vue `gestion_cas_tests_tache_view`

**Avant** :
```python
peut_executer = ServiceTests._peut_executer_tests(user, projet)
```

**Après** :
```python
# Peut exécuter : QA, Admin, Créateur du projet, Responsable du projet, Responsable de la tâche
peut_executer = (
    ServiceTests._peut_executer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache.responsable == user
)
```

#### 2. Vue `executer_cas_test_view` (2 occurrences)

**Avant** :
```python
# Vérifier les permissions
if not ServiceTests._peut_executer_tests(user, projet):
    return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

**Après** :
```python
# Vérifier les permissions
# Peut exécuter : QA, Admin, Créateur du projet, Responsable du projet, Responsable de la tâche
responsable_projet = projet.get_responsable_principal()
peut_executer = (
    ServiceTests._peut_executer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    cas_test.tache_etape.responsable == user
)

if not peut_executer:
    return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

## Logique de Vérification

```python
# Obtenir le responsable principal du projet
responsable_projet = projet.get_responsable_principal()

peut_executer = (
    # Permissions de base (via ServiceTests)
    utilisateur.est_super_admin() or
    utilisateur.role_systeme.nom == 'QA' or
    projet.createur == utilisateur or
    
    # Nouvelles permissions
    (responsable_projet and responsable_projet == utilisateur) or
    cas_test.tache_etape.responsable == utilisateur
)
```

## Boutons d'Action Concernés

Dans l'interface des cas de test, les boutons suivants sont maintenant visibles pour les responsables :

1. **Bouton "Voir" (👁️)** - Voir les détails du cas de test
2. **Bouton "Marquer comme Passé" (✅)** - Marquer le cas comme réussi
3. **Bouton "Marquer comme Échoué" (❌)** - Marquer le cas comme échoué

### Condition d'Affichage

```django
{% if peut_executer %}
<div class="flex items-center justify-center space-x-2">
    <!-- Bouton Voir -->
    <button onclick="voirDetailsCas('{{ cas.id }}')">
        <i class="fas fa-eye text-sm"></i>
    </button>
    
    {% if cas.statut != 'PASSE' %}
    <!-- Bouton Marquer comme Passé -->
    <button onclick="executerCas('{{ cas.id }}', 'PASSE', '{{ cas.nom|escapejs }}')">
        <i class="fas fa-check text-sm"></i>
    </button>
    {% endif %}
    
    {% if cas.statut != 'ECHEC' %}
    <!-- Bouton Marquer comme Échoué -->
    <button onclick="executerCas('{{ cas.id }}', 'ECHEC', '{{ cas.nom|escapejs }}')">
        <i class="fas fa-times text-sm"></i>
    </button>
    {% endif %}
</div>
{% endif %}
```

## Cas d'Usage

### Scénario 1 : Responsable de Projet Exécute les Tests

```
1. Responsable de projet accède aux cas de test
2. Voit les boutons d'action (✅ ❌)
3. Exécute un cas de test
4. Marque comme passé ou échoué
5. Le statut est mis à jour
```

### Scénario 2 : Responsable de Tâche Exécute ses Tests

```
1. Responsable de tâche va dans "Mes Tâches"
2. Clique sur l'icône 🧪 "Cas de Test"
3. Voit les boutons d'action (✅ ❌)
4. Exécute ses cas de test
5. Valide sa tâche
```

### Scénario 3 : QA Exécute les Tests (Comportement Inchangé)

```
1. QA accède à n'importe quelle tâche TESTS
2. Voit les boutons d'action
3. Exécute les cas de test
4. Comportement identique à avant
```

## Avantages

1. **Cohérence** : Qui peut créer peut aussi exécuter
2. **Autonomie** : Les responsables gèrent leurs tests de bout en bout
3. **Efficacité** : Pas besoin d'attendre un QA pour exécuter
4. **Responsabilité** : Le responsable valide son propre travail
5. **Flexibilité** : Processus de test plus agile

## Matrice de Permissions Complète

| Utilisateur | Peut Créer | Peut Exécuter | Changement |
|-------------|------------|---------------|------------|
| Super Admin | ✅ | ✅ | - |
| QA | ✅ | ✅ | - |
| Chef de Projet | ✅ | ❌ | - |
| Créateur du projet | ✅ | ✅ | - |
| Responsable du projet | ✅ | ✅ | ✨ **NOUVEAU** |
| Responsable de la tâche | ✅ | ✅ | ✨ **NOUVEAU** |
| Membre simple | ❌ | ❌ | - |

**Note** : Le Chef de Projet peut créer mais pas exécuter (logique métier : il définit les tests, le QA les exécute).

## Impact sur l'Interface

### Boutons d'Action Visibles

Les boutons d'action dans la colonne "Actions" du tableau des cas de test sont maintenant visibles pour :
- Les responsables de projet
- Les responsables de tâche

### État Vide

Si aucun cas de test n'existe et que l'utilisateur peut créer, le bouton "Créer un Cas de Test" est affiché.

## Sécurité

### Vérifications Maintenues

1. **Accès au projet** : L'utilisateur doit avoir accès au projet
2. **Étape TESTS** : La fonctionnalité est limitée aux étapes de tests
3. **Validation du statut** : Seuls 'PASSE' et 'ECHEC' sont acceptés
4. **Audit** : L'exécution est enregistrée avec l'exécuteur

### Pas de Régression

- Les permissions existantes sont préservées
- Aucune permission n'a été retirée
- Seulement des permissions supplémentaires ont été ajoutées

## Tests Recommandés

### Test 1 : Responsable de Projet

1. Se connecter en tant que responsable de projet
2. Accéder à une tâche TESTS du projet
3. Vérifier que les boutons d'action sont visibles
4. Marquer un cas de test comme passé
5. Vérifier la mise à jour du statut

### Test 2 : Responsable de Tâche

1. Se connecter en tant que responsable d'une tâche TESTS
2. Accéder à "Mes Tâches"
3. Cliquer sur l'icône "Cas de Test"
4. Vérifier que les boutons d'action sont visibles
5. Marquer un cas de test comme échoué
6. Vérifier la mise à jour du statut

### Test 3 : Utilisateur Sans Permission

1. Se connecter en tant que membre simple de l'équipe
2. Accéder à une tâche TESTS (si possible)
3. Vérifier que les boutons d'action ne sont PAS visibles
4. Tenter d'exécuter un cas de test via API
5. Vérifier le refus avec message "Permissions insuffisantes"

### Test 4 : QA (Régression)

1. Se connecter en tant que QA
2. Accéder à n'importe quelle tâche TESTS
3. Vérifier que les boutons d'action sont visibles
4. Exécuter un cas de test
5. Vérifier que le comportement est identique à avant

## Fichiers Modifiés

| Fichier | Fonction | Lignes | Statut |
|---------|----------|--------|--------|
| `core/views_tests.py` | `gestion_cas_tests_tache_view` | ~69-74 | ✅ Modifié |
| `core/views_tests.py` | `executer_cas_test_view` (1ère) | ~174-183 | ✅ Modifié |
| `core/views_tests.py` | `executer_cas_test_view` (2ème) | ~687-696 | ✅ Modifié |

## Notes Techniques

### Doublons de Fonction

Le fichier contenait deux définitions identiques de `executer_cas_test_view`. Les deux ont été modifiées pour maintenir la cohérence.

### Performance

- Aucun impact sur les performances
- Les vérifications sont simples (comparaisons d'égalité)
- Pas de requêtes supplémentaires à la base de données

### Compatibilité

- Compatible avec toutes les versions existantes
- Pas de migration de base de données nécessaire
- Pas de modification des modèles

## Prochaines Améliorations Possibles

1. Permettre au Chef de Projet d'exécuter les tests
2. Ajouter une permission pour les contributeurs du module
3. Créer un rôle "Testeur" spécifique
4. Ajouter des permissions configurables par projet

## Statut

✅ **Implémenté**
⏳ **Tests en attente**

## Conclusion

Cette modification rend le système de tests plus cohérent et autonome, permettant aux responsables de gérer leurs cas de test de bout en bout (création ET exécution) sans dépendre exclusivement de l'équipe QA.
