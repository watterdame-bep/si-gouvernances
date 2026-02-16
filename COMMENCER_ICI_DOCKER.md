# 🚀 Démarrage Rapide - SI-Gouvernance avec Docker

## ✅ Ce Qui a Été Implémenté

Architecture production-ready complète avec Celery + Redis pour alertes automatiques toutes les 4 heures.

---

## 📋 Étapes de Déploiement

### 1. Configuration (2 minutes)

```bash
# Copier le template d'environnement
cp .env.docker.example .env

# Éditer avec vos valeurs
nano .env
```

**Variables critiques à modifier:**
- `DJANGO_SECRET_KEY` - Générer avec: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` - Mot de passe fort pour MySQL
- `DB_ROOT_PASSWORD` - Mot de passe root MySQL
- `EMAIL_HOST_USER` - Votre email Gmail
- `EMAIL_HOST_PASSWORD` - Mot de passe d'application Gmail (16 caractères)
- `FLOWER_PASSWORD` - Mot de passe pour Flower monitoring

### 2. Démarrage (5 minutes)

```bash
# Rendre le script exécutable
chmod +x docker-start.sh

# Démarrage complet (build + migrate + collectstatic)
./docker-start.sh --fresh
```

### 3. Vérification (1 minute)

```bash
# Tester que Celery fonctionne
docker-compose exec web python test_celery_docker.py

# Vérifier les services
docker-compose ps

# Voir les logs
docker-compose logs -f celery_beat
```

---

## 🎯 Ce Qui S'Exécute Automatiquement

Les alertes s'exécutent **toutes les 4 heures** (0h, 4h, 8h, 12h, 16h, 20h):

| Heure | Tâche | Description |
|-------|-------|-------------|
| XX:00 | Échéances projets | J-7, J-3, J-1, retards |
| XX:05 | Retards étapes | Étapes en retard |
| XX:10 | Tâches en retard | Tâches dépassées |
| XX:15 | Budgets | Dépassements budget |
| XX:20 | Contrats | Expirations contrats |

**Aucune intervention manuelle nécessaire!**

---

## 📊 Monitoring

### Voir les Logs

```bash
# Logs Celery Beat (planificateur)
docker-compose logs -f celery_beat

# Logs Celery Worker (exécution)
docker-compose logs -f celery_worker

# Tous les logs
docker-compose logs -f
```

### Flower Dashboard (Optionnel)

```bash
# Démarrer avec Flower
docker-compose --profile monitoring up -d

# Accéder à: http://localhost:5555
# Credentials: Définis dans .env (FLOWER_USER / FLOWER_PASSWORD)
```

---

## 🔧 Commandes Utiles

### Gestion des Services

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer
docker-compose restart

# État des services
docker-compose ps
```

### Tests

```bash
# Test complet Celery
docker-compose exec web python test_celery_docker.py

# Test manuel d'une commande
docker-compose exec web python manage.py check_project_deadlines

# Test email
docker-compose exec web python test_email_smtp.py
```

### Accès aux Conteneurs

```bash
# Shell Django
docker-compose exec web python manage.py shell

# Shell Bash
docker-compose exec web bash

# MySQL
docker-compose exec db mysql -u root -p

# Redis
docker-compose exec redis redis-cli
```

---

## 📚 Documentation Complète

### Quick Start
→ `README_DOCKER.md`

### Guide Complet
→ `DEPLOIEMENT_DOCKER_PRODUCTION.md`
- Installation étape par étape
- Configuration détaillée
- Monitoring et logs
- Sécurité production
- Scaling et performance
- Dépannage

### Architecture
→ `ARCHITECTURE_CELERY_PRODUCTION.md`
- Schémas d'architecture
- Flux d'exécution
- Configuration technique
- Monitoring avancé

### Résumé Implémentation
→ `IMPLEMENTATION_CELERY_COMPLETE.md`

---

## 🐛 Dépannage Rapide

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

### Erreurs de Connexion

```bash
# Vérifier Redis
docker-compose ps redis
docker-compose exec redis redis-cli ping

# Vérifier MySQL
docker-compose ps db
docker-compose exec db mysql -u root -p -e "SHOW DATABASES;"
```

---

## ✅ Checklist Post-Déploiement

- [ ] Tous les services UP (`docker-compose ps`)
- [ ] Test Celery passé (`test_celery_docker.py`)
- [ ] Email de test envoyé
- [ ] Logs sans erreurs
- [ ] Tâches planifiées actives
- [ ] Application accessible (http://localhost:8000)

---

## 🎉 C'est Tout!

Votre système d'alertes est maintenant opérationnel et s'exécutera automatiquement toutes les 4 heures.

**Prochaines étapes:**
1. Créer un superuser: `docker-compose exec web python manage.py createsuperuser`
2. Accéder à l'admin: http://localhost:8000/admin
3. Monitorer les logs: `docker-compose logs -f`

---

**Questions? Consultez la documentation complète dans les fichiers mentionnés ci-dessus.**
