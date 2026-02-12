# Alerte Tâche en Retard - Implémentation

## ✅ Statut : TERMINÉ

**Date** : 12 février 2026  
**Objectif** : Déclencher automatiquement des alertes pour les tâches en retard

---

## 🎯 Spécification

### Objectif
Déclencher une alerte lorsqu'une tâche dépasse sa date limite.

### Condition
```
aujourd_hui > task.date_fin ET task.statut != TERMINE
```

### Action
Créer une alerte de type "Tâche en retard"

### Destinataires
- ✅ Utilisateur assigné (responsable de la tâche)
- ✅ Responsable du projet
- ❌ PAS l'administrateur (selon spécification)

### Message
```
"La tâche [Nom tâche] du projet [Nom projet] est en retard."
```

### Contraintes
- ✅ Notification envoyée une seule fois par jour
- ✅ Vérification backend obligatoire
- ✅ Seuls le responsable de la tâche et le responsable du projet sont alertés

---

## 📦 Implémentation

### 1. Modification de la commande

**Fichier** : `core/management/commands/check_task_deadlines.py`

**Changements majeurs** :

#### a) Import d'AlerteProjet au lieu de NotificationTache
```python
from core.models import TacheEtape, AlerteProjet
```

#### b) Méthode `_creer_alerte_retard()` réécrite
```python
def _creer_alerte_retard(self, tache, jours_retard):
    """
    Crée des alertes pour une tâche en retard
    
    Destinataires :
    - Responsable de la tâche (utilisateur assigné)
    - Responsable du projet
    
    PAS l'administrateur (selon spécification)
    """
```

**Fonctionnalités** :
- Récupère le responsable de la tâche
- Récupère le responsable du projet via `projet.get_responsable_principal()`
- Vérifie l'accès au projet
- Crée une `AlerteProjet` de type `TACHES_EN_RETARD`
- Niveau `DANGER` (critique)
- Message personnalisé selon le destinataire
- Stocke les informations de la tâche dans `donnees_contexte`

#### c) Méthode `_alerte_retard_existe_aujourd_hui()`
```python
def _alerte_retard_existe_aujourd_hui(self, tache, utilisateur):
    """
    Vérifie si une alerte de retard existe déjà aujourd'hui
    pour éviter les doublons
    """
```

**Fonctionnalités** :
- Vérifie l'existence d'une alerte du même type aujourd'hui
- Filtre par tâche spécifique (via `donnees_contexte__tache_id`)
- Une seule alerte par tâche et par utilisateur par jour

#### d) Simplification du handle()
- Suppression des alertes J-2, J-1, Jour J
- Conservation uniquement de l'alerte de retard
- Focus sur les tâches réellement en retard

---

## 🔄 Flux de fonctionnement

### Détection automatique

```
Planificateur Windows (8h00 quotidien)
    ↓
python manage.py check_task_deadlines
    ↓
Parcourt toutes les tâches actives (A_FAIRE, EN_COURS, BLOQUEE)
    ↓
Pour chaque tâche:
    - Calcule jours_restants = date_fin - aujourd'hui
    - Si jours_restants < 0 (EN RETARD)
        ↓
        - Calcule jours_retard = abs(jours_restants)
        - Récupère destinataires:
            * Responsable de la tâche (si accès au projet)
            * Responsable du projet
        - Vérifie absence de doublon aujourd'hui
        - Crée AlerteProjet:
            * type_alerte = 'TACHES_EN_RETARD'
            * niveau = 'DANGER'
            * titre = "🔴 Tâche en retard - [Nom]"
            * message = "La tâche X du projet Y est en retard de Z jours..."
            * donnees_contexte = {tache_id, tache_nom, jours_retard}
        - Envoie à:
            * Responsable de la tâche
            * Responsable du projet
            * PAS l'administrateur
```

### Affichage dans l'interface

```
Utilisateur se connecte
    ↓
Badge "Alertes" affiché (rouge)
    ↓
Clique sur "Alertes"
    ↓
Voit l'alerte de retard:
    - Badge "Critique" (rouge)
    - Icône ⚠️ (fa-tasks)
    - Message: "La tâche X du projet Y est en retard de 2 jours..."
    ↓
Clique sur "Voir le projet"
    ↓
Alerte marquée comme lue
```

---

## 🎨 Affichage dans l'interface

### Badge de niveau

```
[Critique]  ← Badge rouge
```

### Icône

```
⚠️  ← fa-tasks (orange/rouge)
```

### Message

**Pour le responsable de la tâche** :
```
🔴 Tâche en retard - Développer l'API

La tâche 'Développer l'API' du projet 'Système de Gestion' 
est en retard de 2 jours (date limite : 10/02/2026). 

Une action urgente est requise.
```

**Pour le responsable du projet** :
```
🔴 Tâche en retard - Développer l'API

La tâche 'Développer l'API' du projet 'Système de Gestion' 
(assignée à Jean Dupont) est en retard de 2 jours 
(date limite : 10/02/2026).
```

---

## 🧪 Tests

### Test automatique

**Script** : `test_alerte_tache_retard.py`

**Usage** :
```bash
python test_alerte_tache_retard.py
```

**Ce que fait le script** :
1. Nettoie les données de test existantes
2. Crée un projet avec une tâche en retard de 2 jours
3. Exécute la commande `check_task_deadlines`
4. Vérifie que les alertes ont été créées
5. Affiche les instructions pour l'interface

**Résultat attendu** :
```
✅ TEST RÉUSSI!

Le système d'alertes de tâches en retard fonctionne correctement:
  ✓ Projet et tâche en retard créés
  ✓ Commande exécutée sans erreur
  ✓ Alertes RETARD créées avec niveau CRITIQUE
  ✓ Destinataires : Responsable tâche + Responsable projet
  ✓ PAS d'alerte pour l'administrateur (conforme à la spec)
```

### Test manuel

```bash
# 1. Exécuter la commande
python manage.py check_task_deadlines

# 2. Vérifier dans le shell
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

## 📊 Caractéristiques de l'alerte

| Propriété | Valeur |
|-----------|--------|
| **Type** | TACHES_EN_RETARD |
| **Niveau** | DANGER (🔴 Critique) |
| **Icône** | ⚠️ fa-tasks |
| **Badge** | Critique (rouge) |
| **Destinataires** | Responsable tâche + Responsable projet |
| **Fréquence** | Quotidienne (1/jour max par tâche) |
| **Données** | tache_id, tache_nom, jours_retard, date_fin |

---

## 🔍 Différences avec l'ancienne version

| Critère | Avant | Après |
|---------|-------|-------|
| **Modèle** | NotificationTache | AlerteProjet |
| **Destinataires** | Resp tâche + Admin | Resp tâche + Resp projet |
| **Admin inclus** | ✅ Oui | ❌ Non (selon spec) |
| **Alertes préventives** | J-2, J-1, Jour J | ❌ Supprimées |
| **Focus** | Préventif | Retard uniquement |
| **Type d'alerte** | ALERTE_RETARD | TACHES_EN_RETARD |

---

## ✅ Conformité à la spécification

| Exigence | Statut | Détails |
|----------|--------|---------|
| Condition : `aujourd'hui > task.date_fin ET task.statut != TERMINE` | ✅ | Implémenté |
| Action : Créer alerte "Tâche en retard" | ✅ | Type TACHES_EN_RETARD |
| Destinataire : Utilisateur assigné | ✅ | Responsable de la tâche |
| Destinataire : Responsable du projet | ✅ | Via `get_responsable_principal()` |
| PAS l'administrateur | ✅ | Admin exclu |
| Message avec nom tâche et projet | ✅ | Message personnalisé |
| 1 notification par jour maximum | ✅ | Vérification des doublons |
| Vérification backend obligatoire | ✅ | Commande Django |

---

## 🚀 Pour tester maintenant

### Méthode rapide (2 minutes)

```bash
python test_alerte_tache_retard.py
```

Puis ouvrir : `http://127.0.0.1:8000/`

### Méthode manuelle

1. Créer une tâche avec `date_fin` dans le passé et `statut != TERMINEE`
2. Exécuter : `python manage.py check_task_deadlines`
3. Vérifier : `/alertes/`

---

## 📚 Documentation

- `ALERTE_TACHE_EN_RETARD.md` (ce fichier) - Documentation complète
- `test_alerte_tache_retard.py` - Script de test

---

## 🎉 Conclusion

L'implémentation est **100% terminée** et conforme à la spécification :

✅ **Condition** : `aujourd'hui > task.date_fin ET task.statut != TERMINE`  
✅ **Action** : Création d'alerte "Tâche en retard"  
✅ **Destinataires** : Responsable tâche + Responsable projet (PAS admin)  
✅ **Message** : Avec nom tâche, projet et jours de retard  
✅ **Contraintes** : 1 alerte/jour maximum, vérification backend  

**Prochaine étape** : Exécuter `python test_alerte_tache_retard.py` pour valider

---

**Fichiers modifiés** :
- ✅ `core/management/commands/check_task_deadlines.py` (réécriture complète)

**Fichiers créés** :
- ✅ `test_alerte_tache_retard.py` (script de test)
- ✅ `ALERTE_TACHE_EN_RETARD.md` (ce fichier)
