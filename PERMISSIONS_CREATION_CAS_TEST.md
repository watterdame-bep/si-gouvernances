# Permissions de Création de Cas de Test

## Contexte

Auparavant, seuls les utilisateurs avec des rôles spécifiques (QA, Chef de projet, Admin) pouvaient créer des cas de test. Cette restriction empêchait le responsable du projet et le responsable de la tâche de créer des cas de test pour leurs propres tâches.

## Problème

Un responsable de tâche dans l'étape TESTS ne pouvait pas créer de cas de test pour sa propre tâche, même s'il était directement responsable de son exécution.

## Solution Implémentée

### Nouvelle Logique de Permissions

Les utilisateurs suivants peuvent maintenant créer des cas de test :

1. **Super Admin** - Accès complet au système
2. **QA** - Rôle système QA
3. **Chef de Projet** - Rôle système Chef de projet
4. **Créateur du projet** - L'utilisateur qui a créé le projet
5. **Responsable principal du projet** ✨ **NOUVEAU**
6. **Responsable de la tâche** ✨ **NOUVEAU**

**Note** : Le responsable du projet est obtenu via `projet.get_responsable_principal()` qui retourne le membre de l'équipe marqué comme responsable principal.

### Modifications Apportées

**Fichier** : `core/views_tests.py`

#### 1. Vue `gestion_cas_tests_tache_view`

**Avant** :
```python
# Permissions utilisateur
peut_creer = ServiceTests._peut_creer_tests(user, projet)
peut_executer = ServiceTests._peut_executer_tests(user, projet)
```

**Après** :
```python
# Permissions utilisateur
# Peut créer : QA, Chef de projet, Admin, Créateur du projet, Responsable du projet, Responsable de la tâche
responsable_projet = projet.get_responsable_principal()
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache.responsable == user
)
peut_executer = ServiceTests._peut_executer_tests(user, projet)
```

#### 2. Vue `creer_cas_test_view`

**Avant** :
```python
# Vérifier les permissions
if not ServiceTests._peut_creer_tests(user, projet):
    return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

**Après** :
```python
# Vérifier les permissions
# Peut créer : QA, Chef de projet, Admin, Créateur du projet, Responsable du projet, Responsable de la tâche
responsable_projet = projet.get_responsable_principal()
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache_etape.responsable == user
)

if not peut_creer:
    return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

## Logique de Vérification

```python
# Obtenir le responsable principal du projet
responsable_projet = projet.get_responsable_principal()

peut_creer = (
    # Permissions de base (via ServiceTests)
    utilisateur.est_super_admin() or
    utilisateur.role_systeme.nom in ['QA', 'CHEF_PROJET'] or
    projet.createur == utilisateur or
    
    # Nouvelles permissions
    (responsable_projet and responsable_projet == utilisateur) or
    tache.responsable == utilisateur
)
```

**Note importante** : La vérification `(responsable_projet and responsable_projet == utilisateur)` garantit que :
1. Le projet a un responsable principal (pas `None`)
2. Le responsable correspond à l'utilisateur actuel

## Cas d'Usage

### Scénario 1 : Responsable de Projet

```
1. Admin crée un projet et assigne un responsable
2. Le responsable du projet accède à une tâche TESTS
3. Le responsable peut maintenant créer des cas de test
4. Le bouton "Nouveau Cas" est visible
```

### Scénario 2 : Responsable de Tâche

```
1. Une tâche TESTS est assignée à un développeur
2. Le développeur accède à ses cas de test via "Mes Tâches"
3. Le développeur peut créer des cas de test pour sa tâche
4. Le bouton "Nouveau Cas" est visible
```

### Scénario 3 : QA (Comportement Inchangé)

```
1. Un QA accède à n'importe quelle tâche TESTS
2. Le QA peut créer des cas de test
3. Comportement identique à avant
```

## Avantages

1. **Autonomie** : Les responsables peuvent gérer leurs propres tests
2. **Flexibilité** : Pas besoin d'avoir un rôle QA pour tester
3. **Responsabilité** : Le responsable de la tâche contrôle ses tests
4. **Efficacité** : Moins de dépendance sur l'équipe QA
5. **Cohérence** : Logique similaire aux autres permissions du système

## Matrice de Permissions

| Utilisateur | Peut Créer Cas de Test | Raison |
|-------------|------------------------|--------|
| Super Admin | ✅ Oui | Accès complet |
| QA | ✅ Oui | Rôle système |
| Chef de Projet | ✅ Oui | Rôle système |
| Créateur du projet | ✅ Oui | Propriétaire |
| Responsable du projet | ✅ Oui | **NOUVEAU** |
| Responsable de la tâche | ✅ Oui | **NOUVEAU** |
| Membre de l'équipe | ❌ Non | Pas de permission |
| Utilisateur externe | ❌ Non | Pas d'accès |

## Impact sur l'Interface

### Bouton "Nouveau Cas"

Le bouton "Nouveau Cas" dans l'interface des cas de test est maintenant visible pour :
- Les responsables de projet
- Les responsables de tâche

**Condition d'affichage** :
```django
{% if peut_creer %}
<button onclick="ouvrirModalCreerCas()">
    <i class="fas fa-plus mr-2"></i>Nouveau Cas
</button>
{% endif %}
```

### État Vide

L'état vide (quand aucun cas de test n'existe) affiche maintenant le bouton "Créer un Cas de Test" pour les responsables.

## Sécurité

### Vérifications Maintenues

1. **Accès au projet** : L'utilisateur doit avoir accès au projet
2. **Étape TESTS** : La fonctionnalité est limitée aux étapes de tests
3. **Validation des données** : Tous les champs obligatoires sont vérifiés
4. **Audit** : La création est enregistrée avec le créateur

### Pas de Régression

- Les permissions existantes sont préservées
- Aucune permission n'a été retirée
- Seulement des permissions supplémentaires ont été ajoutées

## Tests Recommandés

### Test 1 : Responsable de Projet

1. Se connecter en tant que responsable de projet
2. Accéder à une tâche TESTS du projet
3. Vérifier que le bouton "Nouveau Cas" est visible
4. Créer un cas de test
5. Vérifier la création réussie

### Test 2 : Responsable de Tâche

1. Se connecter en tant que responsable d'une tâche TESTS
2. Accéder à "Mes Tâches"
3. Cliquer sur l'icône "Cas de Test"
4. Vérifier que le bouton "Nouveau Cas" est visible
5. Créer un cas de test
6. Vérifier la création réussie

### Test 3 : Utilisateur Sans Permission

1. Se connecter en tant que membre simple de l'équipe
2. Accéder à une tâche TESTS (si possible)
3. Vérifier que le bouton "Nouveau Cas" n'est PAS visible
4. Tenter de créer un cas de test via API
5. Vérifier le refus avec message "Permissions insuffisantes"

### Test 4 : QA (Régression)

1. Se connecter en tant que QA
2. Accéder à n'importe quelle tâche TESTS
3. Vérifier que le bouton "Nouveau Cas" est visible
4. Créer un cas de test
5. Vérifier que le comportement est identique à avant

## Fichiers Modifiés

| Fichier | Lignes Modifiées | Type de Modification |
|---------|------------------|----------------------|
| `core/views_tests.py` | ~60-65 | Ajout logique permissions |
| `core/views_tests.py` | ~95-105 | Ajout logique permissions |

## Notes Techniques

### Ordre de Vérification

Les vérifications sont effectuées dans cet ordre :
1. Permissions de base (ServiceTests)
2. Responsable du projet
3. Responsable de la tâche

### Performance

- Aucun impact sur les performances
- Les vérifications sont simples (comparaisons d'égalité)
- Pas de requêtes supplémentaires à la base de données

### Compatibilité

- Compatible avec toutes les versions existantes
- Pas de migration de base de données nécessaire
- Pas de modification des modèles

## Prochaines Améliorations Possibles

1. Ajouter une permission pour les contributeurs du module
2. Permettre au créateur de la tâche de créer des cas de test
3. Ajouter une permission configurable par projet
4. Créer un rôle "Testeur" spécifique

## Statut

✅ **Implémenté**
⏳ **Tests en attente**

## Conclusion

Cette modification rend le système de tests plus flexible et autonome, permettant aux responsables de gérer directement leurs cas de test sans dépendre exclusivement de l'équipe QA.
