# Correction : Redirection des Notifications vers les Tickets

## 📅 Date : 12 février 2026

## ❌ Problème Rencontré

### Symptôme
Lorsqu'un utilisateur clique sur une notification de ticket de maintenance, il est redirigé vers la page de détails du projet au lieu de la page de détails du ticket.

### Cause
La vue `notification_redirect_view()` dans `core/views.py` ne prenait pas en compte le champ `lien` dans `donnees_contexte` pour les `NotificationProjet`. Elle redirigait systématiquement vers `/projets/{projet.id}/`.

### Code Problématique

**Fichier** : `core/views.py` (ligne ~4080)

```python
# Chercher dans NotificationProjet
try:
    notif = NotificationProjet.objects.get(id=notification_id, destinataire=user)
    if not notif.lue:
        notif.marquer_comme_lue()
    
    # ❌ PROBLÈME : Ignore le lien dans donnees_contexte
    if notif.projet:
        redirect_url = f'/projets/{notif.projet.id}/'
    
    return redirect(redirect_url)
except NotificationProjet.DoesNotExist:
    pass
```

## ✅ Solution Appliquée

### Modification de la Vue

**Fichier** : `core/views.py`

**Code corrigé** :
```python
# Chercher dans NotificationProjet
try:
    notif = NotificationProjet.objects.get(id=notification_id, destinataire=user)
    if not notif.lue:
        notif.marquer_comme_lue()
    
    # ✅ SOLUTION : Utiliser le lien dans donnees_contexte si disponible
    if notif.donnees_contexte and 'lien' in notif.donnees_contexte:
        redirect_url = notif.donnees_contexte['lien']
    elif notif.projet:
        # Fallback vers la page du projet
        redirect_url = f'/projets/{notif.projet.id}/'
    
    return redirect(redirect_url)
except NotificationProjet.DoesNotExist:
    pass
```

### Logique de Redirection

1. **Priorité 1** : Utiliser le lien dans `donnees_contexte['lien']` si disponible
2. **Priorité 2** : Fallback vers la page du projet si pas de lien spécifique

## 🔄 Flux Complet

### Création de la Notification

**Dans** : `core/views_maintenance_v2.py`

```python
NotificationProjet.objects.create(
    destinataire=dev,
    projet=projet,
    type_notification='ASSIGNATION_TICKET_MAINTENANCE',
    titre=f'Ticket de maintenance {ticket.numero_ticket}',
    message=f'Vous avez été assigné au ticket...',
    emetteur=user,
    donnees_contexte={
        'ticket_id': str(ticket.id),
        'ticket_numero': ticket.numero_ticket,
        'lien': f'/projets/{projet.id}/tickets/{ticket.id}/?from=notifications'
    }
)
```

### Clic sur la Notification

**URL appelée** : `/notifications/{notification_id}/redirect/`

**Vue** : `notification_redirect_view()`

**Traitement** :
1. Récupère la notification
2. Marque comme lue
3. Lit `donnees_contexte['lien']`
4. Redirige vers le lien : `/projets/{projet_id}/tickets/{ticket_id}/?from=notifications`

### Affichage du Ticket

**Template** : `templates/core/detail_ticket.html`

**Détection** : `request.GET.from == 'notifications'`

**Bouton** : "Notifications" pointant vers `/notifications/taches/`

## 📊 Comparaison Avant/Après

### Avant (Problème)

```
Notification → Clic → notification_redirect_view()
                      ↓
                      Ignore donnees_contexte['lien']
                      ↓
                      Redirige vers /projets/{id}/
                      ↓
                      ❌ Page du projet (incorrect)
```

### Après (Corrigé)

```
Notification → Clic → notification_redirect_view()
                      ↓
                      Lit donnees_contexte['lien']
                      ↓
                      Redirige vers /projets/{id}/tickets/{ticket_id}/?from=notifications
                      ↓
                      ✅ Page du ticket (correct)
                      ↓
                      Bouton "Notifications" affiché
```

## 🎯 Types de Notifications Concernées

Cette correction affecte toutes les `NotificationProjet` qui ont un lien personnalisé dans `donnees_contexte` :

### 1. Assignation de Ticket

**Type** : `ASSIGNATION_TICKET_MAINTENANCE`

**Lien** : `/projets/{projet_id}/tickets/{ticket_id}/?from=notifications`

**Destination** : Détails du ticket

### 2. Autres Notifications Projet (Futures)

Toute notification de type `NotificationProjet` peut maintenant utiliser un lien personnalisé :

```python
NotificationProjet.objects.create(
    destinataire=user,
    projet=projet,
    type_notification='CUSTOM_TYPE',
    titre='Titre',
    message='Message',
    donnees_contexte={
        'lien': '/custom/url/'  # ✅ Sera utilisé pour la redirection
    }
)
```

## 🔍 Vérification

### Test 1 : Notification avec Lien Personnalisé

**Données** :
```python
donnees_contexte = {
    'lien': '/projets/abc/tickets/def/?from=notifications'
}
```

**Résultat** : ✅ Redirige vers `/projets/abc/tickets/def/?from=notifications`

### Test 2 : Notification sans Lien (Fallback)

**Données** :
```python
donnees_contexte = {}  # Pas de lien
```

**Résultat** : ✅ Redirige vers `/projets/{projet.id}/` (fallback)

### Test 3 : Notification sans donnees_contexte

**Données** :
```python
donnees_contexte = None
```

**Résultat** : ✅ Redirige vers `/projets/{projet.id}/` (fallback)

## 📝 Notes Techniques

### Vérification de l'Existence du Lien

```python
if notif.donnees_contexte and 'lien' in notif.donnees_contexte:
    # Utiliser le lien personnalisé
    redirect_url = notif.donnees_contexte['lien']
```

**Sécurité** :
- ✅ Vérifie que `donnees_contexte` n'est pas `None`
- ✅ Vérifie que la clé `'lien'` existe
- ✅ Pas de risque de `KeyError`

### Fallback Robuste

```python
elif notif.projet:
    # Fallback vers la page du projet
    redirect_url = f'/projets/{notif.projet.id}/'
```

**Avantages** :
- ✅ Toujours une destination valide
- ✅ Pas de redirection vers une page d'erreur
- ✅ Rétrocompatible avec les anciennes notifications

## ✅ Résultat Final

### Comportement Corrigé

1. **Notification de ticket** → Clic → **Détails du ticket** ✅
2. **Paramètre `?from=notifications`** → Bouton "Notifications" affiché ✅
3. **Clic sur "Notifications"** → Retour aux notifications ✅

### Flux Complet Fonctionnel

```
Notifications
    ↓ (clic sur notification ticket)
Détails du ticket (?from=notifications)
    ↓ (bouton "Notifications")
Retour aux notifications
```

## 🎉 Conclusion

La correction permet maintenant aux notifications de tickets de rediriger correctement vers les détails du ticket au lieu de la page du projet. Le système de navigation intelligente fonctionne de bout en bout.

## 📁 Fichiers Modifiés

1. **core/views.py** (ligne ~4080)
   - Modification de `notification_redirect_view()`
   - Ajout de la lecture de `donnees_contexte['lien']`
   - Ajout du fallback vers la page du projet

## 🚀 Extension Possible

Cette approche peut être utilisée pour d'autres types de notifications :

```python
# Notification vers un module
NotificationProjet.objects.create(
    donnees_contexte={
        'lien': f'/projets/{projet.id}/modules/{module.id}/?from=notifications'
    }
)

# Notification vers une étape
NotificationProjet.objects.create(
    donnees_contexte={
        'lien': f'/projets/{projet.id}/etapes/{etape.id}/?from=notifications'
    }
)

# Notification vers un déploiement
NotificationProjet.objects.create(
    donnees_contexte={
        'lien': f'/projets/{projet.id}/deploiements/{deploiement.id}/?from=notifications'
    }
)
```

Toutes ces notifications utiliseront automatiquement le lien personnalisé !

