# Guide d'utilisation - Mes Tâches

## 📋 Fonctionnalité "Mes Tâches" pour les Membres

Cette fonctionnalité permet aux membres d'un projet de visualiser et gérer leurs tâches assignées de manière autonome.

## 🎯 Objectifs

- Permettre aux membres de voir toutes leurs tâches dans un projet
- Donner la possibilité de changer le statut de leurs tâches
- Offrir une interface simple pour marquer les tâches comme terminées
- Fournir des statistiques sur l'avancement personnel

## 🚀 Accès à la fonctionnalité

### Pour les membres d'un projet :

1. **Accéder au projet** : Aller sur la page de détail du projet
2. **Cliquer sur "Mes Tâches"** : Le bouton apparaît automatiquement pour les membres du projet
3. **Gérer ses tâches** : Utiliser l'interface pour voir et modifier ses tâches

### Conditions d'accès :

- ✅ Être membre actif du projet (avoir une affectation active)
- ✅ Avoir des tâches assignées dans le projet
- ✅ Être connecté avec un compte utilisateur valide

## 🎨 Interface utilisateur

### Tableau de bord des tâches

L'interface affiche :

- **Statistiques en temps réel** :
  - Total des tâches assignées
  - Tâches en cours
  - Tâches terminées
  - Tâches bloquées

- **Filtres disponibles** :
  - Par statut (À faire, En cours, Terminée, Bloquée)
  - Par priorité (Basse, Moyenne, Haute, Critique)

### Informations par tâche

Pour chaque tâche, l'utilisateur voit :

- **Nom et description** de la tâche
- **Étape** à laquelle elle appartient
- **Dates** de début et fin prévues
- **Barre de progression** (pourcentage de completion)
- **Statut actuel** avec badge coloré
- **Priorité** avec indicateur visuel
- **Actions disponibles** (voir ci-dessous)

## ⚡ Actions disponibles

### 1. Changer le statut d'une tâche

Les membres peuvent modifier le statut de leurs tâches :

- **⏸️ À faire** : Tâche pas encore commencée
- **⏳ En cours** : Tâche en cours d'exécution
- **🚫 Bloquée** : Tâche bloquée (avec possibilité d'ajouter une raison)
- **✅ Terminée** : Tâche complètement terminée

### 2. Terminer rapidement une tâche

- **Bouton "Terminer"** : Action rapide pour marquer une tâche comme terminée
- **Confirmation** : Modal de confirmation pour éviter les erreurs
- **Mise à jour automatique** : Date de fin réelle enregistrée automatiquement

### 3. Filtrer et rechercher

- **Filtres par statut** : Voir seulement les tâches d'un statut donné
- **Filtres par priorité** : Se concentrer sur les tâches prioritaires
- **Reset des filtres** : Revenir à la vue complète

## 🔧 Fonctionnalités techniques

### Gestion des permissions

- **Vérification d'accès** : Seuls les responsables de tâches peuvent les modifier
- **Audit complet** : Toutes les actions sont enregistrées dans l'audit
- **Sécurité** : Validation côté serveur de toutes les modifications

### Mise à jour en temps réel

- **AJAX** : Modifications sans rechargement de page
- **Notifications** : Messages de confirmation pour chaque action
- **Actualisation** : Rechargement automatique après modification

### Suivi et historique

- **Date de début réelle** : Enregistrée automatiquement au passage "En cours"
- **Date de fin réelle** : Enregistrée à la completion
- **Pourcentage** : Mis à 100% automatiquement à la completion
- **Audit trail** : Historique complet des changements

## 📊 Statistiques et rapports

### Métriques personnelles

- **Taux de completion** : Pourcentage de tâches terminées
- **Répartition par statut** : Vue d'ensemble de l'avancement
- **Charge de travail** : Nombre total de tâches assignées

### Données pour les responsables

Les actions des membres génèrent des données utiles pour :

- **Suivi de projet** : Avancement réel vs prévisionnel
- **Gestion d'équipe** : Performance individuelle
- **Planification** : Estimation des délais

## 🛠️ Configuration technique

### URLs disponibles

```python
# Vue principale des tâches
path('projets/<uuid:projet_id>/mes-taches/', views.mes_taches_view, name='mes_taches')

# Terminer une tâche
path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/terminer/<str:type_tache>/', views.terminer_tache_view, name='terminer_tache')

# Changer le statut d'une tâche
path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/changer-statut/<str:type_tache>/', views.changer_statut_ma_tache_view, name='changer_statut_ma_tache')
```

### Modèles concernés

- **TacheEtape** : Tâches liées aux étapes
- **TacheModule** : Tâches liées aux modules (si disponible)
- **ActionAudit** : Enregistrement des actions

## 🔍 Tests et validation

### Script de test inclus

Un script `test_mes_taches.py` est fourni pour :

- Vérifier la configuration
- Créer des données de test
- Valider le fonctionnement

### Exécution des tests

```bash
python test_mes_taches.py
```

## 🚨 Gestion des erreurs

### Erreurs courantes

1. **"Vous n'êtes pas responsable de cette tâche"**
   - Cause : Tentative de modification d'une tâche non assignée
   - Solution : Vérifier l'assignation des tâches

2. **"Cette tâche est déjà terminée"**
   - Cause : Tentative de terminer une tâche déjà terminée
   - Solution : Actualiser la page

3. **"Accès refusé au projet"**
   - Cause : Utilisateur non membre du projet
   - Solution : Vérifier les affectations de projet

### Logs et audit

Toutes les actions sont enregistrées avec :

- **Utilisateur** qui a effectué l'action
- **Timestamp** précis
- **Données avant/après** modification
- **Adresse IP** et informations de session

## 📈 Évolutions futures

### Fonctionnalités prévues

- **Commentaires** sur les tâches
- **Pièces jointes** aux tâches
- **Notifications** push en temps réel
- **Estimation du temps** passé
- **Dépendances** entre tâches

### Intégrations possibles

- **Calendrier** personnel
- **Notifications email** automatiques
- **Rapports** d'activité
- **API** pour applications mobiles

## 💡 Conseils d'utilisation

### Pour les membres

1. **Consultez régulièrement** vos tâches
2. **Mettez à jour le statut** dès que possible
3. **Utilisez les filtres** pour vous organiser
4. **Marquez comme bloqué** si vous rencontrez des obstacles

### Pour les chefs de projet

1. **Assignez clairement** les tâches
2. **Suivez l'avancement** via les statistiques
3. **Communiquez** sur les priorités
4. **Utilisez l'audit** pour le suivi

---

## 🎉 Résumé

La fonctionnalité "Mes Tâches" offre aux membres une autonomie complète dans la gestion de leurs tâches tout en maintenant un suivi rigoureux pour les responsables de projet. Elle s'intègre parfaitement dans l'écosystème SI-Gouvernance existant.