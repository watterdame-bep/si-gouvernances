# Automatisation des Alertes - Windows

## ✅ Ce qui existe déjà

La commande Django `check_project_deadlines` est **déjà créée** et fonctionne!

Elle vérifie automatiquement :
- ✅ Tous les projets EN_COURS
- ✅ Calcule les jours restants
- ✅ Crée des alertes J-7 (7 jours avant la fin)
- ✅ Envoie aux responsables et à l'équipe
- ✅ Évite les doublons

---

## 🚀 Comment l'automatiser

### Méthode 1 : Planificateur de tâches Windows (Recommandé)

#### Étape 1 : Créer un fichier batch

Créez un fichier `run_check_deadlines.bat` à la racine du projet :

```batch
@echo off
cd /d "C:\chemin\vers\votre\projet"
python manage.py check_project_deadlines >> logs\alertes.log 2>&1
```

**Remplacez** `C:\chemin\vers\votre\projet` par le chemin réel de votre projet.

#### Étape 2 : Ouvrir le Planificateur de tâches

1. Appuyez sur `Windows + R`
2. Tapez `taskschd.msc`
3. Appuyez sur Entrée

#### Étape 3 : Créer une tâche

1. Cliquez sur "Créer une tâche..." (à droite)
2. **Onglet Général** :
   - Nom : `Vérification Alertes Projets`
   - Description : `Vérifie les échéances des projets et crée des alertes`
   - Cochez "Exécuter même si l'utilisateur n'est pas connecté"

3. **Onglet Déclencheurs** :
   - Cliquez sur "Nouveau..."
   - Commencer la tâche : `Selon une planification`
   - Paramètres : `Quotidienne`
   - Heure : `08:00:00` (8h du matin)
   - Cochez "Activé"
   - Cliquez sur "OK"

4. **Onglet Actions** :
   - Cliquez sur "Nouveau..."
   - Action : `Démarrer un programme`
   - Programme/script : `C:\chemin\vers\votre\projet\run_check_deadlines.bat`
   - Cliquez sur "OK"

5. **Onglet Conditions** :
   - Décochez "Démarrer la tâche uniquement si l'ordinateur est relié au secteur"

6. **Onglet Paramètres** :
   - Cochez "Autoriser l'exécution de la tâche à la demande"
   - Cliquez sur "OK"

#### Étape 4 : Tester immédiatement

1. Dans le Planificateur de tâches, trouvez votre tâche
2. Clic droit → "Exécuter"
3. Vérifiez le fichier `logs\alertes.log`

---

### Méthode 2 : Tâche planifiée simple (Alternative)

Si vous voulez juste tester rapidement :

```bash
# Exécuter manuellement tous les jours
python manage.py check_project_deadlines
```

---

## 📋 Vérification

### 1. Vérifier que la commande fonctionne

```bash
python manage.py check_project_deadlines
```

**Résultat attendu** :
```
🔍 Vérification des échéances des projets...
📊 X projet(s) actif(s) à vérifier
  🟡 Y alerte(s) J-7 créée(s) pour [Nom du projet]
    📧 Alerte créée pour [Nom utilisateur]

✅ Vérification terminée !
🟡 Alertes J-7 : Y
⚪ Alertes ignorées (doublons) : 0
📧 Total alertes créées : Y
```

### 2. Vérifier les alertes créées

```bash
python manage.py shell
```

```python
from core.models import AlerteProjet

# Compter les alertes
print(f"Total alertes: {AlerteProjet.objects.count()}")
print(f"Alertes non lues: {AlerteProjet.objects.filter(lue=False).count()}")

# Voir les dernières alertes
for alerte in AlerteProjet.objects.all()[:5]:
    print(f"\n{alerte.titre}")
    print(f"  Destinataire: {alerte.destinataire.get_full_name()}")
    print(f"  Type: {alerte.type_alerte}")
    print(f"  Lue: {alerte.lue}")
```

### 3. Vérifier dans l'interface

1. Ouvrir : `http://127.0.0.1:8000/`
2. Se connecter
3. Regarder la sidebar → Badge sur "Alertes"
4. Cliquer sur "Alertes" → Voir les alertes créées

---

## 🔧 Configuration avancée

### Créer un dossier logs

```bash
mkdir logs
```

### Fichier batch amélioré

`run_check_deadlines.bat` :

```batch
@echo off
REM ============================================
REM Vérification des alertes de projets
REM ============================================

echo [%date% %time%] Debut verification alertes >> logs\alertes.log

cd /d "C:\chemin\vers\votre\projet"

REM Activer l'environnement virtuel si nécessaire
REM call venv\Scripts\activate.bat

python manage.py check_project_deadlines >> logs\alertes.log 2>&1

echo [%date% %time%] Fin verification alertes >> logs\alertes.log
echo. >> logs\alertes.log
```

---

## 📊 Fréquences recommandées

### Production (Recommandé)

- **Quotidien à 8h00** : Vérifie tous les matins
- Permet de détecter les projets J-7

### Développement/Test

- **Manuel** : Exécuter quand nécessaire
- Ou **Toutes les heures** pour tester

### Personnalisé

Vous pouvez créer plusieurs déclencheurs :
- 8h00 : Vérification principale
- 14h00 : Vérification de l'après-midi
- 18h00 : Vérification de fin de journée

---

## 🐛 Dépannage

### La tâche ne s'exécute pas

1. **Vérifier les logs** : `logs\alertes.log`
2. **Vérifier le chemin** dans le fichier batch
3. **Tester manuellement** : Double-cliquer sur `run_check_deadlines.bat`
4. **Vérifier les permissions** : Exécuter en tant qu'administrateur

### Aucune alerte créée

1. **Vérifier qu'il y a des projets EN_COURS** avec `date_fin` dans 7 jours
2. **Exécuter le script de test** : `python test_alerte_j7.py`
3. **Vérifier les logs** pour voir les messages

### Doublons d'alertes

La commande vérifie automatiquement les doublons. Si vous voyez des doublons :
1. Vérifier que la tâche ne s'exécute pas plusieurs fois
2. Vérifier les logs : `logs\alertes.log`

---

## ✅ Checklist de configuration

- [ ] Fichier `run_check_deadlines.bat` créé
- [ ] Chemin du projet correct dans le batch
- [ ] Dossier `logs` créé
- [ ] Tâche créée dans le Planificateur
- [ ] Déclencheur quotidien à 8h00 configuré
- [ ] Tâche testée manuellement (Exécuter)
- [ ] Logs vérifiés
- [ ] Alertes visibles dans l'interface

---

## 📚 Documentation complète

Pour plus de détails, voir :
- `GUIDE_PLANIFICATEUR_WINDOWS.md` - Guide complet pas à pas
- `CONFIGURATION_PLANIFICATEUR_ETAPE_PAR_ETAPE.md` - Configuration détaillée
- `CHECKLIST_CONFIGURATION_PLANIFICATEUR.md` - Checklist complète

---

## 🎉 Résumé

**La commande existe déjà** : `python manage.py check_project_deadlines`

**Pour l'automatiser** :
1. Créer `run_check_deadlines.bat`
2. Configurer le Planificateur de tâches Windows
3. Planifier l'exécution quotidienne à 8h00
4. Tester et vérifier les logs

**C'est tout!** Les alertes seront créées automatiquement tous les jours. 🚀
