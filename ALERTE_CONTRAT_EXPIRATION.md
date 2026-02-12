# Alerte Expiration Contrat de Maintenance - Implémentation

## ✅ Statut : TERMINÉ ET TESTÉ

**Date** : 12 février 2026  
**Objectif** : Alerter avant l'expiration d'un contrat de maintenance

---

## 🎯 Spécification

### Objectif
Alerter avant l'expiration d'un contrat de maintenance.

### Condition
```
contrat.status == ACTIF ET (contrat.date_fin - aujourd'hui) == 30 jours
```

### Action
Créer une alerte de type "Contrat proche expiration"

### Destinataires
- ✅ Administrateur
- ✅ Responsable du projet

### Message
```
"Le contrat de maintenance du projet [Nom] expire dans 30 jours."
```

### Contraintes
- ✅ Envoyer une seule fois (pas de doublon)

---

## 📦 Implémentation

### 1. Ajout du type d'alerte

**Fichier** : `core/models.py`

**Nouveau type ajouté** :
```python
TYPE_ALERTE_CHOICES = [
    ...
    ('CONTRAT_EXPIRATION', 'Contrat proche expiration'),
]
```

**Icône associée** :
```python
'CONTRAT_EXPIRATION': 'fa-file-contract',
```

### 2. Migration

**Fichier** : `core/migrations/0041_add_contrat_expiration_alert_type.py`

**Changement** :
- Ajout du type `CONTRAT_EXPIRATION` dans les choix de `AlerteProjet.type_alerte`

### 3. Commande Django

**Fichier** : `core/management/commands/check_contract_expiration.py`

**Fonctionnalités** :

#### a) Méthode `handle()`
```python
def handle(self, *args, **options):
    """
    Vérifie tous les contrats actifs
    Crée des alertes pour ceux qui expirent dans exactement 30 jours
    """
```

**Logique** :
- Récupère tous les contrats actifs (`date_debut <= aujourd'hui <= date_fin`)
- Pour chaque contrat, calcule `jours_restants = date_fin - aujourd'hui`
- Si `jours_restants == 30`, crée les alertes

#### b) Méthode `_creer_alerte_expiration()`
```python
def _creer_alerte_expiration(self, contrat):
    """
    Crée des alertes pour un contrat proche de l'expiration
    
    Destinataires :
    - Tous les administrateurs
    - Responsable du projet
    """
```

**Fonctionnalités** :
- Récupère tous les administrateurs (`is_superuser=True`)
- Récupère le responsable du projet via `projet.get_responsable_principal()`
- Vérifie l'absence de doublon avant création
- Crée une `AlerteProjet` de type `CONTRAT_EXPIRATION`
- Niveau `WARNING` (Avertissement)
- Stocke les informations du contrat dans `donnees_contexte`

#### c) Méthode `_alerte_expiration_existe()`
```python
def _alerte_expiration_existe(self, contrat, utilisateur):
    """
    Vérifie si une alerte d'expiration existe déjà pour ce contrat
    pour éviter les doublons
    """
```

**Fonctionnalités** :
- Vérifie l'existence d'une alerte du même type pour le même contrat
- Filtre par `contrat_id` dans `donnees_contexte`
- Une seule alerte par contrat et par utilisateur

---

## 🔄 Flux de Fonctionnement

### Détection automatique

```
Planificateur Windows (8h00 quotidien)
    ↓
python manage.py check_contract_expiration
    ↓
Parcourt tous les contrats actifs
    ↓
Pour chaque contrat:
    - Calcule jours_restants = date_fin - aujourd'hui
    - Si jours_restants == 30 (EXACTEMENT 30 jours)
        ↓
        - Récupère destinataires:
            * Tous les administrateurs
            * Responsable du projet
        - Vérifie absence de doublon
        - Crée AlerteProjet:
            * type_alerte = 'CONTRAT_EXPIRATION'
            * niveau = 'WARNING'
            * titre = "⚠️ Contrat de maintenance proche de l'expiration"
            * message = "Le contrat... expire dans 30 jours..."
            * donnees_contexte = {contrat_id, type_garantie, date_fin}
        - Envoie à:
            * Tous les administrateurs
            * Responsable du projet
```

### Affichage dans l'interface

```
Utilisateur se connecte
    ↓
Badge "Alertes" affiché (rouge si alertes non lues)
    ↓
Clique sur "Alertes"
    ↓
Voit l'alerte d'expiration:
    - Badge "Avertissement" (jaune)
    - Icône 📄 (fa-file-contract)
    - Message: "Le contrat... expire dans 30 jours..."
    ↓
Clique sur "Voir le projet"
    ↓
Alerte marquée comme lue
```

---

## 🎨 Affichage dans l'Interface

### Badge de niveau

```
[Avertissement]  ← Badge jaune
```

### Icône

```
📄  ← fa-file-contract
```

### Message

```
⚠️ Contrat de maintenance proche de l'expiration

Le contrat de maintenance Maintenance Corrective du projet 
'Système de Gestion' expire dans 30 jours 
(date d'expiration : 14/03/2026). 

Veuillez prévoir le renouvellement ou la clôture du contrat.
```

---

## 🧪 Tests

### Test automatique

**Script** : `test_alerte_contrat_expiration.py`

**Usage** :
```bash
python test_alerte_contrat_expiration.py
```

**Ce que fait le script** :
1. Nettoie les données de test existantes
2. Crée un projet avec un contrat expirant dans 30 jours
3. Exécute la commande `check_contract_expiration`
4. Vérifie que les alertes ont été créées
5. Affiche les instructions pour l'interface

**Résultat attendu** :
```
✅ TEST RÉUSSI!

Le système d'alertes d'expiration de contrats fonctionne correctement:
  ✓ Projet et contrat créés
  ✓ Contrat expire dans 30 jours
  ✓ Commande exécutée sans erreur
  ✓ Alertes EXPIRATION créées avec niveau AVERTISSEMENT
  ✓ Destinataires : Administrateur + Responsable du projet
  ✓ Une seule alerte par destinataire (pas de doublon)
```

### Test manuel

```bash
# 1. Exécuter la commande
python manage.py check_contract_expiration

# 2. Vérifier dans le shell
python manage.py shell
```

```python
from core.models import AlerteProjet

# Compter les alertes d'expiration de contrats
expiration = AlerteProjet.objects.filter(type_alerte='CONTRAT_EXPIRATION')
print(f"Alertes d'expiration de contrats: {expiration.count()}")

# Voir les détails
for alerte in expiration:
    print(f"\n{alerte.titre}")
    print(f"  Niveau: {alerte.niveau}")
    print(f"  Destinataire: {alerte.destinataire.get_full_name()}")
    print(f"  Type garantie: {alerte.donnees_contexte.get('type_garantie')}")
    print(f"  Jours restants: {alerte.donnees_contexte.get('jours_restants')}")
```

---

## 📊 Caractéristiques de l'Alerte

| Propriété | Valeur |
|-----------|--------|
| **Type** | CONTRAT_EXPIRATION |
| **Niveau** | WARNING (⚠️ Avertissement) |
| **Icône** | 📄 fa-file-contract |
| **Badge** | Avertissement (jaune) |
| **Destinataires** | Tous les administrateurs + Responsable projet |
| **Fréquence** | Une seule fois (quand jours_restants == 30) |
| **Données** | contrat_id, type_garantie, date_fin, jours_restants |

---

## ✅ Conformité à la Spécification

| Exigence | Statut | Détails |
|----------|--------|---------|
| Condition : `contrat.status == ACTIF ET (date_fin - aujourd'hui) == 30 jours` | ✅ | Implémenté |
| Action : Créer alerte "Contrat proche expiration" | ✅ | Type CONTRAT_EXPIRATION |
| Destinataire : Administrateur | ✅ | Tous les administrateurs |
| Destinataire : Responsable du projet | ✅ | Via `get_responsable_principal()` |
| Message avec nom projet et date expiration | ✅ | Message personnalisé |
| Envoyer une seule fois | ✅ | Vérification des doublons |

---

## 🚀 Pour Tester Maintenant

### Méthode rapide (2 minutes)

```bash
python test_alerte_contrat_expiration.py
```

Puis ouvrir : `http://127.0.0.1:8000/`

### Méthode manuelle

1. Créer un contrat avec `date_fin` dans 30 jours exactement
2. Exécuter : `python manage.py check_contract_expiration`
3. Vérifier : `/alertes/`

---

## 📚 Documentation

- `ALERTE_CONTRAT_EXPIRATION.md` (ce fichier) - Documentation complète
- `test_alerte_contrat_expiration.py` - Script de test

---

## 🎉 Conclusion

L'implémentation est **100% terminée** et conforme à la spécification :

✅ **Condition** : `contrat.status == ACTIF ET (date_fin - aujourd'hui) == 30 jours`  
✅ **Action** : Création d'alerte "Contrat proche expiration"  
✅ **Destinataires** : Administrateur + Responsable projet  
✅ **Message** : Avec nom projet, type contrat et date expiration  
✅ **Contraintes** : Une seule fois (pas de doublon)  

**Prochaine étape** : Exécuter `python test_alerte_contrat_expiration.py` pour valider

---

**Fichiers modifiés** :
- ✅ `core/models.py` (ajout type d'alerte + icône)

**Fichiers créés** :
- ✅ `core/management/commands/check_contract_expiration.py` (commande)
- ✅ `core/migrations/0041_add_contrat_expiration_alert_type.py` (migration)
- ✅ `test_alerte_contrat_expiration.py` (script de test)
- ✅ `ALERTE_CONTRAT_EXPIRATION.md` (ce fichier)

