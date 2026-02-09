# 🏗️ Architecture - Démarrage et Suivi Temporel des Projets

## 📋 Vue d'ensemble

Implémentation d'une logique professionnelle de démarrage et suivi temporel des projets avec alertes automatiques à J-7.

## 🎯 Règles Métier

### 1️⃣ Création du Projet
```
État initial :
- statut = CREE
- date_debut = NULL
- date_fin = NULL
- duree_projet = X jours (défini par l'admin)
- responsable = assigné
```

### 2️⃣ Démarrage du Projet
```
Déclencheur : Responsable clique sur "Commencer le projet"

Actions :
- date_debut = aujourd'hui
- date_fin = date_debut + duree_projet
- statut = EN_COURS
- Notification à l'équipe
```

### 3️⃣ Alerte J-7
```
Détection automatique :
- Projets EN_COURS
- date_fin dans 7 jours

Notifications :
- Administrateur
- Responsable du projet
- Équipe du projet
```

## 🗄️ Modifications du Modèle

### Projet (ajouts)
```python
# Nouveaux champs
duree_projet = IntegerField(help_text="Durée en jours")
date_debut = DateField(null=True, blank=True)
date_fin = DateField(null=True, blank=True)

# Méthodes
def peut_etre_demarre()
def demarrer_projet(utilisateur)
def jours_restants()
def est_proche_fin()  # J-7
```

## 📁 Fichiers à Créer/Modifier

### 1. Migration
- `core/migrations/0027_add_projet_timing_fields.py`

### 2. Modèle
- `core/models.py` (Projet)

### 3. Vue
- `core/views.py` (demarrer_projet_view)

### 4. Template
- `templates/core/projet_detail.html` (bouton démarrage)

### 5. URL
- `core/urls.py`

### 6. Management Command
- `core/management/commands/check_project_deadlines.py`

### 7. Tests
- `test_demarrage_projet.py`

## 🔄 Flux de Travail

```
1. Admin crée projet
   ↓
2. Responsable reçoit notification
   ↓
3. Responsable ouvre projet
   ↓
4. Voit bouton "Commencer le projet"
   ↓
5. Clique → date_debut/date_fin calculées
   ↓
6. Projet EN_COURS
   ↓
7. Command quotidien vérifie J-7
   ↓
8. Crée alertes si nécessaire
```

## 🎨 Interface

### Bouton "Commencer le projet"
```
Visible si :
- utilisateur = responsable
- statut = CREE
- date_debut = NULL

Style : Bouton vert proéminent
```

### Affichage Temporel
```
Si EN_COURS :
- Date de début
- Date de fin
- Jours restants (badge coloré)
- Barre de progression
```

## 🔔 Notifications

### Type 1 : Affectation Responsable
```
Titre : "Vous êtes responsable du projet X"
Message : "Cliquez pour démarrer le projet"
Type : AFFECTATION_RESPONSABLE
```

### Type 2 : Projet Démarré
```
Titre : "Le projet X a démarré"
Message : "Date de fin : DD/MM/YYYY"
Destinataires : Équipe
Type : PROJET_DEMARRE
```

### Type 3 : Alerte J-7
```
Titre : "⚠️ Projet X - Fin dans 7 jours"
Message : "Le projet se termine le DD/MM/YYYY"
Destinataires : Admin + Responsable + Équipe
Type : ALERTE_FIN_PROJET
```

## 📊 Statuts du Projet

```python
STATUT_CHOICES = [
    ('CREE', 'Créé'),           # Nouveau
    ('EN_COURS', 'En cours'),   # Démarré
    ('TERMINE', 'Terminé'),
    ('SUSPENDU', 'Suspendu'),
    ('ANNULE', 'Annulé'),
]
```

## ✅ Checklist d'Implémentation

- [ ] Migration : Ajouter champs au modèle Projet
- [ ] Modèle : Ajouter méthodes métier
- [ ] Vue : Créer vue de démarrage
- [ ] Template : Ajouter bouton et affichage temporel
- [ ] URL : Ajouter route
- [ ] Command : Créer check_project_deadlines
- [ ] Tests : Tester le flux complet
- [ ] Documentation : Documenter l'utilisation

---

**Date** : 09/02/2026  
**Statut** : Architecture définie  
**Prochaine étape** : Implémentation
