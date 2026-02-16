# SI-Gouvernance

Système de gestion de projets informatiques avec gouvernance complète.

## 🚀 Démarrage Rapide

### Windows
```cmd
deploy-local.bat
```
Choisir option 1 → http://localhost:8000 → Connexion: `jovi` / `jovi123`

### Linux/Mac
```bash
cp .env.example .env
docker-compose up -d
```

## 📖 Documentation

- **[COMMENCER_ICI.md](COMMENCER_ICI.md)** - Guide de démarrage rapide
- **[README_DEPLOIEMENT.md](README_DEPLOIEMENT.md)** - Documentation complète
- **[DEPLOIEMENT_UNIFIE_FINAL.md](DEPLOIEMENT_UNIFIE_FINAL.md)** - Guide technique

## 🎯 Fonctionnalités

- ✅ Gestion de projets et étapes
- ✅ Gestion des modules et tâches
- ✅ Système de tests hiérarchiques
- ✅ Tickets de maintenance
- ✅ Alertes automatiques (échéances, retards, budgets)
- ✅ Notifications par email
- ✅ Système d'audit complet
- ✅ Gestion des rôles et permissions

## 🔄 Alertes Automatiques

Exécution toutes les 4 heures:
- Échéances projets
- Retards d'étapes
- Tâches en retard
- Dépassements budget
- Expirations contrats

## 🏗️ Architecture

- **Backend:** Django 4.2
- **Base de données:** MySQL 8.0
- **Cache/Broker:** Redis 7
- **Tasks:** Celery + Celery Beat
- **Frontend:** HTML/CSS/JavaScript + Tailwind CSS
- **Déploiement:** Docker + Docker Compose

## 📝 Commandes

### Local
```bash
docker-compose up -d              # Démarrer
docker-compose logs -f            # Logs
docker-compose down               # Arrêter
```

### Production
```bash
docker-compose --profile production up -d    # Démarrer
docker-compose --profile production logs -f  # Logs
docker-compose --profile production down     # Arrêter
```

## 🔧 Configuration

### Local
```bash
cp .env.example .env
# Les valeurs par défaut fonctionnent
```

### Production
```bash
cp .env.production.example .env.production
# Modifier TOUTES les valeurs
```

## 📊 Services

- **Application:** http://localhost:8000
- **Flower (monitoring):** http://localhost:5555
- **Base de données:** localhost:3306
- **Redis:** localhost:6379

## 🛠️ Développement

```bash
# Shell Django
docker-compose exec web python manage.py shell

# Créer un utilisateur
docker-compose exec web python manage.py createsuperuser

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

## 📦 Prérequis

- Docker Desktop
- 4 GB RAM minimum
- Ports disponibles: 8000, 3306, 6379, 5555

## 🎓 Support

Consultez la documentation dans les fichiers `.md` du projet.

## 📄 Licence

Propriétaire - Tous droits réservés
