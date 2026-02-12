# Comment Tester l'Alerte de Tâche en Retard ? 🔴

## ✅ PROBLÈME RÉSOLU : ProtectedError

**Problème initial** : Le script échouait avec l'erreur `ProtectedError` lors de la suppression des projets de test car ils avaient des `ActionAudit` liés avec une clé étrangère protégée (`on_delete=models.PROTECT`).

**Solution appliquée** : Suppression des `ActionAudit` liés AVANT de supprimer les projets.

```python
# Dans la fonction nettoyer_tests()
from core.models import ActionAudit
for projet in projets_test:
    ActionAudit.objects.filter(projet=projet).delete()

# Maintenant supprimer les projets
projets_test.delete()
```

---

## En 2 commandes

### 1. Exécuter le script de test
```bash
python test_alerte_tache_retard.py
```

**Appuyez sur Entrée** quand demandé pour lancer le test.

### 2. Ouvrir le navigateur
```
http://127.0.0.1:8000/
```

Se connecter avec le responsable de la tâche ou du projet

Regarder la sidebar à gauche → Le menu "Alertes" devrait avoir un badge rouge

Cliquer sur "Alertes" → Voir l'alerte de RETARD avec badge "Critique" (rouge)

---

## C'est tout ! ✅

Le script fait automatiquement :
- ✅ Nettoie les données de test (supprime ActionAudit puis projets)
- ✅ Crée un projet avec une tâche en retard de 2 jours
- ✅ Exécute la commande de vérification
- ✅ Crée les alertes de niveau CRITIQUE
- ✅ Affiche les instructions

---

## Résultat attendu

### Dans la console
```
✅ TEST RÉUSSI!

Le système d'alertes de tâches en retard fonctionne correctement:
  ✓ Projet et tâche en retard créés
  ✓ Commande exécutée sans erreur
  ✓ Alertes RETARD créées avec niveau CRITIQUE
  ✓ Destinataires : Responsable tâche + Responsable projet
  ✓ PAS d'alerte pour l'administrateur (conforme à la spec)
```

### Dans l'interface
- Badge rouge sur "Alertes"
- Alerte avec badge "Critique" (rouge)
- Icône ⚠️ (fa-tasks)
- Message : "La tâche X du projet Y est en retard de 2 jours..."

---

## Destinataires

✅ **Responsable de la tâche** (utilisateur assigné)  
✅ **Responsable du projet**  
❌ **PAS l'administrateur** (selon spécification)

---

## Test manuel (alternative)

Si vous voulez tester manuellement sans le script :

### 1. Créer une tâche en retard

```bash
python manage.py shell
```

```python
from core.models import *
from datetime import date, timedelta

# Récupérer un projet
projet = Projet.objects.first()

# Récupérer une étape
etape = EtapeProjet.objects.filter(projet=projet).first()

# Créer une tâche en retard
tache = TacheEtape.objects.create(
    etape=etape,
    nom="Tâche test en retard",
    responsable=projet.get_responsable_principal(),
    statut='EN_COURS',
    date_debut=date.today() - timedelta(days=7),
    date_fin=date.today() - timedelta(days=2),  # En retard de 2 jours
    createur=projet.createur
)
```

### 2. Exécuter la commande

```bash
python manage.py check_task_deadlines
```

### 3. Vérifier les alertes

```bash
python manage.py shell
```

```python
from core.models import AlerteProjet

# Compter les alertes de tâches en retard
retard = AlerteProjet.objects.filter(type_alerte='TACHES_EN_RETARD')
print(f"Alertes de tâches en retard: {retard.count()}")

# Voir les détails
for alerte in retard:
    print(f"\n{alerte.titre}")
    print(f"  Niveau: {alerte.niveau}")
    print(f"  Destinataire: {alerte.destinataire.get_full_name()}")
    print(f"  Tâche: {alerte.donnees_contexte.get('tache_nom')}")
    print(f"  Jours de retard: {alerte.donnees_contexte.get('jours_retard')}")
```

---

## Guide complet

Pour plus de détails : `ALERTE_TACHE_EN_RETARD.md`

---

## Fichiers modifiés

- ✅ `test_alerte_tache_retard.py` - Correction du nettoyage des données
- ✅ `core/management/commands/check_task_deadlines.py` - Implémentation complète
- ✅ `COMMENT_TESTER_ALERTE_TACHE_RETARD.md` - Ce fichier (mis à jour)

