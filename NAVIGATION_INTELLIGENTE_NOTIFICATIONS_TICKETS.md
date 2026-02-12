# Navigation Intelligente : Notifications vers Tickets

## 📅 Date : 12 février 2026

## 🎯 Objectif

Implémenter une navigation intelligente qui permet à l'utilisateur de revenir aux notifications après avoir consulté un ticket depuis une notification.

## 🔄 Flux de Navigation

### Scénario 1 : Depuis une Notification

```
Notifications → Clic sur notification → Détails du ticket → Bouton "Notifications" → Retour aux notifications
```

### Scénario 2 : Navigation Normale

```
Liste des tickets → Clic sur ticket → Détails du ticket → Bouton "Retour" → Retour à la liste
```

## 🔧 Implémentation

### 1. Modification des Notifications

**Fichier** : `core/views_maintenance_v2.py`

**Changement** : Ajout du paramètre `?from=notifications` dans le lien de la notification

#### Dans `creer_ticket_view()` (ligne ~265)

**Avant** :
```python
donnees_contexte={
    'ticket_id': str(ticket.id),
    'ticket_numero': ticket.numero_ticket,
    'lien': f'/projets/{projet.id}/tickets/{ticket.id}/'
}
```

**Après** :
```python
donnees_contexte={
    'ticket_id': str(ticket.id),
    'ticket_numero': ticket.numero_ticket,
    'lien': f'/projets/{projet.id}/tickets/{ticket.id}/?from=notifications'
}
```

#### Dans `assigner_ticket_view()` (ligne ~372)

**Avant** :
```python
donnees_contexte={
    'ticket_id': str(ticket.id),
    'ticket_numero': ticket.numero_ticket,
    'lien': f'/projets/{ticket.projet.id}/tickets/{ticket.id}/'
}
```

**Après** :
```python
donnees_contexte={
    'ticket_id': str(ticket.id),
    'ticket_numero': ticket.numero_ticket,
    'lien': f'/projets/{ticket.projet.id}/tickets/{ticket.id}/?from=notifications'
}
```

### 2. Modification du Template Détails du Ticket

**Fichier** : `templates/core/detail_ticket.html`

**Changement** : Bouton retour intelligent qui détecte le paramètre `from`

**Code ajouté** :
```django
{% if request.GET.from == 'notifications' %}
<a href="{% url 'notifications_taches' %}" 
   class="ml-2 px-3 py-2 md:px-4 text-gray-600 hover:text-gray-900 transition flex items-center text-sm">
    <i class="fas fa-arrow-left mr-1 md:mr-2"></i> <span class="hidden md:inline">Notifications</span>
</a>
{% else %}
<a href="{% url 'gestion_tickets' projet.id %}" 
   class="ml-2 px-3 py-2 md:px-4 text-gray-600 hover:text-gray-900 transition flex items-center text-sm">
    <i class="fas fa-arrow-left mr-1 md:mr-2"></i> <span class="hidden md:inline">Retour</span>
</a>
{% endif %}
```

## 📊 Logique de Détection

### Paramètre URL

**Format** : `?from=notifications`

**Détection** : `request.GET.from == 'notifications'`

### Comportement du Bouton

| Provenance | Paramètre | Texte du bouton | Destination |
|------------|-----------|-----------------|-------------|
| Notification | `?from=notifications` | "Notifications" | `/notifications/taches/` |
| Liste tickets | Aucun | "Retour" | `/projets/{id}/tickets/` |
| Mes tickets | Aucun | "Retour" | `/projets/{id}/tickets/` |
| Tous tickets | Aucun | "Retour" | `/projets/{id}/tickets/` |

## 🎨 Interface

### Bouton "Notifications"

```html
<a href="/notifications/taches/">
    <i class="fas fa-arrow-left"></i> Notifications
</a>
```

**Visible** : Uniquement si `?from=notifications`

### Bouton "Retour"

```html
<a href="/projets/{id}/tickets/">
    <i class="fas fa-arrow-left"></i> Retour
</a>
```

**Visible** : Par défaut (sans paramètre)

## 🔍 Exemple de Flux Complet

### Étape 1 : Création de la Notification

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

### Étape 2 : Utilisateur Clique sur la Notification

**URL générée** : `/projets/abc-123/tickets/def-456/?from=notifications`

### Étape 3 : Page Détails du Ticket

**Détection** : `request.GET.from == 'notifications'` → `True`

**Bouton affiché** : "Notifications" pointant vers `/notifications/taches/`

### Étape 4 : Utilisateur Clique sur "Notifications"

**Redirection** : Retour à la page des notifications

## ✅ Avantages

1. **UX Améliorée** : L'utilisateur revient là où il était
2. **Navigation Intuitive** : Pas de perte de contexte
3. **Flexible** : Fonctionne pour tous les types de navigation
4. **Simple** : Un seul paramètre URL suffit
5. **Rétrocompatible** : Les liens sans paramètre fonctionnent toujours

## 🔐 Sécurité

### Validation du Paramètre

Le paramètre `from` est simplement lu, pas exécuté :
```python
request.GET.from == 'notifications'  # Comparaison de chaîne sûre
```

### Pas de Risque

- ✅ Pas d'injection SQL (lecture simple)
- ✅ Pas d'XSS (pas d'affichage du paramètre)
- ✅ Pas de redirection arbitraire (URLs codées en dur)

## 📱 Responsive

### Mobile

**Bouton "Notifications"** :
```
[←] (icône uniquement)
```

### Desktop

**Bouton "Notifications"** :
```
[← Notifications]
```

**CSS** :
```html
<span class="hidden md:inline">Notifications</span>
```

## 🧪 Tests à Effectuer

### Test 1 : Navigation depuis Notification

1. Créer un ticket et assigner un développeur
2. Le développeur reçoit une notification
3. Cliquer sur la notification
4. Vérifier l'URL : `?from=notifications` présent
5. Vérifier le bouton : "Notifications" affiché
6. Cliquer sur "Notifications"
7. Vérifier : Retour à la page des notifications

### Test 2 : Navigation Normale

1. Aller dans "Mes tickets"
2. Cliquer sur un ticket
3. Vérifier l'URL : Pas de paramètre `from`
4. Vérifier le bouton : "Retour" affiché
5. Cliquer sur "Retour"
6. Vérifier : Retour à la liste des tickets

### Test 3 : Navigation Directe

1. Copier l'URL d'un ticket avec `?from=notifications`
2. Coller dans le navigateur
3. Vérifier : Bouton "Notifications" affiché
4. Cliquer sur "Notifications"
5. Vérifier : Redirection vers notifications

## 📝 Notes Techniques

### Paramètre GET

**Lecture** :
```python
request.GET.from  # Retourne la valeur ou None
request.GET.get('from')  # Alternative
```

**Comparaison** :
```django
{% if request.GET.from == 'notifications' %}
```

### URL avec Paramètre

**Format** : `base_url?param=value`

**Exemple** : `/projets/abc/tickets/def/?from=notifications`

### Préservation du Paramètre

Le paramètre est automatiquement préservé dans l'URL tant qu'on ne change pas de page.

## 🎯 Résultat Final

Une navigation intelligente qui :
- ✅ Détecte la provenance de l'utilisateur
- ✅ Adapte le bouton retour en conséquence
- ✅ Améliore l'expérience utilisateur
- ✅ Maintient le contexte de navigation
- ✅ Fonctionne sur mobile et desktop

## 🚀 Extension Possible

Cette approche peut être étendue à d'autres contextes :

```python
# Depuis un projet
'lien': f'/tickets/{id}/?from=projet&projet_id={projet.id}'

# Depuis un module
'lien': f'/tickets/{id}/?from=module&module_id={module.id}'

# Depuis un dashboard
'lien': f'/tickets/{id}/?from=dashboard'
```

Le template peut alors gérer plusieurs cas :
```django
{% if request.GET.from == 'notifications' %}
    <!-- Retour notifications -->
{% elif request.GET.from == 'projet' %}
    <!-- Retour projet -->
{% elif request.GET.from == 'module' %}
    <!-- Retour module -->
{% else %}
    <!-- Retour par défaut -->
{% endif %}
```

