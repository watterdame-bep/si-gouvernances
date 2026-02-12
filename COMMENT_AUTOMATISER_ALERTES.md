# Comment Automatiser les Alertes ? 🤖

## ✅ La commande existe déjà!

```bash
python manage.py check_project_deadlines
```

Cette commande :
- ✅ Vérifie tous les projets EN_COURS
- ✅ Crée des alertes J-7 (7 jours avant la fin)
- ✅ Envoie aux responsables et à l'équipe
- ✅ Évite les doublons

---

## 🚀 Pour l'automatiser (3 étapes)

### Étape 1 : Créer le dossier logs

```bash
mkdir logs
```

### Étape 2 : Tester la commande

```bash
python manage.py check_project_deadlines
```

Vous devriez voir :
```
🔍 Vérification des échéances des projets...
📊 X projet(s) actif(s) à vérifier
✅ Vérification terminée !
```

### Étape 3 : Configurer le Planificateur Windows

1. **Ouvrir le Planificateur** : `Windows + R` → `taskschd.msc`

2. **Créer une tâche** :
   - Nom : `Vérification Alertes Projets`
   - Déclencheur : Quotidien à 8h00
   - Action : Exécuter `run_check_deadlines.bat`

3. **Tester** : Clic droit sur la tâche → "Exécuter"

---

## 📋 Fichier batch fourni

Le fichier `run_check_deadlines.bat` est déjà créé pour vous!

Il contient :
```batch
cd /d "%~dp0"
python manage.py check_project_deadlines >> logs\alertes.log 2>&1
```

---

## ✅ C'est tout!

Les alertes seront créées automatiquement tous les jours à 8h00.

---

## 📚 Guide complet

Pour plus de détails : `AUTOMATISATION_ALERTES_WINDOWS.md`
