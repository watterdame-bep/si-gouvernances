# Configuration Email pour Production

## 🎯 Objectif

Configurer l'envoi réel d'emails pour le système d'activation sécurisé.

---

## 📧 Option 1: Gmail (Recommandé pour les Tests)

### Étape 1: Créer un Mot de Passe d'Application Gmail

1. Allez sur https://myaccount.google.com/security
2. Activez la "Validation en deux étapes" si ce n'est pas déjà fait
3. Allez dans "Mots de passe des applications"
4. Créez un nouveau mot de passe pour "Mail"
5. Copiez le mot de passe généré (16 caractères)

### Étape 2: Créer/Modifier le Fichier `.env`

Créez un fichier `.env` à la racine du projet:

```env
# Configuration Email - Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
DEFAULT_FROM_EMAIL=SI-Gouvernance <votre-email@gmail.com>
```

**Remplacez:**
- `votre-email@gmail.com` par votre email Gmail
- `votre-mot-de-passe-application` par le mot de passe d'application généré

### Étape 3: Redémarrer Django

```bash
# Arrêter le serveur (Ctrl+C)
# Relancer
python manage.py runserver
```

### Étape 4: Tester

Créez un nouveau compte ou utilisez le bouton "Renvoyer lien" - l'email sera envoyé réellement!

---

## 📧 Option 2: Outlook/Office 365

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@outlook.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=SI-Gouvernance <votre-email@outlook.com>
```

---

## 📧 Option 3: Serveur SMTP Personnalisé

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votre-domaine.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@votre-domaine.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
DEFAULT_FROM_EMAIL=SI-Gouvernance <noreply@votre-domaine.com>
```

---

## 🧪 Mode Développement (Actuel)

Pour garder le mode console (emails affichés dans le terminal):

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Avantages:**
- Pas besoin de configuration SMTP
- Voir les emails dans le terminal
- Pas de limite d'envoi

**Inconvénients:**
- Les emails ne sont pas envoyés réellement
- Il faut copier/coller le lien manuellement

---

## 🔧 Script de Test d'Email

Créez un fichier `test_email_config.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")

try:
    send_mail(
        'Test Email - SI Gouvernance',
        'Ceci est un email de test.',
        settings.DEFAULT_FROM_EMAIL,
        ['votre-email-test@example.com'],
        fail_silently=False,
    )
    print("\n✅ Email envoyé avec succès!")
except Exception as e:
    print(f"\n❌ Erreur: {str(e)}")
```

Exécutez:
```bash
python test_email_config.py
```

---

## 🚨 Sécurité

### ⚠️ IMPORTANT

1. **Ne JAMAIS commiter le fichier `.env`** dans Git
2. Ajoutez `.env` dans `.gitignore`
3. Utilisez des mots de passe d'application (pas votre mot de passe principal)
4. En production, utilisez des variables d'environnement serveur

### Vérifier `.gitignore`

Assurez-vous que `.gitignore` contient:

```
.env
*.env
.env.local
.env.production
```

---

## 📝 Exemple Complet de `.env`

```env
# Django
SECRET_KEY=votre-secret-key-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données
DATABASE_URL=sqlite:///db.sqlite3

# Email - Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@example.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=SI-Gouvernance <admin@example.com>

# Sécurité (Production uniquement)
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True
```

---

## 🎯 Recommandation

### Pour le Développement (Actuel)

Gardez le mode console et utilisez:
1. Le script `verifier_activation_joe.py` pour générer des liens
2. Le bouton "Renvoyer lien" dans l'interface
3. Copiez/collez les liens manuellement

### Pour la Production

Configurez Gmail ou un serveur SMTP professionnel pour envoyer de vrais emails.

---

## 🆘 Dépannage

### Erreur: "SMTPAuthenticationError"

**Cause:** Identifiants incorrects ou mot de passe d'application non utilisé

**Solution:**
1. Vérifiez EMAIL_HOST_USER et EMAIL_HOST_PASSWORD
2. Utilisez un mot de passe d'application Gmail (pas votre mot de passe)
3. Activez "Accès moins sécurisé" si nécessaire (Gmail)

### Erreur: "SMTPServerDisconnected"

**Cause:** Problème de connexion au serveur SMTP

**Solution:**
1. Vérifiez EMAIL_HOST et EMAIL_PORT
2. Vérifiez votre connexion internet
3. Vérifiez que le port 587 n'est pas bloqué par un firewall

### Les emails vont dans les spams

**Solution:**
1. Configurez SPF et DKIM pour votre domaine
2. Utilisez un domaine professionnel (pas Gmail)
3. Ajoutez un lien de désinscription
4. Évitez les mots "spam" dans le contenu

---

## ✅ Checklist de Configuration

- [ ] Fichier `.env` créé
- [ ] Mot de passe d'application Gmail généré
- [ ] Variables EMAIL_* configurées
- [ ] `.env` ajouté dans `.gitignore`
- [ ] Django redémarré
- [ ] Test d'envoi effectué
- [ ] Email reçu avec succès

---

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs Django
2. Testez avec `test_email_config.py`
3. Vérifiez la configuration Gmail
4. Consultez la documentation Django: https://docs.djangoproject.com/en/4.2/topics/email/
