# 🚀 Déploiement SI-Gouvernance

## 📋 Prérequis

- Docker Desktop installé et démarré
- 4 GB RAM minimum
- Ports disponibles: 8000, 3306, 6379, 5555

## ⚡ Déploiement Local Rapide

### Windows

```cmd
deploy-local.bat
```

Choisir l'option **1** pour le premier déploiement.

### Linux/Mac

```bash
# Copier la configuration
cp .env.example .env

# Démarrer (mode local par défaut)
docker-compose up -d

# Attendre 30 secondes puis vérifier
docker-compose ps
```

## 🏭 Déploiement Production

```bash
# Copier la configuration production
cp .env.production.example .env.production

# Éditer .env.production avec vos valeurs

# Démarrer en mode production
docker-compose --profile production up -d
```

## 👤 Connexion (Local)

Après le déploiement local, un superutilisateur est créé automatiquement:

- **URL**: http://localhost:8000
- **Username**: `jovi`
- **Password**: `jovi123`

⚠️ **Changez le mot de passe après la première connexion!**

## 📊 Monitoring (Optionnel)

Pour activer Flower (monitoring Celery):

```bash
# Local
docker-compose --profile monitoring up -d

# Production
docker-compose --profile production --profile monitoring up -d
```

Accès: http://localhost:5555

## 🔄 Alertes Automatiques

Les alertes s'exécutent automatiquement toutes les 4 heures:
- Vérification des échéances projets
- Vérification des retards d'étapes
- Vérification des tâches en retard
- Vérification des dépassements de budget
- Vérification des expirations de contrats

## 📝 Commandes Utiles

### Local

```cmd
# Voir les logs
docker-compose logs -f

# Voir les logs d'un service spécifique
docker-compose logs -f web
docker-compose logs -f celery_worker

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# Shell Django
docker-compose exec web python manage.py shell

# Créer un utilisateur
docker-compose exec web python manage.py createsuperuser
```

### Production

```bash
# Démarrer
docker-compose --profile production up -d

# Arrêter
docker-compose --profile production down

# Logs
docker-compose --profile production logs -f

# Shell Django
docker-compose --profile production exec web_prod python manage.py shell
```

## 🗂️ Architecture

### Mode Local (par défaut)
```
docker-compose up -d
├── db                      # MySQL 8.0
├── redis                   # Redis 7 (broker Celery)
├── web                     # Django runserver (dev)
├── celery_worker           # Worker Celery
└── celery_beat             # Scheduler (alertes)
```

### Mode Production
```
docker-compose --profile production up -d
├── db                      # MySQL 8.0
├── redis                   # Redis 7
├── nginx                   # Reverse proxy
├── web_prod                # Django + Gunicorn
├── celery_worker           # Worker Celery
└── celery_beat             # Scheduler
```

## 🔧 Configuration

### Local
Modifier `.env`:
- Ports
- Mots de passe base de données
- Configuration email (console par défaut)
- Fréquence des alertes

### Production
Modifier `.env.production`:
- Secrets sécurisés
- Configuration SMTP réelle
- Domaine et HTTPS
- Limites ressources

## ❓ Problèmes Courants

### Port déjà utilisé
```cmd
# Changer le port dans .env
WEB_PORT=8001
```

### Services ne démarrent pas
```cmd
# Vérifier les logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

### Base de données corrompue
```cmd
# Nettoyer et redémarrer
docker-compose down -v
docker-compose up -d
```

### Passer de local à production
```bash
# Arrêter le mode local
docker-compose down

# Démarrer en production
docker-compose --profile production up -d
```

## 📧 Support

Pour toute question, consulter:
- `DEPLOIEMENT_LOCAL_SIMPLIFIE.md` - Guide détaillé local
- `DEPLOIEMENT_PRODUCTION_ENTERPRISE.md` - Guide production
- `.env.example` - Configuration locale
- `.env.production.example` - Configuration production
