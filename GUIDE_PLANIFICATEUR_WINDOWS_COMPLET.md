# Guide Complet - Planificateur de Tâches Windows

## ✅ OUI, ÇA VA FONCTIONNER!

Le Planificateur de tâches Windows est **parfaitement adapté** pour exécuter les commandes d'alertes automatiques.

---

## 📋 PRÉREQUIS

Avant de configurer le planificateur, vérifiez que:

1. ✅ Python est installé et accessible depuis la ligne de commande
2. ✅ Le projet Django fonctionne correctement
3. ✅ Les commandes management fonctionnent manuellement
4. ✅ La configuration SMTP est opérationnelle

### Test rapide des commandes

Ouvrez un terminal dans le dossier du projet et testez:

```bash
# Test 1: Échéances de projets
python manage.py check_project_deadlines

# Test 2: Retards d'étapes
python manage.py check_stage_delays

# Test 3: Tâches en retard
python manage.py check_task_deadlines

# Test 4: Budget
python manage.py check_budget

# Test 5: Contrats
python manage.py check_contract_expiration
```

Si toutes ces commandes fonctionnent sans erreur, vous êtes prêt! ✅

---

## 🚀 CONFIGURATION DU PLANIFICATEUR

### Étape 1: Ouvrir le Planificateur de tâches

1. Appuyez sur `Windows + R`
2. Tapez `taskschd.msc`
3. Appuyez sur `Entrée`

### Étape 2: Créer une nouvelle tâche

1. Dans le panneau de droite, cliquez sur **"Créer une tâche..."**
2. Ne pas utiliser "Créer une tâche de base" (moins d'options)

---

## 📝 CONFIGURATION DÉTAILLÉE

### TÂCHE 1: Vérification des échéances de projets

#### Onglet "Général"
- **Nom**: `SI-Gouvernance - Alertes Projets`
- **Description**: `Vérifie les échéances des projets et envoie des alertes (J-7, J-3, J-1, retards)`
- **Compte d'utilisateur**: Votre compte Windows
- ✅ Cocher: **"Exécuter même si l'utilisateur n'est pas connecté"**
- ✅ Cocher: **"Exécuter avec les autorisations maximales"**

#### Onglet "Déclencheurs"
1. Cliquez sur **"Nouveau..."**
2. **Lancer la tâche**: `Selon une planification`
3. **Paramètres**: `Quotidien`
4. **Démarrer le**: Date d'aujourd'hui
5. **Heure**: `09:00:00` (9h du matin)
6. **Répéter la tâche toutes les**: (laisser vide pour une seule exécution par jour)
7. ✅ Cocher: **"Activé"**
8. Cliquez sur **"OK"**

#### Onglet "Actions"
1. Cliquez sur **"Nouveau..."**
2. **Action**: `Démarrer un programme`
3. **Programme/script**: `E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_deadlines.bat`
   - ⚠️ Remplacez par le chemin complet vers votre fichier `.bat`
4. **Commencer dans (facultatif)**: `E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE`
   - ⚠️ Remplacez par le chemin de votre projet
5. Cliquez sur **"OK"**

#### Onglet "Conditions"
- ✅ Décocher: **"Démarrer la tâche uniquement si l'ordinateur est relié au secteur"**
- ✅ Cocher: **"Réveiller l'ordinateur pour exécuter cette tâche"** (optionnel)

#### Onglet "Paramètres"
- ✅ Cocher: **"Autoriser l'exécution de la tâche à la demande"**
- ✅ Cocher: **"Exécuter la tâche dès que possible si un démarrage planifié est manqué"**
- **Si la tâche échoue, redémarrer toutes les**: `1 minute`
- **Tenter de redémarrer jusqu'à**: `3 fois`

---

### TÂCHE 2: Vérification des retards d'étapes

Répétez la même procédure avec:

- **Nom**: `SI-Gouvernance - Alertes Étapes`
- **Description**: `Vérifie les retards d'étapes et envoie des alertes`
- **Heure**: `09:15:00` (9h15 - 15 minutes après la première)
- **Programme/script**: `E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_stage_delays.bat`

---

### TÂCHE 3: Vérification des tâches en retard

- **Nom**: `SI-Gouvernance - Alertes Tâches`
- **Description**: `Vérifie les tâches en retard et envoie des alertes`
- **Heure**: `09:30:00` (9h30)
- **Programme/script**: `E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_all_alerts.bat`

---

### TÂCHE 4: Vérification des budgets

- **Nom**: `SI-Gouvernance - Alertes Budgets`
- **Description**: `Vérifie les dépassements de budget`
- **Heure**: `10:00:00` (10h)
- **Programme/script**: `E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_budget.bat`

---

### TÂCHE 5: Vérification des contrats

- **Nom**: `SI-Gouvernance - Alertes Contrats`
- **Description**: `Vérifie les expirations de contrats`
- **Heure**: `10:15:00` (10h15)
- **Script**: Créez `run_check_contracts.bat`:

```batch
@echo off
cd /d "%~dp0"
python manage.py check_contract_expiration
pause
```

---

## 🔧 FICHIERS BATCH NÉCESSAIRES

Vérifiez que vous avez ces fichiers dans votre projet:

### 1. run_check_deadlines.bat
```batch
@echo off
REM Vérification des échéances de projets
cd /d "%~dp0"
python manage.py check_project_deadlines
pause
```

### 2. run_check_stage_delays.bat
```batch
@echo off
REM Vérification des retards d'étapes
cd /d "%~dp0"
python manage.py check_stage_delays
pause
```

### 3. run_check_budget.bat
```batch
@echo off
REM Vérification des budgets
cd /d "%~dp0"
python manage.py check_budget
pause
```

### 4. run_check_all_alerts.bat
```batch
@echo off
REM Vérification de toutes les alertes
cd /d "%~dp0"
echo ========================================
echo Verification des alertes
echo ========================================
echo.

echo [1/3] Verification des echeances de projets...
python manage.py check_project_deadlines
echo.

echo [2/3] Verification des taches en retard...
python manage.py check_task_deadlines
echo.

echo [3/3] Verification des contrats...
python manage.py check_contract_expiration
echo.

echo ========================================
echo Verification terminee
echo ========================================
pause
```

---

## ✅ VÉRIFICATION DE LA CONFIGURATION

### Test manuel d'une tâche

1. Dans le Planificateur de tâches, trouvez votre tâche
2. Clic droit → **"Exécuter"**
3. Vérifiez que:
   - La tâche s'exécute sans erreur
   - Les alertes sont créées dans la base de données
   - Les emails sont envoyés

### Vérifier l'historique

1. Sélectionnez votre tâche
2. Onglet **"Historique"** en bas
3. Vérifiez les codes de résultat:
   - `0x0` = Succès ✅
   - `0x1` = Erreur ❌

### Vérifier les logs

Créez un fichier de log pour chaque tâche:

```batch
@echo off
cd /d "%~dp0"
echo [%date% %time%] Debut verification >> logs\planificateur.log
python manage.py check_project_deadlines >> logs\planificateur.log 2>&1
echo [%date% %time%] Fin verification >> logs\planificateur.log
```

---

## 🐛 DÉPANNAGE

### Problème 1: La tâche ne s'exécute pas

**Solutions:**
1. Vérifiez que le compte utilisateur a les droits nécessaires
2. Vérifiez le chemin complet vers le fichier `.bat`
3. Vérifiez que "Exécuter avec les autorisations maximales" est coché
4. Testez le fichier `.bat` manuellement en double-cliquant dessus

### Problème 2: Erreur "Python n'est pas reconnu"

**Solutions:**
1. Utilisez le chemin complet vers Python:
   ```batch
   C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe manage.py check_project_deadlines
   ```
2. Ou ajoutez Python au PATH système

### Problème 3: Erreur "manage.py introuvable"

**Solutions:**
1. Vérifiez que le "Commencer dans" est bien défini
2. Utilisez `cd /d "%~dp0"` dans le fichier `.bat`

### Problème 4: Les emails ne sont pas envoyés

**Solutions:**
1. Vérifiez la configuration SMTP dans `.env`
2. Testez l'envoi d'email manuellement:
   ```bash
   python test_email_smtp.py
   ```
3. Vérifiez les logs d'erreurs

### Problème 5: La tâche s'exécute mais rien ne se passe

**Solutions:**
1. Vérifiez qu'il y a des projets/étapes/tâches en retard
2. Vérifiez les logs de la commande
3. Exécutez la commande manuellement pour voir les erreurs

---

## 📊 MONITORING

### Créer un tableau de bord

Créez un script pour vérifier l'état des tâches:

```python
# verifier_taches_planifiees.py
import subprocess
import datetime

print("=" * 80)
print("ÉTAT DES TÂCHES PLANIFIÉES")
print("=" * 80)
print()

taches = [
    "SI-Gouvernance - Alertes Projets",
    "SI-Gouvernance - Alertes Étapes",
    "SI-Gouvernance - Alertes Tâches",
    "SI-Gouvernance - Alertes Budgets",
    "SI-Gouvernance - Alertes Contrats"
]

for tache in taches:
    try:
        result = subprocess.run(
            ['schtasks', '/Query', '/TN', tache, '/FO', 'LIST'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {tache}")
            # Extraire la dernière exécution et le prochain démarrage
            for line in result.stdout.split('\n'):
                if 'Dernière exécution' in line or 'Last Run Time' in line:
                    print(f"   {line.strip()}")
                if 'Prochaine exécution' in line or 'Next Run Time' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"❌ {tache} - Non trouvée")
    except Exception as e:
        print(f"❌ {tache} - Erreur: {e}")
    
    print()

print("=" * 80)
```

---

## 🎯 RECOMMANDATIONS

### Horaires recommandés

| Tâche | Heure | Fréquence | Priorité |
|-------|-------|-----------|----------|
| Alertes Projets | 09:00 | Quotidien | Haute |
| Alertes Étapes | 09:15 | Quotidien | Haute |
| Alertes Tâches | 09:30 | Quotidien | Moyenne |
| Alertes Budgets | 10:00 | Quotidien | Moyenne |
| Alertes Contrats | 10:15 | Quotidien | Basse |

### Bonnes pratiques

1. ✅ Espacez les tâches de 15 minutes pour éviter la surcharge
2. ✅ Exécutez les tâches le matin (9h-10h) pour que les utilisateurs voient les alertes
3. ✅ Créez des logs pour chaque exécution
4. ✅ Testez manuellement avant d'activer
5. ✅ Surveillez les premières exécutions
6. ✅ Configurez des notifications en cas d'échec

---

## ✅ CHECKLIST FINALE

Avant de mettre en production:

- [ ] Toutes les commandes fonctionnent manuellement
- [ ] Les fichiers `.bat` sont créés et testés
- [ ] Les tâches sont créées dans le Planificateur
- [ ] Les horaires sont configurés correctement
- [ ] Les chemins sont corrects (absolus)
- [ ] "Exécuter avec les autorisations maximales" est coché
- [ ] Les conditions sont désactivées (secteur, etc.)
- [ ] Test manuel de chaque tâche réussi
- [ ] Les emails sont bien envoyés
- [ ] Les logs sont créés et accessibles
- [ ] L'historique des tâches est activé

---

## 🎉 CONCLUSION

**OUI, le Planificateur de tâches Windows va fonctionner parfaitement!**

Une fois configuré:
- ✅ Les alertes seront envoyées automatiquement chaque jour
- ✅ Les emails seront envoyés aux utilisateurs concernés
- ✅ Aucune intervention manuelle nécessaire
- ✅ Système fiable et robuste

**Le système est prêt pour la production!** 🚀
