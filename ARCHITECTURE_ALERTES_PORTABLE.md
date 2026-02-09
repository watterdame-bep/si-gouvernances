# 🏗️ Architecture Portable du Système d'Alertes

## ✅ ARCHITECTURE ACTUELLE

### Séparation des responsabilités

```
┌─────────────────────────────────────────────────────────────┐
│                    LOGIQUE MÉTIER                           │
│         core/management/commands/check_task_deadlines.py    │
│                                                             │
│  - Vérification des échéances                              │
│  - Création des alertes                                    │
│  - Vérification des permissions                            │
│  - Gestion des doublons                                    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            │ Appel via
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│  Planificateur │  │    Cron     │  │     Celery      │
│    Windows     │  │   (Linux)   │  │  (Production)   │
│                │  │             │  │                 │
│  Task          │  │  0 8 * * *  │  │  @periodic_task │
│  Scheduler     │  │             │  │                 │
└────────────────┘  └─────────────┘  └─────────────────┘
```

### Avantages de cette architecture

✅ **Portabilité** : La logique métier est indépendante du système de planification
✅ **Testabilité** : Peut être testée manuellement avec `python manage.py check_task_deadlines`
✅ **Flexibilité** : Changement de planificateur sans toucher au code métier
✅ **Maintenabilité** : Un seul endroit pour modifier la logique d'alertes

## 🔄 OPTIONS DE MIGRATION

### Option 1 : Planificateur Windows (ACTUEL - Phase de test)

**Avantages** :
- ✅ Facile à configurer
- ✅ Intégré à Windows
- ✅ Interface graphique
- ✅ Logs automatiques

**Inconvénients** :
- ⚠️ Spécifique à Windows
- ⚠️ Nécessite que le serveur soit allumé

**Configuration** :
```batch
# run_check_deadlines.bat
@echo off
cd /d E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
python manage.py check_task_deadlines
```

**Commande** : Planificateur de tâches Windows (voir GUIDE_PLANIFICATEUR_WINDOWS.md)

---

### Option 2 : Cron (Linux/Production)

**Avantages** :
- ✅ Standard Linux
- ✅ Très fiable
- ✅ Léger en ressources
- ✅ Logs via syslog

**Inconvénients** :
- ⚠️ Spécifique à Linux
- ⚠️ Configuration en ligne de commande

**Configuration** :
```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne (exécution tous les jours à 8h00)
0 8 * * * cd /path/to/SI-GOUVERNANCE && /path/to/python manage.py check_task_deadlines >> /var/log/alertes.log 2>&1
```

**Avec environnement virtuel** :
```bash
0 8 * * * cd /path/to/SI-GOUVERNANCE && /path/to/venv/bin/python manage.py check_task_deadlines >> /var/log/alertes.log 2>&1
```

**Migration depuis Windows** :
1. Copier le projet sur le serveur Linux
2. Configurer le crontab
3. Tester : `python manage.py check_task_deadlines`
4. Vérifier les logs : `tail -f /var/log/alertes.log`

---

### Option 3 : Celery Beat (Production avancée)

**Avantages** :
- ✅ Asynchrone et distribué
- ✅ Gestion avancée des tâches
- ✅ Monitoring intégré
- ✅ Retry automatique en cas d'erreur
- ✅ Multi-plateforme (Windows, Linux, Mac)

**Inconvénients** :
- ⚠️ Nécessite Redis ou RabbitMQ
- ⚠️ Configuration plus complexe
- ⚠️ Plus de ressources

**Installation** :
```bash
pip install celery redis
```

**Configuration** :

1. **Créer `si_gouvernance/celery.py`** :
```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')

app = Celery('si_gouvernance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'check-task-deadlines-daily': {
        'task': 'core.tasks.check_task_deadlines',
        'schedule': crontab(hour=8, minute=0),  # Tous les jours à 8h00
    },
}
```

2. **Créer `core/tasks.py`** :
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def check_task_deadlines():
    """
    Tâche Celery pour vérifier les échéances
    Appelle simplement le management command existant
    """
    call_command('check_task_deadlines')
```

3. **Ajouter dans `si_gouvernance/__init__.py`** :
```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

4. **Ajouter dans `settings.py`** :
```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Paris'
```

**Démarrage** :
```bash
# Terminal 1 : Démarrer Redis
redis-server

# Terminal 2 : Démarrer Celery Worker
celery -A si_gouvernance worker -l info

# Terminal 3 : Démarrer Celery Beat (planificateur)
celery -A si_gouvernance beat -l info
```

**Migration depuis Windows/Cron** :
1. Installer Redis
2. Créer les fichiers Celery
3. Démarrer les services
4. Désactiver l'ancien planificateur

---

### Option 4 : Django-Q (Alternative légère à Celery)

**Avantages** :
- ✅ Plus simple que Celery
- ✅ Intégré à Django Admin
- ✅ Utilise la base de données Django (pas besoin de Redis)
- ✅ Interface web pour monitoring

**Inconvénients** :
- ⚠️ Moins performant que Celery pour gros volumes
- ⚠️ Moins de fonctionnalités avancées

**Installation** :
```bash
pip install django-q
```

**Configuration** :

1. **Ajouter dans `settings.py`** :
```python
INSTALLED_APPS = [
    # ...
    'django_q',
]

Q_CLUSTER = {
    'name': 'SI-Gouvernance',
    'workers': 4,
    'recycle': 500,
    'timeout': 60,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'default',
}
```

2. **Migrations** :
```bash
python manage.py migrate
```

3. **Créer une tâche planifiée** :
```python
# Dans Django shell ou un script
from django_q.models import Schedule

Schedule.objects.create(
    func='django.core.management.call_command',
    args="'check_task_deadlines'",
    schedule_type=Schedule.DAILY,
    next_run=timezone.now().replace(hour=8, minute=0, second=0),
    name='Vérification échéances quotidienne'
)
```

**Démarrage** :
```bash
python manage.py qcluster
```

**Interface Admin** :
- Aller sur `/admin/django_q/`
- Voir les tâches planifiées, l'historique, les résultats

---

## 📊 COMPARAISON DES OPTIONS

| Critère | Windows Task | Cron | Celery | Django-Q |
|---------|-------------|------|--------|----------|
| **Complexité** | ⭐ Facile | ⭐⭐ Moyen | ⭐⭐⭐⭐ Complexe | ⭐⭐⭐ Moyen |
| **Portabilité** | ❌ Windows | ❌ Linux | ✅ Multi-OS | ✅ Multi-OS |
| **Performance** | ⭐⭐⭐ Bon | ⭐⭐⭐ Bon | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐ Bon |
| **Monitoring** | ⭐⭐ Basique | ⭐ Logs | ⭐⭐⭐⭐ Avancé | ⭐⭐⭐⭐ Interface web |
| **Dépendances** | ✅ Aucune | ✅ Aucune | ❌ Redis/RabbitMQ | ✅ Aucune |
| **Retry auto** | ⚠️ Manuel | ⚠️ Manuel | ✅ Automatique | ✅ Automatique |
| **Scalabilité** | ⭐ Faible | ⭐⭐ Moyenne | ⭐⭐⭐⭐⭐ Excellente | ⭐⭐⭐ Bonne |

## 🎯 RECOMMANDATIONS PAR PHASE

### Phase 1 : Développement/Test (ACTUEL)
**Recommandation** : **Planificateur Windows**
- Simple à configurer
- Pas de dépendances
- Facile à déboguer

### Phase 2 : Pré-production
**Recommandation** : **Cron** (si Linux) ou **Django-Q**
- Cron : Si serveur Linux simple
- Django-Q : Si besoin d'interface de monitoring

### Phase 3 : Production
**Recommandation** : **Celery Beat**
- Scalabilité
- Fiabilité
- Monitoring avancé
- Gestion d'erreurs

## 🔄 PLAN DE MIGRATION

### Étape 1 : Validation (ACTUEL)
```bash
# Tester le management command
python manage.py check_task_deadlines

# Vérifier les résultats
python verification_systeme_alertes.py
```

### Étape 2 : Planificateur Windows (Phase de test)
```
1. Configurer Task Scheduler
2. Tester pendant 1 semaine
3. Valider que les alertes sont créées correctement
```

### Étape 3 : Migration vers production
```
Option A (Cron) :
1. Déployer sur serveur Linux
2. Configurer crontab
3. Tester l'exécution
4. Monitorer les logs

Option B (Celery) :
1. Installer Redis
2. Créer les fichiers Celery
3. Configurer les tâches périodiques
4. Démarrer les workers
5. Monitorer via Flower (interface web)

Option C (Django-Q) :
1. Installer django-q
2. Créer la tâche planifiée
3. Démarrer qcluster
4. Monitorer via Django Admin
```

## 📝 CHECKLIST DE MIGRATION

Quelle que soit l'option choisie, vérifier :

- [ ] Le management command fonctionne manuellement
- [ ] Les permissions d'accès projet sont respectées
- [ ] Les doublons sont évités
- [ ] Les logs sont accessibles
- [ ] Le système peut être redémarré facilement
- [ ] Les erreurs sont gérées correctement
- [ ] Un monitoring est en place
- [ ] La documentation est à jour

## 🎉 CONCLUSION

Votre architecture est **déjà portable** ! La logique métier est dans le management command Django, ce qui permet de changer de planificateur sans modifier le code.

**Actuellement** :
```bash
python manage.py check_task_deadlines  # ✅ Fonctionne
```

**Avec n'importe quel planificateur** :
```bash
# Windows Task Scheduler
run_check_deadlines.bat

# Cron
0 8 * * * python manage.py check_task_deadlines

# Celery
call_command('check_task_deadlines')

# Django-Q
call_command('check_task_deadlines')
```

**La logique métier reste identique** : vérification des échéances, création des alertes, respect des permissions. Seul le **déclencheur** change.

---

**Date** : 09/02/2026  
**Architecture** : ✅ Portable et prête pour migration  
**Prochaine étape** : Test avec Planificateur Windows, puis migration vers Celery en production
