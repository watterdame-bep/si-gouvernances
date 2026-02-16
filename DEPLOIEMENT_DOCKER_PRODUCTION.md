# Guide de Déploiement Docker Production - SI-Gouvernance

## 🎯 Architecture Complète

### Services Docker

```
┌─────────────────────────────────────────────────────────────┐
│                    SI-GOUVERNANCE                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   WEB    │  │  CELERY  │  │  CELERY  │  │  FLOWER  │   │
│  │  Django  │  │  WORKER  │  │   BEAT   │  │ Monitor  │   │
│  │  :8000   │  │          │  │          │  │  :5555   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
│       └─────────────┴──────────────┴─────────────┘          │
│                     │              │                        │
│              ┌──────┴──────┐  ┌───┴────┐                   │
│              │    REDIS    │  │  MYSQL │                   │
│              │   :6379     │  │  :3306 │                   │
│              └─────────────┘  └────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Rôles des Services

1. **web**: Application Django (Gunicorn)
2. **celery_worker**: Exécute les tâches asynchrones
3. **celery_beat**: Planifie les tâches (toutes les 4 heures)
4. **redis**: Broker Celery + Cache
5. **db**: Base de données MySQL
6. **flower**: Monitoring Celery (optionnel)

---

## 📋 Prérequis

### Logiciels Requis

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git

### Vérification

```bash
docker --version
docker-compose --version
```

---

## 🚀 Installation Initiale

### Étape 1: Cloner le Projet

```bash
git clone <votre-repo>
cd SI-GOUVERNANCE
```

### Étape 2: Configuration Environnement

```bash
# Copier le fichier d'exemple
cp .env.docker.example .env

# Éditer avec vos valeurs
nano .env
```

### Variables Critiques à Modifier

```env
# Django
DJANGO_SECRET_KEY=<générer-une-clé-secrète-50-chars>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com

# Base de données
DB_PASSWORD=<mot-de-passe-fort>
DB_ROOT_PASSWORD=<mot-de-passe-root-fort>

# Email
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=<mot-de-passe-application-gmail>

# Flower
FLOWER_PASSWORD=<mot-de-passe-fort>
```

### Étape 3: Générer une Clé Secrète Django

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Étape 4: Build des Images

```bash
docker-compose build
```

### Étape 5: Démarrage Initial

```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier que tous les services sont UP
docker-compose ps
```

### Étape 6: Migrations et Superuser

```bash
# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Créer un superuser
docker-compose exec web python manage.py createsuperuser

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput
```

---

## ⚙️ Configuration Celery Beat

### Initialiser les Tâches Planifiées

Les tâches sont automatiquement configurées dans `si_gouvernance/celery.py`.

Pour vérifier:

```bash
# Entrer dans le conteneur web
docker-compose exec web python manage.py shell

# Vérifier les tâches planifiées
from django_celery_beat.models import PeriodicTask
for task in PeriodicTask.objects.all():
    print(f"{task.name}: {task.enabled}")
```

### Planification Actuelle

Toutes les tâches s'exécutent **toutes les 4 heures** (0h, 4h, 8h, 12h, 16h, 20h):

| Tâche | Horaire | Description |
|-------|---------|-------------|
| check-project-deadlines | XX:00 | Échéances projets (J-7, J-3, J-1, retards) |
| check-stage-delays | XX:05 | Retards d'étapes |
| check-task-deadlines | XX:10 | Tâches en retard |
| check-budget | XX:15 | Dépassements de budget |
| check-contract-expiration | XX:20 | Expirations de contrats |

---

## 🔍 Monitoring et Logs

### Voir les Logs en Temps Réel

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f celery_beat
docker-compose logs -f celery_worker
docker-compose logs -f web

# Dernières 100 lignes
docker-compose logs --tail=100 celery_beat
```

### Flower (Interface Web)

Démarrer avec monitoring:

```bash
docker-compose --profile monitoring up -d
```

Accéder à: `http://localhost:5555`

Credentials: Définis dans `.env` (FLOWER_USER / FLOWER_PASSWORD)

### Vérifier l'État des Services

```bash
# État des conteneurs
docker-compose ps

# Santé des services
docker-compose exec web python manage.py check

# Ping Celery
docker-compose exec celery_worker celery -A si_gouvernance inspect ping

# Tâches actives
docker-compose exec celery_worker celery -A si_gouvernance inspect active

# Tâches planifiées
docker-compose exec celery_worker celery -A si_gouvernance inspect scheduled
```

---

## 🧪 Tests

### Tester Celery

```bash
# Entrer dans le shell Django
docker-compose exec web python manage.py shell

# Tester une tâche
from core.tasks import test_celery_task
result = test_celery_task.delay()
print(result.get())
```

### Tester les Alertes Manuellement

```bash
# Exécuter une commande manuellement
docker-compose exec web python manage.py check_project_deadlines
docker-compose exec web python manage.py check_stage_delays
docker-compose exec web python manage.py check_task_deadlines
docker-compose exec web python manage.py check_budget
docker-compose exec web python manage.py check_contract_expiration
```

### Tester l'Envoi d'Emails

```bash
docker-compose exec web python test_email_smtp.py
```

---

## 🔄 Commandes Utiles

### Démarrage / Arrêt

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer un service
docker-compose restart celery_beat

# Arrêter et supprimer les volumes (⚠️ PERTE DE DONNÉES)
docker-compose down -v
```

### Mise à Jour du Code

```bash
# Pull du nouveau code
git pull

# Rebuild si nécessaire
docker-compose build

# Redémarrer les services
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate

# Collecter les statiques
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup Base de Données

```bash
# Backup
docker-compose exec db mysqldump -u root -p${DB_ROOT_PASSWORD} si_gouvernance > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker-compose exec -T db mysql -u root -p${DB_ROOT_PASSWORD} si_gouvernance < backup_20260216_120000.sql
```

### Accès aux Conteneurs

```bash
# Shell dans le conteneur web
docker-compose exec web bash

# Shell Django
docker-compose exec web python manage.py shell

# MySQL
docker-compose exec db mysql -u root -p

# Redis CLI
docker-compose exec redis redis-cli
```

---

## 🔒 Sécurité Production

### Checklist Sécurité

- [ ] `DJANGO_DEBUG=False` dans `.env`
- [ ] `DJANGO_SECRET_KEY` unique et fort (50+ caractères)
- [ ] Mots de passe forts pour DB, Flower
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] HTTPS activé (reverse proxy Nginx/Traefik)
- [ ] Firewall configuré (ports 8000, 3306, 6379 fermés publiquement)
- [ ] Backups automatiques configurés
- [ ] Monitoring actif (Flower, logs)

### Configuration HTTPS (Nginx)

Exemple de configuration Nginx en reverse proxy:

```nginx
server {
    listen 80;
    server_name votre-domaine.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name votre-domaine.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }

    location /media/ {
        alias /path/to/media/;
    }
}
```

---

## 📊 Performance et Scaling

### Augmenter les Workers Celery

Modifier `docker-compose.yml`:

```yaml
celery_worker:
  command: celery -A si_gouvernance worker --loglevel=info --concurrency=4
```

### Ajouter des Workers Supplémentaires

```bash
docker-compose up -d --scale celery_worker=3
```

### Optimisation Redis

Modifier `docker-compose.yml`:

```yaml
redis:
  command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
```

---

## 🐛 Dépannage

### Les Tâches ne S'Exécutent Pas

```bash
# Vérifier que Beat est actif
docker-compose logs celery_beat

# Vérifier que Worker est actif
docker-compose logs celery_worker

# Vérifier les tâches planifiées
docker-compose exec web python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.filter(enabled=True).count()
```

### Erreurs de Connexion Redis

```bash
# Vérifier que Redis est UP
docker-compose ps redis

# Tester la connexion
docker-compose exec redis redis-cli ping
```

### Erreurs de Base de Données

```bash
# Vérifier que MySQL est UP
docker-compose ps db

# Tester la connexion
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

### Logs d'Erreurs

```bash
# Logs Django
docker-compose exec web cat logs/django.log

# Logs Celery
docker-compose exec web cat logs/celery/celery.log
```

---

## 📈 Monitoring Avancé

### Métriques Celery

```bash
# Stats du worker
docker-compose exec celery_worker celery -A si_gouvernance inspect stats

# Tâches enregistrées
docker-compose exec celery_worker celery -A si_gouvernance inspect registered

# Tâches actives
docker-compose exec celery_worker celery -A si_gouvernance inspect active
```

### Flower Dashboard

Accéder à `http://localhost:5555` pour voir:

- Tâches en cours
- Tâches terminées
- Tâches échouées
- Graphiques de performance
- Workers actifs

---

## 🚀 Déploiement VPS/Cloud

### Prérequis Serveur

- Ubuntu 20.04+ / Debian 11+
- 2 CPU minimum
- 4 GB RAM minimum
- 20 GB disque minimum
- Docker + Docker Compose installés

### Installation sur VPS

```bash
# 1. Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. Installer Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Cloner le projet
git clone <votre-repo>
cd SI-GOUVERNANCE

# 4. Configuration
cp .env.docker.example .env
nano .env

# 5. Démarrage
docker-compose up -d

# 6. Migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

---

## ✅ Checklist Déploiement

### Avant le Déploiement

- [ ] Code testé localement
- [ ] `.env` configuré avec valeurs production
- [ ] Secrets générés (SECRET_KEY, passwords)
- [ ] Backups configurés
- [ ] Monitoring configuré

### Après le Déploiement

- [ ] Tous les services UP (`docker-compose ps`)
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Tâches Celery planifiées actives
- [ ] Emails de test envoyés
- [ ] Logs vérifiés (pas d'erreurs)
- [ ] Flower accessible (si activé)
- [ ] Application accessible via navigateur

---

## 📞 Support

### Logs Importants

- Django: `logs/django.log`
- Celery: `logs/celery/celery.log`
- Docker: `docker-compose logs`

### Commandes de Debug

```bash
# État complet du système
docker-compose ps
docker-compose logs --tail=50

# Santé de l'application
docker-compose exec web python manage.py check --deploy

# Test Celery
docker-compose exec web python manage.py shell
>>> from core.tasks import test_celery_task
>>> test_celery_task.delay()
```

---

**🎉 Votre application SI-Gouvernance est maintenant déployée en production avec Celery + Redis!**

Les alertes s'exécuteront automatiquement toutes les 4 heures sans intervention manuelle.
