# Notification : Cas de Test Passé

## Contexte

Lorsqu'un cas de test est marqué comme passé, le responsable du projet doit être informé pour suivre l'avancement des tests.

## Fonctionnalité Implémentée

### Notification Automatique

Lorsqu'un cas de test est marqué comme **PASSÉ**, une notification est automatiquement envoyée au **responsable principal du projet**.

### Déclencheur

La notification est créée dans la méthode `marquer_comme_passe()` du modèle `CasTest`.

## Implémentation

### 1. Nouveau Type de Notification

**Fichier** : `core/models.py`

Ajout du type `CAS_TEST_PASSE` dans `NotificationEtape` :

```python
TYPE_NOTIFICATION_CHOICES = [
    ('ETAPE_TERMINEE', 'Étape terminée'),
    ('ETAPE_ACTIVEE', 'Étape activée'),
    ('MODULES_DISPONIBLES', 'Modules disponibles'),
    ('RETARD_ETAPE', 'Retard d\'étape'),
    ('CHANGEMENT_STATUT', 'Changement de statut'),
    ('CAS_TEST_PASSE', 'Cas de test passé'),  # ✨ NOUVEAU
]
```

### 2. Logique de Notification

**Fichier** : `core/models.py` - Méthode `CasTest.marquer_comme_passe()`

```python
def marquer_comme_passe(self, executeur, resultats_obtenus=""):
    """Marquer le cas comme passé"""
    self.statut = 'PASSE'
    self.executeur = executeur
    self.resultats_obtenus = resultats_obtenus
    self.date_execution = timezone.now()
    self.save()
    
    # Mettre à jour la progression de la tâche d'étape parente
    self.tache_etape.mettre_a_jour_progression_depuis_cas_tests()
    
    # Notifier le responsable du projet
    projet = self.tache_etape.etape.projet
    responsable_projet = projet.get_responsable_principal()
    
    if responsable_projet and responsable_projet != executeur:
        NotificationEtape.objects.create(
            destinataire=responsable_projet,
            etape=self.tache_etape.etape,
            cas_test=self,
            type_notification='CAS_TEST_PASSE',
            titre=f'Cas de test passé : {self.numero_cas}',
            message=f'Le cas de test "{self.nom}" de la tâche "{self.tache_etape.nom}" a été marqué comme passé par {executeur.get_full_name()}.'
        )
```

### 3. Migration

**Fichier** : `core/migrations/0033_add_cas_test_passe_notification.py`

Migration pour ajouter le nouveau type de notification dans la base de données.

## Conditions de Notification

### Notification Envoyée Si :

1. ✅ Le cas de test est marqué comme **PASSÉ**
2. ✅ Le projet a un **responsable principal** défini
3. ✅ Le responsable n'est **pas** l'exécuteur (pas d'auto-notification)

### Notification NON Envoyée Si :

1. ❌ Le projet n'a pas de responsable principal
2. ❌ Le responsable est l'exécuteur lui-même
3. ❌ Le cas de test est marqué comme **ÉCHOUÉ** (pas de notification pour les échecs)

## Contenu de la Notification

### Titre
```
Cas de test passé : {numero_cas}
```

**Exemple** : `Cas de test passé : CT-001`

### Message
```
Le cas de test "{nom}" de la tâche "{tache_nom}" a été marqué comme passé par {executeur}.
```

**Exemple** : 
```
Le cas de test "Test connexion utilisateur" de la tâche "Tests d'authentification" 
a été marqué comme passé par Jean Dupont.
```

### Métadonnées

- **Type** : `CAS_TEST_PASSE`
- **Destinataire** : Responsable principal du projet
- **Étape** : Étape TESTS concernée
- **Cas de test** : Référence au cas de test passé
- **Date** : Date de création automatique

## Flux de Notification

```
Utilisateur marque un cas de test comme passé
    ↓
Méthode marquer_comme_passe() appelée
    ↓
Statut mis à jour → PASSE
    ↓
Progression de la tâche mise à jour
    ↓
Vérification : Projet a un responsable ?
    ↓ Oui
Vérification : Responsable ≠ Exécuteur ?
    ↓ Oui
Création de la notification
    ↓
Notification envoyée au responsable du projet ✅
```

## Cas d'Usage

### Scénario 1 : QA Exécute un Test

```
1. QA marque un cas de test comme passé
2. Le responsable du projet reçoit une notification
3. Le responsable voit la progression des tests
4. Le responsable peut suivre l'avancement
```

### Scénario 2 : Responsable de Tâche Exécute son Test

```
1. Responsable de tâche marque son cas de test comme passé
2. Le responsable du projet reçoit une notification
3. Le responsable du projet est informé de l'avancement
```

### Scénario 3 : Responsable de Projet Exécute un Test

```
1. Responsable de projet marque un cas de test comme passé
2. Pas de notification (auto-notification évitée)
3. Le responsable est déjà au courant
```

## Interface de Notification

### Affichage dans l'Interface

La notification apparaît dans :
- Le centre de notifications (icône cloche)
- La liste des notifications de l'utilisateur
- Avec une icône spécifique pour les cas de test

### Icône Suggérée

- 🧪 Fiole (pour les tests)
- ✅ Check (pour le succès)
- 📊 Graphique (pour la progression)

### Couleur Suggérée

- **Vert** : Indique un succès (test passé)
- **Badge** : "Cas de test passé"

## Avantages

1. **Suivi en Temps Réel** : Le responsable est informé immédiatement
2. **Visibilité** : Meilleure visibilité sur l'avancement des tests
3. **Réactivité** : Permet une réaction rapide si nécessaire
4. **Traçabilité** : Historique des tests passés
5. **Communication** : Améliore la communication dans l'équipe

## Évolutions Possibles

### Notifications Supplémentaires

1. **Cas de test échoué** : Notifier en cas d'échec (priorité haute)
2. **Tous les cas passés** : Notifier quand tous les cas d'une tâche sont passés
3. **Taux de réussite** : Notifier quand un seuil est atteint (ex: 80% de réussite)
4. **Cas bloqué** : Notifier si un cas est bloqué trop longtemps

### Personnalisation

1. **Préférences** : Permettre au responsable de choisir les notifications
2. **Seuils** : Configurer des seuils de notification
3. **Groupement** : Grouper les notifications similaires
4. **Résumé** : Envoyer un résumé quotidien/hebdomadaire

## Tests Recommandés

### Test 1 : Notification Envoyée

1. Assigner un responsable principal à un projet
2. Se connecter avec un autre utilisateur (QA ou responsable de tâche)
3. Marquer un cas de test comme passé
4. Vérifier que le responsable du projet reçoit une notification
5. Vérifier le contenu de la notification

### Test 2 : Pas d'Auto-Notification

1. Se connecter en tant que responsable du projet
2. Marquer un cas de test comme passé
3. Vérifier qu'aucune notification n'est créée pour soi-même

### Test 3 : Projet Sans Responsable

1. Créer un projet sans responsable principal
2. Marquer un cas de test comme passé
3. Vérifier qu'aucune erreur ne se produit
4. Vérifier qu'aucune notification n'est créée

### Test 4 : Contenu de la Notification

1. Marquer un cas de test comme passé
2. Vérifier le titre de la notification
3. Vérifier le message de la notification
4. Vérifier que le numéro du cas et le nom de la tâche sont corrects

## Fichiers Modifiés

| Fichier | Modification | Statut |
|---------|--------------|--------|
| `core/models.py` | Ajout type `CAS_TEST_PASSE` | ✅ |
| `core/models.py` | Logique notification dans `marquer_comme_passe()` | ✅ |
| `core/migrations/0033_add_cas_test_passe_notification.py` | Migration | ✅ |

## Migration

### Appliquer la Migration

```bash
python manage.py migrate
```

### Vérifier la Migration

```bash
python manage.py showmigrations core
```

## Commandes de Test

### Créer une Notification de Test

```python
from core.models import CasTest, NotificationEtape

# Récupérer un cas de test
cas_test = CasTest.objects.first()

# Marquer comme passé (déclenche la notification)
cas_test.marquer_comme_passe(executeur=user, resultats_obtenus="Test réussi")

# Vérifier les notifications
notifications = NotificationEtape.objects.filter(type_notification='CAS_TEST_PASSE')
print(f"Notifications créées : {notifications.count()}")
```

### Vérifier les Notifications d'un Utilisateur

```python
from core.models import Utilisateur, NotificationEtape

# Récupérer un utilisateur
user = Utilisateur.objects.get(username='responsable')

# Voir ses notifications de cas de test
notifications = NotificationEtape.objects.filter(
    destinataire=user,
    type_notification='CAS_TEST_PASSE',
    lue=False
)

for notif in notifications:
    print(f"{notif.titre} - {notif.message}")
```

## Statut

✅ **Implémenté**
⏳ **Migration en attente**
⏳ **Tests en attente**

## Conclusion

Le responsable du projet est maintenant notifié automatiquement lorsqu'un cas de test est marqué comme passé, lui permettant de suivre en temps réel l'avancement des tests et la qualité du projet.
