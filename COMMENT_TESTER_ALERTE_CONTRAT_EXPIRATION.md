# Comment Tester l'Alerte d'Expiration de Contrat ? ⚠️

## En 2 commandes

### 1. Exécuter le script de test
```bash
python test_alerte_contrat_expiration.py
```

**Appuyez sur Entrée** quand demandé pour lancer le test.

### 2. Ouvrir le navigateur
```
http://127.0.0.1:8000/
```

Se connecter avec un administrateur ou le responsable du projet

Regarder la sidebar à gauche → Le menu "Alertes" devrait avoir un badge rouge

Cliquer sur "Alertes" → Voir l'alerte d'EXPIRATION avec badge "Avertissement" (jaune)

---

## C'est tout ! ✅

Le script fait automatiquement :
- ✅ Crée un projet avec un contrat expirant dans 30 jours
- ✅ Exécute la commande de vérification
- ✅ Crée les alertes de niveau AVERTISSEMENT
- ✅ Affiche les instructions

---

## Résultat attendu

### Dans la console
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

### Dans l'interface
- Badge rouge sur "Alertes"
- Alerte avec badge "Avertissement" (jaune)
- Icône 📄 (fa-file-contract)
- Message : "Le contrat de maintenance... expire dans 30 jours..."

---

## Destinataires

✅ **Tous les administrateurs**  
✅ **Responsable du projet**

---

## Test manuel (alternative)

Si vous voulez tester manuellement sans le script :

### 1. Créer un contrat expirant dans 30 jours

```bash
python manage.py shell
```

```python
from core.models import *
from datetime import date, timedelta

# Récupérer un projet
projet = Projet.objects.first()

# Créer un contrat expirant dans 30 jours
contrat = ContratGarantie.objects.create(
    projet=projet,
    type_garantie='CORRECTIVE',
    date_debut=date.today() - timedelta(days=335),
    date_fin=date.today() + timedelta(days=30),  # Expire dans 30 jours
    sla_heures=48,
    description_couverture="Test expiration",
    cree_par=projet.createur
)
```

### 2. Exécuter la commande

```bash
python manage.py check_contract_expiration
```

### 3. Vérifier les alertes

```bash
python manage.py shell
```

```python
from core.models import AlerteProjet

# Compter les alertes d'expiration
expiration = AlerteProjet.objects.filter(type_alerte='CONTRAT_EXPIRATION')
print(f"Alertes d'expiration: {expiration.count()}")

# Voir les détails
for alerte in expiration:
    print(f"\n{alerte.titre}")
    print(f"  Niveau: {alerte.niveau}")
    print(f"  Destinataire: {alerte.destinataire.get_full_name()}")
    print(f"  Type garantie: {alerte.donnees_contexte.get('type_garantie')}")
```

---

## Guide complet

Pour plus de détails : `ALERTE_CONTRAT_EXPIRATION.md`

---

## Fichiers créés

- ✅ `core/management/commands/check_contract_expiration.py` - Commande
- ✅ `core/migrations/0041_add_contrat_expiration_alert_type.py` - Migration
- ✅ `test_alerte_contrat_expiration.py` - Script de test
- ✅ `ALERTE_CONTRAT_EXPIRATION.md` - Documentation
- ✅ `COMMENT_TESTER_ALERTE_CONTRAT_EXPIRATION.md` - Ce fichier

