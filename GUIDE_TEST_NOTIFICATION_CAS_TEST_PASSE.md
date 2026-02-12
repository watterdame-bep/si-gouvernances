# Guide de Test : Notification Cas de Test Passé

## Objectif

Vérifier que le responsable du projet reçoit une notification lorsqu'un cas de test est marqué comme passé.

## Prérequis

1. Appliquer la migration : `python manage.py migrate`
2. Un projet avec un responsable principal assigné
3. Une étape TESTS avec une tâche
4. Au moins un cas de test créé
5. Un utilisateur différent du responsable (QA ou responsable de tâche)

## Test 1 : Notification Envoyée

### Étapes

1. **Préparation**
   - Se connecter en tant qu'admin
   - Créer ou sélectionner un projet
   - Assigner un responsable principal au projet
   - Créer une tâche dans l'étape TESTS
   - Créer un cas de test pour cette tâche

2. **Connexion Exécuteur**
   - Se déconnecter
   - Se connecter avec un compte QA ou responsable de tâche
   - (PAS le responsable du projet)

3. **Exécution du Test**
   - Accéder aux cas de test de la tâche
   - Cliquer sur le bouton ✅ "Marquer comme Passé"
   - Remplir les résultats obtenus
   - Confirmer

4. **Vérification Notification**
   - Se déconnecter
   - Se connecter avec le compte du responsable du projet
   - Cliquer sur l'icône de notifications (cloche)
   - ✅ Vérifier qu'une notification "Cas de test passé" est présente

5. **Vérification Contenu**
   - ✅ Titre : "Cas de test passé : CT-XXX"
   - ✅ Message contient le nom du cas de test
   - ✅ Message contient le nom de la tâche
   - ✅ Message contient le nom de l'exécuteur
   - ✅ Notification non lue (badge ou indicateur)

### Résultat Attendu

Le responsable du projet reçoit une notification avec toutes les informations correctes.

---

## Test 2 : Pas d'Auto-Notification

### Objectif

Vérifier qu'un responsable de projet ne reçoit pas de notification quand il exécute lui-même un test.

### Étapes

1. **Connexion Responsable**
   - Se connecter en tant que responsable du projet

2. **Compter les Notifications**
   - Noter le nombre actuel de notifications

3. **Exécution du Test**
   - Accéder aux cas de test
   - Marquer un cas de test comme passé

4. **Vérification**
   - Vérifier les notifications
   - ✅ Le nombre de notifications n'a PAS augmenté
   - ✅ Pas de notification "Cas de test passé" pour soi-même

### Résultat Attendu

Aucune auto-notification n'est créée.

---

## Test 3 : Projet Sans Responsable

### Objectif

Vérifier qu'aucune erreur ne se produit si le projet n'a pas de responsable.

### Étapes

1. **Préparation**
   - Créer un projet SANS responsable principal
   - Créer une tâche TESTS avec un cas de test

2. **Exécution**
   - Se connecter en tant que QA
   - Marquer le cas de test comme passé

3. **Vérification**
   - ✅ Aucune erreur ne se produit
   - ✅ Le cas de test est bien marqué comme passé
   - ✅ Aucune notification n'est créée (normal)

### Résultat Attendu

Le système fonctionne normalement même sans responsable.

---

## Test 4 : Plusieurs Cas de Test

### Objectif

Vérifier que chaque cas de test passé génère une notification distincte.

### Étapes

1. **Préparation**
   - Créer 3 cas de test pour une même tâche

2. **Exécution**
   - Se connecter en tant que QA
   - Marquer les 3 cas de test comme passés (un par un)

3. **Vérification**
   - Se connecter en tant que responsable du projet
   - ✅ Vérifier qu'il y a 3 notifications
   - ✅ Chaque notification correspond à un cas de test différent

### Résultat Attendu

Une notification par cas de test passé.

---

## Test 5 : Notification Non Lue

### Objectif

Vérifier que la notification apparaît comme non lue.

### Étapes

1. **Exécution**
   - Marquer un cas de test comme passé

2. **Vérification**
   - Se connecter en tant que responsable du projet
   - ✅ Badge de notification visible (nombre)
   - ✅ Notification marquée comme non lue
   - ✅ Indicateur visuel (gras, couleur, etc.)

3. **Marquer comme Lue**
   - Cliquer sur la notification
   - ✅ La notification est marquée comme lue
   - ✅ Le badge diminue

### Résultat Attendu

Le système de notifications fonctionne correctement.

---

## Test 6 : Contenu Détaillé

### Objectif

Vérifier que toutes les informations sont correctes dans la notification.

### Étapes

1. **Préparation**
   - Cas de test : "Test connexion utilisateur"
   - Tâche : "Tests d'authentification"
   - Exécuteur : "Jean Dupont"

2. **Exécution**
   - Marquer le cas de test comme passé

3. **Vérification Détaillée**
   - ✅ Titre : "Cas de test passé : CT-001" (ou numéro correct)
   - ✅ Message : "Le cas de test "Test connexion utilisateur" de la tâche "Tests d'authentification" a été marqué comme passé par Jean Dupont."
   - ✅ Type : CAS_TEST_PASSE
   - ✅ Lien vers le cas de test (si implémenté)

### Résultat Attendu

Toutes les informations sont présentes et correctes.

---

## Checklist Complète

### Fonctionnalité

- [ ] Notification créée quand cas de test passé
- [ ] Notification envoyée au responsable du projet
- [ ] Pas d'auto-notification
- [ ] Pas d'erreur si pas de responsable
- [ ] Une notification par cas de test

### Contenu

- [ ] Titre correct avec numéro du cas
- [ ] Message contient nom du cas de test
- [ ] Message contient nom de la tâche
- [ ] Message contient nom de l'exécuteur
- [ ] Type de notification correct

### Interface

- [ ] Notification visible dans le centre de notifications
- [ ] Badge de notification mis à jour
- [ ] Notification marquée comme non lue
- [ ] Possibilité de marquer comme lue
- [ ] Icône appropriée (si implémentée)

### Cas Limites

- [ ] Projet sans responsable : pas d'erreur
- [ ] Responsable exécute : pas d'auto-notification
- [ ] Plusieurs cas de test : plusieurs notifications
- [ ] Cas de test échoué : pas de notification (normal)

---

## Commandes de Vérification

### Vérifier les Notifications Créées

```python
from core.models import NotificationEtape

# Toutes les notifications de cas de test passé
notifications = NotificationEtape.objects.filter(type_notification='CAS_TEST_PASSE')
print(f"Total : {notifications.count()}")

# Notifications non lues
non_lues = notifications.filter(lue=False)
print(f"Non lues : {non_lues.count()}")

# Détails
for notif in notifications:
    print(f"{notif.titre} → {notif.destinataire.get_full_name()}")
```

### Vérifier les Notifications d'un Utilisateur

```python
from core.models import Utilisateur, NotificationEtape

user = Utilisateur.objects.get(username='responsable')
notifications = NotificationEtape.objects.filter(
    destinataire=user,
    type_notification='CAS_TEST_PASSE'
)

for notif in notifications:
    print(f"[{'✓' if notif.lue else ' '}] {notif.titre}")
    print(f"    {notif.message}")
    print(f"    Créée le : {notif.date_creation}")
```

---

## Problèmes Potentiels et Solutions

### Problème : Pas de Notification Créée

**Solutions** :
1. Vérifier que la migration est appliquée
2. Vérifier que le projet a un responsable principal
3. Vérifier que l'exécuteur n'est pas le responsable
4. Vérifier les logs pour les erreurs

### Problème : Notification Créée Mais Pas Visible

**Solutions** :
1. Vérifier que l'interface de notifications fonctionne
2. Rafraîchir la page
3. Vérifier les filtres de notifications
4. Vérifier que la notification n'est pas marquée comme lue

### Problème : Erreur lors de l'Exécution

**Solutions** :
1. Vérifier que `NotificationEtape` est importé
2. Vérifier que le champ `cas_test` existe dans le modèle
3. Vérifier les permissions de la base de données

---

## Résultats Attendus

| Test | Statut | Notes |
|------|--------|-------|
| Test 1 : Notification envoyée | ⏳ | À tester |
| Test 2 : Pas d'auto-notification | ⏳ | À tester |
| Test 3 : Projet sans responsable | ⏳ | À tester |
| Test 4 : Plusieurs cas de test | ⏳ | À tester |
| Test 5 : Notification non lue | ⏳ | À tester |
| Test 6 : Contenu détaillé | ⏳ | À tester |

---

## Conclusion

Ces tests garantissent que le système de notification pour les cas de test passés fonctionne correctement et que le responsable du projet est bien informé de l'avancement des tests.
