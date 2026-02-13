# Guide Complet - Configuration Email Gmail

**Date**: 13 février 2026  
**Objectif**: Configurer l'envoi réel d'emails via Gmail SMTP  
**Durée**: 15 minutes

---

## 📋 Vue d'Ensemble

Actuellement, votre application est en mode développement où les emails sont affichés dans la console. Ce guide vous permet de configurer Gmail pour envoyer de vrais emails.

---

## 🎯 Étape 1: Créer un Mot de Passe d'Application Gmail

### Pourquoi un mot de passe d'application?

Gmail ne permet plus d'utiliser votre mot de passe principal pour les applications tierces. Vous devez créer un "mot de passe d'application" spécifique.

### Instructions Détaillées

1. **Allez sur votre compte Google**
   - Ouvrez: https://myaccount.google.com/security
   - Connectez-vous avec votre compte Gmail

2. **Activez la validation en deux étapes** (si pas déjà fait)
   - Cherchez "Validation en deux étapes"
   - Cliquez sur "Activer"
   - Suivez les instructions (SMS ou application)

3. **Créez un mot de passe d'application**
   - Retournez sur: https://myaccount.google.com/security
   - Cherchez "Mots de passe des applications"
   - Cliquez dessus
   - Sélectionnez "Autre (nom personnalisé)"
   - Tapez: "SI Gouvernance Django"
   - Cliquez sur "Générer"

4. **Copiez le mot de passe**
   - Un mot de passe de 16 caractères apparaît (ex: `abcd efgh ijkl mnop`)
   - ⚠️ **COPIEZ-LE IMMÉDIATEMENT** - vous ne pourrez plus le voir après
   - Gardez-le dans un endroit sûr temporairement

---

## 🎯 Étape 2: Créer le Fichier `.env`

### Option A: Copier depuis l'exemple (RECOMMANDÉ)

Ouvrez un terminal dans le dossier du projet et exécutez:

```bash
copy .env.example .env
```

### Option B: Créer manuellement

Créez un nouveau fichier nommé `.env` à la racine du projet (même niveau que `manage.py`).

---

## 🎯 Étape 3: Configurer le Fichier `.env`

Ouvrez le fichier `.env` et modifiez les lignes suivantes:

```env
# Configuration de base
DEBUG=True

# Base de données
DB_NAME=si-gouvernance
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Configuration Email - GMAIL SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
DEFAULT_FROM_EMAIL=SI-Gouvernance <votre-email@gmail.com>
```

### ⚠️ IMPORTANT - Remplacez:

1. **`votre-email@gmail.com`** → Votre adresse Gmail complète
2. **`abcd efgh ijkl mnop`** → Le mot de passe d'application (16 caractères)
3. **`SI-Gouvernance <votre-email@gmail.com>`** → Nom d'affichage + votre email

### Exemple Réel:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=admin@example.com
EMAIL_HOST_PASSWORD=xyzw abcd efgh ijkl
DEFAULT_FROM_EMAIL=SI-Gouvernance <admin@example.com>
```

---

## 🎯 Étape 4: Vérifier la Sécurité

### Vérifier que `.env` est dans `.gitignore`

Ouvrez le fichier `.gitignore` et vérifiez qu'il contient:

```
.env
*.env
.env.local
.env.production
```

Si ce n'est pas le cas, ajoutez ces lignes!

### ⚠️ CRITIQUE: Ne JAMAIS commiter `.env`

Le fichier `.env` contient des informations sensibles (mot de passe). Il ne doit JAMAIS être envoyé sur Git/GitHub.

---

## 🎯 Étape 5: Redémarrer Django

1. **Arrêtez le serveur Django**
   - Dans le terminal où Django tourne
   - Appuyez sur `Ctrl + C`

2. **Relancez le serveur**
   ```bash
   python manage.py runserver
   ```

3. **Vérifiez les logs**
   - Vous devriez voir Django démarrer normalement
   - Aucune erreur liée à l'email

---

## 🎯 Étape 6: Tester l'Envoi d'Email

### Test 1: Renvoyer le lien à Joe

1. Allez dans **"Gestion des Comptes"**
2. Trouvez **JOE NKONDOLO** (badge rouge "Inactif")
3. Cliquez sur le **bouton violet** "Renvoyer lien"
4. Confirmez dans la modale
5. ✅ **L'email sera envoyé réellement à joelnkondolo@gmail.com**

### Test 2: Créer un nouveau compte test

1. Créez un compte avec VOTRE email personnel
2. Vérifiez votre boîte de réception
3. Vous devriez recevoir l'email d'activation
4. Cliquez sur le lien et testez l'activation

### Test 3: Utiliser le script de test

Créez un fichier `test_email_smtp.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 70)
print("TEST CONFIGURATION EMAIL SMTP")
print("=" * 70)
print(f"\nBackend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Port: {settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"From: {settings.DEFAULT_FROM_EMAIL}")

email_test = input("\nEntrez votre email pour le test: ")

print(f"\n📧 Envoi d'un email de test à {email_test}...")

try:
    send_mail(
        'Test Email - SI Gouvernance',
        'Ceci est un email de test.\n\nSi vous recevez cet email, la configuration SMTP fonctionne correctement!',
        settings.DEFAULT_FROM_EMAIL,
        [email_test],
        fail_silently=False,
    )
    print("\n✅ Email envoyé avec succès!")
    print(f"📬 Vérifiez la boîte de réception de {email_test}")
    print("⚠️ Vérifiez aussi les spams/courrier indésirable")
except Exception as e:
    print(f"\n❌ Erreur lors de l'envoi: {str(e)}")
    print("\n💡 Vérifiez:")
    print("   1. Le mot de passe d'application Gmail")
    print("   2. La validation en deux étapes est activée")
    print("   3. Le fichier .env est bien configuré")
    print("   4. Django a été redémarré après modification du .env")
```

Exécutez:
```bash
python test_email_smtp.py
```

---

## 🆘 Dépannage

### Erreur: "SMTPAuthenticationError: Username and Password not accepted"

**Causes possibles:**
1. Mot de passe d'application incorrect
2. Validation en deux étapes non activée
3. Email incorrect dans EMAIL_HOST_USER

**Solutions:**
1. Régénérez un nouveau mot de passe d'application
2. Vérifiez que la validation en deux étapes est active
3. Vérifiez l'orthographe de votre email
4. Redémarrez Django après modification

### Erreur: "SMTPServerDisconnected"

**Causes possibles:**
1. Problème de connexion internet
2. Port 587 bloqué par un firewall
3. Configuration SMTP incorrecte

**Solutions:**
1. Vérifiez votre connexion internet
2. Essayez le port 465 avec EMAIL_USE_SSL=True
3. Désactivez temporairement le firewall pour tester

### Les emails vont dans les spams

**Solutions:**
1. Demandez au destinataire de marquer comme "Non spam"
2. Utilisez un domaine professionnel (pas Gmail) en production
3. Configurez SPF et DKIM pour votre domaine

### L'email n'arrive pas

**Vérifications:**
1. Vérifiez les spams/courrier indésirable
2. Vérifiez l'adresse email du destinataire
3. Regardez les logs Django pour les erreurs
4. Testez avec votre propre email d'abord

---

## 📊 Comparaison: Console vs SMTP

### Mode Console (Actuel)

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

**Avantages:**
- ✅ Pas de configuration nécessaire
- ✅ Pas de limite d'envoi
- ✅ Voir les emails dans le terminal
- ✅ Pas de risque d'envoyer des emails par erreur

**Inconvénients:**
- ❌ Les emails ne sont pas envoyés réellement
- ❌ Il faut copier/coller les liens manuellement
- ❌ Pas adapté pour la production

### Mode SMTP (Gmail)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

**Avantages:**
- ✅ Les emails sont envoyés réellement
- ✅ Les utilisateurs reçoivent les liens automatiquement
- ✅ Plus professionnel
- ✅ Prêt pour la production

**Inconvénients:**
- ❌ Nécessite une configuration
- ❌ Limite d'envoi Gmail (500 emails/jour)
- ❌ Risque d'envoyer des emails de test par erreur

---

## 🎯 Recommandations

### Pour le Développement

**Option 1: Garder le mode console**
- Utilisez `verifier_activation_joe.py` pour générer des liens
- Copiez/collez les liens manuellement
- Aucun risque d'envoyer des emails par erreur

**Option 2: Utiliser Gmail SMTP**
- Configurez Gmail une seule fois
- Les emails sont envoyés automatiquement
- Plus proche de la production

### Pour la Production

**Utilisez un service professionnel:**
- SendGrid (gratuit jusqu'à 100 emails/jour)
- Mailgun (gratuit jusqu'à 5000 emails/mois)
- Amazon SES (très bon marché)
- Serveur SMTP dédié

---

## ✅ Checklist de Configuration

- [ ] Validation en deux étapes activée sur Gmail
- [ ] Mot de passe d'application créé et copié
- [ ] Fichier `.env` créé à la racine du projet
- [ ] Variables EMAIL_* configurées dans `.env`
- [ ] `.env` ajouté dans `.gitignore`
- [ ] Django redémarré
- [ ] Test d'envoi effectué avec succès
- [ ] Email reçu dans la boîte de réception

---

## 🎓 Pour Joe Nkondolo

Une fois la configuration terminée:

1. Allez dans "Gestion des Comptes"
2. Cliquez sur "Renvoyer lien" pour Joe
3. L'email sera envoyé automatiquement à joelnkondolo@gmail.com
4. Joe recevra le lien d'activation
5. Joe clique sur le lien et définit son mot de passe
6. Compte activé!

---

## 📞 Support

Si vous avez besoin d'aide:
1. Exécutez `python test_email_smtp.py`
2. Vérifiez les logs Django
3. Consultez la section "Dépannage"
4. Vérifiez que Django a été redémarré

---

## 🏆 Conclusion

La configuration Gmail SMTP est simple et rapide. Une fois configurée, tous les emails d'activation seront envoyés automatiquement aux utilisateurs.

**Prochaines étapes:**
1. Suivez les étapes 1 à 5 de ce guide
2. Testez avec votre propre email
3. Renvoyez le lien à Joe
4. Profitez de l'envoi automatique d'emails!
