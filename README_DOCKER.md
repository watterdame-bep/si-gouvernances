# SI-Gouvernance - Déploiement Docker Production

## 🎯 Vue d'Ensemble

Architecture complète production-ready avec:
- **Django** (Gunicorn) - Application web
- **Celery Worker** - Exécution des tâches asynchrones
- **Celery Beat** - Planification automatique (toutes les 4 heures)
- **Redis** - Broker Celery + Cache
- **MySQL** - Base de données
- **Flower** - Monitoring Celery (optionnel)

## ⚡ Quick Start

### 1. Prérequis

```bash
# Vérifier Docker
docker --version  # 20.10+
docker-compose --version  # 2.0+
```

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp .env.docker.example .env

# Éditer avec vos valeurs
nano .env
```

**Variables critiques à modifier:**
- `DJANGO_SECRET_KEY` - Générer une clé unique
- `DB_PASSWORD` - Mot de passe fort
- `EMAIL_HOST_USER` - Votre email Gmail
- `EMAIL_HOST_PASSWORD` - Mot de passe d'application Gmail

### 3. Démarrage

```bash
# Méthode 1: Script automatique (recommandé)
chmod +x docker-start.sh
./docker-start.sh --fresh

# Méthode 2: Manuelle
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Vérification

```bash
# Tester Celery
docker-compose exec web python test_celery_docker.py

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f
```

## 📋 Tâches Automatiques

Les alertes s'exécutent **automatiquement toutes les 4 heures** (0h, 4h, 8h, 12h, 16h, 20h):

| Tâche | Horaire | Description |
|-------|---------|-------------|
| Échéances projets | XX:00 | J-7, J-3, J-1, retards |
| Retards étapes | XX:05 | Étapes en retard |
| Tâches en retard | XX:10 | Tâches dépassées |
| Budgets | XX:15 | Dépassements budget |
| Contrats | XX:20 | Expirations contrats |

## 🔍 Monitoring

### Logs en Temps Réel

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f celery_beat
docker-compose logs -f celery_worker
```

### Flower (Interface Web)

```bash
# Démarrer avec Flower
docker-compose --profile monitoring up -d

# Accéder à: http://localhost:5555
# Credentials: Définis dans .env
```

### Commandes Utiles

```bash
# État des services
docker-compose ps

# Santé Celery
docker-compose exec celery_worker celery -A si_gouvernance inspect ping

# Tâches actives
docker-compose exec celery_worker celery -A si_gouvernance inspect active

# Tâches planifiées
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> for task in PeriodicTask.objects.all():
...     print(f"{task.name}: {task.enabled}")
```

## 🧪 Tests

### Test Complet

```bash
docker-compose exec web python test_celery_docker.py
```

### Tests Manuels

```bash
# Tester une commande d'alerte
docker-compose exec web python manage.py check_project_deadlines

# Tester l'envoi d'email
docker-compose exec web python test_email_smtp.py

# Shell Django
docker-compose exec web python manage.py shell
```

## 🔄 Opérations Courantes

### Mise à Jour

```bash
git pull
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup Base de Données

```bash
# Backup
docker-compose exec db mysqldump -u root -p${DB_ROOT_PASSWORD} si_gouvernance > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db mysql -u root -p${DB_ROOT_PASSWORD} si_gouvernance < backup_20260216.sql
```

### Redémarrage

```bash
# Tous les services
docker-compose restart

# Service spécifique
docker-compose restart celery_beat
```

## 🐛 Dépannage

### Les Tâches ne S'Exécutent Pas

```bash
# 1. Vérifier Beat
docker-compose logs celery_beat | grep -i error

# 2. Vérifier Worker
docker-compose logs celery_worker | grep -i error

# 3. Vérifier les tâches planifiées
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.filter(enabled=True).count()
```

### Erreurs Redis

```bash
# Vérifier Redis
docker-compose ps redis
docker-compose exec redis redis-cli ping
```

### Erreurs Base de Données

```bash
# Vérifier MySQL
docker-compose ps db
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

## 📊 Performance

### Scaling Workers

```bash
# Augmenter le nombre de workers
docker-compose up -d --scale celery_worker=3
```

### Optimisation Redis

Modifier `docker-compose.yml`:

```yaml
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

## 🔒 Sécurité Production

### Checklist

- [ ] `DJANGO_DEBUG=False`
- [ ] `DJANGO_SECRET_KEY` unique et fort
- [ ] Mots de passe forts (DB, Flower)
- [ ] `ALLOWED_HOSTS` configuré
- [ ] HTTPS activé (reverse proxy)
- [ ] Firewall configuré
- [ ] Backups automatiques
- [ ] Monitoring actif

### Ports à Protéger

- 3306 (MySQL) - Accès interne uniquement
- 6379 (Redis) - Accès interne uniquement
- 8000 (Django) - Via reverse proxy uniquement

## 📁 Structure des Fichiers

```
SI-GOUVERNANCE/
├── docker-compose.yml          # Configuration Docker
├── Dockerfile                  # Image Docker
├── .env                        # Variables d'environnement (à créer)
├── .env.docker.example         # Template .env
├── docker-start.sh             # Script de démarrage
├── test_celery_docker.py       # Tests Celery
├── si_gouvernance/
│   ├── celery.py              # Configuration Celery
│   ├── settings.py            # Settings Django (avec Celery)
│   └── __init__.py            # Import Celery
├── core/
│   └── tasks.py               # Tâches Celery
└── logs/
    ├── django.log             # Logs Django
    └── celery/
        └── celery.log         # Logs Celery
```

## 🚀 Déploiement VPS

### Installation Serveur

```bash
# 1. Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Cloner et démarrer
git clone <votre-repo>
cd SI-GOUVERNANCE
cp .env.docker.example .env
nano .env
./docker-start.sh --fresh
```

## 📞 Support

### Documentation Complète

Voir `DEPLOIEMENT_DOCKER_PRODUCTION.md` pour:
- Guide détaillé étape par étape
- Configuration avancée
- Monitoring et logs
- Sécurité production
- Scaling et performance

### Logs Importants

- Django: `logs/django.log`
- Celery: `logs/celery/celery.log`
- Docker: `docker-compose logs`

### Commandes de Debug

```bash
# État complet
docker-compose ps
docker-compose logs --tail=50

# Santé application
docker-compose exec web python manage.py check --deploy

# Test Celery
docker-compose exec web python test_celery_docker.py
```

## ✅ Checklist Post-Déploiement

- [ ] Tous les services UP
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Tests Celery passés
- [ ] Email de test envoyé
- [ ] Logs sans erreurs
- [ ] Tâches planifiées actives
- [ ] Application accessible

---

**🎉 Votre application est prête pour la production!**

Les alertes s'exécuteront automatiquement toutes les 4 heures sans intervention manuelle.
