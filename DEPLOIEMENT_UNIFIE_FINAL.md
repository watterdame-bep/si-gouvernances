# ✅ Déploiement Unifié - Configuration Finale

## 🎯 Objectif Atteint

UN SEUL fichier `docker-compose.yml` pour gérer LOCAL et PRODUCTION avec des profils Docker.

## 📁 Architecture Simplifiée

### ✅ Fichiers Essentiels

```
SI-Gouvernance/
├── docker-compose.yml              # ✅ FICHIER UNIQUE (local + production)
├── .env.example                    # ✅ Configuration locale
├── .env.production.example         # ✅ Configuration production
├── deploy-local.bat                # ✅ Script déploiement Windows
├── README_DEPLOIEMENT.md           # ✅ Documentation
├── Dockerfile                      # ✅ Multi-stage (dev + prod)
└── core/management/commands/
    ├── create_superuser_jovi.py    # ✅ Création auto superuser
    └── setup_celery_beat.py        # ✅ Configuration auto alertes
```

### ❌ Fichiers Supprimés

- ~~docker-compose.prod.yml~~ → Fusionné dans docker-compose.yml
- ~~docker-compose.local.yml~~ → Fusionné dans docker-compose.yml
- ~~.env.docker.example~~ → Remplacé par .env.example
- ~~.env.local~~ → Remplacé par .env.example
- ~~docker-start.sh~~ → Remplacé par deploy-local.bat

## 🚀 Utilisation

### Mode Local (Développement)

```cmd
# Windows
deploy-local.bat

# Linux/Mac
docker-compose up -d
```

**Caractéristiques:**
- Django runserver (hot reload)
- Volumes montés (code modifiable)
- Superuser "jovi" créé automatiquement
- Emails en console
- Debug activé
- Ports exposés: 8000, 3306, 6379

### Mode Production

```bash
# Démarrer en production
docker-compose --profile production up -d
```

**Caractéristiques:**
- Gunicorn (serveur production)
- Nginx reverse proxy
- Pas de volumes code (sécurité)
- Emails SMTP réels
- Debug désactivé
- Limites ressources
- Logs professionnels

### Mode Monitoring (Optionnel)

```bash
# Local avec monitoring
docker-compose --profile monitoring up -d

# Production avec monitoring
docker-compose --profile production --profile monitoring up -d
```

## 🔄 Profils Docker

Le fichier `docker-compose.yml` utilise des profils pour gérer les différents modes:

### Profil par défaut (LOCAL)
- Services: `db`, `redis`, `web`, `celery_worker`, `celery_beat`
- Commande: `docker-compose up -d`

### Profil `production`
- Services: `db`, `redis`, `web_prod`, `nginx`, `celery_worker`, `celery_beat`
- Commande: `docker-compose --profile production up -d`

### Profil `monitoring`
- Service additionnel: `flower`
- Commande: `docker-compose --profile monitoring up -d`

## 📊 Comparaison des Modes

| Fonctionnalité | Local | Production |
|----------------|-------|------------|
| Serveur | runserver | Gunicorn + Nginx |
| Code modifiable | ✅ Oui | ❌ Non |
| Superuser auto | ✅ jovi/jovi123 | ❌ Manuel |
| Emails | Console | SMTP réel |
| Debug | ✅ Activé | ❌ Désactivé |
| Volumes code | ✅ Montés | ❌ Pas montés |
| Limites ressources | ❌ Non | ✅ Oui |
| HTTPS | ❌ Non | ✅ Oui (Nginx) |
| Ports exposés | Tous | 80, 443 uniquement |

## 🔧 Configuration

### Fichier .env (Local)

```bash
# Copier le template
cp .env.example .env

# Valeurs par défaut OK pour local
# Modifier si besoin
```

### Fichier .env.production (Production)

```bash
# Copier le template
cp .env.production.example .env.production

# IMPORTANT: Modifier TOUTES les valeurs
# - Secrets sécurisés
# - Mots de passe forts
# - Configuration SMTP
# - Domaine
```

## 🎯 Avantages de l'Unification

### Avant (Complexe)
- ❌ 2 fichiers docker-compose séparés
- ❌ Confusion sur quel fichier utiliser
- ❌ Duplication de configuration
- ❌ Maintenance difficile

### Après (Simple)
- ✅ 1 seul fichier docker-compose.yml
- ✅ Profils clairs (local/production)
- ✅ Pas de duplication
- ✅ Maintenance facile
- ✅ Transition local → production simple

## 📝 Commandes Complètes

### Local

```bash
# Démarrage
docker-compose up -d

# Avec monitoring
docker-compose --profile monitoring up -d

# Arrêt
docker-compose down

# Logs
docker-compose logs -f

# Shell
docker-compose exec web python manage.py shell
```

### Production

```bash
# Démarrage
docker-compose --profile production up -d

# Avec monitoring
docker-compose --profile production --profile monitoring up -d

# Arrêt
docker-compose --profile production down

# Logs
docker-compose --profile production logs -f

# Shell
docker-compose --profile production exec web_prod python manage.py shell
```

### Nettoyage

```bash
# Arrêter et supprimer volumes
docker-compose down -v

# Nettoyage complet
docker system prune -f
```

## 🔄 Migration Local → Production

```bash
# 1. Arrêter le mode local
docker-compose down

# 2. Configurer production
cp .env.production.example .env.production
# Éditer .env.production

# 3. Démarrer en production
docker-compose --profile production up -d
```

## ✨ Fonctionnalités Automatiques

### Mode Local
1. ✅ Création superuser "jovi"
2. ✅ Migrations automatiques
3. ✅ Configuration Celery Beat
4. ✅ Collectstatic
5. ✅ Alertes toutes les 4 heures

### Mode Production
1. ✅ Migrations automatiques
2. ✅ Collectstatic
3. ✅ Gunicorn optimisé
4. ✅ Nginx reverse proxy
5. ✅ Limites ressources
6. ✅ Logs rotatifs

## 🎉 Résultat Final

**UN SEUL fichier docker-compose.yml** qui gère:
- ✅ Développement local
- ✅ Production entreprise
- ✅ Monitoring optionnel
- ✅ Configuration claire
- ✅ Transition facile

**Commandes simples:**
- Local: `docker-compose up -d`
- Production: `docker-compose --profile production up -d`
- Monitoring: `--profile monitoring`

**Projet propre et professionnel!** 🚀
