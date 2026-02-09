# 🔔 Système d'Alertes d'Échéances - Documentation

## 📋 Vue d'ensemble

Le système d'alertes d'échéances envoie automatiquement des notifications aux utilisateurs concernés lorsque les tâches approchent de leur date limite ou sont en retard.

## 🎯 Types d'alertes implémentées

### 1. ⚠️ Alerte 2 jours avant échéance
- **Destinataire** : Responsable de la tâche
- **Déclencheur** : 2 jours avant la date_fin
- **Message** : "La tâche 'XXX' arrive à échéance dans 2 jours (DD/MM/YYYY)"
- **Type** : ALERTE_ECHEANCE

### 2. 🔔 Alerte 1 jour avant échéance
- **Destinataire** : Responsable de la tâche
- **Déclencheur** : 1 jour avant la date_fin (demain)
- **Message** : "Urgent : La tâche 'XXX' arrive à échéance demain !"
- **Type** : ALERTE_ECHEANCE

### 3. 🚨 Alerte jour J (échéance aujourd'hui)
- **Destinataires** : Responsable de la tâche + Responsable du projet
- **Déclencheur** : Le jour de la date_fin
- **Message** : "Critique : La tâche 'XXX' doit être terminée aujourd'hui"
- **Type** : ALERTE_CRITIQUE

### 4. ❌ Alerte de retard
- **Destinataires** : Responsable de la tâche + Responsable du projet
- **Déclencheur** : Chaque jour après la date_fin si statut != TERMINEE
- **Message** : "La tâche 'XXX' est en retard de N jour(s)"
- **Type** : ALERTE_RETARD

## 🔧 Installation et Configuration

### Étape 1 : Appliquer la migration

```bash
python manage.py migrate
```

Cette migration ajoute les nouveaux types de notifications (ALERTE_ECHEANCE, ALERTE_CRITIQUE, ALERTE_RETARD).

### Étape 2 : Tester manuellement

```bash
# Test complet avec création de tâches de test
python test_alertes_echeances.py

# Ou exécution directe de la commande
python manage.py check_task_deadlines
```

### Étape 3 : Planifier l'exécution automatique

#### Sur Windows (Planificateur de tâches)

1. Ouvrir le **Planificateur de tâches Windows**
2. Créer une nouvelle tâche :
   - **Nom** : Vérification échéances tâches SI-Gouvernance
   - **Déclencheur** : Quotidien à 8h00
   - **Action** : Démarrer un programme
   - **Programme** : `C:\chemin\vers\votre\projet\run_check_deadlines.bat`
3. Configurer pour s'exécuter même si l'utilisateur n'est pas connecté

#### Sur Linux/Mac (cron)

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne pour exécuter tous les jours à 8h
0 8 * * * cd /chemin/vers/projet && python manage.py check_task_deadlines >> /var/log/check_deadlines.log 2>&1
```

## 📊 Fonctionnement

### Logique de vérification

1. La commande récupère toutes les tâches **non terminées** (statuts : A_FAIRE, EN_COURS, BLOQUEE)
2. Pour chaque tâche avec une `date_fin` définie :
   - Calcule le nombre de jours restants
   - Crée les alertes appropriées selon les seuils
3. Évite les doublons (une seule alerte par type et par jour)

### Prévention des doublons

Le système vérifie si une alerte du même type a déjà été créée aujourd'hui pour la même tâche et le même utilisateur avant d'en créer une nouvelle.

## 📧 Visualisation des alertes

Les alertes apparaissent dans :
- L'interface de notifications (icône cloche)
- Badge rouge avec le nombre de notifications non lues
- Section "Aujourd'hui" pour les alertes récentes

## 🧪 Tests

### Test manuel rapide

```bash
python test_alertes_echeances.py
```

Ce script :
1. Crée 4 tâches de test avec différentes échéances
2. Exécute la commande de vérification
3. Affiche les notifications créées
4. Propose de nettoyer les données de test

### Vérifier les logs

```bash
# Exécuter avec sortie détaillée
python manage.py check_task_deadlines
```

Sortie attendue :
```
🔍 Vérification des échéances des tâches...
📊 X tâches actives à vérifier
  🟡 Alerte 2 jours créée pour Jean Dupont - Développer API
  🟠 Alerte 1 jour créée pour Marie Martin - Tester module
  🔴 Alerte jour J créée pour Pierre Durand - Déployer application
  🔴 Alerte retard créée pour Sophie Bernard - Corriger bugs

✅ Vérification terminée !
🟡 Alertes 2 jours : 5
🟠 Alertes 1 jour : 3
🔴 Alertes jour J : 2
🔴 Alertes retard : 8
📧 Total alertes créées : 18
```

## 🔍 Dépannage

### Problème : Aucune alerte créée

**Vérifications** :
1. Les tâches ont-elles une `date_fin` définie ?
2. Les tâches ont-elles un responsable assigné ?
3. Les tâches sont-elles dans un statut actif (pas TERMINEE) ?

```python
# Vérifier dans le shell Django
python manage.py shell

from core.models import TacheEtape
from datetime import date, timedelta

# Tâches avec échéance dans 2 jours
taches = TacheEtape.objects.filter(
    date_fin=date.today() + timedelta(days=2),
    statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']
).exclude(responsable__isnull=True)

print(f"Tâches trouvées : {taches.count()}")
for t in taches:
    print(f"- {t.nom} (responsable: {t.responsable.get_full_name()})")
```

### Problème : Doublons de notifications

Le système devrait éviter les doublons automatiquement. Si vous en voyez :
1. Vérifiez que la commande n'est pas exécutée plusieurs fois par jour
2. Vérifiez les logs du planificateur de tâches

### Problème : Notifications non visibles

1. Vérifier que les notifications sont créées :
```python
from core.models import NotificationTache
from datetime import date

notifs = NotificationTache.objects.filter(date_creation__date=date.today())
print(f"Notifications aujourd'hui : {notifs.count()}")
```

2. Vérifier l'interface de notifications dans l'application

## 📈 Statistiques

Pour voir les statistiques des alertes :

```python
from core.models import NotificationTache
from datetime import date, timedelta

# Alertes des 7 derniers jours
debut = date.today() - timedelta(days=7)
alertes = NotificationTache.objects.filter(
    date_creation__date__gte=debut,
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
)

print(f"Total alertes (7 jours) : {alertes.count()}")
print(f"Alertes échéance : {alertes.filter(type_notification='ALERTE_ECHEANCE').count()}")
print(f"Alertes critiques : {alertes.filter(type_notification='ALERTE_CRITIQUE').count()}")
print(f"Alertes retard : {alertes.filter(type_notification='ALERTE_RETARD').count()}")
```

## 🚀 Évolutions futures (Phase 2 et 3)

### Phase 2 - Alertes avancées
- Synthèse quotidienne pour responsable projet
- Alertes de tâches bloquées
- Alertes de tâches non assignées
- Alertes de surcharge (trop de tâches par personne)

### Phase 3 - Fonctionnalités expertes
- Prédiction de retard avec IA
- Alertes personnalisables par utilisateur
- Notifications par email/SMS
- Dashboard d'analyse des retards

## 📞 Support

Pour toute question ou problème :
1. Vérifier les logs de la commande
2. Exécuter le script de test
3. Consulter cette documentation

---

**Version** : 1.0  
**Date** : Février 2026  
**Auteur** : Système SI-Gouvernance JCM
