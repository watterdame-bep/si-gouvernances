# ✅ Checklist de Configuration du Planificateur

## 📋 Avant de commencer

- [ ] Le fichier `run_check_deadlines.bat` existe
- [ ] Le dossier `logs` existe
- [ ] La commande `python manage.py check_task_deadlines` fonctionne manuellement
- [ ] Vous avez les droits administrateur sur Windows

## 🚀 Configuration (5 minutes)

### Étape 1 : Ouvrir le Planificateur
- [ ] Appuyer sur `Windows`
- [ ] Taper `Planificateur de tâches`
- [ ] Ouvrir l'application

### Étape 2 : Créer la tâche
- [ ] Cliquer sur "Créer une tâche" (panneau de droite)
- [ ] ⚠️ Ne PAS cliquer sur "Créer une tâche de base"

### Étape 3 : Onglet "Général"
- [ ] Nom : `Alertes SI-Gouvernance`
- [ ] Description : `Vérification quotidienne des échéances de tâches`
- [ ] ☑️ Cocher "Exécuter même si l'utilisateur n'est pas connecté"
- [ ] ☑️ Cocher "Exécuter avec les autorisations maximales"
- [ ] Configurer pour : `Windows 10`

### Étape 4 : Onglet "Déclencheurs"
- [ ] Cliquer sur "Nouveau"
- [ ] Commencer la tâche : `Selon une planification`
- [ ] Paramètres : `Quotidien`
- [ ] Heure : `08:00:00`
- [ ] Répéter tous les : `1 jours`
- [ ] ☑️ Cocher "Activé"
- [ ] Cliquer sur "OK"

### Étape 5 : Onglet "Actions"
- [ ] Cliquer sur "Nouveau"
- [ ] Action : `Démarrer un programme`
- [ ] Programme/script : Parcourir et sélectionner :
  ```
  E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_deadlines.bat
  ```
- [ ] Cliquer sur "OK"

### Étape 6 : Onglet "Conditions"
- [ ] ☐ Décocher "Démarrer la tâche uniquement si l'ordinateur est branché"
- [ ] ☑️ Cocher "Réveiller l'ordinateur pour exécuter cette tâche"

### Étape 7 : Onglet "Paramètres"
- [ ] ☑️ Cocher "Autoriser l'exécution de la tâche à la demande"
- [ ] ☑️ Cocher "Exécuter la tâche dès que possible si un démarrage planifié est manqué"
- [ ] ☑️ Cocher "Si la tâche échoue, recommencer toutes les" : `10 minutes`
- [ ] Nombre de tentatives : `3`
- [ ] ☐ Décocher "Arrêter la tâche si elle s'exécute plus de"

### Étape 8 : Enregistrer
- [ ] Cliquer sur "OK"
- [ ] Entrer le mot de passe Windows si demandé
- [ ] La tâche apparaît dans la liste

## ✅ Test Immédiat

- [ ] Trouver la tâche "Alertes SI-Gouvernance" dans la liste
- [ ] Clic droit → "Exécuter"
- [ ] Attendre quelques secondes
- [ ] Vérifier l'historique : Clic droit → Propriétés → Onglet "Historique"
- [ ] Code de sortie doit être : `0` (succès)

## 🔍 Vérification des Résultats

### Vérifier le fichier de log
```bash
type logs\planificateur.log
```

Vous devriez voir :
```
========================================================================
[09/02/2026 14:57:03] Demarrage verification echeances
========================================================================
🔍 Vérification des échéances des tâches...
📊 8 tâches actives à vérifier
...
✅ Vérification terminée !
📧 Total alertes créées : 8
[09/02/2026 14:57:03] Verification terminee avec succes
```

### Vérifier les alertes créées
```bash
python verification_systeme_alertes.py
```

Vous devriez voir :
```
✅ Points positifs :
  - 8 tâche(s) active(s) à surveiller
  - X alerte(s) dans le système
  - Toutes les alertes respectent les permissions
  - Fichier batch prêt pour le planificateur
```

### Vérifier dans l'interface web

- [ ] Se connecter à l'application
- [ ] Cliquer sur l'icône de notifications (cloche)
- [ ] Vérifier que les alertes apparaissent pour les utilisateurs concernés

## 📊 Monitoring (Semaine de test)

### Chaque jour pendant 7 jours

**Jour 1** (Aujourd'hui)
- [ ] Configuration terminée
- [ ] Test manuel réussi
- [ ] Alertes visibles dans l'interface

**Jour 2**
- [ ] Vérifier que la tâche s'est exécutée à 8h00
- [ ] Vérifier le fichier de log
- [ ] Vérifier les nouvelles alertes

**Jour 3**
- [ ] Vérifier l'exécution automatique
- [ ] Vérifier le log
- [ ] Noter les éventuels problèmes

**Jour 4**
- [ ] Vérifier l'exécution automatique
- [ ] Vérifier le log

**Jour 5**
- [ ] Vérifier l'exécution automatique
- [ ] Vérifier le log

**Jour 6**
- [ ] Vérifier l'exécution automatique
- [ ] Vérifier le log

**Jour 7**
- [ ] Vérifier l'exécution automatique
- [ ] Vérifier le log
- [ ] Faire un bilan de la semaine

## 📈 Bilan de la Semaine

Après 7 jours de test :

- [ ] La tâche s'est exécutée tous les jours à 8h00
- [ ] Aucune erreur dans les logs
- [ ] Les alertes sont créées correctement
- [ ] Les utilisateurs reçoivent leurs notifications
- [ ] Aucune alerte incorrecte (permissions respectées)

### Si tout fonctionne bien

- [ ] Supprimer les tâches de test créées pour les tests
- [ ] Nettoyer les anciennes alertes de test
- [ ] Documenter la configuration
- [ ] Planifier la migration vers Celery (optionnel)

### Si des problèmes sont détectés

- [ ] Noter les problèmes dans un fichier
- [ ] Vérifier les logs pour identifier la cause
- [ ] Corriger les problèmes
- [ ] Relancer les tests

## 🔧 Commandes Utiles

### Voir les logs
```bash
# Voir les 50 dernières lignes
type logs\planificateur.log | more

# Voir tout le fichier
notepad logs\planificateur.log
```

### Tester manuellement
```bash
# Exécuter le script batch
run_check_deadlines.bat

# Exécuter la commande Django directement
python manage.py check_task_deadlines
```

### Vérifier le système
```bash
# Vérification complète
python verification_systeme_alertes.py

# Vérifier un utilisateur spécifique
python test_don_dieu_alertes.py
```

### Nettoyer les alertes de test
```bash
python nettoyer_alertes_incorrectes.py
```

## 📞 Support

### En cas de problème

1. **Vérifier les logs** : `logs\planificateur.log`
2. **Vérifier l'historique** : Planificateur → Clic droit sur tâche → Historique
3. **Tester manuellement** : `run_check_deadlines.bat`
4. **Consulter la documentation** : `GUIDE_PLANIFICATEUR_WINDOWS.md`

### Codes de sortie

- `0` : Succès ✅
- `1` : Erreur générale ❌
- Autre : Erreur spécifique ❌

## 🎯 Objectifs de la Phase de Test

- ✅ Valider que le système fonctionne automatiquement
- ✅ Vérifier la fiabilité sur 7 jours
- ✅ S'assurer que les permissions sont respectées
- ✅ Confirmer que les utilisateurs reçoivent leurs alertes
- ✅ Identifier les éventuels problèmes avant la production

## 🚀 Après la Phase de Test

Une fois la phase de test validée (7 jours sans problème) :

1. **Court terme** :
   - Supprimer les tâches de test
   - Nettoyer les alertes de test
   - Documenter la configuration finale

2. **Moyen terme** :
   - Ajouter des alertes supplémentaires (tâches bloquées, synthèse)
   - Créer un tableau de bord des échéances
   - Permettre aux utilisateurs de configurer leurs préférences

3. **Long terme** :
   - Migrer vers Celery pour la production (voir MIGRATION_CELERY_READY.md)
   - Ajouter l'envoi d'emails
   - Implémenter des rapports hebdomadaires

---

**Date** : 09/02/2026  
**Phase** : Configuration et test  
**Durée** : 7 jours de test  
**Prochaine étape** : Bilan après 7 jours
