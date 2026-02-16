# Guide: Créer de Nouveaux Templates d'Email

## Introduction

Ce guide explique comment créer de nouveaux templates d'email professionnels pour SI-Gouvernance en utilisant le système de templates HTML mis en place.

## Structure de Base

Tous les templates d'email héritent de `templates/emails/base_email.html` qui fournit:
- Header avec logo
- Footer avec copyright
- Style CSS professionnel
- Responsive design

## Étapes de Création

### 1. Créer le Fichier Template

Créez un nouveau fichier dans `templates/emails/` avec un nom descriptif:

```
templates/emails/notification_[type].html
```

Exemples:
- `notification_tache_terminee.html`
- `notification_budget_depasse.html`
- `notification_nouveau_membre.html`

### 2. Structure du Template

```html
{% extends "emails/base_email.html" %}

{% block title %}Titre de l'Email - SI-Gouvernance{% endblock %}

{% block header_title %}Titre Principal{% endblock %}
{% block header_subtitle %}Sous-titre descriptif{% endblock %}

{% block content %}
<!-- Votre contenu ici -->
{% endblock %}
```

### 3. Éléments Disponibles

#### a) Salutation
```html
<div class="greeting">
    Bonjour {{ destinataire_nom }},
</div>
```

#### b) Message Principal
```html
<div class="message-content">
    <p>Votre message principal ici...</p>
</div>
```

#### c) Carte d'Information
```html
<div class="info-card">
    <div class="info-card-title">
        <span class="info-card-icon">📋</span>
        Titre de la Carte
    </div>
    <ul class="info-list">
        <li class="info-item">
            <span class="info-label">Label:</span>
            <span class="info-value">{{ valeur }}</span>
        </li>
        <!-- Plus d'items... -->
    </ul>
</div>
```

#### d) Bouton d'Action
```html
<div class="action-button-container">
    <a href="{{ url_action }}" class="action-button">
        🚀 Texte du Bouton
    </a>
</div>
```

#### e) Alertes

**Alerte Info (bleue)**:
```html
<div class="alert-box alert-box-info">
    <div class="alert-title">💡 Titre</div>
    <div class="alert-message">
        Message d'information...
    </div>
</div>
```

**Alerte Warning (jaune)**:
```html
<div class="alert-box alert-box-warning">
    <div class="alert-title">⚠️ Attention</div>
    <div class="alert-message">
        Message d'avertissement...
    </div>
</div>
```

**Alerte Success (verte)**:
```html
<div class="alert-box alert-box-success">
    <div class="alert-title">✅ Succès</div>
    <div class="alert-message">
        Message de succès...
    </div>
</div>
```

#### f) Signature
```html
<div class="message-content">
    <p style="margin-top: 20px;">
        Cordialement,<br>
        <strong>L'équipe SI-Gouvernance</strong>
    </p>
</div>
```

## Exemple Complet

### Template: `notification_tache_terminee.html`

```html
{% extends "emails/base_email.html" %}

{% block title %}Tâche Terminée - SI-Gouvernance{% endblock %}

{% block header_title %}Tâche Terminée{% endblock %}
{% block header_subtitle %}Une tâche a été complétée{% endblock %}

{% block content %}
<div class="greeting">
    Bonjour {{ destinataire_nom }},
</div>

<div class="message-content">
    <p>La tâche <strong>{{ tache_nom }}</strong> a été marquée comme terminée.</p>
</div>

<div class="info-card">
    <div class="info-card-title">
        <span class="info-card-icon">✅</span>
        Détails de la Tâche
    </div>
    <ul class="info-list">
        <li class="info-item">
            <span class="info-label">Tâche:</span>
            <span class="info-value"><strong>{{ tache_nom }}</strong></span>
        </li>
        <li class="info-item">
            <span class="info-label">Projet:</span>
            <span class="info-value">{{ projet_nom }}</span>
        </li>
        <li class="info-item">
            <span class="info-label">Complétée par:</span>
            <span class="info-value">{{ complete_par }}</span>
        </li>
        <li class="info-item">
            <span class="info-label">Date:</span>
            <span class="info-value">{{ date_completion }}</span>
        </li>
    </ul>
</div>

<div class="action-button-container">
    <a href="{{ tache_url }}" class="action-button">
        👁️ Voir la Tâche
    </a>
</div>

<div class="alert-box alert-box-success">
    <div class="alert-title">✅ Félicitations</div>
    <div class="alert-message">
        Cette tâche a été complétée avec succès. Merci pour votre travail !
    </div>
</div>

<div class="message-content">
    <p style="margin-top: 20px;">
        Cordialement,<br>
        <strong>L'équipe SI-Gouvernance</strong>
    </p>
</div>
{% endblock %}
```

## Intégration dans le Code

### 1. Ajouter le Contexte dans `utils_notifications_email.py`

Dans la fonction `preparer_email_context`, ajoutez un nouveau cas:

```python
elif type_model == 'tache_terminee':
    tache = notification.tache
    projet = tache.etape.projet if hasattr(tache, 'etape') else tache.module.projet
    
    context.update({
        'tache_nom': tache.nom,
        'projet_nom': projet.nom,
        'complete_par': notification.emetteur.get_full_name() if notification.emetteur else 'Système',
        'date_completion': notification.date_creation.strftime('%d/%m/%Y à %H:%M'),
        'tache_url': f"{base_url}/projets/{projet.id}/",
    })
    
    sujet = f"[SI-Gouvernance] Tâche Terminée: {tache.nom}"
    template_name = 'emails/notification_tache_terminee.html'
```

### 2. Créer une Fonction d'Envoi (Optionnel)

```python
def envoyer_email_tache_terminee(notification, request=None):
    """Envoie un email pour une tâche terminée"""
    return envoyer_email_notification(notification, 'tache_terminee', request)
```

## Variables de Contexte Disponibles

### Variables Communes (Toujours Disponibles)
- `destinataire_nom` - Nom complet du destinataire
- `date_notification` - Date formatée (dd/mm/yyyy à HH:MM)
- `base_url` - URL de base de l'application
- `logo_url` - URL complète du logo
- `site_name` - "SI-Gouvernance"

### Variables Spécifiques par Type

Ajoutez vos propres variables selon le type de notification:
- Informations du projet
- Informations de la tâche
- Informations de l'utilisateur
- Dates et échéances
- URLs d'action
- Etc.

## Bonnes Pratiques

### 1. Nommage
- Utilisez des noms descriptifs: `notification_[action]_[objet].html`
- Exemples: `notification_assignation_tache.html`, `notification_alerte_budget.html`

### 2. Icônes
Utilisez des emojis pour rendre les emails plus visuels:
- 📋 Informations générales
- ✅ Succès, validation
- ⚠️ Avertissement
- 🚀 Action, démarrage
- 💡 Conseil, astuce
- 🔒 Sécurité
- 📊 Statistiques
- 👤 Utilisateur
- 📧 Email
- ⏰ Temps, échéance

### 3. Structure
- Commencez toujours par une salutation
- Utilisez des cartes pour les informations structurées
- Ajoutez un bouton d'action principal
- Terminez par une signature

### 4. Responsive
- Le template de base est déjà responsive
- Évitez les largeurs fixes
- Utilisez les classes fournies

### 5. Texte Alternatif
Fournissez toujours un message texte (fallback) dans la fonction d'envoi.

## Test

### 1. Créer un Script de Test

```python
# test_nouveau_template.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

# Préparer le contexte
context = {
    'destinataire_nom': 'Test User',
    'tache_nom': 'Tâche de Test',
    'projet_nom': 'Projet Test',
    'complete_par': 'Admin',
    'date_completion': '16/02/2026 à 14:30',
    'tache_url': 'http://localhost:8000/projets/123/',
    'base_url': 'http://localhost:8000',
    'logo_url': 'http://localhost:8000/media/logos/jconsult_logo.png',
}

# Générer le HTML
message_html = render_to_string('emails/notification_tache_terminee.html', context)

# Envoyer l'email de test
email = EmailMultiAlternatives(
    subject='[TEST] Tâche Terminée',
    body='Version texte...',
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['votre-email@example.com'],
)

email.attach_alternative(message_html, "text/html")
email.send()

print("✅ Email de test envoyé!")
```

### 2. Exécuter le Test

```bash
docker-compose exec web python test_nouveau_template.py
```

## Dépannage

### Le logo ne s'affiche pas
- Vérifiez que le fichier existe: `media/logos/jconsult_logo.png`
- Vérifiez l'URL complète dans le contexte
- Assurez-vous que le serveur web sert les fichiers media

### Le style ne s'applique pas
- Le CSS est inline dans `base_email.html`
- Vérifiez que vous héritez bien de `base_email.html`
- Utilisez les classes fournies

### L'email n'est pas responsive
- Le template de base gère le responsive
- Évitez d'ajouter des styles qui cassent le responsive
- Testez sur mobile

## Ressources

### Fichiers de Référence
- `templates/emails/base_email.html` - Template de base
- `templates/emails/notification_responsable_projet.html` - Exemple complet
- `core/utils_notifications_email.py` - Logique d'envoi
- `test_email_professionnel.py` - Exemples de tests

### Documentation
- `AMELIORATION_EMAILS_PROFESSIONNELS.md` - Documentation complète
- `SESSION_2026_02_16_EMAILS_PROFESSIONNELS.md` - Détails de l'implémentation

## Support

Pour toute question:
1. Consultez les templates existants
2. Vérifiez la documentation
3. Testez avec le script de test
4. Contactez l'équipe de développement

---

**Date**: 16 février 2026  
**Version**: 1.0  
**Auteur**: Équipe SI-Gouvernance
