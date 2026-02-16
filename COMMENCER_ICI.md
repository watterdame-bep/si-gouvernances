# 🚀 COMMENCER ICI - SI-Gouvernance

## ⚡ Démarrage Rapide (2 minutes)

### Windows

```cmd
deploy-local.bat
```

Choisir **option 1** → Attendre 30 secondes → Aller sur http://localhost:8000

**Connexion:** `jovi` / `jovi123`

### Linux/Mac

```bash
cp .env.example .env
docker-compose up -d
```

Attendre 30 secondes → http://localhost:8000

## 📁 Structure du Projet

```
SI-Gouvernance/
├── docker-compose.yml          # ✅ Configuration Docker UNIQUE
├── .env.example                # ✅ Configuration locale
├── .env.production.example     # ✅ Configuration production
├── deploy-local.bat            # ✅ Script déploiement
├── README_DEPLOIEMENT.md       # 📖 Documentation complète
└── DEPLOIEMENT_UNIFIE_FINAL.md # 📖 Guide technique
```

## 🎯 Modes de Déploiement

### 1️⃣ Local (Développement)

**Commande:**
```bash
docker-compose up -d
```

**Caractéristiques:**
- Serveur de développement Django
- Code modifiable en temps réel
- Superuser "jovi" créé automatiquement
- Emails affichés dans la console
- Ports exposés pour debug

**Accès:**
- Application: http://localhost:8000
- Base de données: localhost:3306
- Redis: localhost:6379

### 2️⃣ Production

**Commande:**
```bash
docker-compose --profile production up -d
```

**Caractéristiques:**
- Gunicorn + Nginx
- Sécurité renforcée
- Emails SMTP réels
- Limites ressources
- Logs professionnels

**Accès:**
- Application: http://localhost (via Nginx)
- HTTPS: https://localhost (si configuré)

### 3️⃣ Monitoring (Optionnel)

**Commande:**
```bash
# Local
docker-compose --profile monitoring up -d

# Production
docker-compose --profile production --profile monitoring up -d
```

**Accès:**
- Flower: http://localhost:5555

## 🔄 Alertes Automatiques

Les alertes s'exécutent automatiquement toutes les 4 heures:

✅ Échéances projets  
✅ Retards d'étapes  
✅ Tâches en retard  
✅ Dépassements budget  
✅ Expirations contrats  

## 📝 Commandes Essentielles

### Démarrage
```bash
# Local
docker-compose up -d

# Production
docker-compose --profile production up -d
```

### Arrêt
```bash
docker-compose down
```

### Logs
```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f web
docker-compose logs -f celery_worker
```

### Shell Django
```bash
# Local
docker-compose exec web python manage.py shell

# Production
docker-compose --profile production exec web_prod python manage.py shell
```

### Redémarrage
```bash
docker-compose restart
```

## 🔧 Configuration

### Local (.env)

```bash
# Copier le template
cp .env.example .env

# Les valeurs par défaut fonctionnent directement
# Modifier uniquement si nécessaire
```

### Production (.env.production)

```bash
# Copier le template
cp .env.production.example .env.production

# IMPORTANT: Modifier TOUTES les valeurs
# - DJANGO_SECRET_KEY (générer une clé sécurisée)
# - DB_PASSWORD (mot de passe fort)
# - EMAIL_HOST_USER et EMAIL_HOST_PASSWORD
# - DJANGO_ALLOWED_HOSTS (votre domaine)
```

## 🎓 Documentation Complète

- **README_DEPLOIEMENT.md** - Guide utilisateur complet
- **DEPLOIEMENT_UNIFIE_FINAL.md** - Guide technique détaillé
- **.env.example** - Configuration locale commentée
- **.env.production.example** - Configuration production commentée

## ❓ Problèmes Courants

### Port 8000 déjà utilisé
```bash
# Dans .env, changer:
WEB_PORT=8001
```

### Services ne démarrent pas
```bash
# Vérifier les logs
docker-compose logs

# Rebuild complet
docker-compose down
docker-compose build
docker-compose up -d
```

### Réinitialiser la base de données
```bash
# ATTENTION: Supprime toutes les données!
docker-compose down -v
docker-compose up -d
```

### Passer de local à production
```bash
# 1. Arrêter local
docker-compose down

# 2. Configurer production
cp .env.production.example .env.production
# Éditer .env.production

# 3. Démarrer production
docker-compose --profile production up -d
```

## 🎉 C'est Tout!

Votre application est maintenant déployée avec:

✅ Base de données MySQL  
✅ Cache Redis  
✅ Serveur web Django  
✅ Workers Celery  
✅ Alertes automatiques  
✅ Superuser créé  

**Prêt à l'emploi en 2 minutes!** 🚀

---

**Besoin d'aide?** Consultez `README_DEPLOIEMENT.md` pour plus de détails.
