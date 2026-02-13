# Liste Complète des Notifications Utilisateurs

## Vue d'Ensemble

Le système dispose de **4 types de notifications** et **1 système d'alertes** pour informer les utilisateurs des événements importants.

---

## 1. NOTIFICATIONS DE TÂCHES (NotificationTache)

### Types de Notifications

| Type | Nom | Description | Déclencheur |
|------|-----|-------------|-------------|
| `ASSIGNATION` | Assignation de tâche | Vous avez été assigné à une tâche | Création/modification de tâche avec responsable |
| `CHANGEMENT_STATUT` | Changement de statut | Le statut d'une tâche a changé | Modification du statut d'une tâche |
| `COMMENTAIRE` | Nouveau commentaire | Nouveau commentaire sur une tâche | Ajout d'un commentaire |
| `MENTION` | Mention dans un commentaire | Vous avez été mentionné | Mention @utilisateur dans un commentaire |
| `ECHEANCE` | Échéance approchante | Une tâche approche de sa date limite | Système automatique (à implémenter) |
| `RETARD` | Tâche en retard | Une tâche est en retard | Système automatique (à implémenter) |
| `PIECE_JOINTE` | Nouvelle pièce jointe | Nouvelle pièce jointe ajoutée | Upload de fichier sur une tâche |
| `ALERTE_ECHEANCE` | Alerte échéance (2j ou 1j) | Alerte 2 jours ou 1 jour avant échéance | Système automatique (à implémenter) |
| `ALERTE_CRITIQUE` | Alerte critique (jour J) | Alerte le jour de l'échéance | Système automatique (à implémenter) |
| `ALERTE_RETARD` | Alerte retard | Alerte pour tâche en retard | Système automatique (à implémenter) |

### Destinataires
- Responsable de la tâche
- Responsable du projet (pour tâches terminées)
- Administrateurs (pour tâches terminées)
- Utilisateurs mentionnés dans les commentaires

### Statut Actuel
✅ **Implémenté**: ASSIGNATION (tâches d'étape et de module)
✅ **Implémenté**: Notification de tâche terminée (responsable projet + admins)
⏳ **À implémenter**: COMMENTAIRE, MENTION, PIECE_JOINTE
⏳ **À implémenter**: Alertes automatiques d'échéance

---

## 2. NOTIFICATIONS D'ÉTAPES (NotificationEtape)

### Types de Notifications

| Type | Nom | Description | Déclencheur |
|------|-----|-------------|-------------|
| `ETAPE_TERMINEE` | Étape terminée | Une étape du projet est terminée | Toutes les tâches de l'étape terminées |
| `ETAPE_ACTIVEE` | Étape activée | Une nouvelle étape est activée | Activation manuelle d'une étape |
| `MODULES_DISPONIBLES` | Modules disponibles | Des modules sont disponibles pour affectation | Étape de développement activée |
| `RETARD_ETAPE` | Retard d'étape | Une étape est en retard | Système automatique (à implémenter) |
| `CHANGEMENT_STATUT` | Changement de statut | Le statut d'une étape a changé | Modification du statut |
| `CAS_TEST_PASSE` | Cas de test passé | Un cas de test a été marqué comme passé | Exécution réussie d'un cas de test |

### Destinataires
- Responsable du projet
- Administrateurs
- Membres de l'équipe projet

### Statut Actuel
✅ **Implémenté**: CAS_TEST_PASSE
⏳ **À implémenter**: ETAPE_TERMINEE, ETAPE_ACTIVEE, MODULES_DISPONIBLES
⏳ **À implémenter**: RETARD_ETAPE, CHANGEMENT_STATUT

---

## 3. NOTIFICATIONS DE MODULES (NotificationModule)

### Types de Notifications

| Type | Nom | Description | Déclencheur |
|------|-----|-------------|-------------|
| `AFFECTATION_MODULE` | Affectation au module | Vous avez été affecté à un module | Affectation d'un utilisateur à un module |
| `RETRAIT_MODULE` | Retrait du module | Vous avez été retiré d'un module | Retrait d'une affectation |
| `NOUVELLE_TACHE` | Nouvelle tâche assignée | Une nouvelle tâche vous a été assignée | Création de tâche de module |
| `TACHE_TERMINEE` | Tâche terminée | Une tâche du module est terminée | Tâche marquée à 100% |
| `CHANGEMENT_ROLE` | Changement de rôle | Votre rôle sur le module a changé | Modification du rôle d'affectation |
| `MODULE_TERMINE` | Module terminé | Un module a été clôturé | Clôture d'un module |

### Destinataires
- Responsable du module
- Responsable du projet
- Membres affectés au module

### Statut Actuel
✅ **Implémenté**: NOUVELLE_TACHE (création de tâche)
✅ **Implémenté**: TACHE_TERMINEE (progression à 100%)
✅ **Implémenté**: MODULE_TERMINE (clôture de module)
✅ **Implémenté**: CHANGEMENT_ROLE (transfert de tâche)
⏳ **À implémenter**: AFFECTATION_MODULE, RETRAIT_MODULE

---

## 4. NOTIFICATIONS DE PROJETS (NotificationProjet)

### Types de Notifications

| Type | Nom | Description | Déclencheur |
|------|-----|-------------|-------------|
| `AFFECTATION_RESPONSABLE` | Affectation comme responsable | Vous êtes responsable d'un projet | Affectation avec rôle responsable |
| `AJOUT_EQUIPE` | Ajout à l'équipe du projet | Vous avez été ajouté à l'équipe | Ajout d'un membre au projet |
| `PROJET_DEMARRE` | Projet démarré | Le projet a démarré | Démarrage officiel du projet |
| `ALERTE_FIN_PROJET` | Alerte fin de projet (J-7) | Le projet se termine dans 7 jours | Système automatique |
| `PROJET_TERMINE` | Projet terminé | Le projet est terminé | Toutes les étapes terminées |
| `PROJET_SUSPENDU` | Projet suspendu | Le projet a été suspendu | Changement de statut |
| `CHANGEMENT_ECHEANCE` | Changement d'échéance | La date de fin a été modifiée | Modification de la date |
| `ASSIGNATION_TICKET_MAINTENANCE` | Assignation ticket de maintenance | Un ticket vous a été assigné | Assignation d'un ticket |
| `TICKET_RESOLU` | Ticket de maintenance résolu | Un ticket a été résolu | Résolution d'un ticket |

### Destinataires
- Responsable du projet
- Membres de l'équipe
- Administrateurs
- Développeurs assignés aux tickets

### Statut Actuel
✅ **Implémenté**: AJOUT_EQUIPE
✅ **Implémenté**: ASSIGNATION_TICKET_MAINTENANCE
✅ **Implémenté**: TICKET_RESOLU
⏳ **À implémenter**: AFFECTATION_RESPONSABLE, PROJET_DEMARRE
⏳ **À implémenter**: ALERTE_FIN_PROJET, PROJET_TERMINE, PROJET_SUSPENDU
⏳ **À implémenter**: CHANGEMENT_ECHEANCE

---

## 5. ALERTES SYSTÈME (AlerteProjet)

### Types d'Alertes

| Type | Nom | Niveau | Description | Déclencheur |
|------|-----|--------|-------------|-------------|
| `ECHEANCE_J7` | Échéance dans 7 jours | WARNING | Projet se termine dans 7 jours | Commande automatique |
| `ECHEANCE_J3` | Échéance dans 3 jours | WARNING | Projet se termine dans 3 jours | Commande automatique |
| `ECHEANCE_J1` | Échéance dans 1 jour | DANGER | Projet se termine demain | Commande automatique |
| `ECHEANCE_DEPASSEE` | Échéance dépassée | DANGER | Projet en retard | Commande automatique |
| `BUDGET_DEPASSE` | Budget dépassé | DANGER | Budget du projet dépassé | À implémenter |
| `TACHES_EN_RETARD` | Tâches en retard | WARNING | Tâches en retard sur le projet | Commande automatique |
| `CONTRAT_EXPIRATION` | Contrat proche expiration | WARNING | Contrat expire dans 30 jours | Commande automatique |
| `CONTRAT_EXPIRE` | Contrat expiré | DANGER | Contrat de maintenance expiré | Commande automatique |

### Niveaux d'Alerte
- **INFO**: Information simple
- **WARNING**: Avertissement (jaune)
- **DANGER**: Critique (rouge)

### Destinataires
- Responsable du projet
- Administrateurs système

### Statut Actuel
✅ **Implémenté**: ECHEANCE_J7 (via `check_project_deadlines.py`)
✅ **Implémenté**: ECHEANCE_DEPASSEE (via `check_project_deadlines.py`)
✅ **Implémenté**: TACHES_EN_RETARD (via `check_task_deadlines.py`)
✅ **Implémenté**: CONTRAT_EXPIRATION (via `check_contract_expiration.py`)
✅ **Implémenté**: CONTRAT_EXPIRE (via `check_contract_expiration.py`)
⏳ **À implémenter**: ECHEANCE_J3, ECHEANCE_J1
⏳ **À implémenter**: BUDGET_DEPASSE

---

## Commandes Automatiques

### Alertes Projets
```bash
python manage.py check_project_deadlines
```
- Vérifie les échéances de projets (J-7 et dépassées)
- Envoie des emails aux responsables
- Crée des alertes dans le système

### Alertes Tâches
```bash
python manage.py check_task_deadlines
```
- Vérifie les tâches en retard
- Envoie des emails aux responsables
- Crée des alertes dans le système

### Alertes Contrats
```bash
python manage.py check_contract_expiration
```
- Vérifie les contrats expirant dans 30 jours
- Vérifie les contrats expirés
- Envoie des emails aux responsables
- Crée des alertes dans le système

### Automatisation Windows
Fichiers batch créés:
- `run_check_deadlines.bat` - Vérifie projets et tâches
- `run_check_all_alerts.bat` - Vérifie tout (projets, tâches, contrats)

---

## Caractéristiques Communes

### Tous les Types de Notifications

**Champs communs**:
- `destinataire`: Utilisateur qui reçoit la notification
- `titre`: Titre court de la notification
- `message`: Message détaillé
- `lue`: Statut lu/non lu
- `date_creation`: Date de création
- `date_lecture`: Date de lecture (si lue)
- `emetteur`: Utilisateur qui a déclenché la notification (optionnel)
- `donnees_contexte`: Données JSON supplémentaires

**Méthodes**:
- `marquer_comme_lue()`: Marque la notification comme lue

---

## Interface Utilisateur

### Accès aux Notifications
- **Icône cloche** dans la navbar (badge avec nombre de non lues)
- **Page dédiée** pour chaque type:
  - Mes Tâches (notifications de tâches)
  - Mes Modules (notifications de modules)
  - Mes Projets (notifications de projets)
  - Alertes (page dédiée `/alertes/`)

### Affichage
- Notifications non lues en gras
- Badge de couleur selon le type
- Lien direct vers l'élément concerné
- Possibilité de marquer comme lu

---

## Statistiques Actuelles

### Notifications Implémentées
- **NotificationTache**: 2/10 types (20%)
- **NotificationEtape**: 1/6 types (17%)
- **NotificationModule**: 4/6 types (67%)
- **NotificationProjet**: 3/9 types (33%)
- **AlerteProjet**: 5/8 types (63%)

### Total Global
**15/39 types de notifications implémentés (38%)**

---

## Prochaines Implémentations Recommandées

### Priorité Haute
1. **NotificationEtape.ETAPE_TERMINEE** - Informer quand une étape est terminée
2. **NotificationModule.AFFECTATION_MODULE** - Informer lors de l'affectation
3. **NotificationProjet.PROJET_DEMARRE** - Informer du démarrage du projet
4. **AlerteProjet.ECHEANCE_J3** et **ECHEANCE_J1** - Alertes supplémentaires

### Priorité Moyenne
5. **NotificationTache.COMMENTAIRE** - Système de commentaires
6. **NotificationTache.PIECE_JOINTE** - Notification d'upload
7. **NotificationProjet.PROJET_TERMINE** - Fin de projet
8. **NotificationEtape.MODULES_DISPONIBLES** - Modules prêts

### Priorité Basse
9. **NotificationTache.MENTION** - Système de mentions @
10. **AlerteProjet.BUDGET_DEPASSE** - Suivi budgétaire

---

## Fichiers Concernés

### Modèles
- `core/models.py` (lignes 2050-2320)

### Vues
- `core/views.py` (notifications de tâches d'étape)
- `core/views_taches_module.py` (notifications de modules)
- `core/views_maintenance_v2.py` (notifications de tickets)

### Commandes
- `core/management/commands/check_project_deadlines.py`
- `core/management/commands/check_task_deadlines.py`
- `core/management/commands/check_contract_expiration.py`

### Templates
- `templates/core/alertes.html` (page des alertes)
- `templates/base.html` (icône cloche dans navbar)

---

## Notes Importantes

1. **Différence Notifications vs Alertes**:
   - **Notifications**: Déclenchées par des actions utilisateurs
   - **Alertes**: Générées automatiquement par le système

2. **Envoi d'Emails**:
   - Les alertes système envoient des emails automatiquement
   - Les notifications peuvent être configurées pour envoyer des emails

3. **Performance**:
   - Index sur `destinataire`, `lue`, `date_creation`
   - Requêtes optimisées pour l'affichage

4. **Sécurité**:
   - Seul le destinataire peut voir ses notifications
   - Les notifications sont supprimées avec le compte utilisateur
