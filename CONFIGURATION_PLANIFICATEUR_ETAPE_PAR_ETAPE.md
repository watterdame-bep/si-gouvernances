# 📅 Configuration du Planificateur - Guide Pas à Pas

## 🎯 Objectif

Configurer Windows pour exécuter automatiquement `python manage.py check_task_deadlines` tous les jours à 8h00.

## ⚡ Configuration Rapide (5 minutes)

### Étape 1 : Ouvrir le Planificateur de tâches

**Méthode la plus simple** :
1. Appuyez sur la touche `Windows` de votre clavier
2. Tapez : `Planificateur de tâches`
3. Cliquez sur l'application qui apparaît

OU

1. Appuyez sur `Windows + R`
2. Tapez : `taskschd.msc`
3. Appuyez sur `Entrée`

### Étape 2 : Créer la tâche

1. Dans le panneau de **droite**, cliquez sur **"Créer une tâche"**
   - ⚠️ **Important** : Ne cliquez PAS sur "Créer une tâche de base"

### Étape 3 : Onglet "Général"

Remplissez les champs suivants :

```
Nom : Alertes SI-Gouvernance

Description : Vérification quotidienne des échéances de tâches

☑️ Cocher : "Exécuter même si l'utilisateur n'est pas connecté"
☑️ Cocher : "Exécuter avec les autorisations maximales"

Configurer pour : Windows 10
```

### Étape 4 : Onglet "Déclencheurs"

1. Cliquez sur **"Nouveau"**
2. Configurez :
   ```
   Commencer la tâche : Selon une planification
   Paramètres : Quotidien
   Démarrer le : [Date d'aujourd'hui]
   Heure : 08:00:00
   Répéter tous les : 1 jours
   ☑️ Activé
   ```
3. Cliquez sur **OK**

### Étape 5 : Onglet "Actions"

1. Cliquez sur **"Nouveau"**
2. Configurez :
   ```
   Action : Démarrer un programme
   
   Programme/script : Cliquez sur "Parcourir" et sélectionnez :
   E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_deadlines.bat
   
   Commencer dans : [Laisser vide]
   ```
3. Cliquez sur **OK**

### Étape 6 : Onglet "Conditions"

Configurez :
```
Alimentation :
☐ Décocher : "Démarrer la tâche uniquement si l'ordinateur est branché"
☑️ Cocher : "Réveiller l'ordinateur pour exécuter cette tâche"
```

### Étape 7 : Onglet "Paramètres"

Configurez :
```
☑️ Cocher : "Autoriser l'exécution de la tâche à la demande"
☑️ Cocher : "Exécuter la tâche dès que possible si un démarrage planifié est manqué"
☑️ Cocher : "Si la tâche échoue, recommencer toutes les" : 10 minutes
Nombre de tentatives : 3
☐ Décocher : "Arrêter la tâche si elle s'exécute plus de"
```

### Étape 8 : Enregistrer

1. Cliquez sur **OK**
2. Si demandé, entrez votre **mot de passe Windows**
3. La tâche apparaît maintenant dans la liste

## ✅ Test Immédiat

Pour tester sans attendre 8h00 demain :

1. Dans la liste des tâches, trouvez **"Alertes SI-Gouvernance"**
2. **Clic droit** sur la tâche
3. Cliquez sur **"Exécuter"**
4. Attendez quelques secondes
5. Vérifiez dans l'interface que des alertes ont été créées

## 🔍 Vérification

### Vérifier que la tâche s'est exécutée

1. **Clic droit** sur la tâche → **"Propriétés"**
2. Onglet **"Historique"**
3. Vous devriez voir une entrée avec :
   - **Code de sortie : 0** (succès)
   - **Dernière exécution** : Date et heure récentes

### Vérifier les alertes créées

```bash
cd E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
python verification_systeme_alertes.py
```

Vous devriez voir :
```
✅ Alertes créées aujourd'hui : [nombre]
✅ Utilisateurs avec alertes : [nombre]
```

## 🎉 C'est fait !

Votre système d'alertes est maintenant **100% automatisé** !

Chaque jour à 8h00, Windows va :
1. Exécuter `run_check_deadlines.bat`
2. Lancer `python manage.py check_task_deadlines`
3. Créer les alertes pour les utilisateurs concernés
4. Les utilisateurs verront leurs notifications dans l'interface

## 📊 Monitoring

### Voir l'historique d'exécution

1. Ouvrir le Planificateur de tâches
2. Trouver la tâche "Alertes SI-Gouvernance"
3. Onglet "Historique"
4. Voir toutes les exécutions passées

### Voir les logs

Le fichier `run_check_deadlines.bat` peut être modifié pour créer des logs :

```batch
@echo off
cd /d E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE
echo [%date% %time%] Démarrage vérification échéances >> logs\planificateur.log
python manage.py check_task_deadlines >> logs\planificateur.log 2>&1
echo [%date% %time%] Fin vérification échéances >> logs\planificateur.log
echo. >> logs\planificateur.log
```

Puis créer le dossier logs :
```bash
mkdir logs
```

## 🔧 Dépannage

### La tâche ne s'exécute pas

**Vérification 1** : Permissions
- Onglet Général → Vérifier que "Exécuter avec les autorisations maximales" est coché

**Vérification 2** : Chemin du fichier
- Onglet Actions → Vérifier que le chemin vers `run_check_deadlines.bat` est correct
- Tester en double-cliquant sur le fichier .bat

**Vérification 3** : Historique
- Onglet Historique → Regarder les erreurs
- Code de sortie 0 = succès
- Autre code = erreur

### La tâche s'exécute mais aucune alerte

**Vérification 1** : Tâches à vérifier
```bash
python manage.py shell
>>> from core.models import TacheEtape
>>> TacheEtape.objects.filter(statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']).exclude(date_fin__isnull=True).count()
```

Si 0, il n'y a pas de tâches à vérifier.

**Vérification 2** : Exécution manuelle
```bash
python manage.py check_task_deadlines
```

Regarder les messages affichés.

## 📅 Prochaines Étapes

### Cette semaine
- [ ] Tester l'exécution automatique pendant 7 jours
- [ ] Vérifier chaque jour que les alertes sont créées
- [ ] Noter les éventuels problèmes

### Semaine prochaine
- [ ] Analyser les statistiques d'alertes
- [ ] Supprimer les tâches de test si nécessaire
- [ ] Décider si migration vers Celery nécessaire

### Plus tard
- [ ] Migrer vers Celery pour la production (voir MIGRATION_CELERY_READY.md)
- [ ] Ajouter des alertes supplémentaires (tâches bloquées, synthèse quotidienne)
- [ ] Implémenter l'envoi d'emails

---

**Date** : 09/02/2026  
**Statut** : Prêt pour configuration  
**Durée estimée** : 5 minutes
