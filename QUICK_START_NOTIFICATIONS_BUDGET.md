# Quick Start - Notifications Budget

## 🚀 Démarrage Rapide

### Prérequis
- Docker installé et démarré
- Configuration email dans `.env`

### Démarrer le Système
```bash
# 1. Démarrer Docker
docker-compose up -d

# 2. Vérifier que tout fonctionne
docker-compose ps
```

---

## 📋 Fonctionnalités

### 1. Notification Définition Budget

**Quand ?** Lorsqu'un admin/responsable définit le budget d'un projet

**Qui est notifié ?** Tous les administrateurs

**Comment ?**
1. Aller dans un projet
2. Cliquer sur "Paramètres"
3. Cliquer sur l'icône 💰 dans "Budget Total"
4. Entrer le montant
5. Valider

**Résultat :**
- ✅ Notification dans l'app
- ✅ Email envoyé

---

### 2. Alerte Dépassement Budget

**Quand ?** Lorsque les dépenses dépassent le budget total

**Qui est notifié ?**
- Administrateur (créateur)
- Responsable du projet

**Comment ?**
1. Définir un budget (ex: 10000€)
2. Ajouter des dépenses qui dépassent
3. Exécuter : `python manage.py check_budget`

**Résultat :**
- ✅ Alerte dans l'app
- ✅ Email envoyé

---

## 🧪 Tests Rapides

### Test 1 : Définition Budget
```bash
# 1. Démarrer Docker
docker-compose up -d

# 2. Aller dans l'interface web
# 3. Projet → Paramètres → Définir budget
# 4. Vérifier notification + email
```

### Test 2 : Dépassement Budget
```bash
# 1. Définir budget : 10000€
# 2. Ajouter dépenses : 11000€
# 3. Exécuter commande
python manage.py check_budget

# 4. Vérifier alertes + emails
```

### Test Automatique
```bash
# Exécuter le script de test complet
python test_notifications_budget.py
```

---

## ⚙️ Configuration Automatique

### Windows (Task Scheduler)

**Créer** : `run_check_budget.bat`
```batch
@echo off
cd /d "C:\chemin\vers\projet"
python manage.py check_budget >> logs\budget_checks.log 2>&1
```

**Planifier** : Tous les jours à 9h00

### Linux (cron)

```bash
# Ajouter dans crontab -e
0 9 * * * cd /chemin/vers/projet && python manage.py check_budget >> logs/budget_checks.log 2>&1
```

---

## 📧 Vérifier les Emails

### Dans l'Application
1. Cliquer sur l'icône 🔔 (notifications)
2. Voir les notifications de budget

### Dans la Boîte Email
Chercher les emails avec sujet :
- `[SI-Gouvernance] Projet: Budget défini - ...`
- `[SI-Gouvernance] ⚠️ Alerte: 🔴 Budget dépassé - ...`

---

## 🔍 Vérifications

### Vérifier les Notifications
```python
python manage.py shell

# Notifications définition budget
from core.models import NotificationProjet
NotificationProjet.objects.filter(
    donnees_contexte__type_action='DEFINITION_BUDGET'
).order_by('-date_creation')[:5]

# Alertes dépassement budget
from core.models import AlerteProjet
AlerteProjet.objects.filter(
    type_alerte='BUDGET_DEPASSE'
).order_by('-date_creation')[:5]
```

### Vérifier les Logs
```bash
# Logs de vérification budget
type logs\budget_checks.log

# Logs Django
type logs\django.log
```

---

## 🐛 Dépannage

### Problème : Pas de notification

**Vérifier** :
1. L'utilisateur est bien admin ?
2. L'email est configuré dans `.env` ?
3. Docker est démarré ?

### Problème : Pas d'email

**Vérifier** :
1. Configuration SMTP dans `.env`
2. Email de l'utilisateur renseigné
3. Logs : `logs/django.log`

### Problème : Pas d'alerte dépassement

**Vérifier** :
1. Budget total défini ?
2. Dépenses ajoutées ?
3. Commande `check_budget` exécutée ?

---

## 📊 Calcul du Budget

```
Budget Total = Montant défini par admin/responsable
Budget Consommé = Somme(Matériel) + Somme(Services)
Budget Disponible = Budget Total - Budget Consommé

Si Budget Disponible < 0 → ALERTE DÉPASSEMENT
```

---

## 📝 Fichiers Importants

- `core/views.py` - Notification définition budget
- `core/management/commands/check_budget.py` - Alerte dépassement
- `test_notifications_budget.py` - Script de test
- `templates/emails/notification_projet.html` - Template email notification
- `templates/emails/notification_alerte_projet.html` - Template email alerte

---

## ✅ Checklist de Vérification

Avant de mettre en production :

- [ ] Docker démarré
- [ ] Configuration email dans `.env`
- [ ] Test définition budget OK
- [ ] Test dépassement budget OK
- [ ] Emails reçus
- [ ] Tâche automatique configurée
- [ ] Logs surveillés

---

## 🚀 Commandes Utiles

```bash
# Démarrer Docker
docker-compose up -d

# Arrêter Docker
docker-compose down

# Voir les logs
docker-compose logs -f web

# Vérifier budget manuellement
python manage.py check_budget

# Tester les notifications
python test_notifications_budget.py

# Shell Django
python manage.py shell
```

---

**Date** : 2026-02-16
**Statut** : ✅ Prêt à l'emploi
