# 🚀 Démarrage Rapide - Système d'Alertes

## ✅ Ce qui a été créé

1. **Commande Django** : `core/management/commands/check_task_deadlines.py`
2. **Migration** : `core/migrations/0026_add_alert_notification_types.py`
3. **Script de test** : `test_alertes_echeances.py`
4. **Script Windows** : `run_check_deadlines.bat`
5. **Documentation complète** : `SYSTEME_ALERTES_ECHEANCES.md`

## 🎯 Types d'alertes

- 🟡 **2 jours avant** → Responsable tâche
- 🟠 **1 jour avant** → Responsable tâche
- 🔴 **Jour J** → Responsable tâche + Responsable projet
- 🔴 **Retard** → Responsable tâche + Responsable projet

## 🔧 Installation (3 étapes)

### 1. Appliquer la migration
```bash
python manage.py migrate
```

### 2. Tester
```bash
python test_alertes_echeances.py
```

### 3. Planifier (Windows)
1. Ouvrir **Planificateur de tâches**
2. Créer une tâche quotidienne à 8h
3. Action : Exécuter `run_check_deadlines.bat`

## 📊 Vérification rapide

```bash
# Exécuter manuellement
python manage.py check_task_deadlines

# Voir les notifications créées
python manage.py shell
>>> from core.models import NotificationTache
>>> from datetime import date
>>> NotificationTache.objects.filter(date_creation__date=date.today()).count()
```

## ✨ Prochaines étapes

Une fois testé et validé, vous pourrez ajouter :
- Synthèse quotidienne pour responsables projet
- Alertes de tâches bloquées
- Alertes de surcharge
- Notifications par email

---

**Tout est prêt à être testé ! 🎉**
