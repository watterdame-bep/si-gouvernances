# 📅 Guide : Planificateur de tâches Windows

## 🎯 Objectif

Configurer Windows pour exécuter automatiquement la vérification des échéances tous les jours à 8h00.

## 📋 Prérequis

- ✅ Windows 10 ou supérieur
- ✅ Droits administrateur
- ✅ Le fichier `run_check_deadlines.bat` existe dans le projet
- ✅ Le serveur Django peut être démarré (base de données accessible)

## 🚀 Configuration en 5 minutes

### Étape 1 : Ouvrir le Planificateur de tâches

**Méthode 1** : Via la recherche Windows
1. Appuyer sur `Windows`
2. Taper `Planificateur de tâches`
3. Cliquer sur l'application

**Méthode 2** : Via Exécuter
1. Appuyer sur `Windows + R`
2. Taper `taskschd.msc`
3. Appuyer sur `Entrée`

### Étape 2 : Créer une nouvelle tâche

1. Dans le panneau de droite, cliquer sur **"Créer une tâche"**
   - ⚠️ Ne pas cliquer sur "Créer une tâche de base" (moins d'options)

### Étape 3 : Onglet "Général"

Remplir les informations suivantes :

- **Nom** : `Alertes SI-Gouvernance`
- **Description** : `Vérification quotidienne des échéances de tâches`
- **Options de sécurité** :
  - ☑️ Cocher "Exécuter même si l'utilisateur n'est pas connecté"
  - ☑️ Cocher "Exécuter avec les autorisations maximales"
- **Configurer pour** : `Windows 10`

### Étape 4 : Onglet "Déclencheurs"

1. Cliquer sur **"Nouveau"**
2. Configurer :
   - **Commencer la tâche** : `Selon une planification`
   - **Paramètres** : Sélectionner `Quotidien`
   - **Démarrer le** : Date d'aujourd'hui
   - **Heure** : `08:00:00`
   - **Répéter tous les** : `1 jours`
   - ☑️ Cocher "Activé"
3. Cliquer sur **OK**

### Étape 5 : Onglet "Actions"

1. Cliquer sur **"Nouveau"**
2. Configurer :
   - **Action** : `Démarrer un programme`
   - **Programme/script** : Cliquer sur "Parcourir" et sélectionner :
     ```
     E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_deadlines.bat
     ```
   - **Commencer dans (facultatif)** : Laisser vide
3. Cliquer sur **OK**

### Étape 6 : Onglet "Conditions"

Configurer les conditions d'exécution :

- **Alimentation** :
  - ☐ Décocher "Démarrer la tâche uniquement si l'ordinateur est branché"
  - ☑️ Cocher "Réveiller l'ordinateur pour exécuter cette tâche"

- **Réseau** :
  - ☐ Laisser décoché (pas nécessaire)

### Étape 7 : Onglet "Paramètres"

Configurer les paramètres avancés :

- ☑️ Cocher "Autoriser l'exécution de la tâche à la demande"
- ☑️ Cocher "Exécuter la tâche dès que possible si un démarrage planifié est manqué"
- ☑️ Cocher "Si la tâche échoue, recommencer toutes les" : `10 minutes`
- **Nombre de tentatives** : `3`
- ☐ Décocher "Arrêter la tâche si elle s'exécute plus de" (pas de limite)

### Étape 8 : Enregistrer

1. Cliquer sur **OK**
2. Si demandé, entrer votre **mot de passe Windows**
3. La tâche apparaît maintenant dans la liste

## ✅ Vérification

### Test immédiat

Pour tester sans attendre 8h00 :

1. Dans le Planificateur de tâches, trouver la tâche `Alertes SI-Gouvernance`
2. Clic droit → **"Exécuter"**
3. Vérifier dans l'interface que les alertes sont créées

### Vérifier l'historique

1. Clic droit sur la tâche → **"Propriétés"**
2. Onglet **"Historique"**
3. Vérifier que la tâche s'est exécutée avec succès

### Vérifier les logs

Le fichier `run_check_deadlines.bat` crée un log :
```
E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\logs\check_deadlines.log
```

Ouvrir ce fichier pour voir les résultats de la dernière exécution.

## 🔧 Dépannage

### Problème : La tâche ne s'exécute pas

**Solution 1** : Vérifier les permissions
- Clic droit sur la tâche → Propriétés
- Onglet Général
- Vérifier que "Exécuter avec les autorisations maximales" est coché

**Solution 2** : Vérifier le chemin
- Onglet Actions
- Vérifier que le chemin vers `run_check_deadlines.bat` est correct
- Tester le fichier manuellement en double-cliquant dessus

**Solution 3** : Vérifier l'historique
- Onglet Historique
- Regarder les erreurs éventuelles
- Code de sortie 0 = succès

### Problème : La tâche s'exécute mais aucune alerte n'est créée

**Vérification 1** : Tester manuellement
```bash
cd E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
python manage.py check_task_deadlines
```

**Vérification 2** : Vérifier qu'il y a des tâches à vérifier
- Les tâches doivent avoir un statut : A_FAIRE, EN_COURS, ou BLOQUEE
- Les tâches doivent avoir une date de fin définie
- Les tâches doivent être proches de leur échéance

**Vérification 3** : Vérifier les permissions d'accès
- Les utilisateurs doivent avoir accès au projet
- Utiliser `test_don_dieu_alertes.py` pour vérifier

### Problème : Trop d'alertes créées

**Cause** : La commande est exécutée plusieurs fois par jour

**Solution** : Vérifier les déclencheurs
- Onglet Déclencheurs
- S'assurer qu'il n'y a qu'UN SEUL déclencheur
- Vérifier que la répétition est bien "1 jours"

## 📊 Monitoring

### Vérifier l'exécution quotidienne

Créer un script de monitoring :

```python
# monitoring_alertes.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationTache
from django.utils import timezone
from datetime import timedelta

# Alertes créées aujourd'hui
aujourd_hui = timezone.now().date()
alertes_aujourd_hui = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD'],
    date_creation__date=aujourd_hui
)

print(f"📊 Alertes créées aujourd'hui : {alertes_aujourd_hui.count()}")

# Alertes créées cette semaine
il_y_a_7_jours = aujourd_hui - timedelta(days=7)
alertes_semaine = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD'],
    date_creation__date__gte=il_y_a_7_jours
)

print(f"📊 Alertes créées cette semaine : {alertes_semaine.count()}")
```

### Dashboard admin (optionnel)

Ajouter une page dans l'interface admin pour voir :
- Dernière exécution de la commande
- Nombre d'alertes créées aujourd'hui
- Nombre d'alertes créées cette semaine
- Tâches en retard
- Tâches à échéance proche

## 🎯 Bonnes pratiques

### Fréquence d'exécution

- ✅ **Recommandé** : 1 fois par jour (8h00)
- ⚠️ **Déconseillé** : Plusieurs fois par jour (risque de doublons)
- ❌ **À éviter** : Toutes les heures (spam de notifications)

### Heure d'exécution

- ✅ **8h00** : Début de journée, les utilisateurs voient les alertes en arrivant
- ✅ **7h00** : Avant l'arrivée des utilisateurs
- ⚠️ **12h00** : Milieu de journée, moins visible
- ❌ **23h00** : Trop tard, les utilisateurs ne verront pas avant le lendemain

### Maintenance

- 📅 **Hebdomadaire** : Vérifier l'historique d'exécution
- 📅 **Mensuel** : Vérifier les logs et nettoyer les anciennes alertes
- 📅 **Trimestriel** : Analyser les statistiques d'alertes

## 📚 Ressources

### Fichiers du projet

- `run_check_deadlines.bat` : Script d'exécution
- `core/management/commands/check_task_deadlines.py` : Commande Django
- `test_alertes_echeances.py` : Script de test
- `SYSTEME_ALERTES_ECHEANCES.md` : Documentation complète

### Documentation Microsoft

- [Planificateur de tâches Windows](https://docs.microsoft.com/fr-fr/windows/win32/taskschd/task-scheduler-start-page)
- [Créer une tâche planifiée](https://support.microsoft.com/fr-fr/windows/planifier-une-t%C3%A2che-dans-le-planificateur-de-t%C3%A2ches-de-windows-10-3a6e7c5c-4e4e-4e4e-8e4e-4e4e4e4e4e4e)

## ✅ Checklist finale

Avant de considérer la configuration terminée :

- [ ] Le Planificateur de tâches est ouvert
- [ ] La tâche "Alertes SI-Gouvernance" est créée
- [ ] Le déclencheur est configuré pour 8h00 quotidien
- [ ] L'action pointe vers le bon fichier .bat
- [ ] La tâche a été testée manuellement (Exécuter)
- [ ] Des alertes ont été créées lors du test
- [ ] L'historique montre une exécution réussie (code 0)
- [ ] Le fichier de log existe et contient les résultats

## 🎉 Félicitations !

Votre système d'alertes est maintenant **100% automatisé** !

Les utilisateurs recevront automatiquement leurs alertes chaque matin à 8h00, sans aucune intervention de votre part.

---

**Date** : 09/02/2026  
**Statut** : Guide complet  
**Prochaine étape** : Configuration du Planificateur de tâches
