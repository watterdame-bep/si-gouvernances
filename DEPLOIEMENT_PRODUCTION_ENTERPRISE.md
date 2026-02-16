# Guide de Déploiement Production Enterprise - SI-Gouvernance

## 🎯 Architecture Production

Cette architecture est conçue pour un déploiement entreprise réel avec:
- ✅ Nginx reverse proxy avec HTTPS
- ✅ Sécurité renforcée (pas de secrets en dur)
- ✅ Limitation des ressources Docker
- ✅ Logs professionnels rotatifs
- ✅ Scaling ready
- ✅ Flower accessible uniquement en interne
- ✅ Fréquence des alertes configurable

---

## 📋 Prérequis

### Serveur

- Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- 4 CPU minimum (8 recommandé)
- 8 GB RAM minimum (16 GB recommandé)
- 50 GB disque minimum (SSD recommandé)
- Docker 20.10+
- Docker Compose 2.0+

### Domaine

- Nom de domaine configuré (ex: si-gouvernance.votreentreprise.com)
- DNS pointant vers le serveur
- Certificat SSL (Let's Encrypt recommandé)

---

## 🚀 Installation Étape par Étape

### Étape 1: Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation de Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Installation de Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Vérification
docker --version
docker-compose --version
```

### Étape 2: Clonage du Projet

```bash
# Créer le dossier de déploiement
sudo mkdir -p /opt/si-gouvernance
sudo chown $USER:$USER /opt/si-gouvernance
cd /opt/si-gouvernance

# Cloner le projet
git clone <votre-repo> .
```

### Étape 3: Configuration Environnement

```bash
# Copier le template production
cp .env.production.example .env.production

# Éditer avec vos valeurs
nano .env.production
```

**Variables OBLIGATOIRES à configurer:**

```env
# Django
DJANGO_SECRET_KEY=<générer-clé-unique-50-chars>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=si-gouvernance.votreentreprise.com,www.si-gouvernance.votreentreprise.com

# Base de données
DB_PASSWORD=<mot-de-passe-fort-32-chars>
DB_ROOT_PASSWORD=<mot-de-passe-root-fort-32-chars>

# Email
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=<mot-de-passe-application-16-chars>

# Flower (si monitoring activé)
FLOWER_PASSWORD=<mot-de-passe-fort-32-chars>

# Domaine
DOMAIN_NAME=si-gouvernance.votreentreprise.com
```

**Générer une clé secrète Django:**

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Étape 4: Certificats SSL

#### Option A: Let's Encrypt (Recommandé)

```bash
# Installer Certbot
sudo apt install certbot

# Obtenir le certificat
sudo certbot certonly --standalone -d si-gouvernance.votreentreprise.com -d www.si-gouvernance.votreentreprise.com

# Copier les certificats
sudo cp /etc/letsencrypt/live/si-gouvernance.votreentreprise.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/si-gouvernance.votreentreprise.com/privkey.pem docker/nginx/ssl/key.pem
sudo chown $USER:$USER docker/nginx/ssl/*.pem
```

#### Option B: Certificat Auto-signé (Développement uniquement)

```bash
# Générer un certificat auto-signé
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=FR/ST=IDF/L=Paris/O=VotreEntreprise/CN=si-gouvernance.votreentreprise.com"
```

### Étape 5: Configuration Nginx

```bash
# Éditer la configuration Nginx
nano docker/nginx/conf.d/si-gouvernance.conf

# Remplacer ${DOMAIN_NAME} par votre domaine réel
sed -i 's/${DOMAIN_NAME}/si-gouvernance.votreentreprise.com/g' docker/nginx/conf.d/si-gouvernance.conf
```

### Étape 6: Build et Démarrage

```bash
# Build des images
docker-compose -f docker-compose.prod.yml build

# Démarrage des services
docker-compose -f docker-compose.prod.yml up -d

# Vérifier que tous les services sont UP
docker-compose -f docker-compose.prod.yml ps
```

### Étape 7: Initialisation de la Base de Données

```bash
# Appliquer les migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Créer un superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Initialiser les tâches Celery Beat
docker-compose -f docker-compose.prod.yml exec web python manage.py setup_celery_beat

# Collecter les fichiers statiques
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### Étape 8: Vérification

```bash
# Tester Celery
docker-compose -f docker-compose.prod.yml exec web python test_celery_docker.py

# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs --tail=50

# Tester l'accès HTTPS
curl -I https://si-gouvernance.votreentreprise.com
```

---

## 🔒 Sécurité Production

### Checklist Sécurité

- [ ] `DJANGO_DEBUG=False` dans `.env.production`
- [ ] `DJANGO_SECRET_KEY` unique et fort (50+ caractères)
- [ ] Mots de passe forts pour DB (32+ caractères)
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] HTTPS activé avec certificat valide
- [ ] Firewall configuré (ports 80, 443 ouverts uniquement)
- [ ] Flower NON exposé publiquement (profile monitoring)
- [ ] Backups automatiques configurés
- [ ] Monitoring actif
- [ ] Logs rotatifs configurés

### Configuration Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Vérifier
sudo ufw status
```

### Renouvellement Automatique SSL

```bash
# Ajouter au crontab
sudo crontab -e

# Ajouter cette ligne (renouvellement tous les jours à 3h)
0 3 * * * certbot renew --quiet && docker-compose -f /opt/si-gouvernance/docker-compose.prod.yml restart nginx
```

---

## 📊 Monitoring

### Flower (Monitoring Celery)

**⚠️  Flower n'est PAS exposé publiquement par défaut pour des raisons de sécurité.**

#### Activer Flower Temporairement

```bash
# Démarrer avec le profile monitoring
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Flower est accessible uniquement en réseau interne Docker
# Pour y accéder, utiliser un tunnel SSH:
ssh -L 5555:localhost:5555 user@votre-serveur

# Puis accéder à: http://localhost:5555
```

#### Désactiver Flower

```bash
# Arrêter Flower
docker-compose -f docker-compose.prod.yml stop flower
docker-compose -f docker-compose.prod.yml rm -f flower
```

### Logs

```bash
# Logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Logs d'un service spécifique
docker-compose -f docker-compose.prod.yml logs -f celery_beat
docker-compose -f docker-compose.prod.yml logs -f celery_worker
docker-compose -f docker-compose.prod.yml logs -f nginx

# Logs fichiers
tail -f /opt/si-gouvernance/logs/celery/beat.log
tail -f /opt/si-gouvernance/logs/celery/worker.log
tail -f /opt/si-gouvernance/logs/gunicorn-access.log
```

---

## ⚙️ Configuration des Alertes

### Fréquence Configurable

La fréquence des alertes est configurable via `.env.production`:

```env
# Fréquence en heures (par défaut: 4)
CELERY_ALERTS_FREQUENCY_HOURS=4
```

**Valeurs possibles:**
- `1` = Toutes les heures
- `2` = Toutes les 2 heures
- `4` = Toutes les 4 heures (recommandé)
- `6` = Toutes les 6 heures
- `12` = Toutes les 12 heures

**Après modification, redémarrer Celery Beat:**

```bash
docker-compose -f docker-compose.prod.yml restart celery_beat
```

---

## 🔧 Scaling

### Augmenter les Workers Celery

```bash
# Méthode 1: Modifier docker-compose.prod.yml
# Changer CELERY_WORKER_CONCURRENCY dans .env.production
CELERY_WORKER_CONCURRENCY=4

# Redémarrer
docker-compose -f docker-compose.prod.yml restart celery_worker

# Méthode 2: Ajouter des workers supplémentaires
docker-compose -f docker-compose.prod.yml up -d --scale celery_worker=3
```

### Augmenter les Workers Gunicorn

```bash
# Modifier dans .env.production
GUNICORN_WORKERS=8

# Redémarrer
docker-compose -f docker-compose.prod.yml restart web
```

---

## 💾 Backups

### Backup Base de Données

```bash
# Script de backup
#!/bin/bash
BACKUP_DIR="/opt/backups/si-gouvernance"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup MySQL
docker-compose -f /opt/si-gouvernance/docker-compose.prod.yml exec -T db \
  mysqldump -u root -p${DB_ROOT_PASSWORD} si_gouvernance | \
  gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/si-gouvernance/media/

# Garder seulement les 30 derniers backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup terminé: $DATE"
```

### Automatiser les Backups

```bash
# Ajouter au crontab
sudo crontab -e

# Backup quotidien à 2h du matin
0 2 * * * /opt/si-gouvernance/scripts/backup.sh >> /var/log/si-gouvernance-backup.log 2>&1
```

---

## 🔄 Mise à Jour

### Procédure de Mise à Jour

```bash
cd /opt/si-gouvernance

# 1. Backup avant mise à jour
./scripts/backup.sh

# 2. Pull du nouveau code
git pull

# 3. Rebuild des images
docker-compose -f docker-compose.prod.yml build

# 4. Arrêt des services
docker-compose -f docker-compose.prod.yml down

# 5. Démarrage avec nouvelles images
docker-compose -f docker-compose.prod.yml up -d

# 6. Migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 7. Collecte des statiques
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 8. Vérification
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=50
```

---

## 🐛 Dépannage

### Services ne Démarrent Pas

```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs

# Vérifier les healthchecks
docker-compose -f docker-compose.prod.yml ps

# Redémarrer un service spécifique
docker-compose -f docker-compose.prod.yml restart web
```

### Erreurs de Connexion Base de Données

```bash
# Vérifier que MySQL est UP
docker-compose -f docker-compose.prod.yml ps db

# Tester la connexion
docker-compose -f docker-compose.prod.yml exec db mysql -u root -p -e "SHOW DATABASES;"

# Vérifier les logs MySQL
docker-compose -f docker-compose.prod.yml logs db
```

### Celery ne Fonctionne Pas

```bash
# Vérifier Beat
docker-compose -f docker-compose.prod.yml logs celery_beat

# Vérifier Worker
docker-compose -f docker-compose.prod.yml logs celery_worker

# Tester Celery
docker-compose -f docker-compose.prod.yml exec web python test_celery_docker.py
```

---

## ✅ Checklist Post-Déploiement

- [ ] Tous les services UP
- [ ] HTTPS fonctionnel
- [ ] Certificat SSL valide
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Tâches Celery planifiées actives
- [ ] Test Celery passé
- [ ] Email de test envoyé
- [ ] Logs sans erreurs critiques
- [ ] Backups configurés
- [ ] Monitoring configuré
- [ ] Firewall configuré
- [ ] DNS configuré
- [ ] Application accessible publiquement

---

## 📞 Support et Maintenance

### Commandes Utiles

```bash
# État des services
docker-compose -f docker-compose.prod.yml ps

# Redémarrer tous les services
docker-compose -f docker-compose.prod.yml restart

# Voir l'utilisation des ressources
docker stats

# Nettoyer les images inutilisées
docker system prune -a

# Voir les volumes
docker volume ls
```

### Monitoring Système

```bash
# CPU et mémoire
htop

# Espace disque
df -h

# Logs système
journalctl -u docker -f
```

---

**🎉 Votre application SI-Gouvernance est maintenant déployée en production enterprise-grade!**

Les alertes s'exécuteront automatiquement selon la fréquence configurée sans intervention manuelle.
