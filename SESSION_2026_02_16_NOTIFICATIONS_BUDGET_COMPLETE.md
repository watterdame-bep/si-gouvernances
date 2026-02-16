# Session 2026-02-16 : Notifications Budget - Implémentation Complète

## 📋 Résumé de la Session

Implémentation complète du système de notifications pour la gestion budgétaire des projets, incluant les notifications lors de la définition du budget et lors du dépassement du budget.

---

## ✅ Fonctionnalités Implémentées

### 1. Notification lors de la Définition du Budget

**Déclencheur**: Lorsqu'un administrateur ou responsable de projet définit/modifie le budget total d'un projet

**Destinataires**: Tous les administrateurs (Super Admins)

**Canaux**: 
- Notification dans l'application (NotificationProjet)
- Email professionnel HTML

**Fichiers modifiés**:
- `core/views.py` - Fonction `modifier_budget_projet()`

**Détails de l'implémentation**:
```python
# Créer notification pour les administrateurs
from .models import NotificationProjet
from .utils_notifications_email import envoyer_email_notification_projet

admins = Utilisateur.objects.filter(is_superuser=True, statut_actif=True)
for admin in admins:
    notification = NotificationProjet.objects.create(
        destinataire=admin,
        projet=projet,
        type_notification='CHANGEMENT_ECHEANCE',
        titre=f'Budget défini - {projet.nom}',
        message=f'{user.get_full_name()} a défini le budget du projet "{projet.nom}" à {nouveau_budget:,.0f}€',
        emetteur=user,
        donnees_contexte={
            'ancien_budget': ancien_budget,
            'nouveau_budget': nouveau_budget,
            'type_action': 'DEFINITION_BUDGET'
        }
    )
    
    # Envoyer email
    envoyer_email_notification_projet(notification)
```

**Informations dans la notification**:
- Nom du projet
- Montant du budget défini
- Nom de la personne qui a défini le budget
- Ancien budget (dans donnees_contexte)
- Nouveau budget (dans donnees_contexte)

---

### 2. Notification lors du Dépassement du Budget

**Déclencheur**: Lorsque le budget consommé (somme des dépenses) dépasse le budget total défini

**Destinataires**: 
- Administrateur (créateur du projet)
- Responsable principal du projet

**Canaux**:
- Alerte dans l'application (AlerteProjet)
- Email professionnel HTML

**Fichiers modifiés**:
- `core/management/commands/check_budget.py`

**Détails de l'implémentation**:

#### Calcul du Budget Consommé
```python
def _calculer_budget_consomme(self, projet):
    from core.models_budget import ResumeBudget
    
    # Utiliser la classe ResumeBudget pour calculer le budget consommé
    resume = ResumeBudget(projet)
    return resume.total_depenses
```

#### Création des Alertes
```python
def _creer_alerte_budget_depasse(self, projet, budget_consomme, depassement, pourcentage_depassement):
    from core.utils_notifications_email import envoyer_email_alerte_projet
    
    destinataires = set()
    
    # 1. Administrateur (créateur du projet)
    if projet.createur:
        destinataires.add(projet.createur)
    
    # 2. Responsable du projet
    responsable = projet.get_responsable_principal()
    if responsable:
        destinataires.add(responsable)
    
    for destinataire in destinataires:
        alerte = AlerteProjet.objects.create(
            destinataire=destinataire,
            projet=projet,
            type_alerte='BUDGET_DEPASSE',
            niveau='DANGER',
            titre=f"🔴 Budget dépassé - {projet.nom}",
            message=message,
            lue=False,
            donnees_contexte={
                'budget_previsionnel': float(projet.budget_previsionnel),
                'budget_consomme': float(budget_consomme),
                'depassement': float(depassement),
                'pourcentage_depassement': float(pourcentage_depassement),
                'devise': projet.devise,
                'type_alerte': 'BUDGET_DEPASSE'
            }
        )
        
        # Envoyer email
        envoyer_email_alerte_projet(alerte)
```

**Informations dans l'alerte**:
- Nom du projet
- Budget prévu
- Budget consommé
- Montant du dépassement
- Pourcentage de dépassement
- Message personnalisé selon le rôle (admin ou responsable)

---

## 📁 Fichiers Créés/Modifiés

### Fichiers Modifiés

1. **core/views.py**
   - Fonction `modifier_budget_projet()` - Ajout des notifications pour les admins
   - Correction: Utilisation de `NotificationProjet` avec CharField au lieu de TypeNotification
   - Correction: Utilisation de `envoyer_email_notification_projet()` au lieu de `envoyer_notification_email()`

2. **core/management/commands/check_budget.py**
   - Fonction `_calculer_budget_consomme()` - Implémentation du calcul réel avec ResumeBudget
   - Fonction `_creer_alerte_budget_depasse()` - Ajout de l'envoi d'emails
   - Ajout de logs pour le suivi des emails envoyés

### Fichiers Créés

1. **test_notifications_budget.py**
   - Script de test complet pour les deux types de notifications
   - Test 1: Notification définition budget
   - Test 2: Notification budget dépassé
   - Simulation complète avec création/suppression de données de test

2. **SESSION_2026_02_16_NOTIFICATIONS_BUDGET_COMPLETE.md** (ce fichier)
   - Documentation complète de l'implémentation

---

## 🧪 Tests

### Script de Test

Un script de test complet a été créé: `test_notifications_budget.py`

**Exécution**:
```bash
python test_notifications_budget.py
```

**Tests inclus**:

1. **Test Notification Définition Budget**
   - Récupère un projet EN_COURS
   - Modifie le budget
   - Crée les notifications pour tous les admins
   - Envoie les emails
   - Vérifie le nombre de notifications créées

2. **Test Notification Budget Dépassé**
   - Récupère un projet avec budget défini
   - Calcule le budget actuel
   - Ajoute une dépense qui dépasse le budget
   - Crée les alertes pour admin + responsable
   - Envoie les emails
   - Nettoie les données de test

### Test Manuel

#### Test 1: Définition du Budget

1. Se connecter en tant qu'administrateur
2. Aller dans un projet
3. Cliquer sur "Paramètres"
4. Définir un budget total (ex: 50000€)
5. Valider

**Résultat attendu**:
- Message de succès: "Budget total défini à 50 000€"
- Notification dans l'application pour tous les admins
- Email envoyé à tous les admins

#### Test 2: Dépassement du Budget

1. Définir un budget total (ex: 10000€)
2. Ajouter des dépenses qui dépassent le budget:
   - Matériel: 6000€
   - Service: 5000€
   - Total: 11000€ (dépasse de 1000€)
3. Exécuter la commande de vérification:
   ```bash
   python manage.py check_budget
   ```

**Résultat attendu**:
- Alerte créée pour l'admin (créateur)
- Alerte créée pour le responsable
- Emails envoyés aux deux destinataires
- Message dans les logs: "🔴 Alertes BUDGET_DEPASSE : 2"

---

## 🔧 Configuration

### Commande Automatique

La commande `check_budget` doit être exécutée quotidiennement pour vérifier les dépassements de budget.

**Exécution manuelle**:
```bash
python manage.py check_budget
```

**Automatisation Windows (Task Scheduler)**:

Créer un fichier `run_check_budget.bat`:
```batch
@echo off
cd /d "C:\chemin\vers\projet"
python manage.py check_budget >> logs\budget_checks.log 2>&1
```

Planifier l'exécution quotidienne à 9h00 via le Planificateur de tâches Windows.

**Automatisation Linux (cron)**:
```bash
# Ajouter dans crontab -e
0 9 * * * cd /chemin/vers/projet && python manage.py check_budget >> logs/budget_checks.log 2>&1
```

---

## 📧 Templates Email

Les notifications utilisent les templates HTML professionnels existants:

1. **Notification Projet** (définition budget):
   - Template: `templates/emails/notification_projet.html`
   - Hérite de: `templates/emails/base_email.html`
   - Style: Gradient violet/bleu, logo, bouton d'action

2. **Alerte Projet** (budget dépassé):
   - Template: `templates/emails/notification_alerte_projet.html`
   - Hérite de: `templates/emails/base_email.html`
   - Style: Alerte rouge, icône d'avertissement

---

## 🎯 Logique Métier

### Définition du Budget

**Qui peut définir le budget?**
- Super Admin (is_superuser=True)
- Responsable principal du projet (est_responsable_principal=True)

**Quand?**
- À tout moment après la création du projet
- Peut être modifié plusieurs fois

**Notifications**:
- Tous les administrateurs sont notifiés
- Email + notification dans l'application

### Dépassement du Budget

**Comment est calculé le budget consommé?**
```python
Budget Consommé = Somme(Matériel) + Somme(Services)
```

**Quand une alerte est-elle créée?**
- Lorsque Budget Consommé > Budget Total
- Une seule alerte par jour par destinataire (évite les doublons)

**Qui est notifié?**
- Administrateur (créateur du projet)
- Responsable principal du projet

**Informations dans l'alerte**:
- Budget prévu
- Budget consommé
- Montant du dépassement
- Pourcentage de dépassement
- Message personnalisé selon le rôle

---

## 📊 Modèles de Données

### NotificationProjet

```python
NotificationProjet.objects.create(
    destinataire=admin,                    # Utilisateur destinataire
    projet=projet,                         # Projet concerné
    type_notification='CHANGEMENT_ECHEANCE',  # Type (réutilisé)
    titre='Budget défini - Projet X',     # Titre court
    message='Admin a défini le budget...',  # Message détaillé
    emetteur=user,                         # Qui a fait l'action
    donnees_contexte={                     # Données supplémentaires
        'ancien_budget': 0,
        'nouveau_budget': 50000,
        'type_action': 'DEFINITION_BUDGET'
    }
)
```

### AlerteProjet

```python
AlerteProjet.objects.create(
    destinataire=responsable,              # Utilisateur destinataire
    projet=projet,                         # Projet concerné
    type_alerte='BUDGET_DEPASSE',         # Type d'alerte
    niveau='DANGER',                       # Niveau de criticité
    titre='🔴 Budget dépassé - Projet X', # Titre avec emoji
    message='Le budget a été dépassé...', # Message détaillé
    lue=False,                            # Non lue par défaut
    donnees_contexte={                     # Données contextuelles
        'budget_previsionnel': 10000,
        'budget_consomme': 11000,
        'depassement': 1000,
        'pourcentage_depassement': 10.0,
        'devise': 'EUR'
    }
)
```

---

## 🔍 Vérification

### Vérifier les Notifications dans l'Application

1. Se connecter en tant qu'admin
2. Cliquer sur l'icône de notification (cloche)
3. Vérifier la présence de la notification "Budget défini"

### Vérifier les Alertes dans l'Application

1. Se connecter en tant qu'admin ou responsable
2. Aller dans "Alertes" (menu latéral)
3. Vérifier la présence de l'alerte "Budget dépassé"

### Vérifier les Emails

1. Consulter la boîte email de l'admin
2. Chercher les emails avec sujet:
   - "[SI-Gouvernance] Projet: Budget défini - Projet X"
   - "[SI-Gouvernance] ⚠️ Alerte: 🔴 Budget dépassé - Projet X"

### Vérifier les Logs

```bash
# Logs de la commande check_budget
type logs\budget_checks.log

# Logs Django
type logs\django.log
```

---

## 🐛 Corrections Apportées

### Problème 1: TypeNotification n'existe pas

**Erreur initiale**:
```python
type_notif = TypeNotification.objects.filter(code='MODIFICATION_BUDGET').first()
```

**Correction**:
Le modèle `NotificationProjet` utilise un CharField avec choices, pas une ForeignKey vers TypeNotification.

```python
notification = NotificationProjet.objects.create(
    type_notification='CHANGEMENT_ECHEANCE',  # CharField avec choices
    ...
)
```

### Problème 2: Mauvais nom de fonction

**Erreur initiale**:
```python
envoyer_notification_email(notification)
```

**Correction**:
```python
envoyer_email_notification_projet(notification)
```

### Problème 3: Mauvais nom de champ

**Erreur initiale**:
```python
NotificationProjet.objects.create(
    utilisateur=admin,  # Mauvais nom de champ
    ...
)
```

**Correction**:
```python
NotificationProjet.objects.create(
    destinataire=admin,  # Bon nom de champ
    ...
)
```

---

## 📈 Statistiques

### Notifications Créées

- **Définition budget**: 1 notification par admin
- **Budget dépassé**: 1 alerte par destinataire (admin + responsable)

### Emails Envoyés

- **Définition budget**: 1 email par admin
- **Budget dépassé**: 1 email par destinataire (admin + responsable)

### Fréquence

- **Définition budget**: À chaque modification du budget
- **Budget dépassé**: 1 fois par jour maximum (évite les doublons)

---

## ✅ Statut Final

**IMPLÉMENTATION COMPLÈTE ET FONCTIONNELLE**

✅ Notification définition budget (app + email)
✅ Notification budget dépassé (app + email)
✅ Calcul du budget consommé avec ResumeBudget
✅ Envoi d'emails HTML professionnels
✅ Prévention des doublons
✅ Script de test complet
✅ Documentation complète

---

## 📝 Notes Importantes

1. **Type de notification réutilisé**: Pour la définition du budget, on réutilise le type `CHANGEMENT_ECHEANCE` car il n'y a pas de type spécifique pour le budget dans les choices existantes. Le champ `donnees_contexte` contient `type_action: 'DEFINITION_BUDGET'` pour différencier.

2. **Prévention des doublons**: La fonction `_alerte_budget_depasse_existe_aujourd_hui()` vérifie qu'une alerte similaire n'a pas déjà été créée aujourd'hui pour éviter de spammer les utilisateurs.

3. **Calcul du budget**: Le budget consommé est calculé en temps réel à partir des lignes budgétaires (LigneBudget) via la classe ResumeBudget.

4. **Emails HTML**: Les emails utilisent les templates HTML professionnels créés précédemment avec le design gradient violet/bleu et le logo JCM.

---

## 🚀 Prochaines Étapes Possibles

1. **Ajouter un type de notification spécifique** pour le budget dans les choices de NotificationProjet
2. **Créer un template email dédié** pour les notifications de budget
3. **Ajouter des alertes préventives** (ex: alerte à 90% du budget)
4. **Dashboard budgétaire** avec graphiques et statistiques
5. **Export des rapports budgétaires** en PDF

---

**Date**: 2026-02-16
**Auteur**: Kiro AI Assistant
**Statut**: ✅ Complet et Testé
