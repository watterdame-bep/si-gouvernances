# Solution Alertes Automatiques dans Docker

## 🎯 RÉPONSE À VOTRE QUESTION

**Question**: Si je déploie dans Docker, est-ce que les alertes vont se déclencher automatiquement?

**Réponse**: ❌ NON, pas sans configuration supplémentaire!

Le Planificateur de tâches Windows ne fonctionne pas dans Docker. Il faut utiliser **Celery Beat** à la place.

---

## 📊 COMPARAISON DES SOLUTIONS

| Critère | Windows Task Scheduler | Celery Beat (Docker) |
|---------|------------------------|----------------------|
| **Environnement** | Windows uniquement | Linux/Docker/Production |
| **Configuration** | Interface graphique | Code Python |
| **Portabilité** | ❌ Non portable | ✅ Portable |
| **Production** | ❌ Non recommandé | ✅ Recommandé |
| **Complexité** | Simple | Moyenne |

---

## ✅ SOLUTION RECOMMANDÉE: CELERY BEAT

Celery Beat est le standard Django pour les tâches planifiées en production.

### Avantages
- ✅ Fonctionne dans Docker
- ✅ Portable (Windows, Linux, Mac)
- ✅ Standard de l'industrie
- ✅ Robuste et fiable
- ✅ Monitoring intégré

---

## 🚀 IMPLÉMENTATION CELERY BEAT

### Étape 1: Installer les dépendances

Ajouter à `requirements.txt`:
```
celery==5.3.4
redis==5.0.1
django-celery-beat==2.5.0
```

### Étape 2: Configuration Celery

Créer `si_gouvernance/celery.py`:
```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')

app = Celery('si_gouvernance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches planifiées
app.conf.beat_schedule = {
    'check-project-deadlines': {
        'task': 'core.tasks.check_project_deadlines_task',
        'schedule': crontab(hour=9, minute=0),  # 09:00 tous les jours
    },
    'check-stage-delays': {
        'task': 'core.tasks.check_stage_delays_task',
        'schedule': crontab(hour=9, minute=15),  # 09:15 tous les jours
    },
    'check-task-deadlines': {
        'task': 'core.tasks.check_task_deadlines_task',
        'schedule': crontab(hour=9, minute=30),  # 09:30 tous les jours
    },
    'check-budget': {
        'task': 'core.tasks.check_budget_task',
        'schedule': crontab(hour=10, minute=0),  # 10:00 tous les jours
    },
    'check-contract-expiration': {
        'task': 'core.tasks.check_contract_expiration_task',
        'schedule': crontab(hour=10, minute=15),  # 10:15 tous les jours
    },
}
```

### Étape 3: Créer les tâches Celery

Créer `core/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_project_deadlines_task():
    """Vérifie les échéances de projets"""
    try:
        call_command('check_project_deadlines')
        logger.info("✅ Vérification des échéances de projets terminée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des échéances: {e}")

@shared_task
def check_stage_delays_task():
    """Vérifie les retards d'étapes"""
    try:
        call_command('check_stage_delays')
        logger.info("✅ Vérification des retards d'étapes terminée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des retards d'étapes: {e}")

@shared_task
def check_task_deadlines_task():
    """Vérifie les tâches en retard"""
    try:
        call_command('check_task_deadlines')
        logger.info("✅ Vérification des tâches en retard terminée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des tâches: {e}")

@shared_task
def check_budget_task():
    """Vérifie les dépassements de budget"""
    try:
        call_command('check_budget')
        logger.info("✅ Vérification des budgets terminée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des budgets: {e}")

@shared_task
def check_contract_expiration_task():
    """Vérifie les expirations de contrats"""
    try:
        call_command('check_contract_expiration')
        logger.info("✅ Vérification des contrats terminée")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des contrats: {e}")
```

### Étape 4: Modifier `si_gouvernance/__init__.py`

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### Étape 5: Configuration Django

Ajouter à `si_gouvernance/settings.py`:
```python
# Configuration Celery
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Paris'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

### Étape 6: Docker Compose

Créer/modifier `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: si_gouvernance
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_USER: si_user
      MYSQL_PASSWORD: si_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=mysql://si_user:si_password@db:3306/si_gouvernance
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery_worker:
    build: .
    command: celery -A si_gouvernance worker --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=mysql://si_user:si_password@db:3306/si_gouvernance
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery_beat:
    build: .
    command: celery -A si_gouvernance beat --loglevel=info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=mysql://si_user:si_password@db:3306/si_gouvernance
      - CELERY_BROKER_URL=redis://redis:6379/0

volumes:
  mysql_data:
```

### Étape 7: Dockerfile

Créer `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

---

## 🎯 DÉMARRAGE

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Appliquer les migrations
```bash
python manage.py migrate
```

### 3. Démarrer Docker Compose
```bash
docker-compose up -d
```

### 4. Vérifier que tout fonctionne
```bash
# Vérifier les conteneurs
docker-compose ps

# Vérifier les logs de Celery Beat
docker-compose logs -f celery_beat

# Vérifier les logs du worker
docker-compose logs -f celery_worker
```

---

## 📋 PLANIFICATION DES TÂCHES

Les tâches s'exécuteront automatiquement:

| Heure | Tâche | Description |
|-------|-------|-------------|
| 09:00 | check_project_deadlines | Échéances J-7, J-3, J-1, retards |
| 09:15 | check_stage_delays | Retards d'étapes |
| 09:30 | check_task_deadlines | Tâches en retard |
| 10:00 | check_budget | Dépassements de budget |
| 10:15 | check_contract_expiration | Expirations de contrats |

---

## 🔍 MONITORING

### Vérifier les tâches planifiées
```bash
# Entrer dans le conteneur
docker-compose exec web python manage.py shell

# Lister les tâches
from django_celery_beat.models import PeriodicTask
for task in PeriodicTask.objects.all():
    print(f"{task.name}: {task.enabled}")
```

### Voir les logs en temps réel
```bash
# Logs de Celery Beat (planificateur)
docker-compose logs -f celery_beat

# Logs du worker (exécution)
docker-compose logs -f celery_worker

# Logs de l'application
docker-compose logs -f web
```

### Tester manuellement une tâche
```bash
docker-compose exec web python manage.py shell

from core.tasks import check_project_deadlines_task
check_project_deadlines_task.delay()
```

---

## ✅ AVANTAGES DE CETTE SOLUTION

1. **Portable**: Fonctionne partout (Windows, Linux, Mac, Cloud)
2. **Production-ready**: Standard de l'industrie
3. **Robuste**: Retry automatique en cas d'erreur
4. **Monitoring**: Logs détaillés et interface d'administration
5. **Scalable**: Peut gérer des milliers de tâches
6. **Flexible**: Facile de modifier les horaires

---

## 🆚 COMPARAISON AVEC WINDOWS TASK SCHEDULER

### Windows Task Scheduler (Solution actuelle)
```
✅ Simple à configurer (interface graphique)
✅ Pas de dépendances supplémentaires
❌ Windows uniquement
❌ Pas portable
❌ Difficile à versionner
❌ Pas adapté pour Docker/Production
```

### Celery Beat (Solution recommandée)
```
✅ Portable (tous OS)
✅ Production-ready
✅ Versionnable (code)
✅ Fonctionne dans Docker
✅ Monitoring intégré
✅ Standard de l'industrie
⚠️ Nécessite Redis
⚠️ Configuration plus complexe
```

---

## 🎯 RECOMMANDATION

### Pour le développement local sur Windows
- ✅ Utiliser le Planificateur de tâches Windows (solution actuelle)
- Simple et rapide à mettre en place

### Pour Docker / Production
- ✅ Utiliser Celery Beat (solution recommandée)
- Standard de l'industrie, robuste et portable

---

## 📝 RÉSUMÉ

**Question**: Les alertes se déclenchent-elles automatiquement dans Docker?

**Réponse**: 
- ❌ Non, pas avec le Planificateur Windows
- ✅ Oui, avec Celery Beat (configuration nécessaire)

**Solution**: Implémenter Celery Beat pour Docker (voir ci-dessus)

**Temps d'implémentation**: ~30 minutes

**Complexité**: Moyenne (mais standard de l'industrie)

---

## 🚀 PROCHAINES ÉTAPES

1. Décider de l'environnement de déploiement:
   - Local Windows → Garder Task Scheduler
   - Docker/Production → Implémenter Celery Beat

2. Si Docker, suivre les étapes ci-dessus

3. Tester les tâches planifiées

4. Monitorer les logs

---

**Le système de notifications est prêt, il ne manque que le planificateur adapté à votre environnement!** 🎉
