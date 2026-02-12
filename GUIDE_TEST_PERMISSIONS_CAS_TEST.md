# Guide de Test : Permissions Création Cas de Test

## Objectif

Vérifier que le responsable du projet et le responsable de la tâche peuvent créer des cas de test.

## Prérequis

1. Un projet avec une étape TESTS
2. Au moins une tâche dans l'étape TESTS
3. Un utilisateur assigné comme responsable du projet
4. Un utilisateur assigné comme responsable de la tâche
5. Un utilisateur simple (membre de l'équipe sans rôle spécial)

## Test 1 : Responsable de Projet

### Objectif
Vérifier que le responsable du projet peut créer des cas de test.

### Étapes

1. **Préparation**
   - Se connecter en tant qu'admin
   - Créer ou sélectionner un projet
   - Assigner un responsable au projet (pas QA, pas Chef de projet)
   - Créer une étape TESTS avec une tâche

2. **Connexion Responsable**
   - Se déconnecter
   - Se connecter avec le compte du responsable du projet

3. **Navigation**
   - Aller dans le projet
   - Accéder à l'étape TESTS
   - Cliquer sur "Gestion des Tâches"
   - Accéder aux cas de test d'une tâche

4. **Vérification Interface**
   - ✅ Vérifier que le bouton "Nouveau Cas" est visible
   - ✅ Vérifier que le bouton est cliquable (pas grisé)

5. **Création de Cas de Test**
   - Cliquer sur "Nouveau Cas"
   - Remplir le formulaire :
     - Nom : "Test connexion responsable projet"
     - Description : "Test créé par le responsable du projet"
     - Priorité : Moyenne
     - Étapes d'exécution : "1. Ouvrir l'app\n2. Se connecter"
     - Résultats attendus : "Connexion réussie"
   - Cliquer sur "Créer"

6. **Vérification Résultat**
   - ✅ Vérifier le message de succès
   - ✅ Vérifier que le cas de test apparaît dans la liste
   - ✅ Vérifier que le créateur est le responsable du projet

### Résultat Attendu
Le responsable du projet peut créer des cas de test sans erreur.

---

## Test 2 : Responsable de Tâche

### Objectif
Vérifier que le responsable de la tâche peut créer des cas de test.

### Étapes

1. **Préparation**
   - Se connecter en tant qu'admin
   - Assigner un utilisateur comme responsable d'une tâche TESTS
   - L'utilisateur ne doit pas être QA, Chef de projet, ou responsable du projet

2. **Connexion Responsable Tâche**
   - Se déconnecter
   - Se connecter avec le compte du responsable de la tâche

3. **Navigation via "Mes Tâches"**
   - Aller dans "Mes Tâches"
   - Trouver la tâche TESTS
   - Cliquer sur l'icône fiole 🧪 "Cas de Test"

4. **Vérification Interface**
   - ✅ Vérifier que le bouton "Nouveau Cas" est visible
   - ✅ Vérifier que le bouton est cliquable

5. **Création de Cas de Test**
   - Cliquer sur "Nouveau Cas"
   - Remplir le formulaire :
     - Nom : "Test connexion responsable tâche"
     - Description : "Test créé par le responsable de la tâche"
     - Priorité : Haute
     - Étapes d'exécution : "1. Lancer l'app\n2. Tester la fonctionnalité"
     - Résultats attendus : "Fonctionnalité opérationnelle"
   - Cliquer sur "Créer"

6. **Vérification Résultat**
   - ✅ Vérifier le message de succès
   - ✅ Vérifier que le cas de test apparaît dans la liste
   - ✅ Vérifier que le créateur est le responsable de la tâche

### Résultat Attendu
Le responsable de la tâche peut créer des cas de test pour sa propre tâche.

---

## Test 3 : Utilisateur Sans Permission

### Objectif
Vérifier qu'un utilisateur sans permission ne peut PAS créer de cas de test.

### Étapes

1. **Préparation**
   - Se connecter en tant qu'admin
   - Créer un utilisateur simple (pas QA, pas Chef de projet)
   - Ajouter l'utilisateur à l'équipe du projet
   - NE PAS l'assigner comme responsable du projet ou de la tâche

2. **Connexion Utilisateur Simple**
   - Se déconnecter
   - Se connecter avec le compte de l'utilisateur simple

3. **Tentative d'Accès**
   - Aller dans le projet
   - Essayer d'accéder à l'étape TESTS
   - Si possible, accéder aux cas de test d'une tâche

4. **Vérification Interface**
   - ✅ Vérifier que le bouton "Nouveau Cas" n'est PAS visible
   - ✅ Vérifier l'état vide ne propose pas de créer un cas

5. **Tentative de Création (API)**
   - Ouvrir la console du navigateur
   - Tenter une requête POST vers l'URL de création
   - ✅ Vérifier le message d'erreur "Permissions insuffisantes"

### Résultat Attendu
L'utilisateur sans permission ne peut pas créer de cas de test.

---

## Test 4 : QA (Test de Régression)

### Objectif
Vérifier que le comportement pour les QA n'a pas changé.

### Étapes

1. **Connexion QA**
   - Se connecter avec un compte QA

2. **Navigation**
   - Accéder à n'importe quelle tâche TESTS
   - Même si le QA n'est pas responsable

3. **Vérification Interface**
   - ✅ Vérifier que le bouton "Nouveau Cas" est visible
   - ✅ Vérifier que le comportement est identique à avant

4. **Création de Cas de Test**
   - Créer un cas de test
   - ✅ Vérifier la création réussie

### Résultat Attendu
Le QA peut toujours créer des cas de test comme avant.

---

## Test 5 : Cas Limites

### Test 5.1 : Responsable de Projet ET de Tâche
1. Assigner le même utilisateur comme responsable du projet ET de la tâche
2. Vérifier qu'il peut créer des cas de test
3. ✅ Pas de doublon de permissions

### Test 5.2 : Changement de Responsable
1. Créer des cas de test en tant que responsable
2. Changer le responsable de la tâche
3. Vérifier que l'ancien responsable ne peut plus créer
4. Vérifier que le nouveau responsable peut créer

### Test 5.3 : Tâche Sans Responsable
1. Créer une tâche TESTS sans responsable
2. Vérifier que seuls QA, Chef de projet, Admin peuvent créer
3. Assigner un responsable
4. Vérifier que le responsable peut maintenant créer

---

## Checklist Complète

### Permissions de Création

- [ ] Super Admin peut créer
- [ ] QA peut créer
- [ ] Chef de Projet peut créer
- [ ] Créateur du projet peut créer
- [ ] Responsable du projet peut créer ✨ **NOUVEAU**
- [ ] Responsable de la tâche peut créer ✨ **NOUVEAU**
- [ ] Membre simple ne peut PAS créer

### Interface

- [ ] Bouton "Nouveau Cas" visible pour les autorisés
- [ ] Bouton "Nouveau Cas" caché pour les non-autorisés
- [ ] État vide adapté selon les permissions
- [ ] Pas d'erreurs dans la console

### Fonctionnalité

- [ ] Création de cas de test réussie
- [ ] Message de succès affiché
- [ ] Cas de test apparaît dans la liste
- [ ] Créateur correctement enregistré
- [ ] Pas de régression pour les QA

### Sécurité

- [ ] Tentative de création via API refusée pour non-autorisés
- [ ] Message d'erreur approprié
- [ ] Pas de fuite d'information

---

## Commandes Utiles

### Vérifier les Responsables

```python
# Dans le shell Django
from core.models import Projet, TacheEtape

# Vérifier le responsable du projet
projet = Projet.objects.get(id='...')
print(f"Responsable projet: {projet.responsable}")

# Vérifier le responsable de la tâche
tache = TacheEtape.objects.get(id='...')
print(f"Responsable tâche: {tache.responsable}")
```

### Créer un Utilisateur de Test

```python
from core.models import Utilisateur, RoleSysteme

# Créer un utilisateur simple
user = Utilisateur.objects.create_user(
    username='test_responsable',
    email='test@example.com',
    password='test123',
    first_name='Test',
    last_name='Responsable'
)

# Assigner un rôle simple (pas QA, pas Chef de projet)
role = RoleSysteme.objects.get(nom='DEVELOPPEUR')
user.role_systeme = role
user.save()
```

---

## Problèmes Potentiels et Solutions

### Problème : Bouton "Nouveau Cas" toujours caché

**Solution** : Vérifier que :
- L'utilisateur est bien responsable du projet ou de la tâche
- La variable `peut_creer` est correctement calculée dans la vue
- Le template utilise bien `{% if peut_creer %}`

### Problème : Erreur "Permissions insuffisantes"

**Solution** : Vérifier que :
- La logique de permissions dans `creer_cas_test_view` est à jour
- L'utilisateur a bien accès au projet
- La tâche appartient bien à une étape TESTS

### Problème : Responsable ne peut pas créer

**Solution** : Vérifier que :
- Le champ `responsable` est bien renseigné (pas NULL)
- L'utilisateur connecté correspond bien au responsable
- Pas de cache côté navigateur

---

## Résultats Attendus

| Test | Statut | Notes |
|------|--------|-------|
| Test 1 : Responsable Projet | ⏳ | À tester |
| Test 2 : Responsable Tâche | ⏳ | À tester |
| Test 3 : Sans Permission | ⏳ | À tester |
| Test 4 : QA (Régression) | ⏳ | À tester |
| Test 5 : Cas Limites | ⏳ | À tester |

---

## Conclusion

Ces tests garantissent que :
1. Les nouvelles permissions fonctionnent correctement
2. Les permissions existantes sont préservées
3. La sécurité est maintenue
4. L'expérience utilisateur est cohérente
