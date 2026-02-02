# SI-Gouvernance JCM

## 📋 Description

SI-Gouvernance JCM est une application web moderne de gestion de projets développée avec Django. Elle offre une interface intuitive pour la gestion complète des projets, des équipes, des tâches et des membres avec un système d'audit avancé.

## ✨ Fonctionnalités Principales

### 🔐 Gestion des Utilisateurs et Sécurité
- **Authentification sécurisée** avec audit automatique
- **Gestion des rôles** (Super Admin, Chef de Projet, Utilisateur)
- **Profil utilisateur complet** avec informations RH
- **Changement de mot de passe** avec notification email
- **Système d'audit complet** de toutes les actions

### 👥 Gestion des Membres (RH)
- **Profils RH détaillés** (informations personnelles et professionnelles)
- **Gestion des compétences** et spécialités
- **Suivi des informations de contact** (personnel et urgence)
- **Liaison avec les comptes utilisateur**

### 📊 Gestion de Projets
- **Création et gestion de projets** avec statuts avancés
- **Gestion d'équipes** avec rôles spécifiques
- **Affectation et transfert** de responsabilités
- **Suivi budgétaire** avec validation hiérarchique

### 📋 Gestion des Tâches
- **Architecture étapes/modules/tâches** flexible
- **Interface "Mes Tâches"** moderne et responsive
- **Changement de statut** en temps réel
- **Suivi de progression** avec pourcentages
- **Notifications** automatiques

### 🔔 Système de Notifications
- **Notifications en temps réel** pour les tâches
- **Interface moderne** avec onglets et filtres
- **Marquage automatique** des notifications lues
- **API REST** pour les notifications

### 📧 Notifications Email
- **Emails de sécurité** pour changement de mot de passe
- **Templates HTML modernes** avec design responsive
- **Configuration SMTP flexible** (développement/production)

## 🛠️ Technologies Utilisées

- **Backend** : Django 5.2.5, Python 3.x
- **Base de données** : MySQL
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Styling** : Tailwind CSS avec design moderne
- **Email** : Django Email avec templates HTML
- **Sécurité** : Audit automatique, validation CSRF

## 📦 Installation

### Prérequis
- Python 3.8+
- MySQL 5.7+
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/votre-username/si-gouvernance-jcm.git
cd si-gouvernance-jcm
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration de la base de données**
```bash
# Créer la base de données MySQL
mysql -u root -p
CREATE DATABASE si_gouvernance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Configuration des variables d'environnement**
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
DB_NAME=si_gouvernance
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
EMAIL_HOST_USER=votre_email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
```

6. **Migrations de la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Initialiser les données de base**
```bash
python manage.py init_data
```

8. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

L'application sera accessible sur `http://127.0.0.1:8000/`

## 👤 Comptes par Défaut

Après l'initialisation des données :

- **Super Admin** : `admin` / `admin123`
- **Utilisateur Test** : `user_test` / `password123`

## 🎨 Interface Utilisateur

### Design Moderne
- **Glassmorphism** avec effets de transparence
- **Animations fluides** et transitions
- **Responsive design** pour tous les appareils
- **Dark/Light mode** adaptatif

### Fonctionnalités UX
- **Navigation intuitive** avec sidebar moderne
- **Notifications en temps réel** avec badges
- **Formulaires intelligents** avec validation
- **Feedback visuel** pour toutes les actions

## 📱 Responsive Design

L'application est entièrement responsive et optimisée pour :
- **Desktop** (1024px+)
- **Tablet** (768px - 1024px)
- **Mobile** (320px - 768px)

## 🔧 Configuration Email

### Développement
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (Gmail)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

## 📊 Architecture

### Modèles Principaux
- **Utilisateur** : Comptes système avec authentification
- **Membre** : Profils RH avec informations détaillées
- **Projet** : Gestion de projets avec équipes
- **EtapeProjet** / **ModuleProjet** : Structure hiérarchique
- **TacheEtape** / **TacheModule** : Gestion des tâches
- **ActionAudit** : Traçabilité complète

### Sécurité
- **Audit automatique** de toutes les actions
- **Contrôle d'accès** basé sur les rôles
- **Validation des données** côté serveur
- **Protection CSRF** sur tous les formulaires

## 🚀 Fonctionnalités Avancées

### Système d'Audit
- **Traçabilité complète** des actions utilisateur
- **Détection d'intrusion** et tentatives suspectes
- **Logs sécurisés** avec hash d'intégrité
- **Interface d'administration** pour les Super Admins

### Gestion des Tâches
- **Interface moderne** "Mes Tâches" responsive
- **Changement de statut** en temps réel
- **Filtres avancés** par statut et priorité
- **Statistiques personnelles** en temps réel

### Notifications
- **Système temps réel** avec WebSocket-like updates
- **Interface moderne** avec onglets
- **Marquage automatique** des notifications lues
- **API REST** pour intégrations futures

## 📈 Évolutions Futures

- [ ] **API REST complète** pour applications mobiles
- [ ] **Authentification à deux facteurs** (2FA)
- [ ] **Intégration calendrier** (Google Calendar, Outlook)
- [ ] **Rapports avancés** avec graphiques
- [ ] **Mode hors ligne** avec synchronisation
- [ ] **Intégration Slack/Teams** pour notifications

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**JConsult MY** - Développement et conception

## 📞 Support

Pour toute question ou support :
- Email : support@jconsult.com
- Documentation : [Wiki du projet](https://github.com/votre-username/si-gouvernance-jcm/wiki)

---

⭐ **N'hésitez pas à donner une étoile au projet si vous le trouvez utile !**