# Correction : Erreur AttributeError 'Projet' object has no attribute 'responsable'

## Problème

Lors de l'accès à l'interface des cas de test, une erreur `AttributeError` se produisait :

```
AttributeError: 'Projet' object has no attribute 'responsable'
```

**Ligne concernée** : `core/views_tests.py`, ligne 64

```python
projet.responsable == user or
```

## Cause

Le modèle `Projet` n'a pas d'attribut direct `responsable`. Au lieu de cela, il utilise une méthode `get_responsable_principal()` qui retourne le responsable principal via les affectations.

### Structure du Modèle Projet

```python
class Projet(models.Model):
    # ... autres champs ...
    createur = models.ForeignKey(Utilisateur, ...)
    
    def get_responsable_principal(self):
        """Retourne le responsable principal du projet"""
        affectation = self.affectations.filter(
            est_responsable_principal=True, 
            date_fin__isnull=True
        ).first()
        if affectation:
            return affectation.utilisateur
        return None
```

## Solution

Utiliser la méthode `get_responsable_principal()` au lieu d'accéder directement à un attribut `responsable`.

### Correction 1 : Vue `gestion_cas_tests_tache_view`

**Avant** :
```python
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    projet.responsable == user or
    tache.responsable == user
)
```

**Après** :
```python
responsable_projet = projet.get_responsable_principal()
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache.responsable == user
)
```

### Correction 2 : Vue `creer_cas_test_view`

**Avant** :
```python
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    projet.responsable == user or
    tache_etape.responsable == user
)
```

**Après** :
```python
responsable_projet = projet.get_responsable_principal()
peut_creer = (
    ServiceTests._peut_creer_tests(user, projet) or
    (responsable_projet and responsable_projet == user) or
    tache_etape.responsable == user
)
```

## Détails de la Correction

### Vérification de Sécurité

La condition `(responsable_projet and responsable_projet == user)` vérifie :
1. Que `responsable_projet` n'est pas `None` (projet a un responsable)
2. Que le responsable correspond à l'utilisateur actuel

### Gestion du Cas `None`

Si le projet n'a pas de responsable principal :
- `get_responsable_principal()` retourne `None`
- La condition `(responsable_projet and ...)` évalue à `False`
- Les autres permissions sont vérifiées normalement

## Impact

### Fonctionnalité Préservée

- Les responsables de projet peuvent toujours créer des cas de test
- Les responsables de tâche peuvent toujours créer des cas de test
- Les autres permissions (QA, Chef de projet, Admin) fonctionnent normalement

### Robustesse Améliorée

- Gestion correcte des projets sans responsable
- Pas d'erreur si le responsable n'est pas défini
- Code aligné avec la structure du modèle

## Tests de Vérification

### Test 1 : Projet avec Responsable

1. Assigner un responsable principal à un projet
2. Se connecter avec ce responsable
3. Accéder aux cas de test d'une tâche
4. ✅ Vérifier que le bouton "Nouveau Cas" est visible
5. ✅ Vérifier qu'aucune erreur ne se produit

### Test 2 : Projet sans Responsable

1. Créer un projet sans responsable principal
2. Se connecter avec un utilisateur QA
3. Accéder aux cas de test d'une tâche
4. ✅ Vérifier que le bouton "Nouveau Cas" est visible (QA)
5. ✅ Vérifier qu'aucune erreur ne se produit

### Test 3 : Responsable de Tâche

1. Assigner un utilisateur comme responsable de tâche
2. Se connecter avec cet utilisateur
3. Accéder aux cas de test via "Mes Tâches"
4. ✅ Vérifier que le bouton "Nouveau Cas" est visible
5. ✅ Vérifier qu'aucune erreur ne se produit

## Fichiers Modifiés

| Fichier | Fonction | Lignes |
|---------|----------|--------|
| `core/views_tests.py` | `gestion_cas_tests_tache_view` | ~60-67 |
| `core/views_tests.py` | `creer_cas_test_view` | ~97-106 |

## Code Complet Corrigé

### Vue `gestion_cas_tests_tache_view`

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

### Vue `creer_cas_test_view`

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

## Leçons Apprises

### Toujours Vérifier la Structure du Modèle

Avant d'accéder à un attribut, vérifier :
1. Que l'attribut existe dans le modèle
2. S'il s'agit d'un champ direct ou d'une méthode
3. Si la méthode peut retourner `None`

### Pattern de Vérification Sécurisée

```python
# ❌ Mauvais : Accès direct sans vérification
if objet.attribut == valeur:
    ...

# ✅ Bon : Utilisation de méthode avec vérification None
attribut = objet.get_attribut()
if attribut and attribut == valeur:
    ...
```

## Statut

✅ **Corrigé**
✅ **Testé**
✅ **Documenté**

## Conclusion

L'erreur a été corrigée en utilisant la méthode `get_responsable_principal()` au lieu d'accéder directement à un attribut inexistant. La fonctionnalité de permissions pour les responsables de projet fonctionne maintenant correctement.
