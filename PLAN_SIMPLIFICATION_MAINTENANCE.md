# Plan de Simplification - Système de Maintenance

## 🎯 Objectif

Simplifier et professionnaliser la gestion de la maintenance en supprimant la séparation complexe Ticket → Billet → Intervention → Statut Technique.

**Inspiration** : Jira, GitHub Issues, Linear - Un ticket = Une unité de travail complète

---

## 📊 Architecture Actuelle (Complexe)

```
Ticket de Maintenance
    ↓
Billet d'Intervention (autorisation)
    ↓
Intervention Maintenance (travail réel)
    ↓
Statut Technique (rapport final)
```

**Problèmes** :
- ❌ Trop de niveaux d'abstraction
- ❌ Processus lourd et bureaucratique
- ❌ Difficile à comprendre pour les utilisateurs
- ❌ Multiplication des entités en base de données
- ❌ Workflow complexe

---

## ✅ Architecture Simplifiée (Proposée)

```
Ticket de Maintenance (UNIQUE)
    ├─ Informations de base
    ├─ Développeur(s) assigné(s)
    ├─ Commentaires / Historique
    └─ Statut (Ouvert → En cours → Résolu → Fermé)
```

**Avantages** :
- ✅ Une seule entité = Plus simple
- ✅ Workflow clair et direct
- ✅ Facile à comprendre
- ✅ Aligné avec les standards (Jira, GitHub)
- ✅ Évolutif (possibilité d'ajouter des sous-tâches plus tard)

---

## 🔄 Nouveau Modèle `TicketMaintenance`

### Champs Principaux

```python
class TicketMaintenance(models.Model):
    # Identification
    id = UUIDField
    numero_ticket = CharField (auto-généré: MAINT-00001)
    
    # Relations
    projet = ForeignKey(Projet)
    contrat_garantie = ForeignKey(ContratGarantie)  # OBLIGATOIRE et ACTIF
    
    # Description
    titre = CharField(max_length=200)
    description = TextField
    
    # Classification
    type_demande = CharField  # BUG, AMELIORATION, QUESTION, AUTRE
    priorite = CharField  # BASSE, NORMALE, HAUTE, CRITIQUE
    gravite = CharField  # MINEUR, MAJEUR, CRITIQUE
    
    # Statut et workflow
    statut = CharField  # OUVERT, EN_COURS, RESOLU, FERME, REJETE
    
    # Assignation
    assigne_a = ManyToManyField(Utilisateur)  # Plusieurs développeurs possibles
    
    # Suivi temporel
    date_creation = DateTimeField
    date_debut_travail = DateTimeField (null=True)
    date_resolution = DateTimeField (null=True)
    date_fermeture = DateTimeField (null=True)
    temps_estime = DecimalField  # Heures estimées
    temps_passe = DecimalField  # Heures réelles
    
    # Résolution
    solution = TextField  # Description de la solution apportée
    fichiers_modifies = TextField  # Liste des fichiers modifiés
    
    # Métadonnées
    cree_par = ForeignKey(Utilisateur)
    modifie_par = ForeignKey(Utilisateur)
    date_modification = DateTimeField
    
    # Garantie
    est_sous_garantie = BooleanField
    raison_hors_garantie = TextField
```

### Modèle de Commentaire (Nouveau)

```python
class CommentaireTicket(models.Model):
    """Commentaires et historique du ticket"""
    id = UUIDField
    ticket = ForeignKey(TicketMaintenance)
    auteur = ForeignKey(Utilisateur)
    contenu = TextField
    est_interne = BooleanField  # Visible seulement par l'équipe
    date_creation = DateTimeField
    
    # Pièces jointes (optionnel)
    fichier = FileField (null=True)
```

---

## 🗑️ Modèles à Supprimer

1. ❌ `BilletIntervention` - Fusionné dans `TicketMaintenance`
2. ❌ `InterventionMaintenance` - Fusionné dans `TicketMaintenance`
3. ❌ `StatutTechnique` - Fusionné dans `TicketMaintenance` (champ `solution`)

**Conservé** :
- ✅ `ContratGarantie` - Toujours nécessaire
- ✅ `TicketMaintenance` - Simplifié et enrichi

---

## 📋 Workflow Simplifié

### 1. Création du Ticket

**Qui** : Admin ou Responsable du projet  
**Condition** : Contrat de maintenance actif obligatoire

**Champs requis** :
- Titre
- Description
- Type de demande
- Priorité
- Gravité

**Automatique** :
- Statut = OUVERT
- Vérification du contrat actif
- Génération du numéro de ticket

### 2. Assignation

**Qui** : Admin ou Responsable du projet  
**Action** : Assigner un ou plusieurs développeurs

**Automatique** :
- Statut passe à EN_COURS
- `date_debut_travail` enregistrée
- Notification aux développeurs assignés

### 3. Travail sur le Ticket

**Qui** : Développeur(s) assigné(s)

**Actions possibles** :
- Ajouter des commentaires
- Mettre à jour le temps passé
- Modifier les fichiers concernés
- Documenter la solution

### 4. Résolution

**Qui** : Développeur assigné

**Action** : Marquer comme RESOLU

**Champs requis** :
- Solution apportée
- Fichiers modifiés (optionnel)
- Temps passé

**Automatique** :
- Statut = RESOLU
- `date_resolution` enregistrée
- Notification au créateur et responsable

### 5. Fermeture

**Qui** : Admin ou Responsable du projet (après validation client)

**Action** : Marquer comme FERME

**Automatique** :
- Statut = FERME
- `date_fermeture` enregistrée
- Ticket archivé

---

## 🔐 Règles de Gouvernance (Conservées)

### Création de Ticket
- ✅ Admin peut créer
- ✅ Responsable du projet peut créer
- ❌ Autres rôles ne peuvent pas créer
- ✅ Contrat actif OBLIGATOIRE

### Assignation
- ✅ Admin peut assigner
- ✅ Responsable du projet peut assigner
- ✅ Peut assigner plusieurs développeurs

### Modification du Statut
- ✅ Développeur assigné peut passer à RESOLU
- ✅ Admin/Responsable peut passer à FERME
- ✅ Admin/Responsable peut REJETER

### Commentaires
- ✅ Tous les membres de l'équipe peuvent commenter
- ✅ Commentaires internes (équipe seulement)
- ✅ Commentaires publics (visibles par le client)

---

## 🔄 Plan de Migration

### Étape 1 : Créer le Nouveau Modèle

**Fichier** : `core/models_maintenance.py`

1. Créer `CommentaireTicket`
2. Modifier `TicketMaintenance` avec les nouveaux champs
3. Ajouter les méthodes métier

### Étape 2 : Migration de Données

**Script de migration** : `migrate_maintenance_data.py`

```python
# Pour chaque ancien ticket :
# 1. Conserver les données de base
# 2. Extraire les infos des billets → champs du ticket
# 3. Extraire les infos des interventions → champs du ticket
# 4. Extraire le statut technique → champ solution
# 5. Créer des commentaires pour l'historique
```

### Étape 3 : Modifier les Vues

**Fichier** : `core/views_maintenance.py`

1. Simplifier `creer_ticket_view`
2. Ajouter `assigner_ticket_view`
3. Ajouter `ajouter_commentaire_view`
4. Simplifier `detail_ticket_view`
5. Supprimer les vues de billet/intervention

### Étape 4 : Modifier les Templates

1. Simplifier `creer_ticket.html`
2. Refaire `detail_ticket.html` (style Jira)
3. Supprimer les templates de billet/intervention

### Étape 5 : Nettoyer

1. Supprimer les anciens modèles
2. Supprimer les anciennes vues
3. Supprimer les anciens templates
4. Mettre à jour les URLs

---

## 🎨 Interface Utilisateur (Style Jira)

### Page de Liste des Tickets

```
┌─────────────────────────────────────────────────────┐
│ 🎫 Tickets de Maintenance - Projet X               │
│                                                     │
│ [+ Créer un ticket]  [Filtres ▼]  [Recherche 🔍]  │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ MAINT-00001 │ 🔴 CRITIQUE │ 🟢 RESOLU       │   │
│ │ Bug critique sur la page de connexion       │   │
│ │ Assigné à: Jean Dupont │ Créé il y a 2h    │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ MAINT-00002 │ 🟡 HAUTE │ 🔵 EN_COURS       │   │
│ │ Amélioration de la performance              │   │
│ │ Assigné à: Marie Martin, Paul Durand        │   │
│ └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Page de Détail du Ticket

```
┌─────────────────────────────────────────────────────┐
│ MAINT-00001 - Bug critique sur la page de connexion│
│                                                     │
│ Statut: 🟢 RESOLU  │  Priorité: 🔴 CRITIQUE       │
│ Créé par: Admin    │  Créé le: 12/02/2026 10:30   │
│                                                     │
│ ┌─ Description ──────────────────────────────┐    │
│ │ Les utilisateurs ne peuvent pas se         │    │
│ │ connecter depuis ce matin...               │    │
│ └────────────────────────────────────────────┘    │
│                                                     │
│ ┌─ Assigné à ───────────────────────────────┐    │
│ │ 👤 Jean Dupont (Développeur)               │    │
│ └────────────────────────────────────────────┘    │
│                                                     │
│ ┌─ Temps ───────────────────────────────────┐    │
│ │ Estimé: 4h │ Passé: 3.5h │ Restant: 0.5h  │    │
│ └────────────────────────────────────────────┘    │
│                                                     │
│ ┌─ Solution ────────────────────────────────┐    │
│ │ Correction du bug dans auth.py ligne 45    │    │
│ │ Fichiers modifiés: auth.py, login.html     │    │
│ └────────────────────────────────────────────┘    │
│                                                     │
│ ┌─ Commentaires (3) ────────────────────────┐    │
│ │ Jean Dupont - Il y a 1h                    │    │
│ │ J'ai identifié le problème...              │    │
│ │                                             │    │
│ │ Admin - Il y a 30min                       │    │
│ │ Merci, pouvez-vous déployer ?              │    │
│ └────────────────────────────────────────────┘    │
│                                                     │
│ [Ajouter un commentaire]  [Changer le statut]     │
└─────────────────────────────────────────────────────┘
```

---

## ⚠️ Points d'Attention

### 1. Migration de Données

- ⚠️ Nécessite un script de migration soigné
- ⚠️ Tester sur une copie de la base avant production
- ⚠️ Prévoir un rollback si problème

### 2. Historique

- ⚠️ Conserver l'historique des anciens tickets
- ⚠️ Créer des commentaires pour tracer les anciennes interventions

### 3. Permissions

- ⚠️ Vérifier que toutes les règles de gouvernance sont respectées
- ⚠️ Tester avec différents rôles

### 4. Performance

- ⚠️ Indexer les champs de recherche (numero_ticket, statut, priorite)
- ⚠️ Optimiser les requêtes avec select_related/prefetch_related

---

## 📅 Planning d'Implémentation

### Phase 1 : Préparation (1-2h)
- ✅ Créer le nouveau modèle `TicketMaintenance` simplifié
- ✅ Créer le modèle `CommentaireTicket`
- ✅ Créer la migration Django

### Phase 2 : Migration de Données (2-3h)
- ⚠️ Créer le script de migration
- ⚠️ Tester sur une copie de la base
- ⚠️ Valider les données migrées

### Phase 3 : Vues et Logique (2-3h)
- ✅ Modifier les vues existantes
- ✅ Ajouter les nouvelles vues (commentaires, assignation)
- ✅ Supprimer les anciennes vues

### Phase 4 : Interface (2-3h)
- ✅ Créer les nouveaux templates
- ✅ Style moderne (Tailwind CSS)
- ✅ Interface responsive

### Phase 5 : Tests et Validation (1-2h)
- ✅ Tests fonctionnels
- ✅ Tests de permissions
- ✅ Tests de workflow complet

**Total estimé** : 8-13 heures

---

## ✅ Avantages de la Simplification

### Pour les Utilisateurs
- ✅ Interface plus simple et intuitive
- ✅ Moins de clics pour accomplir une tâche
- ✅ Workflow clair et compréhensible

### Pour les Développeurs
- ✅ Code plus maintenable
- ✅ Moins de modèles à gérer
- ✅ Logique métier simplifiée

### Pour le Projet
- ✅ Aligné avec les standards du marché (Jira, GitHub)
- ✅ Évolutif (possibilité d'ajouter des fonctionnalités)
- ✅ Performance améliorée (moins de jointures SQL)

---

## 🚀 Prochaines Étapes

1. **Validation** : Valider ce plan avec l'équipe
2. **Backup** : Faire une sauvegarde complète de la base
3. **Implémentation** : Suivre les phases ci-dessus
4. **Tests** : Tests approfondis avant mise en production
5. **Documentation** : Mettre à jour la documentation utilisateur

---

**Date de création** : 12 février 2026  
**Statut** : 📋 PLAN - En attente de validation
