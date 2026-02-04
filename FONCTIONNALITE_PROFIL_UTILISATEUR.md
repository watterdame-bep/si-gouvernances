# Fonctionnalité Profil Utilisateur avec Notification Email

## Vue d'ensemble

Cette fonctionnalité permet aux utilisateurs (sauf administrateurs) de consulter et modifier leurs informations personnelles, notamment leur mot de passe, via une interface moderne et sécurisée. **Nouveauté : Notification automatique par email lors du changement de mot de passe.**

## Fonctionnalités implémentées

### 1. **Page de Profil (`/profil/`)**
- **Accès** : Utilisateurs connectés (sauf administrateurs)
- **Fonctionnalités** :
  - Affichage des informations personnelles du compte
  - **🆕 Affichage des informations du profil RH (membre)** si associé
  - Statistiques personnelles (projets, tâches)
  - Modification des informations de base du compte
  - Changement de mot de passe sécurisé
  - **🆕 Notification email automatique** lors du changement de mot de passe
  - Affichage des projets récents

### 2. **Informations Affichées**

#### **Informations du compte (modifiables)**
- ✅ Prénom et nom (du compte utilisateur)
- ✅ Email (non modifiable)
- ✅ Numéro de téléphone
- ✅ Rôle système
- ✅ Mot de passe (avec validation sécurisée + notification email)

#### **🆕 Informations du profil RH (lecture seule)**
- ✅ **Nom complet** (du profil membre)
- ✅ **Email personnel** (différent de l'email du compte)
- ✅ **Téléphones** (personnel et d'urgence)
- ✅ **Adresse complète**
- ✅ **Informations professionnelles** :
  - Poste/Fonction
  - Département
  - Niveau d'expérience
  - Date d'embauche
- ✅ **Compétences techniques** (si renseignées)
- ✅ **Spécialités** (si renseignées)
- ✅ **Gestion des cas sans profil RH** avec message informatif

### 3. **Sécurité et Validation**
- Vérification de l'ancien mot de passe avant changement
- Validation de la complexité du nouveau mot de passe (minimum 8 caractères)
- Confirmation du nouveau mot de passe
- **🆕 Notification email automatique** avec détails de sécurité
- Audit complet de toutes les modifications
- Déconnexion automatique après changement de mot de passe

## 🆕 Affichage des Informations du Membre (Profil RH)

### Fonctionnement
La page de profil affiche maintenant deux sections distinctes :

1. **Informations du compte** (modifiables par l'utilisateur)
   - Prénom/nom du compte utilisateur
   - Email du compte (non modifiable)
   - Téléphone du compte
   - Rôle système

2. **🆕 Profil RH** (lecture seule, géré par les RH)
   - Nom complet du membre
   - Email personnel (peut être différent du compte)
   - Téléphones (personnel et d'urgence)
   - Adresse complète
   - Informations professionnelles (poste, département, expérience)
   - Compétences techniques et spécialités

### Gestion des cas
- **Avec profil RH** : Affichage complet des informations membre
- **Sans profil RH** : Message informatif expliquant l'absence de profil
- **Informations manquantes** : Affichage "Non renseigné" pour les champs vides

### Avantages
- ✅ **Vue unifiée** : Toutes les informations personnelles en un seul endroit
- ✅ **Séparation claire** : Distinction entre compte système et profil RH
- ✅ **Sécurité** : Informations RH en lecture seule pour l'utilisateur
- ✅ **Flexibilité** : Fonctionne avec ou sans profil RH associé

## 🆕 Notification Email de Sécurité

### Fonctionnement de l'email
Lorsqu'un utilisateur change son mot de passe :
1. **Validation** des données (ancien/nouveau mot de passe)
2. **Changement** du mot de passe dans la base de données
3. **Envoi automatique** d'un email de notification
4. **Audit** de l'action (succès/échec d'envoi)
5. **Déconnexion** automatique pour sécurité

### Contenu de l'email
L'email de notification contient :
- ✅ **Confirmation** du changement de mot de passe
- ✅ **Date et heure** précises de la modification
- ✅ **Adresse IP** de l'utilisateur
- ✅ **Informations du navigateur** utilisé
- ✅ **Conseils de sécurité** personnalisés
- ✅ **Alerte** en cas de modification non autorisée
- ✅ **Design moderne** responsive (HTML + texte brut)

### Template Email
- **Fichier** : `templates/emails/changement_mot_de_passe.html`
- **Design** : Moderne avec glassmorphism et responsive
- **Contenu** : Sécurisé avec toutes les informations nécessaires
- **Fallback** : Version texte brut incluse

## Configuration Email

### Variables d'environnement (.env)
```bash
# Configuration Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=SI-Gouvernance <noreply@si-gouvernance.com>
```

### Modes de fonctionnement
1. **Développement** : `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
   - Emails affichés dans la console
   - Pas d'envoi réel
   
2. **Production** : `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
   - Envoi réel via SMTP
   - Configuration serveur requise

### Fournisseurs supportés
- ✅ **Gmail** (avec mot de passe d'application)
- ✅ **Outlook/Hotmail**
- ✅ **Yahoo Mail**
- ✅ **Serveurs SMTP personnalisés**

## Architecture technique

### Nouvelles fonctions ajoutées
```python
# core/utils.py
def envoyer_notification_changement_mot_de_passe(utilisateur, request=None):
    """Envoie une notification par email lors du changement de mot de passe"""
```

### Vue modifiée
```python
# core/views.py
@login_required
@require_http_methods(["POST"])
def changer_mot_de_passe_view(request):
    """Changement du mot de passe utilisateur avec notification par email"""
    # ... validation ...
    # Changer le mot de passe
    user.set_password(nouveau_mot_de_passe)
    user.save()
    
    # 🆕 Envoyer la notification par email
    email_envoye = envoyer_notification_changement_mot_de_passe(user, request)
```

### Gestion des erreurs email
- **Succès** : Message confirmant l'envoi
- **Échec** : Message d'avertissement + audit de l'erreur
- **Graceful degradation** : Le changement de mot de passe fonctionne même si l'email échoue

## Interface utilisateur améliorée

### Feedback utilisateur
- ✅ **Message principal** : Confirmation du changement
- ✅ **Message secondaire** : Statut de l'envoi d'email
- ✅ **Types de messages** : Succès, erreur, avertissement, info
- ✅ **Délai de redirection** : Augmenté à 3 secondes pour lire les messages

### Nouveaux types de notifications
```javascript
// Types de messages supportés
- 'success' : Vert avec ✅
- 'error'   : Rouge avec ❌  
- 'warning' : Orange avec ⚠️
- 'info'    : Bleu avec 📧
```

## Sécurité renforcée

### Audit complet
Nouveaux types d'audit ajoutés :
- `CHANGEMENT_MOT_DE_PASSE` : Changement réussi
- `TENTATIVE_CHANGEMENT_MOT_DE_PASSE_ECHOUEE` : Tentative échouée
- `ERREUR_NOTIFICATION_EMAIL` : Échec d'envoi d'email
- `ERREUR_CHANGEMENT_MOT_DE_PASSE` : Erreur technique

### Informations de sécurité dans l'email
- **Adresse IP** : Détection d'accès suspects
- **User Agent** : Identification du navigateur/appareil
- **Horodatage précis** : Traçabilité complète
- **Conseils de sécurité** : Éducation utilisateur

## Tests et validation

### Tests fonctionnels
1. ✅ Changement de mot de passe avec email (mode console)
2. ✅ Changement de mot de passe avec email (mode SMTP)
3. ✅ Gestion des erreurs d'envoi d'email
4. ✅ Validation des données utilisateur
5. ✅ Audit des actions

### Tests de sécurité
1. ✅ Vérification de l'ancien mot de passe
2. ✅ Validation de la complexité
3. ✅ Protection contre les attaques par force brute
4. ✅ Audit des tentatives échouées

### Tests d'email
1. ✅ Rendu HTML correct
2. ✅ Fallback texte brut
3. ✅ Responsive design
4. ✅ Contenu sécurisé (pas de données sensibles)

## Configuration recommandée

### Pour le développement
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Pour la production
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votre-domaine.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@votre-domaine.com
EMAIL_HOST_PASSWORD=mot-de-passe-securise
DEFAULT_FROM_EMAIL=SI-Gouvernance <noreply@votre-domaine.com>
```

## Évolutions futures possibles

### Notifications avancées
- Notification lors de connexion depuis un nouvel appareil
- Notification lors de modifications de profil
- Historique des connexions par email
- Alertes de sécurité personnalisées

### Templates email
- Templates personnalisables par organisation
- Support multilingue
- Thèmes sombres/clairs
- Intégration avec des services d'emailing

### Sécurité avancée
- Authentification à deux facteurs
- Codes de vérification par email
- Blocage temporaire après tentatives suspectes
- Géolocalisation des connexions

## Conclusion

Cette fonctionnalité de profil utilisateur offre maintenant une sécurité renforcée avec notification automatique par email lors des changements de mot de passe. L'implémentation est robuste, sécurisée et offre une excellente expérience utilisateur tout en maintenant un niveau de sécurité élevé.

## Architecture technique

### Vues créées
```python
# core/views.py
@login_required
def profil_view(request):
    """Vue principale du profil utilisateur"""

@login_required
@require_http_methods(["POST"])
def modifier_profil_view(request):
    """Modification des informations personnelles"""

@login_required
@require_http_methods(["POST"])
def changer_mot_de_passe_view(request):
    """Changement sécurisé du mot de passe"""
```

### URLs ajoutées
```python
# core/urls.py
path('profil/', views.profil_view, name='profil'),
path('profil/modifier/', views.modifier_profil_view, name='modifier_profil'),
path('profil/changer-mot-de-passe/', views.changer_mot_de_passe_view, name='changer_mot_de_passe'),
```

### Template créé
- `templates/core/profil.html` : Interface moderne et responsive

## Interface utilisateur

### Design moderne
- **Style** : Glassmorphism avec dégradés subtils
- **Responsive** : Optimisé pour desktop et mobile
- **Animations** : Transitions fluides et feedback visuel
- **Accessibilité** : Contrastes appropriés et navigation au clavier

### Sections de la page
1. **Header** : Nom, avatar et navigation
2. **Statistiques** : Projets actifs, tâches en cours/terminées, ancienneté
3. **Informations personnelles** : Formulaire de modification
4. **Sécurité** : Informations de connexion et changement de mot de passe
5. **Projets récents** : Liste des derniers projets actifs

### Modal de changement de mot de passe
- Interface sécurisée avec validation en temps réel
- Feedback visuel pour les erreurs
- Confirmation avant application

## Sécurité et audit

### Mesures de sécurité
- ✅ Vérification des permissions (pas d'accès admin)
- ✅ Validation de l'ancien mot de passe
- ✅ Complexité du nouveau mot de passe
- ✅ Protection CSRF
- ✅ Sanitisation des données

### Audit automatique
Toutes les actions sont auditées avec les types suivants :
- `CONSULTATION_PROFIL` : Accès à la page de profil
- `MODIFICATION_PROFIL` : Modification des informations personnelles
- `CHANGEMENT_MOT_DE_PASSE` : Changement de mot de passe réussi
- `TENTATIVE_CHANGEMENT_MOT_DE_PASSE_ECHOUEE` : Tentative échouée
- `ERREUR_MODIFICATION_PROFIL` : Erreurs techniques

## Intégration dans l'interface

### Accès au profil
- **Sidebar** : Icône utilisateur avec lien vers le profil (utilisateurs non-admin uniquement)
- **URL directe** : `/profil/`

### Restrictions d'accès
- **Administrateurs** : Redirigés vers le dashboard avec message informatif
- **Utilisateurs non connectés** : Redirection vers la page de connexion

## Statistiques affichées

### Données personnelles
- Nombre de projets actifs
- Nombre de tâches en cours
- Nombre de tâches terminées
- Date d'adhésion au système
- Dernière connexion

### Projets récents
- Affichage des 5 derniers projets actifs
- Statut de chaque projet
- Lien direct vers les détails du projet

## Gestion des erreurs

### Validation côté client
- Vérification de la longueur du mot de passe
- Correspondance des mots de passe
- Feedback visuel immédiat

### Validation côté serveur
- Vérification de l'ancien mot de passe
- Validation des données personnelles
- Gestion des erreurs de base de données

### Messages d'erreur
- Messages clairs et informatifs
- Affichage temporaire avec animations
- Différenciation visuelle (succès/erreur)

## Responsive design

### Breakpoints
- **Mobile** : < 640px - Layout vertical, formulaires empilés
- **Tablet** : 640px - 1024px - Layout hybride
- **Desktop** : > 1024px - Layout en colonnes

### Optimisations mobiles
- Boutons tactiles appropriés
- Formulaires adaptés aux petits écrans
- Navigation simplifiée
- Texte lisible sans zoom

## Tests recommandés

### Tests fonctionnels
1. ✅ Accès à la page de profil
2. ✅ Modification des informations personnelles
3. ✅ Changement de mot de passe avec validation
4. ✅ Restriction d'accès pour les administrateurs
5. ✅ Audit des actions

### Tests de sécurité
1. ✅ Tentative d'accès non autorisé
2. ✅ Validation des mots de passe faibles
3. ✅ Protection CSRF
4. ✅ Sanitisation des données

### Tests d'interface
1. ✅ Responsive design sur différents appareils
2. ✅ Animations et transitions
3. ✅ Accessibilité au clavier
4. ✅ Contraste et lisibilité

## Évolutions futures possibles

### Fonctionnalités avancées
- Photo de profil personnalisée
- Préférences de notification
- Thème sombre/clair
- Authentification à deux facteurs
- Historique des connexions

### Intégrations
- Synchronisation avec Active Directory
- Export des données personnelles
- Intégration avec des services externes

## Conclusion

Cette fonctionnalité de profil utilisateur offre une interface moderne et sécurisée pour la gestion des informations personnelles, tout en maintenant un niveau de sécurité élevé et une expérience utilisateur optimale sur tous les appareils.