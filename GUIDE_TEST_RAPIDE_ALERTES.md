# Guide de Test Rapide - Système d'Alertes

## 🚀 Test en 5 minutes

### Étape 1 : Exécuter le script de test

```bash
python test_alerte_j7.py
```

Ce script va automatiquement :
1. ✅ Nettoyer les projets de test existants
2. ✅ Créer un projet qui se termine dans 7 jours
3. ✅ Exécuter la commande `check_project_deadlines`
4. ✅ Vérifier que l'alerte a été créée
5. ✅ Afficher les instructions pour tester l'interface

---

### Étape 2 : Vérifier dans le navigateur

1. **Ouvrir le navigateur** et aller sur : `http://127.0.0.1:8000/`

2. **Se connecter** avec l'administrateur

3. **Observer la sidebar** :
   - Le menu "Alertes" (⚠️ triangle orange) devrait afficher un badge rouge avec "1"

4. **Cliquer sur "Alertes"** :
   - Vous devriez voir la page `/alertes/`
   - Une alerte "Projet proche de l'échéance" devrait être affichée
   - Badge "Nouveau" visible
   - Badge "Avertissement" visible

5. **Cliquer sur "Voir le projet"** :
   - Vous êtes redirigé vers le projet
   - L'alerte est marquée comme lue

6. **Retourner sur `/alertes/`** :
   - Le badge "Nouveau" a disparu
   - Le badge dans la sidebar a disparu

---

### Étape 3 : Vérifier l'API

Ouvrir dans le navigateur (connecté) :

```
http://127.0.0.1:8000/api/alertes/count/
```

**Résultat attendu** :
```json
{"count": 1}
```

Après avoir marqué l'alerte comme lue :
```json
{"count": 0}
```

---

## 🧪 Tests supplémentaires

### Test J-3 (3 jours avant échéance)

Modifier le script `test_alerte_j7.py` ligne 73 :
```python
date_fin = date_debut + timedelta(days=3)  # Au lieu de 7
```

Puis relancer :
```bash
python test_alerte_j7.py
```

### Test J-1 (1 jour avant échéance)

Modifier le script ligne 73 :
```python
date_fin = date_debut + timedelta(days=1)  # Au lieu de 7
```

**Résultat attendu** : Badge "Critique" (rouge) au lieu de "Avertissement"

### Test échéance dépassée

Modifier le script ligne 73 :
```python
date_fin = date_debut - timedelta(days=1)  # Hier
```

**Résultat attendu** : Badge "Critique" avec icône ❌

---

## 🔍 Vérification manuelle dans le shell

```bash
python manage.py shell
```

```python
from core.models import AlerteProjet

# Lister toutes les alertes
alertes = AlerteProjet.objects.all()
print(f"Total: {alertes.count()}")

# Voir les détails
for alerte in alertes:
    print(f"\n{alerte.titre}")
    print(f"  Type: {alerte.type_alerte}")
    print(f"  Niveau: {alerte.niveau}")
    print(f"  Lue: {alerte.lue}")
    print(f"  Destinataire: {alerte.destinataire.get_full_name()}")

# Compter les non lues
non_lues = AlerteProjet.objects.filter(lue=False).count()
print(f"\nAlertes non lues: {non_lues}")
```

---

## ✅ Checklist de validation

- [ ] Script exécuté sans erreur
- [ ] Projet de test créé
- [ ] Alerte créée dans la base de données
- [ ] Badge affiché dans la sidebar
- [ ] Page `/alertes/` accessible
- [ ] Alerte visible avec badge "Nouveau"
- [ ] Clic sur "Voir le projet" fonctionne
- [ ] Alerte marquée comme lue
- [ ] Badge disparaît de la sidebar
- [ ] API `/api/alertes/count/` répond correctement

---

## 🐛 Problèmes courants

### Le script échoue avec "Aucun administrateur trouvé"

**Solution** : Créer un super utilisateur
```bash
python manage.py createsuperuser
```

### Le script échoue avec "Statut EN_COURS non trouvé"

**Solution** : Initialiser les données
```bash
python manage.py init_data
```

### Le badge ne s'affiche pas

**Causes possibles** :
1. JavaScript non chargé → Vérifier la console (F12)
2. API ne répond pas → Tester `/api/alertes/count/`
3. Alerte déjà lue → Créer une nouvelle alerte

**Solution** : Recharger la page et attendre 60 secondes maximum

### L'alerte n'est pas créée

**Vérifier** :
```bash
python manage.py shell
```

```python
from core.models import Projet
from datetime import date, timedelta

# Vérifier le projet
projet = Projet.objects.filter(nom__startswith="TEST ALERTE").first()
print(f"Projet: {projet.nom}")
print(f"Date fin: {projet.date_fin}")
print(f"Statut: {projet.statut.nom}")
print(f"Jours restants: {(projet.date_fin - date.today()).days}")
```

---

## 📊 Résultats attendus

### Console du script

```
======================================================================
  TEST DU SYSTÈME D'ALERTES - ALERTE J-7
======================================================================

======================================================================
  NETTOYAGE DES PROJETS DE TEST
======================================================================
ℹ️  Aucun projet de test à supprimer

======================================================================
  CRÉATION DU PROJET TEST J-7
======================================================================
✅ Administrateur trouvé: Admin User (admin@example.com)
✅ Statut EN_COURS trouvé

📅 Dates du projet:
   - Date de début: 12/02/2026
   - Date de fin: 19/02/2026
   - Jours restants: 7 jours

✅ Projet créé: TEST ALERTE J-7 - 20260212
   ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
✅ Responsable affecté: Admin User

======================================================================
  EXÉCUTION DE LA COMMANDE check_project_deadlines
======================================================================
Exécution de: python manage.py check_project_deadlines

----------------------------------------------------------------------
[INFO] Vérification des échéances de projets...
[INFO] Projet: TEST ALERTE J-7 - 20260212
[INFO] Jours restants: 7
[INFO] Création d'une alerte J-7
[SUCCESS] Alerte créée pour Admin User
----------------------------------------------------------------------

✅ Commande exécutée avec succès

======================================================================
  VÉRIFICATION DES ALERTES CRÉÉES
======================================================================
Nombre d'alertes créées: 1

📋 Détails des alertes:

   Alerte #1:
   - Type: Échéance dans 7 jours
   - Niveau: Avertissement
   - Titre: Projet proche de l'échéance
   - Destinataire: Admin User
   - Lue: Non
   - Date création: 12/02/2026 14:30

✅ 1 alerte(s) créée(s) avec succès

======================================================================
  RÉSUMÉ DU TEST
======================================================================

✅ TEST RÉUSSI!

Le système d'alertes fonctionne correctement:
  ✓ Projet de test créé
  ✓ Commande exécutée sans erreur
  ✓ Alerte J-7 créée

Prochaines étapes:
  1. Vérifier le badge dans la sidebar
  2. Consulter la page /alertes/
  3. Marquer l'alerte comme lue
  4. Vérifier que le badge disparaît
```

---

## 🎉 Validation finale

Si tous les tests passent, le système d'alertes est **100% opérationnel** !

**Prochaine étape** : Configurer le Planificateur de tâches Windows pour automatiser les vérifications quotidiennes.

Voir : `GUIDE_PLANIFICATEUR_WINDOWS.md`
