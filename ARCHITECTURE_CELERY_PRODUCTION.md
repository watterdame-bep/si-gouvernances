# Architecture Celery + Redis Production - SI-Gouvernance

## 📐 Vue d'Ensemble de l'Architecture

### Schéma Complet

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SI-GOUVERNANCE PRODUCTION                        │
│                     Architecture Celery + Redis + Docker                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            COUCHE APPLICATION                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐         ┌──────────────────┐                     │
│  │   Django Web     │         │  Celery Worker   │                     │
│  │   (Gunicorn)     │         │  (Async Tasks)   │                     │
│  │   Port: 8000     │         │  Concurrency: 2  │                     │
│  │   Workers: 4     │         │  Max Tasks: 1000 │                     │
│  └────────┬─────────┘         └────────┬─────────┘                     │
│           │                            │                                │
│           │    ┌──────────────────┐    │                                │
│           │    │  Celery Beat     │    │                                │
│           │    │  (Scheduler)     │    │                                │
│           │    │  Every 4 hours   │    │                                │
│           │    └────────┬─────────┘    │                                │
│           │             │              │                                │
└───────────┼─────────────┼──────────────┼────────────────────────────────┘
            │             │              │
┌───────────┼─────────────┼──────────────┼────────────────────────────────┐
│           │             │              │    COUCHE DONNÉES              │
├───────────┼─────────────┼──────────────┼────────────────────────────────┤
│           │             │              │                                │
│           ▼             ▼              ▼                                │
│  ┌─────────────────────────────────────────────┐                       │
│  │              Redis (Broker)                  │                       │
│  │  - Message Queue (Celery)                    │                       │
│  │  - Result Backend                            │                       │
│  │  - Cache                                     │                       │
│  │  Port: 6379                                  │                       │
│  └─────────────────────────────────────────────┘                       │
│                                                                          │
│  ┌─────────────────────────────────────────────┐                       │
│  │              MySQL Database                  │                       │
│  │  - Application Data                          │                       │
│  │  - Celery Beat Schedule                      │                       │
│  │  - Task Results                              │                       │
│  │  Port: 3306                                  │                       │
│  └─────────────────────────────────────────────┘                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         COUCHE MONITORING (Optionnel)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    Flower Dashboard                           │      │
│  │  - Real-time task monitoring                                 │      │
│  │  - Worker status                                             │      │
│  │  - Task history                                              │      │
│  │  - Performance metrics                                       │      │
│  │  Port: 5555                                                  │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flux d'Exécution des Tâches

### 1. Planification (Celery Beat)

```
Celery Beat (Scheduler)
    │
    ├─ Lit la planification depuis la DB (django_celery_beat)
    │
    ├─ Toutes les 4 heures (0h, 4h, 8h, 12h, 16h, 20h):
    │   │
    │   ├─ XX:00 → check_project_deadlines_task
    │   ├─ XX:05 → check_stage_delays_task
    │   ├─ XX:10 → check_task_deadlines_task
    │   ├─ XX:15 → check_budget_task
    │   └─ XX:20 → check_contract_expiration_task
    │
    └─ Envoie les tâches à Redis (broker)
```

### 2. Exécution (Celery Worker)

```
Celery Worker
    │
    ├─ Écoute Redis pour nouvelles tâches
    │
    ├─ Reçoit une tâche (ex: check_project_deadlines_task)
    │
    ├─ Exécute la tâche:
    │   │
    │   ├─ Appelle la commande Django management
    │   │   (ex: python manage.py check_project_deadlines)
    │   │
    │   ├─ La commande:
    │   │   ├─ Interroge la base de données
    │   │   ├─ Identifie les projets concernés
    │   │   ├─ Crée des AlerteProjet
    │   │   └─ Les signaux Django envoient les emails
    │   │
    │   └─ Retourne le résultat
    │
    ├─ Stocke le résultat dans Redis
    │
    └─ Passe à la tâche suivante
```

### 3. Notification (Signaux Django)

```
Signal Django (post_save)
    │
    ├─ Détecte la création d'une AlerteProjet
    │
    ├─ Appelle envoyer_email_alerte_projet()
    │
    ├─ Génère l'email HTML
    │
    ├─ Envoie via SMTP Gmail
    │
    └─ Log le résultat
```

---

## 📊 Configuration des Tâches

### Planification Actuelle

| Tâche | Crontab | Fréquence | Description |
|-------|---------|-----------|-------------|
| check_project_deadlines | `0 */4 * * *` | Toutes les 4h à XX:00 | Échéances J-7, J-3, J-1, retards |
| check_stage_delays | `5 */4 * * *` | Toutes les 4h à XX:05 | Retards d'étapes |
| check_task_deadlines | `10 */4 * * *` | Toutes les 4h à XX:10 | Tâches en retard |
| check_budget | `15 */4 * * *` | Toutes les 4h à XX:15 | Dépassements budget |
| check_contract_expiration | `20 */4 * * *` | Toutes les 4h à XX:20 | Expirations contrats |

### Horaires d'Exécution

```
00:00 → Vérification complète (5 tâches sur 25 minutes)
04:00 → Vérification complète (5 tâches sur 25 minutes)
08:00 → Vérification complète (5 tâches sur 25 minutes)
12:00 → Vérification complète (5 tâches sur 25 minutes)
16:00 → Vérification complète (5 tâches sur 25 minutes)
20:00 → Vérification complète (5 tâches sur 25 minutes)
```

---

## 🔧 Configuration Technique

### Celery Worker

```python
# Configuration dans si_gouvernance/celery.py
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Une tâche à la fois
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Redémarre après 1000 tâches
CELERY_TASK_ACKS_LATE = True  # Acknowledge après exécution
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Rejeter si crash
CELERY_TASK_TRACK_STARTED = True  # Tracker le début
```

### Retry Automatique

```python
# Configuration dans core/tasks.py
TASK_CONFIG = {
    'autoretry_for': (Exception,),  # Retry sur toute exception
    'retry_kwargs': {
        'max_retries': 3,  # 3 tentatives max
        'countdown': 60,  # 60 secondes entre tentatives
    },
}
```

### Expiration des Tâches

```python
# Dans si_gouvernance/celery.py
'options': {
    'expires': 3600 * 3,  # Expire après 3h (avant prochaine exécution)
}
```

---

## 🛡️ Sécurité et Robustesse

### Protection Contre Exécutions Multiples

1. **Task ID Unique**: Chaque tâche a un ID unique
2. **Expiration**: Les tâches expirent après 3h
3. **Acks Late**: Acknowledge après exécution complète
4. **Reject on Lost**: Rejeter si worker crash

### Gestion des Erreurs

```python
# Dans chaque tâche
try:
    call_command('check_project_deadlines')
    logger.info("✅ Succès")
except Exception as e:
    logger.error(f"❌ Erreur: {e}")
    raise  # Retry automatique
```

### Logs Détaillés

```python
# Format des logs
[2026-02-16 12:00:00: INFO/Worker-1][check_project_deadlines_task(abc123)] 
🚀 Démarrage: Vérification des échéances de projets
```

---

## 📈 Monitoring et Métriques

### Flower Dashboard

Accessible sur `http://localhost:5555`:

- **Tasks**: Liste de toutes les tâches (actives, terminées, échouées)
- **Workers**: État des workers (actifs, inactifs)
- **Monitor**: Graphiques en temps réel
- **Broker**: État de Redis
- **Configuration**: Paramètres Celery

### Commandes de Monitoring

```bash
# État des workers
celery -A si_gouvernance inspect active

# Tâches planifiées
celery -A si_gouvernance inspect scheduled

# Statistiques
celery -A si_gouvernance inspect stats

# Ping workers
celery -A si_gouvernance inspect ping
```

### Logs

```bash
# Logs Celery
tail -f logs/celery/celery.log

# Logs Django
tail -f logs/django.log

# Logs Docker
docker-compose logs -f celery_beat
docker-compose logs -f celery_worker
```

---

## 🚀 Scaling et Performance

### Scaling Horizontal

```bash
# Ajouter des workers
docker-compose up -d --scale celery_worker=3

# Vérifier
docker-compose ps
```

### Optimisation Redis

```yaml
# docker-compose.yml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Optimisation Worker

```yaml
# docker-compose.yml
celery_worker:
  command: celery -A si_gouvernance worker --concurrency=4 --max-tasks-per-child=1000
```

---

## 🔍 Dépannage

### Problème: Tâches ne S'Exécutent Pas

**Diagnostic:**
```bash
# 1. Vérifier Beat
docker-compose logs celery_beat | grep -i error

# 2. Vérifier Worker
docker-compose logs celery_worker | grep -i error

# 3. Vérifier planification
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> for task in PeriodicTask.objects.all():
...     print(f"{task.name}: enabled={task.enabled}")
```

**Solutions:**
1. Redémarrer Beat: `docker-compose restart celery_beat`
2. Réinitialiser tâches: `docker-compose exec web python manage.py setup_celery_beat`
3. Vérifier Redis: `docker-compose exec redis redis-cli ping`

### Problème: Worker Crash

**Diagnostic:**
```bash
docker-compose logs celery_worker --tail=100
```

**Solutions:**
1. Augmenter la mémoire: Modifier `docker-compose.yml`
2. Réduire concurrency: `--concurrency=1`
3. Vérifier les erreurs dans les tâches

### Problème: Redis Plein

**Diagnostic:**
```bash
docker-compose exec redis redis-cli INFO memory
```

**Solutions:**
1. Augmenter maxmemory: `--maxmemory 512mb`
2. Nettoyer: `docker-compose exec redis redis-cli FLUSHDB`
3. Vérifier expiration des résultats

---

## 📋 Checklist Production

### Avant Déploiement

- [ ] `.env` configuré avec valeurs production
- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_SECRET_KEY` unique et fort
- [ ] Mots de passe forts (DB, Flower)
- [ ] `ALLOWED_HOSTS` configuré
- [ ] Email SMTP configuré et testé
- [ ] Backups configurés
- [ ] Monitoring configuré (Flower)

### Après Déploiement

- [ ] Tous les services UP
- [ ] Migrations appliquées
- [ ] Tâches planifiées créées
- [ ] Test Celery passé (`test_celery_docker.py`)
- [ ] Email de test envoyé
- [ ] Logs sans erreurs
- [ ] Flower accessible (si activé)
- [ ] Application accessible

### Maintenance Régulière

- [ ] Vérifier logs quotidiennement
- [ ] Monitorer Flower hebdomadairement
- [ ] Backup DB hebdomadairement
- [ ] Mettre à jour dépendances mensuellement
- [ ] Vérifier espace disque mensuellement

---

## 📚 Fichiers Importants

### Configuration

- `si_gouvernance/celery.py` - Configuration Celery
- `si_gouvernance/settings.py` - Settings Django + Celery
- `core/tasks.py` - Définition des tâches
- `docker-compose.yml` - Architecture Docker
- `.env` - Variables d'environnement

### Scripts

- `docker-start.sh` - Démarrage automatique
- `test_celery_docker.py` - Tests Celery
- `core/management/commands/setup_celery_beat.py` - Init tâches

### Documentation

- `README_DOCKER.md` - Quick start
- `DEPLOIEMENT_DOCKER_PRODUCTION.md` - Guide complet
- `ARCHITECTURE_CELERY_PRODUCTION.md` - Ce fichier

---

## 🎯 Résumé

### Ce Qui Est Automatisé

✅ Vérification des échéances projets (toutes les 4h)
✅ Vérification des retards d'étapes (toutes les 4h)
✅ Vérification des tâches en retard (toutes les 4h)
✅ Vérification des budgets (toutes les 4h)
✅ Vérification des contrats (toutes les 4h)
✅ Envoi automatique d'emails
✅ Retry automatique en cas d'échec
✅ Logs détaillés
✅ Monitoring via Flower

### Ce Qui Nécessite Intervention

⚠️ Configuration initiale (`.env`)
⚠️ Démarrage des services Docker
⚠️ Création du superuser
⚠️ Monitoring des logs (recommandé)
⚠️ Backups réguliers (recommandé)

---

**🎉 Architecture Production-Ready Complète!**

Votre système d'alertes est maintenant entièrement automatisé et prêt pour un déploiement entreprise long terme.
