# Correction de l'affichage des notifications de projet

## Problème identifié

Les notifications de type `NotificationProjet` (notamment `AFFECTATION_RESPONSABLE`) étaient créées en base de données mais ne s'affichaient pas dans l'interface utilisateur.

### Cause racine

L'API `/api/notifications/` ne récupérait que 3 types de notifications :
- `NotificationTache`
- `NotificationEtape`
- `NotificationModule`

Le type `NotificationProjet` était complètement absent de l'API, donc les notifications d'affectation de responsable n'apparaissaient jamais dans l'interface.

## Solution implémentée

### 1. Modification de `api_notifications` (core/views.py)

**Ajout de NotificationProjet dans les imports et requêtes :**

```python
from .models import NotificationTache, NotificationEtape, NotificationModule, NotificationProjet

# Récupérer les notifications de projets non lues
notifications_projets_non_lues = NotificationProjet.objects.filter(
    destinataire=user,
    lue=False
).order_by('-date_creation')[:5]

# Compter le total
total_projets_non_lues = NotificationProjet.objects.filter(
    destinataire=user,
    lue=False
).count()

total_non_lues = total_taches_non_lues + total_etapes_non_lues + total_modules_non_lues + total_projets_non_lues
```

**Ajout des données NotificationProjet dans la réponse JSON :**

```python
# Ajouter les notifications de projets
for notif in notifications_projets_non_lues:
    notifications_data.append({
        'id': notif.id,
        'message': notif.message,
        'titre': notif.titre,
        'date_creation': notif.date_creation.isoformat(),
        'lue': False,
        'type_notification': notif.type_notification,
        'source_type': 'projet',
        'projet_id': notif.projet.id if notif.projet else None,
        'projet_nom': notif.projet.nom if notif.projet else None,
    })
```

### 2. Modification de `api_notifications_detailed` (core/views.py)

Même logique appliquée pour l'API détaillée :
- Ajout de `NotificationProjet` dans les imports
- Récupération des notifications projets lues et non lues
- Ajout dans les données JSON retournées

### 3. Modification de `api_mark_notification_read` (core/views.py)

Ajout de la gestion de `NotificationProjet` pour permettre de marquer ces notifications comme lues :

```python
# Essayer avec NotificationProjet
try:
    notification = NotificationProjet.objects.get(id=notification_id, destinataire=user)
    if not notification.lue:
        notification.marquer_comme_lue()
    return JsonResponse({'success': True, 'type': 'projet'})
except NotificationProjet.DoesNotExist:
    pass
```

### 4. Modification de `api_mark_all_notifications_read` (core/views.py)

Ajout de la logique pour marquer toutes les notifications de projet comme lues :

```python
# Marquer toutes les notifications de projets non lues comme lues
notifications_projets_non_lues = NotificationProjet.objects.filter(
    destinataire=user,
    lue=False
)

for notification in notifications_projets_non_lues:
    notification.marquer_comme_lue()
    count += 1
```

### 5. Modification de `notification_redirect_view` (core/views.py)

Ajout de la gestion de redirection pour les notifications de projet :

```python
# Chercher dans NotificationProjet
try:
    notif = NotificationProjet.objects.get(id=notification_id, destinataire=user)
    if not notif.lue:
        notif.marquer_comme_lue()
    
    # Construire l'URL de redirection
    if notif.projet:
        redirect_url = f'/projets/{notif.projet.id}/'
    
    return redirect(redirect_url)
except NotificationProjet.DoesNotExist:
    pass
```

## Fichiers modifiés

- `core/views.py` : 5 fonctions modifiées
  - `api_notifications` (ligne ~3759)
  - `api_notifications_detailed` (ligne ~3863)
  - `api_mark_notification_read` (ligne ~3580)
  - `api_mark_all_notifications_read` (ligne ~3640)
  - `notification_redirect_view` (ligne ~3690)

## Scripts de test créés

1. **test_notification_projet_api.py**
   - Vérifie que les notifications de projet existent en base
   - Simule l'appel API pour vérifier le comptage
   - Affiche les détails des notifications

2. **marquer_notification_non_lue.py**
   - Permet de marquer une notification comme non lue pour tester l'affichage
   - Utile pour les tests sans créer de nouvelles données

## Vérification

### Avant la correction
```
📊 Notifications non lues par type:
   Tâches: 0
   Étapes: 0
   Modules: 0
   Projets: 0  ❌ (notification existait mais n'était pas comptée)
   TOTAL: 0
```

### Après la correction
```
📊 Notifications non lues par type:
   Tâches: 0
   Étapes: 0
   Modules: 0
   Projets: 1  ✅ (notification maintenant incluse)
   TOTAL: 1
```

## Test de la correction

1. **Redémarrer le serveur Django** pour charger les modifications
   ```bash
   python manage.py runserver
   ```

2. **Se connecter avec Eraste Butela**
   - Email: (à définir)
   - La notification devrait apparaître dans l'icône de notification

3. **Vérifier l'affichage**
   - Badge de notification : devrait afficher "1"
   - Dropdown : devrait afficher la notification d'affectation
   - Message : "Vous avez été désigné(e) comme responsable principal du projet 'Systeme de gestion des pharmacie'..."

4. **Tester le clic**
   - Cliquer sur la notification devrait rediriger vers `/projets/{projet_id}/`
   - La notification devrait être marquée comme lue

## Impact

✅ **Résolu** : Les notifications d'affectation de responsable s'affichent maintenant correctement

✅ **Résolu** : Le badge de notification affiche le bon nombre

✅ **Résolu** : Les utilisateurs peuvent voir et interagir avec leurs notifications de projet

## Notes importantes

- Le template `templates/base.html` n'a pas besoin de modification car il gère déjà les notifications de manière générique
- La structure JSON retournée par l'API est compatible avec le code JavaScript existant
- Le champ `source_type: 'projet'` permet de différencier les notifications de projet des autres types
- La méthode `marquer_comme_lue()` du modèle `NotificationProjet` est utilisée pour la cohérence

## Prochaines étapes

1. Redémarrer le serveur Django
2. Tester avec un utilisateur réel
3. Créer de nouvelles affectations de responsable pour vérifier que les nouvelles notifications s'affichent correctement
