# Blocage de l'Ajout de Cas de Test pour Tâche Terminée

**Date**: 11 février 2026  
**Statut**: ✅ TERMINÉ

## Objectif

Empêcher l'ajout de nouveaux cas de test lorsqu'une tâche de l'étape Tests est terminée. C'est une règle métier logique : une fois la tâche terminée, les tests doivent être figés et ne plus être modifiables.

## Problème

Actuellement, même si une tâche de test est terminée, le bouton "Nouveau Cas" reste visible et fonctionnel, permettant d'ajouter des cas de test après la clôture de la tâche.

## Solution Implémentée

### 1. Modification de la Vue de Gestion

**Fichier**: `core/views_tests.py`  
**Fonction**: `gestion_cas_tests_tache_view`

**Changement**: Ajout d'une vérification du statut de la tâche pour désactiver la création

```python
# Permissions utilisateur
# Peut créer : QA, Chef de projet, Admin, Créateur du projet, Responsable du projet, Responsable de la tâche
# MAIS seulement si la tâche n'est pas terminée
responsable_projet = projet.get_responsable_principal()
a_permission_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache.responsable == user
)
# Ne peut créer que si la tâche n'est pas terminée
peut_creer = a_permission_creer and tache.statut != 'TERMINEE'
```

**Résultat**: Le bouton "Nouveau Cas" ne s'affiche plus si la tâche est terminée.

### 2. Modification de la Vue de Création

**Fichier**: `core/views_tests.py`  
**Fonction**: `creer_cas_test_view`

**Changement**: Ajout d'une vérification backend pour bloquer la création

```python
# Vérifier que la tâche n'est pas terminée
if tache_etape.statut == 'TERMINEE':
    return JsonResponse({'success': False, 'error': 'Impossible d\'ajouter un cas de test à une tâche terminée'})
```

**Résultat**: Même si quelqu'un tente de créer un cas via l'API directement, la création est bloquée avec un message d'erreur.

## Comportement Final

### Tâche NON Terminée (EN_COURS, EN_ATTENTE, etc.)

**Interface**:
- ✅ Bouton "Nouveau Cas" visible et actif
- ✅ Peut créer des cas de test
- ✅ Peut exécuter les cas de test existants

**Permissions**:
- QA peut créer
- Responsable du projet peut créer
- Responsable de la tâche peut créer
- Chef de projet peut créer
- Super Admin peut créer

### Tâche TERMINÉE

**Interface**:
- ❌ Bouton "Nouveau Cas" masqué
- ✅ Peut consulter les cas de test existants (bouton "Voir détails")
- ✅ Les cas de test déjà exécutés restent consultables

**Tentative de création**:
- ❌ Bloquée au niveau backend
- ❌ Message d'erreur: "Impossible d'ajouter un cas de test à une tâche terminée"

## Logique Métier

### Pourquoi bloquer l'ajout ?

1. **Intégrité des tests**: Une tâche terminée signifie que les tests ont été validés et clôturés
2. **Traçabilité**: Les résultats de tests doivent être figés pour l'audit
3. **Workflow cohérent**: Empêche les modifications après validation
4. **Conformité**: Respecte les bonnes pratiques de gestion de tests

### Que peut-on encore faire ?

- ✅ Consulter les cas de test existants
- ✅ Voir les détails et résultats des tests
- ✅ Exporter les rapports de tests
- ❌ Ajouter de nouveaux cas de test
- ❌ Modifier les cas existants (déjà bloqué)

## Flux Utilisateur

### Scénario 1: Tâche en Cours

1. Utilisateur accède à l'interface "Cas de Test" d'une tâche en cours
2. Le bouton "Nouveau Cas" est visible
3. Utilisateur peut créer des cas de test
4. Utilisateur peut exécuter les cas de test

### Scénario 2: Tâche Terminée

1. Utilisateur accède à l'interface "Cas de Test" d'une tâche terminée
2. Le bouton "Nouveau Cas" n'est PAS visible
3. Utilisateur peut seulement consulter les cas existants
4. Message informatif (optionnel): "Cette tâche est terminée, aucun nouveau cas ne peut être ajouté"

### Scénario 3: Tentative de Création via API

1. Utilisateur tente de créer un cas via l'API (requête POST directe)
2. Backend vérifie le statut de la tâche
3. Retourne une erreur JSON: `{'success': False, 'error': 'Impossible d\'ajouter un cas de test à une tâche terminée'}`
4. Aucun cas de test n'est créé

## Cas Particuliers

### Réouverture d'une Tâche

Si une tâche terminée est réouverte (statut change de TERMINEE à EN_COURS):
- ✅ Le bouton "Nouveau Cas" redevient visible
- ✅ La création de cas de test est à nouveau possible

### Super Admin

Même le Super Admin ne peut pas ajouter de cas de test à une tâche terminée. Cette règle métier s'applique à tous les utilisateurs pour garantir l'intégrité des tests.

## Template

Le template `templates/core/gestion_cas_tests_tache.html` utilise déjà la variable `peut_creer` pour afficher conditionnellement le bouton:

```django
{% if peut_creer %}
<button onclick="ouvrirModalCreerCas()" 
   class="inline-flex items-center px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white font-medium rounded-md text-sm transition-colors">
    <i class="fas fa-plus mr-2"></i>Nouveau Cas
</button>
{% endif %}
```

Aucune modification du template n'est nécessaire.

## Tests de Validation

### Test 1: Tâche en Cours
1. Créer une tâche de test avec statut "EN_COURS"
2. Accéder à l'interface "Cas de Test"
3. Vérifier que le bouton "Nouveau Cas" est visible
4. Créer un cas de test
5. ✅ La création doit réussir

### Test 2: Tâche Terminée
1. Marquer une tâche de test comme "TERMINEE"
2. Accéder à l'interface "Cas de Test"
3. Vérifier que le bouton "Nouveau Cas" n'est PAS visible
4. Vérifier que les cas existants sont consultables
5. ✅ Aucun bouton de création ne doit être visible

### Test 3: Tentative de Création Backend
1. Marquer une tâche de test comme "TERMINEE"
2. Tenter de créer un cas via une requête POST directe à l'API
3. Vérifier que la réponse est: `{'success': False, 'error': 'Impossible d\'ajouter un cas de test à une tâche terminée'}`
4. ✅ La création doit être bloquée

### Test 4: Réouverture de Tâche
1. Marquer une tâche comme "TERMINEE"
2. Vérifier que le bouton "Nouveau Cas" n'est pas visible
3. Changer le statut de la tâche à "EN_COURS"
4. Recharger la page
5. Vérifier que le bouton "Nouveau Cas" est à nouveau visible
6. ✅ La création doit être à nouveau possible

## Fichiers Modifiés

1. ✅ `core/views_tests.py` - Fonction `gestion_cas_tests_tache_view` (ligne ~63-70)
2. ✅ `core/views_tests.py` - Fonction `creer_cas_test_view` (ligne ~110-115)

## Avantages

1. **Intégrité des données**: Les tests validés ne peuvent plus être modifiés
2. **Traçabilité**: Les résultats de tests sont figés pour l'audit
3. **UX cohérente**: L'interface reflète clairement l'état de la tâche
4. **Sécurité**: Protection au niveau backend contre les tentatives de contournement
5. **Conformité**: Respecte les standards de gestion de tests

## Limitations

- Si une tâche doit être réouverte pour ajouter des tests, il faut changer son statut manuellement
- Aucun message informatif n'est affiché pour expliquer pourquoi le bouton n'est pas visible (amélioration future possible)

## Améliorations Futures Possibles

1. Ajouter un message informatif: "Cette tâche est terminée, aucun nouveau cas ne peut être ajouté"
2. Ajouter un bouton "Réouvrir la tâche" pour les responsables
3. Logger les tentatives de création sur tâche terminée pour l'audit
4. Ajouter une confirmation avant de terminer une tâche: "Attention: vous ne pourrez plus ajouter de cas de test"

## Conclusion

L'implémentation est complète et fonctionnelle. Le bouton "Nouveau Cas" est masqué pour les tâches terminées, et la création est bloquée au niveau backend pour garantir l'intégrité des tests.

**Statut**: ✅ TERMINÉ - Prêt pour les tests utilisateur
