# ⚡ Quick Start - Système d'Alertes

## 🎯 En 3 Étapes

### 1️⃣ Configurer (5 minutes)

```
Windows → Planificateur de tâches → Créer une tâche

Nom : Alertes SI-Gouvernance
Déclencheur : Quotidien à 8h00
Action : E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE\run_check_deadlines.bat
```

**Guide détaillé** : `CONFIGURATION_PLANIFICATEUR_ETAPE_PAR_ETAPE.md`

### 2️⃣ Tester (2 minutes)

```bash
# Clic droit sur la tâche → Exécuter
# OU
run_check_deadlines.bat
```

### 3️⃣ Vérifier (1 minute)

```bash
python suivi_quotidien_alertes.py
```

## ✅ C'est fait !

Chaque jour à 8h00, le système va :
1. Vérifier toutes les tâches actives
2. Créer des alertes pour les échéances proches
3. Notifier les utilisateurs concernés

## 📊 Suivi Quotidien

```bash
# Chaque matin
python suivi_quotidien_alertes.py
```

## 📚 Documentation Complète

- `README_SYSTEME_ALERTES.md` - Guide complet
- `CONFIGURATION_PLANIFICATEUR_ETAPE_PAR_ETAPE.md` - Configuration détaillée
- `ETAT_SYSTEME_ALERTES_FINAL.md` - État du système

## 🔧 Commandes Utiles

```bash
# Exécution manuelle
python manage.py check_task_deadlines

# Vérification complète
python verification_systeme_alertes.py

# Voir les logs
type logs\planificateur.log
```

## 🎉 Prêt !

Tout est configuré et prêt à fonctionner automatiquement.

---

**Durée totale** : 8 minutes  
**Difficulté** : Facile ⭐  
**Résultat** : Système 100% automatisé ✅
