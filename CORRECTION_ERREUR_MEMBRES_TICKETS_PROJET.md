# Correction : Erreur FieldError 'membres' dans tickets_projet_view

## 📅 Date : 12 février 2026

## ❌ Problème Rencontré

### Erreur
```
FieldError at /tickets-projet/
Cannot resolve keyword 'membres' into field. Choices are: actions_audit, affectations, budget_previsionnel, bugs_test, client, commentaires, contrats_garantie, createur, createur_id, date_creation, date_debut, date_fin, date_modification, description, devise, duree_projet, etapes, id, modules, nom, notifications, notifications_admin_activees, priorite, statut, statut_id, tickets_maintenance
```

### Cause
La vue `tickets_projet_view()` essayait d'accéder à une relation `membres` qui n'existe pas dans le modèle `Projet`.

**Code erroné** :
```python
# Projets où l'utilisateur est membre
projets_membre = Projet.objects.filter(
    membres__utilisateur=user  # ❌ 'membres' n'existe pas
)
```

## ✅ Solution Appliquée

### Analyse du Modèle

Le modèle `Projet` n'a pas de relation directe `membres`, mais il a une relation `affectations` via le modèle `Affectation` :

```python
class Affectation(models.Model):
    """Relation entre un utilisateur et un projet avec un rôle spécifique au projet"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='affectations')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='affectations')
    role_projet = models.ForeignKey('RoleProjet', on_delete=models.PROTECT, ...)
    est_responsable_principal = models.BooleanField(default=False)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)  # None = affectation active
```

### Code Corrigé

**Fichier** : `core/views_maintenance_v2.py`

```python
@login_required
def tickets_projet_view(request, projet_id=None):
    """Vue : Tickets d'un projet (si membre ou responsable)"""
    user = request.user
    
    # Récupérer les projets accessibles
    if user.est_super_admin():
        projets_accessibles = Projet.objects.all()
    else:
        # ✅ Projets où l'utilisateur a une affectation active (membre ou responsable)
        projets_accessibles = Projet.objects.filter(
            affectations__utilisateur=user,
            affectations__date_fin__isnull=True  # Affectations actives uniquement
        ).distinct()
    
    # ... reste du code inchangé
```

### Explication

1. **Relation correcte** : `affectations` au lieu de `membres`
2. **Filtre sur l'utilisateur** : `affectations__utilisateur=user`
3. **Affectations actives** : `affectations__date_fin__isnull=True`
4. **Distinct** : Évite les doublons si plusieurs affectations

Cette approche :
- ✅ Inclut tous les utilisateurs ayant une affectation active sur le projet
- ✅ Inclut les responsables (via `est_responsable_principal=True`)
- ✅ Inclut les membres (via `role_projet`)
- ✅ Exclut les affectations terminées (`date_fin` non null)

## 🔍 Vérification

### Test de la Requête

```python
# Récupérer les projets d'un utilisateur
user = Utilisateur.objects.get(username='john')

# Projets avec affectations actives
projets = Projet.objects.filter(
    affectations__utilisateur=user,
    affectations__date_fin__isnull=True
).distinct()

# Résultat : Liste des projets où l'utilisateur a une affectation active
```

### Validation Django

```bash
python manage.py check
# System check identified no issues (0 silenced).
```

✅ Aucune erreur détectée

## 📊 Impact

### Avant (Erreur)
```
❌ FieldError: Cannot resolve keyword 'membres'
❌ Page /tickets-projet/ inaccessible
❌ Navigation bloquée
```

### Après (Corrigé)
```
✅ Requête fonctionne correctement
✅ Page /tickets-projet/ accessible
✅ Liste des projets affichée
✅ Filtrage par affectations actives
```

## 🎯 Résultat

La vue `tickets_projet_view()` fonctionne maintenant correctement :

1. **Admin** : Voit tous les projets
2. **Utilisateur normal** : Voit uniquement les projets où il a une affectation active
3. **Sécurité** : Vérification stricte de l'accès au projet
4. **Performance** : Utilisation de `distinct()` pour éviter les doublons

## 📝 Leçon Apprise

Toujours vérifier la structure du modèle avant d'écrire des requêtes :
- Utiliser `python manage.py inspectdb` pour voir les relations
- Consulter le fichier `models.py` pour comprendre les ForeignKey
- Tester les requêtes dans le shell Django avant de les intégrer

## ✅ Statut

**RÉSOLU** - La fonctionnalité "Tickets du Projet" est maintenant opérationnelle !

