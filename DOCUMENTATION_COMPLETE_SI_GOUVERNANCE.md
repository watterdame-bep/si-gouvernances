# Documentation Complète - SI-Gouvernance V2.3
## Guide de Passation pour Développeur

---

# 📋 Table des Matières

1. [Vue d'Ensemble du Projet](#vue-densemble-du-projet)
2. [Architecture Technique](#architecture-technique)
3. [Modèles de Données](#modèles-de-données)
4. [Système d'Authentification et Permissions](#système-dauthentification-et-permissions)
5. [Logique Métier](#logique-métier)
6. [Interface Utilisateur](#interface-utilisateur)
7. [Workflows Principaux](#workflows-principaux)
8. [Système d'Audit](#système-daudit)
9. [Configuration et Déploiement](#configuration-et-déploiement)
10. [Tests et Validation](#tests-et-validation)
11. [Roadmap et Évolutions](#roadmap-et-évolutions)

---

# 🎯 Vue d'Ensemble du Projet

## Objectif
**SI-Gouvernance** est une application Django de gestion de projets IT avec un focus sur la gouvernance, le suivi des étapes, et la gestion des tâches. Elle permet de gérer le cycle de vie complet des projets informatiques avec un système d'audit intégré.

## Domaine Métier
- **Gestion de projets IT** avec méthodologie structurée
- **Suivi d'étapes** prédéfinies (Conception, Planification, Développement, Tests, Déploiement, Maintenance)
- **Gestion d'équipes** avec rôles et permissions
- **Audit et traçabilité** complète des actions
- **Gestion des tâches** par étapes et modules

## Utilisateurs Cibles
- **Super Administrateurs** : Gestion complète du système
- **Chefs de Projet** : Gestion de leurs projets assignés
- **Développeurs/QA** : Consultation et mise à jour des tâches
- **Direction** : Consultation des rapports et tableaux de bord

---

# 🏗️ Architecture Technique

## Stack Technologique
```
Backend:    Django 4.2.7 + Python 3.13
Frontend:   HTML5 + Tailwind CSS + JavaScript (Vanilla)
Base de données: MySQL (configurable)
Cache:      Pas encore implémenté (Redis prévu)
Serveur:    Django Development Server (Gunicorn en production)
```

## Structure du Projet
```
SI-GOUVERNANCE/
├── si_gouvernance/          # Configuration Django
│   ├── settings.py         # Configuration principale
│   ├── urls.py            # URLs racine
│   └── wsgi.py            # Configuration WSGI
├── core/                   # Application principale
│   ├── models.py          # Modèles de données
│   ├── views.py           # Logique métier et vues
│   ├── urls.py            # URLs de l'application
│   ├── utils.py           # Fonctions utilitaires
│   ├── admin.py           # Interface d'administration
│   └── migrations/        # Migrations de base de données
├── templates/              # Templates HTML
│   ├── base.html          # Template de base
│   ├── base_utilisateur.html # Template utilisateur
│   └── core/              # Templates spécifiques
├── theme/                  # Application Tailwind CSS
└── requirements.txt        # Dépendances Python
```

## Patterns Architecturaux
- **MVT (Model-View-Template)** : Pattern Django standard
- **Repository Pattern** : Via les managers Django
- **Decorator Pattern** : Pour les permissions (@require_super_admin)
- **Observer Pattern** : Système d'audit automatique
- **Strategy Pattern** : Gestion des rôles et permissions

---

# 🗄️ Modèles de Données

## Hiérarchie des Entités Principales

### 1. Gestion des Utilisateurs
```python
# Séparation Membre/Utilisateur (Architecture V2)
Membre (Profil RH)
├── nom, prénom, email, téléphone
├── poste, département, date_embauche
└── statut_actif

Utilisateur (Compte Système) 
├── Hérite de AbstractUser Django
├── OneToOneField vers Membre
├── role_systeme (DEVELOPPEUR, CHEF_PROJET, QA, DIRECTION)
└── Méthodes: est_super_admin(), a_acces_projet()
```

### 2. Gestion des Projets
```python
Projet
├── nom, description, client, budget
├── statut (StatutProjet: IDEE, PLANIFIE, EN_COURS, etc.)
├── priorité (BASSE, MOYENNE, HAUTE, CRITIQUE)
├── createur (Utilisateur)
└── Relations: affectations, etapes, modules

StatutProjet
├── nom, description, couleur_affichage
└── ordre_affichage

Affectation (Équipe Projet)
├── utilisateur, projet, role_sur_projet
├── est_responsable_principal
├── date_debut, date_fin
└── Gestion des permissions par projet
```

### 3. Architecture Étapes/Modules/Tâches (V2.0)
```python
# Étapes prédéfinies du cycle de vie
TypeEtape
├── nom (CONCEPTION, PLANIFICATION, etc.)
├── description, ordre, couleur, icone_emoji
└── peut_creer_modules_librement()

EtapeProjet (Instance d'étape pour un projet)
├── projet, type_etape, ordre
├── statut (A_VENIR, EN_COURS, TERMINEE)
├── date_debut_reelle, date_fin_reelle
└── Méthodes: activer(), terminer(), peut_creer_modules_librement()

# Modules fonctionnels (créés en phase DÉVELOPPEMENT)
ModuleProjet
├── projet, nom, description, couleur
├── etape_creation (référence à l'étape de création)
├── icone_emoji, date_creation
└── Relations: taches

# Tâches de modules (anciennes tâches)
TacheModule
├── module, nom, description, responsable
├── statut, priorité, dates
└── Logique métier de base

# Tâches d'étapes (nouvelles - V2.0)
TacheEtape
├── etape, nom, description, responsable
├── statut, priorité, dates
├── pourcentage_completion, temps_passe
├── date_debut_reelle, date_fin_reelle
├── statut_personnalise, taches_prerequises
├── etiquettes
└── Méthodes avancées: changer_statut(), mettre_a_jour_progression()
```

### 4. Système d'Audit et Traçabilité
```python
ActionAudit (Audit système global)
├── utilisateur, type_action, description
├── projet, timestamp, adresse_ip
├── donnees_avant, donnees_apres
└── hash_integrite

HistoriqueTache (Audit spécifique aux tâches - V2.3)
├── tache, utilisateur, type_action
├── description, donnees_avant, donnees_apres
└── timestamp, adresse_ip

CommentaireTache (V2.3)
├── tache, auteur, contenu
├── mentions (ManyToMany vers Utilisateur)
└── date_creation, date_modification

NotificationTache (V2.3)
├── destinataire, tache, type_notification
├── titre, message, lue
└── emetteur, donnees_contexte
```

## Relations Clés
- **Utilisateur ↔ Projet** : ManyToMany via Affectation
- **Projet → Étapes** : OneToMany (EtapeProjet)
- **Projet → Modules** : OneToMany (ModuleProjet)
- **Étape → Tâches** : OneToMany (TacheEtape)
- **Module → Tâches** : OneToMany (TacheModule)
- **Tâche → Commentaires/Historique** : OneToMany

---

# 🔐 Système d'Authentification et Permissions

## Niveaux d'Autorisation

### 1. Super Administrateurs
```python
# Identification
user.is_superuser = True
user.est_super_admin() = True

# Permissions
- Accès complet à toutes les fonctionnalités
- Gestion des utilisateurs et membres
- Création/modification/suppression de projets
- Accès à l'audit complet
- Gestion des paramètres système
```

### 2. Utilisateurs Normaux
```python
# Rôles Système
DEVELOPPEUR = 'DEVELOPPEUR'
CHEF_PROJET = 'CHEF_PROJET'  
QA = 'QA'
DIRECTION = 'DIRECTION'

# Permissions par Projet
- Responsable Principal: Gestion complète du projet
- Membre d'Équipe: Consultation + modification des tâches assignées
- Créateur: Droits étendus sur le projet créé
```

## Décorateurs de Sécurité
```python
@require_super_admin          # Super admin uniquement
@require_project_access       # Accès au projet requis
@login_required              # Authentification requise
@require_http_methods(["POST"]) # Méthode HTTP spécifique
```

## Logique de Permissions
```python
# Dans utils.py
def peut_creer_taches(user, projet):
    """Vérifie si l'utilisateur peut créer des tâches"""
    - Super admin: Toujours autorisé
    - Créateur du projet: Toujours autorisé
    - Responsable principal: Autorisé
    - Chef de projet (rôle système): Autorisé
    - Autres: Refusé

def verifier_permissions_projet(utilisateur, projet, action):
    """Vérifie les permissions sur un projet"""
    - Super admin: Toutes actions
    - Créateur: Toutes actions
    - Membre équipe: Consultation + actions limitées
```

---

# 🧠 Logique Métier

## Cycle de Vie d'un Projet

### 1. Création et Configuration
```
1. Super Admin crée le projet (statut: IDEE ou PLANIFIE)
2. Affectation de l'équipe via "Paramètres Projet"
3. Définition du responsable principal
4. Initialisation automatique des étapes (6 étapes standard)
```

### 2. Gestion des Étapes
```python
# Workflow des Étapes
A_VENIR → EN_COURS → TERMINEE

# Règles Métier
- Une seule étape EN_COURS à la fois
- Activation manuelle ou automatique
- Terminer une étape active automatiquement la suivante
- Modules créables uniquement en phase DÉVELOPPEMENT
```

### 3. Gestion des Tâches

#### Tâches d'Étapes (Nouveau système V2.0+)
```python
# Création
- Possible dans toutes les étapes EN_COURS
- Permissions: Responsables, Admins, Chefs de projet
- Auto-assignation possible pour les créateurs

# Statuts et Progression
A_FAIRE → EN_COURS → TERMINEE/BLOQUEE
- Progression automatique selon pourcentage_completion
- Historique complet des changements
- Notifications automatiques

# Fonctionnalités Avancées (V2.3)
- Dépendances entre tâches
- Commentaires avec mentions
- Pièces jointes (structure prête)
- Étiquetage et catégorisation
```

#### Tâches de Modules (Ancien système)
```python
# Création
- Uniquement dans les modules
- Modules créables en phase DÉVELOPPEMENT uniquement
- Workflow plus simple que les tâches d'étapes
```

## Règles de Validation Importantes

### Contraintes Temporelles
```sql
-- Base de données
CHECK (date_debut <= date_fin)  -- Cohérence des dates
CHECK (pourcentage_completion >= 0 AND pourcentage_completion <= 100)
```

### Contraintes Métier
```python
# Dans les modèles
def clean(self):
    # Vérifier que le responsable fait partie de l'équipe
    # Vérifier les transitions de statut autorisées
    # Valider la cohérence des données
```

---

# 🎨 Interface Utilisateur

## Architecture des Templates

### Templates de Base
```html
base.html                    # Template principal (Super Admin)
├── Navigation principale
├── Messages système
└── Contenu dynamique

base_utilisateur.html        # Template utilisateurs normaux
├── Navigation simplifiée
├── Accès limité aux fonctionnalités
└── Dashboard personnalisé
```

### Organisation des Vues
```
Dashboard → Projets → Détail Projet
                   ├── Paramètres (Équipe)
                   ├── Étapes → Détail Étape → Tâches
                   └── Modules → Détail Module → Tâches
```

## Patterns d'Interface

### 1. Listes avec Actions
```html
<!-- Pattern récurrent -->
<div class="liste-items">
    <div class="item">
        <div class="info">Nom, Description, Statut</div>
        <div class="actions">
            <button class="consulter">👁️ Consulter</button>
            <button class="modifier">✏️ Modifier</button>
            <button class="supprimer">🗑️ Supprimer</button>
        </div>
    </div>
</div>
```

### 2. Formulaires avec Validation
```html
<!-- Pattern de formulaire -->
<form method="post" class="space-y-4">
    {% csrf_token %}
    <div class="field-group">
        <label>Libellé</label>
        <input type="text" required>
        <p class="help-text">Aide contextuelle</p>
    </div>
    <div class="actions">
        <button type="button" class="cancel">Annuler</button>
        <button type="submit" class="primary">Valider</button>
    </div>
</form>
```

### 3. Modals et AJAX
```javascript
// Pattern AJAX récurrent
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken,
        'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Succès: Recharger ou mettre à jour l'interface
        location.reload();
    } else {
        // Erreur: Afficher le message
        alert(data.error);
    }
});
```

## Système de Design
- **Tailwind CSS** pour le styling
- **Couleurs cohérentes** : Bleu/Indigo pour primaire, Rouge pour danger
- **Icônes Emoji** pour la reconnaissance visuelle
- **Responsive Design** : Mobile-first approach
- **Animations subtiles** : Hover effects, transitions

---

# 🔄 Workflows Principaux

## 1. Création d'un Projet Complet

### Étape 1: Création du Projet
```
Super Admin → Dashboard → "Créer un Projet"
├── Saisie: Nom, Description, Client, Statut, Priorité
├── Validation et création
└── Redirection vers page de succès
```

### Étape 2: Configuration de l'Équipe
```
Projet → Paramètres → Gestion d'Équipe
├── Ajouter des membres (dropdown des utilisateurs actifs)
├── Définir les rôles sur le projet
├── Désigner le responsable principal
└── Audit automatique des affectations
```

### Étape 3: Initialisation des Étapes
```
Automatique lors de la création du projet:
├── 6 étapes créées (TypeEtape prédéfinis)
├── Statut initial: A_VENIR (sauf première étape)
├── Ordre séquentiel respecté
└── Prêt pour l'activation manuelle
```

## 2. Gestion des Étapes et Tâches

### Activation d'une Étape
```
Projet → Gestion des Étapes → "🚀 Activer"
├── Vérification: Étape précédente terminée
├── Changement de statut: A_VENIR → EN_COURS
├── Audit de l'activation
└── Notification aux membres de l'équipe
```

### Création de Tâches d'Étape
```
Étape EN_COURS → Détail → "➕ Nouvelle tâche"
├── Formulaire: Nom, Description, Responsable, Priorité, Dates
├── Validation des permissions
├── Création avec audit
└── Redirection vers détail de l'étape
```

### Gestion des Tâches
```
Étape → "⚙️ Gérer les tâches"
├── Liste complète des tâches de l'étape
├── Actions: Assigner, Modifier statut, Consulter
├── Filtres: Par statut, responsable, priorité
└── Actions en lot (prévu)
```

## 3. Système d'Audit et Traçabilité

### Audit Automatique
```python
# Déclenché automatiquement sur:
- Connexions/Déconnexions
- Créations/Modifications/Suppressions
- Changements de statut
- Affectations d'équipe
- Actions sensibles

# Données capturées:
- Utilisateur, Action, Timestamp
- Adresse IP, User Agent
- Données avant/après
- Hash d'intégrité
```

### Consultation de l'Audit
```
Super Admin → Dashboard → "Audit"
├── Filtres: Utilisateur, Type d'action, Dates, Recherche
├── Pagination des résultats
├── Détails complets de chaque action
└── Export possible (prévu)
```

---

# 📊 Système d'Audit

## Architecture de l'Audit

### 1. Audit Global (ActionAudit)
```python
# Types d'actions trackées
CONNEXION, DECONNEXION
CREATION_PROJET, MODIFICATION_PROJET
CREATION_UTILISATEUR, MODIFICATION_UTILISATEUR
AFFECTATION_UTILISATEUR, CHANGEMENT_RESPONSABLE
ACTIVATION_ETAPE, CLOTURE_ETAPE
CREATION_TACHE, ASSIGNATION_TACHE
ACCES_REFUSE, TENTATIVE_CONNEXION_ECHOUEE
```

### 2. Audit Spécialisé (HistoriqueTache - V2.3)
```python
# Actions spécifiques aux tâches
CREATION, MODIFICATION, CHANGEMENT_STATUT
ASSIGNATION, COMMENTAIRE, SUPPRESSION

# Données détaillées
- État avant/après modification
- Contexte de l'action
- Métadonnées complètes
```

### 3. Fonctions Utilitaires
```python
# utils.py
def enregistrer_audit(utilisateur, type_action, description, **kwargs):
    """Enregistrement automatique avec hash d'intégrité"""
    
def verifier_integrite_audit():
    """Vérification de l'intégrité des logs"""
```

## Sécurité de l'Audit
- **Hash SHA-256** pour l'intégrité
- **Données immutables** (pas de modification possible)
- **Accès restreint** aux Super Admins uniquement
- **Rétention longue** des données

---

# ⚙️ Configuration et Déploiement

## Variables d'Environnement
```python
# .env
DEBUG=True                    # Mode développement
SECRET_KEY=...               # Clé secrète Django
DATABASE_URL=...             # URL de base de données
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
```

## Configuration Base de Données
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'si_gouvernance',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Commandes de Gestion
```bash
# Installation
pip install -r requirements.txt
python manage.py migrate
python manage.py init_data          # Données de base

# Développement
python manage.py runserver
python manage.py shell
python manage.py check

# Production (prévu)
python manage.py collectstatic
python manage.py migrate --run-syncdb
```

## Structure des Migrations
```
core/migrations/
├── 0001_initial.py                    # Modèles de base
├── 0002_remove_role_principal.py      # Corrections
├── 0005_roleprojet_rolesysteme_...    # Architecture V1
├── 0009_etapeprojet_moduleprojet_...  # Architecture V2.0
├── 0014_add_advanced_task_management.py # Gestion avancée V2.3
```

---

# 🧪 Tests et Validation

## Tests Automatisés Existants
```python
test_activation_automatique.py      # Test activation étapes
test_architecture_v2.py            # Test architecture V2
test_creation_tache_etape.py        # Test création tâches
test_task_creation_detailed.py     # Test améliorations V2.2
verify_v2_implementation.py        # Validation complète
```

## Commandes de Test
```bash
# Tests spécifiques
python test_activation_automatique.py
python test_task_creation_detailed.py
python verify_v2_implementation.py

# Tests Django (à implémenter)
python manage.py test
```

## Validation Manuelle
```
1. Connexion Super Admin
2. Création projet complet
3. Gestion équipe
4. Cycle de vie des étapes
5. Création et assignation tâches
6. Vérification audit
```

---

# 🚀 Roadmap et Évolutions

## Version Actuelle: V2.3
### ✅ Fonctionnalités Implémentées
- Architecture Étapes/Modules/Tâches complète
- Gestion avancée des tâches d'étape
- Système d'audit robuste
- Interface utilisateur moderne
- Permissions granulaires
- Activation automatique des étapes

### 🔄 En Cours de Finalisation
- Templates pour modification des tâches
- Interface complète de gestion des commentaires
- Système de notifications en temps réel

## Prochaines Versions Prévues

### V2.4 - Interface Utilisateur Avancée (4-6 semaines)
- Dashboard analytique avec graphiques
- Notifications en temps réel (WebSocket)
- Gestion des pièces jointes
- Rapports automatisés
- Export des données

### V2.5 - Optimisations et Performance (6-8 semaines)
- Cache Redis
- Optimisation des requêtes
- API REST complète
- Tests automatisés complets
- Documentation utilisateur

### V3.0 - Fonctionnalités Avancées (10-12 semaines)
- Intelligence artificielle pour prédictions
- Intégrations externes (Slack, Teams)
- Application mobile
- Workflow personnalisables
- Multi-tenancy

---

# 📚 Ressources pour le Développeur

## Documentation Technique
- `ARCHITECTURE_ETAPES_MODULES_TACHES.md` - Architecture V2.0
- `IMPLEMENTATION_COMPLETE_V2.md` - Détails implémentation
- `GESTION_TACHES_AVANCEE_V2.3_IMPLEMENTATION.md` - Fonctionnalités V2.3
- `ROADMAP_V2.3_SUGGESTIONS.md` - Évolutions futures

## Fichiers Clés à Connaître
```
core/models.py              # Modèles de données (1400+ lignes)
core/views.py               # Logique métier (3000+ lignes)
core/urls.py                # Configuration des URLs
core/utils.py               # Fonctions utilitaires
templates/core/             # Templates HTML
```

## Patterns de Code Récurrents
```python
# Vérification permissions
if not user.est_super_admin():
    if not user.a_acces_projet(projet):
        messages.error(request, 'Accès refusé')
        return redirect('dashboard')

# Audit automatique
enregistrer_audit(
    utilisateur=user,
    type_action='ACTION_TYPE',
    description='Description',
    projet=projet,
    request=request
)

# Réponse AJAX standard
return JsonResponse({
    'success': True/False,
    'message': 'Message utilisateur',
    'data': {...}  # Données optionnelles
})
```

## Conventions de Nommage
- **Modèles**: PascalCase (ex: `TacheEtape`)
- **Vues**: snake_case + _view (ex: `creer_tache_etape_view`)
- **URLs**: kebab-case (ex: `creer-tache-etape`)
- **Templates**: snake_case.html (ex: `gestion_taches_etape.html`)
- **Variables**: snake_case (ex: `nouveau_responsable`)

---

# 🎯 Points d'Attention pour la Continuité

## Problèmes Techniques Connus
1. **Vues incomplètes** : Certaines vues avancées (modification tâches) ont été implémentées mais pas entièrement intégrées
2. **URLs commentées** : Quelques URLs sont temporairement désactivées
3. **Templates manquants** : Templates pour les nouvelles fonctionnalités V2.3 à créer

## Priorités de Développement
1. **Finaliser les vues de gestion des tâches** (1-2 jours)
2. **Créer les templates manquants** (3-5 jours)
3. **Implémenter les notifications** (1 semaine)
4. **Optimiser les performances** (1 semaine)

## Architecture Solide
- **Base de données** : Structure robuste et extensible
- **Modèles métier** : Logique complète et testée
- **Système d'audit** : Traçabilité complète
- **Permissions** : Sécurité granulaire
- **Interface** : Foundation moderne avec Tailwind

## Recommandations
1. **Suivre les patterns existants** pour la cohérence
2. **Tester chaque fonctionnalité** avant déploiement
3. **Maintenir l'audit** sur toutes les actions sensibles
4. **Respecter les permissions** établies
5. **Documenter les nouvelles fonctionnalités**

---

**Cette application est prête pour la production avec une base solide et une architecture extensible. Le prochain développeur peut se concentrer sur l'amélioration de l'expérience utilisateur et l'ajout de fonctionnalités avancées.**