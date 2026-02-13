# Guide de Test - Emails de Notifications

## Test Rapide

### 1. Vérifier la Configuration SMTP

```bash
python test_email_smtp.py
```

Devrait afficher:
```
✓ Configuration SMTP chargée
✓ Email envoyé avec succès à watterdame70@gmail.com
```

### 2. Tester l'Envoi Automatique

```bash
python test_notifications_email.py
```

Ce script va:
1. Créer une notification de tâche → Email envoyé
2. Créer une notification de module → Email envoyé
3. Créer une notification de projet → Email envoyé
4. Créer une alerte de projet → Email envoyé

### 3. Vérifier la Boîte Email

Connectez-vous à votre boîte email et vérifiez:
- 4 emails reçus avec le sujet `[SI-Gouvernance]`
- Contenu détaillé avec informations de la notification
- Format professionnel et lisible

---

## Test Manuel dans l'Application

### Test 1: Assignation de Tâche

1. Connectez-vous en tant qu'administrateur
2. Allez dans un projet
3. Créez ou modifiez une tâche
4. Assignez-la à un utilisateur avec email
5. Vérifiez que l'utilisateur reçoit un email

### Test 2: Affectation à un Module

1. Allez dans un module
2. Affectez un utilisateur au module
3. Vérifiez que l'utilisateur reçoit un email d'affectation

### Test 3: Clôture de Module

1. Clôturez un module
2. Vérifiez que le responsable du projet reçoit un email

### Test 4: Ticket de Maintenance

1. Créez un ticket de maintenance
2. Assignez-le à un développeur
3. Vérifiez que le développeur reçoit un email

---

## Vérification des Logs

### Console Django

Lors du démarrage du serveur, vous devriez voir:
```
System check identified no issues (0 silenced).
Signaux de notifications chargés
```

### Lors de la Création d'une Notification

Si tout fonctionne:
```
(Aucun message - email envoyé silencieusement)
```

Si erreur:
```
Erreur lors de l'envoi de l'email pour NotificationTache 123: [détails]
```

---

## Résolution de Problèmes

### Problème: Aucun Email Reçu

**Vérifications**:
1. L'utilisateur a-t-il un email dans son profil?
2. La configuration SMTP est-elle correcte dans `.env`?
3. Le serveur Django est-il redémarré après les modifications?
4. Vérifiez les spams

**Test**:
```bash
python test_email_smtp.py
```

### Problème: Erreur SMTP

**Message**: `SMTPAuthenticationError`

**Solution**:
- Vérifiez le mot de passe d'application Gmail
- Vérifiez que l'authentification à deux facteurs est activée
- Régénérez un mot de passe d'application si nécessaire

### Problème: Emails dans les Spams

**Solutions**:
1. Ajoutez `dev.jconsult@gmail.com` aux contacts
2. Marquez les emails comme "Non spam"
3. En production, configurez SPF/DKIM

---

## Checklist de Validation

- [ ] Configuration SMTP testée avec `test_email_smtp.py`
- [ ] Test automatique réussi avec `test_notifications_email.py`
- [ ] Email reçu pour notification de tâche
- [ ] Email reçu pour notification de module
- [ ] Email reçu pour notification de projet
- [ ] Email reçu pour alerte de projet
- [ ] Format de l'email correct et lisible
- [ ] Liens et informations corrects dans l'email
- [ ] Pas d'erreurs dans les logs Django

---

## Commandes Utiles

### Tester la Configuration Email
```bash
python test_email_smtp.py
```

### Tester Toutes les Notifications
```bash
python test_notifications_email.py
```

### Vérifier les Notifications en Base
```python
python manage.py shell

from core.models import NotificationTache, NotificationModule, NotificationProjet, AlerteProjet

# Compter les notifications
print(f"Tâches: {NotificationTache.objects.count()}")
print(f"Modules: {NotificationModule.objects.count()}")
print(f"Projets: {NotificationProjet.objects.count()}")
print(f"Alertes: {AlerteProjet.objects.count()}")

# Voir les dernières notifications
for notif in NotificationTache.objects.order_by('-date_creation')[:5]:
    print(f"{notif.destinataire.email} - {notif.titre}")
```

### Nettoyer les Notifications de Test
```python
python manage.py shell

from core.models import NotificationTache, NotificationModule, NotificationProjet, AlerteProjet

# Supprimer les notifications de test
NotificationTache.objects.filter(donnees_contexte__test=True).delete()
NotificationModule.objects.filter(donnees_contexte__test=True).delete()
NotificationProjet.objects.filter(donnees_contexte__test=True).delete()
AlerteProjet.objects.filter(donnees_contexte__test=True).delete()

print("Notifications de test supprimées")
```

---

## Résultat Attendu

Après avoir suivi ce guide, vous devriez avoir:

✅ Configuration SMTP fonctionnelle
✅ Emails envoyés automatiquement pour toutes les notifications
✅ 4 emails de test reçus
✅ Système validé et opérationnel

---

## Prochaines Étapes

1. **Tester en conditions réelles** - Utilisez l'application normalement
2. **Surveiller les logs** - Vérifiez qu'il n'y a pas d'erreurs
3. **Recueillir les retours** - Demandez aux utilisateurs s'ils reçoivent bien les emails
4. **Optimiser** - Ajoutez des templates HTML si nécessaire
