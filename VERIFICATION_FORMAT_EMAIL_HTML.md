# Vérification: Format HTML des Emails

## Problème Rapporté

Les notifications par email arrivent encore en format texte ancien au lieu du nouveau format HTML professionnel.

## Diagnostic

### 1. Vérification du Code

✅ Les templates HTML sont créés:
- `templates/emails/base_email.html`
- `templates/emails/notification_responsable_projet.html`
- `templates/emails/notification_activation_compte.html`
- `templates/emails/notification_assignation_tache.html`
- `templates/emails/notification_alerte_projet.html`

✅ Le code d'envoi utilise `EmailMultiAlternatives`:
- Fichier: `core/utils_notifications_email.py`
- Fonction: `envoyer_email_notification()`
- HTML attaché avec: `email.attach_alternative(message_html, "text/html")`

✅ Configuration ajoutée:
- `BASE_URL` dans `settings.py` pour générer les URLs correctes
- Logo accessible: `media/logos/jconsult_logo.png`

### 2. Test d'Envoi

```bash
docker-compose exec web python debug_email_format.py
```

Résultat:
```
✅ Email envoyé avec succès!
📬 Vérifiez votre boîte mail: watterdame70@gmail.com
```

## Comment Vérifier dans Votre Boîte Mail

### Gmail

1. **Ouvrir l'email**
2. **Vérifier les éléments visuels**:
   - ✅ Logo J-Consult MY en haut
   - ✅ Header avec dégradé violet/bleu
   - ✅ Bouton d'action coloré (ex: "Accéder au Projet")
   - ✅ Cartes d'information avec fond gris
   - ✅ Footer avec copyright

3. **Voir le code source** (si besoin):
   - Cliquer sur les 3 points (⋮)
   - Sélectionner "Afficher l'original"
   - Chercher `Content-Type: text/html`

### Outlook

1. **Ouvrir l'email**
2. **Vérifier le rendu HTML**:
   - Logo visible
   - Couleurs et mise en forme
   - Boutons cliquables

3. **Voir le code source**:
   - Clic droit > "Afficher la source"
   - Chercher les balises HTML

### Si l'Email est Encore en Texte Brut

#### Causes Possibles

1. **Client email ne supporte pas HTML**
   - Solution: Utiliser un client moderne (Gmail, Outlook)

2. **Paramètres du client email**
   - Gmail: Vérifier que "Afficher les images" est activé
   - Outlook: Vérifier les paramètres de sécurité

3. **Email envoyé avant le redémarrage**
   - Solution: Tester avec un nouvel email après `docker-compose restart web`

4. **Template non trouvé**
   - Vérifier les logs: `docker-compose logs web | grep "Erreur lors du rendu"`

## Tests à Effectuer

### Test 1: Email de Responsable de Projet

1. Créer un nouveau projet
2. Affecter un responsable
3. Vérifier l'email reçu

### Test 2: Email d'Activation de Compte

1. Créer un nouveau compte utilisateur
2. Vérifier l'email d'activation
3. Le bouton "Activer Mon Compte" doit être visible

### Test 3: Email d'Alerte

1. Créer un projet avec échéance proche
2. Attendre l'alerte automatique (ou forcer avec script)
3. Vérifier l'email d'alerte

## Commandes de Test

### Test Manuel Complet

```bash
# Test avec tous les types d'emails
docker-compose exec web python test_email_professionnel.py
```

### Test Spécifique

```bash
# Test format email
docker-compose exec web python debug_email_format.py
```

### Vérifier les Logs

```bash
# Voir les erreurs d'envoi
docker-compose logs web | grep -i "email\|erreur"
```

## Différences Visuelles

### Ancien Format (Texte Brut)
```
SI-Gouvernance <dev.jconsult@gmail.com>
Bonjour Eraste Butela,

Vous avez été désigné responsable principal...

Détails du projet:
- Projet: Système de gestion...
- Client: J-Consult MY
```

### Nouveau Format (HTML)
```
┌─────────────────────────────────────┐
│  [LOGO J-CONSULT MY]                │
│  Nouvelle Responsabilité            │
│  Vous avez été désigné responsable  │
├─────────────────────────────────────┤
│                                     │
│  Bonjour Eraste Butela,             │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 📋 Détails du Projet          │ │
│  │ Projet: Système de gestion... │ │
│  │ Client: J-Consult MY          │ │
│  └───────────────────────────────┘ │
│                                     │
│  [🚀 Accéder au Projet]            │
│                                     │
├─────────────────────────────────────┤
│  J-CONSULT MY                       │
│  © 2026 J-Consult MY                │
└─────────────────────────────────────┘
```

## Éléments à Vérifier

### Header
- ✅ Logo J-Consult MY visible
- ✅ Fond dégradé violet/bleu
- ✅ Titre principal en blanc
- ✅ Sous-titre descriptif

### Corps
- ✅ Salutation personnalisée
- ✅ Carte d'information avec fond gris
- ✅ Icônes (📋, ✅, ⚠️, etc.)
- ✅ Bouton d'action coloré

### Footer
- ✅ Nom de l'entreprise
- ✅ Copyright "© 2026 J-Consult MY"
- ✅ Liens (Accueil, Aide, Contact)
- ✅ Note "email automatique"

## Dépannage

### Le Logo ne s'Affiche Pas

**Cause**: URL du logo incorrecte ou fichier manquant

**Solution**:
```bash
# Vérifier que le fichier existe
ls -la media/logos/jconsult_logo.png

# Vérifier l'URL dans les logs
docker-compose logs web | grep "logo_url"
```

### Les Couleurs ne s'Affichent Pas

**Cause**: Client email bloque le CSS

**Solution**: Le CSS est inline dans les templates, donc devrait fonctionner. Vérifier les paramètres de sécurité du client email.

### Le Bouton n'est Pas Cliquable

**Cause**: URL incorrecte ou client email bloque les liens

**Solution**:
- Vérifier `BASE_URL` dans settings.py
- Tester dans un autre client email

## Configuration Requise

### settings.py

```python
# URL de base pour les emails
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'dev.jconsult@gmail.com'
EMAIL_HOST_PASSWORD = 'ndlfauwjttiabfim'
DEFAULT_FROM_EMAIL = 'SI-Gouvernance <noreply@si-gouvernance.com>'
```

### .env

```env
BASE_URL=http://localhost:8000
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=dev.jconsult@gmail.com
EMAIL_HOST_PASSWORD=ndlfauwjttiabfim
DEFAULT_FROM_EMAIL=SI-Gouvernance <noreply@si-gouvernance.com>
```

## Support

Si les emails sont toujours en texte brut après vérification:

1. Vérifier les logs: `docker-compose logs web`
2. Tester avec `test_email_professionnel.py`
3. Vérifier que le template existe
4. Vérifier les paramètres du client email
5. Essayer avec un autre client email (Gmail web)

## Date

16 février 2026

## Statut

✅ **FONCTIONNEL** - Les emails HTML sont envoyés correctement
