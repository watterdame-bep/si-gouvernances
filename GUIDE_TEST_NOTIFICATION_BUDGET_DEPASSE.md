# Guide de Test - Notification Budget Dépassé

## Prérequis
- Serveur Docker démarré: `docker-compose up -d`
- Accès admin: http://localhost:8000
- Au moins un projet avec budget défini

## Test 1: Dépassement de budget simple

### Étape 1: Préparer un projet
1. Se connecter en tant qu'admin
2. Aller sur "Projets" → Sélectionner un projet
3. Aller dans "Paramètres" → Onglet "Budget"
4. Noter le budget total (ex: $10,000)
5. Noter les dépenses actuelles (ex: $5,000)
6. Calculer: Budget disponible = $5,000

### Étape 2: Ajouter une dépense qui dépasse
1. Cliquer sur "Ajouter des dépenses"
2. Ajouter une ligne:
   - Type: Matériel
   - Montant: $6,000 (dépasse le disponible de $5,000)
   - Description: "Test dépassement budget"
3. Cliquer sur "Ajouter"

### Étape 3: Vérifier la notification
1. Regarder l'icône cloche en haut à droite
2. ✅ Un badge rouge devrait apparaître avec "1"
3. Cliquer sur la cloche
4. ✅ Voir l'alerte "⚠️ Budget dépassé - [Nom projet]"
5. Lire le message avec les montants
6. Cliquer sur l'alerte
7. ✅ Être redirigé vers les paramètres du projet

### Étape 4: Vérifier l'affichage du budget
1. Dans l'onglet Budget
2. ✅ Voir "Budget disponible" en rouge et négatif
3. ✅ Voir le badge "DÉPASSÉ" en rouge
4. ✅ Voir la barre de progression rouge à > 100%

## Test 2: Pas de doublon de notification

### Étape 1: Ajouter une autre dépense
1. Toujours dans le même projet
2. Ajouter une nouvelle ligne:
   - Type: Service
   - Montant: $1,000
   - Description: "Autre dépense"
3. Cliquer sur "Ajouter"

### Étape 2: Vérifier les notifications
1. Regarder l'icône cloche
2. ✅ Le badge devrait toujours afficher "1" (pas de nouvelle alerte)
3. Ouvrir les alertes
4. ✅ Voir toujours une seule alerte de budget dépassé pour ce projet

## Test 3: Nouvelle notification après lecture

### Étape 1: Marquer l'alerte comme lue
1. Cliquer sur l'alerte de budget dépassé
2. L'alerte disparaît de la liste
3. Le badge diminue

### Étape 2: Supprimer des dépenses
1. Dans l'onglet Budget
2. Supprimer la dépense de $6,000
3. ✅ Le budget redevient positif

### Étape 3: Redépasser le budget
1. Ajouter une nouvelle dépense de $7,000
2. Le budget redépasse

### Étape 4: Vérifier nouvelle notification
1. Regarder l'icône cloche
2. ✅ Un nouveau badge "1" apparaît
3. ✅ Une nouvelle alerte est créée

## Test 4: Notification pour plusieurs admins

### Étape 1: Créer un second admin (si nécessaire)
1. Aller dans "Gestion" → "Comptes"
2. Créer un nouveau compte admin
3. Se déconnecter

### Étape 2: Provoquer un dépassement
1. Se connecter avec le premier admin
2. Ajouter une dépense qui dépasse le budget

### Étape 3: Vérifier pour le second admin
1. Se déconnecter
2. Se connecter avec le second admin
3. ✅ Voir aussi l'alerte dans sa cloche
4. ✅ Chaque admin a sa propre alerte

## Test 5: Script de test automatique

### Exécution
```bash
docker-compose exec web python test_notification_budget_depasse.py
```

### Résultat attendu
```
================================================================================
TEST: Notification de dépassement de budget
================================================================================

✅ Projet trouvé: [Nom du projet]
   Budget total: $10,000.00

📊 État actuel du budget:
   - Dépenses: $5,000.00
   - Disponible: $5,000.00
   - Statut: OK

✅ Administrateur: [Nom Admin] ([email])

📬 Alertes existantes: 0

💰 Ajout d'une dépense de $6,000.00
   (pour dépasser le budget de $1,000.00)

✅ Ligne budgétaire créée: [UUID]

📊 Nouvel état du budget:
   - Dépenses: $11,000.00
   - Disponible: -$1,000.00
   - Statut: DEPASSE
   ⚠️ DÉPASSEMENT: $1,000.00

================================================================================
CRÉATION MANUELLE DE L'ALERTE (simulation de la vue)
================================================================================

✅ Alerte créée: [UUID]
   Titre: ⚠️ Budget dépassé - [Nom projet]
   Message: Le budget du projet "[Nom]" a été dépassé...
   Destinataire: [Nom Admin]
   Lien: /projets/[UUID]/parametres/

📬 Alertes après: 1
   Nouvelles alertes: 1
```

## Test 6: Vérification dans la base de données

### Via Django shell
```bash
docker-compose exec web python manage.py shell
```

```python
from core.models import AlerteProjet

# Compter les alertes de budget dépassé
alertes = AlerteProjet.objects.filter(type_alerte='BUDGET_DEPASSE')
print(f"Total alertes: {alertes.count()}")

# Afficher les détails
for alerte in alertes:
    print(f"\n{alerte.titre}")
    print(f"Projet: {alerte.projet.nom}")
    print(f"Admin: {alerte.utilisateur.get_full_name()}")
    print(f"Lue: {alerte.lue}")
    print(f"Date: {alerte.date_creation}")
```

## Résultats attendus

### ✅ Succès si:
1. L'alerte apparaît dans la cloche après dépassement
2. Le message contient les bons montants
3. Le lien redirige vers les paramètres du projet
4. Pas de doublon si alerte non lue existe
5. Nouvelle alerte après lecture de l'ancienne
6. Tous les admins reçoivent l'alerte
7. Le badge de statut affiche "DÉPASSÉ" en rouge

### ❌ Échec si:
1. Aucune alerte n'apparaît
2. Les montants sont incorrects
3. Le lien ne fonctionne pas
4. Des doublons sont créés
5. L'alerte n'apparaît pas pour tous les admins

## Nettoyage après tests

### Supprimer les alertes de test
```python
# Dans Django shell
from core.models import AlerteProjet

AlerteProjet.objects.filter(
    type_alerte='BUDGET_DEPASSE',
    titre__contains='Test'
).delete()
```

### Supprimer les lignes budgétaires de test
```python
from core.models_budget import LigneBudget

LigneBudget.objects.filter(
    description__contains='Test'
).delete()
```

## Dépannage

### Problème: Aucune alerte créée
- Vérifier que l'utilisateur est bien admin (is_superuser=True)
- Vérifier que le budget est bien dépassé (budget_disponible < 0)
- Vérifier les logs: `docker-compose logs web`

### Problème: Alerte créée mais pas visible
- Rafraîchir la page (F5)
- Vérifier que l'alerte n'est pas déjà lue
- Vérifier le JavaScript de la cloche (console F12)

### Problème: Doublons créés
- Vérifier la logique de vérification dans views_budget.py
- Vérifier que la condition `lue=False` est bien présente

## Notes
- Les alertes sont créées côté serveur (backend)
- L'affichage est géré par le template (frontend)
- Le badge est mis à jour automatiquement
- Les alertes lues restent en base mais ne s'affichent plus
