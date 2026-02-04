# Implémentation du Système de Rôles pour les Modules

## Résumé de l'implémentation

Le système de rôles pour les modules a été implémenté avec succès dans l'application SI-Gouvernance. Cette fonctionnalité permet d'assigner des rôles spécifiques aux membres de l'équipe pour chaque module d'un projet.

## Fonctionnalités implémentées

### 1. Système de rôles pour les modules

**Rôles disponibles :**
- **Responsable** : Peut créer des tâches, les assigner aux contributeurs, voir toutes les tâches du module
- **Contributeur** : Peut voir et terminer les tâches qui lui sont assignées

### 2. Interface de création de module mise à jour

**Nouvelles fonctionnalités dans le formulaire :**
- Sélection obligatoire d'un responsable du module
- Sélection optionnelle de contributeurs (sélection multiple)
- Validation que les utilisateurs sélectionnés font partie de l'équipe du projet
- Interface moderne avec icônes FontAwesome

### 3. Système de notifications

**Notifications par email :**
- Envoi automatique d'emails aux utilisateurs affectés à un module
- Contenu personnalisé selon le rôle (responsable/contributeur)
- Détails des permissions inclus dans l'email

**Notifications in-app :**
- Création de notifications dans l'application
- Modèle `NotificationModule` pour la traçabilité
- Stockage des données contextuelles en JSON

### 4. Système de permissions pour les tâches

**Nouvelles fonctions de permission :**
- `peut_creer_taches_module()` : Vérifie si un utilisateur peut créer des tâches dans un module
- `peut_assigner_taches_module()` : Vérifie si un utilisateur peut assigner des tâches
- `peut_terminer_tache_module()` : Vérifie si un utilisateur peut terminer une tâche

**Règles de permission :**
- Seuls les responsables du module peuvent créer des tâches
- Les responsables peuvent assigner des tâches aux contributeurs
- Les contributeurs ne peuvent terminer que les tâches qui leur sont assignées
- Les responsables peuvent terminer toutes les tâches du module

### 5. Audit et traçabilité

**Enregistrement des actions :**
- Création de module avec affectations
- Assignation de tâches avec rôle du créateur
- Notifications envoyées (email et in-app)

## Modèles de données

### AffectationModule (existant, utilisé)
```python
class AffectationModule(models.Model):
    module = models.ForeignKey(ModuleProjet, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    role_module = models.CharField(max_length=20, choices=ROLE_MODULE_CHOICES)
    peut_creer_taches = models.BooleanField(default=True)
    peut_voir_toutes_taches = models.BooleanField(default=False)
    # ... autres champs
```

### NotificationModule (nouveau)
```python
class NotificationModule(models.Model):
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    module = models.ForeignKey(ModuleProjet, on_delete=models.CASCADE)
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION_CHOICES)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lue = models.BooleanField(default=False)
    # ... autres champs
```

## Fichiers modifiés

### Templates
- `templates/core/creer_module.html` : Ajout du formulaire d'affectation des rôles

### Modèles
- `core/models.py` : Ajout du modèle `NotificationModule`

### Vues
- `core/views.py` : 
  - Mise à jour de `creer_module_view()` pour gérer les affectations
  - Mise à jour de `creer_tache_view()` pour les permissions par rôle

### Utilitaires
- `core/utils.py` : 
  - Nouvelles fonctions de permission pour les modules
  - Fonctions de notification (email et in-app)

## Migration de base de données

Une migration a été créée et appliquée :
- `core/migrations/0016_add_notification_module.py`

## Workflow d'utilisation

1. **Création d'un module :**
   - L'utilisateur accède à l'interface de création de module
   - Il sélectionne un responsable obligatoire
   - Il peut sélectionner des contributeurs optionnels
   - Le système crée le module et les affectations
   - Des notifications sont envoyées par email et créées dans l'app

2. **Création de tâches :**
   - Seuls les responsables du module peuvent créer des tâches
   - Ils peuvent assigner des tâches aux contributeurs du module
   - Le système vérifie les permissions avant la création

3. **Gestion des tâches :**
   - Les contributeurs voient seulement leurs tâches assignées
   - Les responsables voient toutes les tâches du module
   - Chacun peut terminer les tâches selon ses permissions

## Sécurité et validation

- Validation que les utilisateurs affectés font partie de l'équipe du projet
- Vérification des permissions à chaque action
- Audit complet de toutes les actions
- Gestion des erreurs avec messages utilisateur appropriés

## Tests recommandés

1. Créer un module avec un responsable et des contributeurs
2. Vérifier la réception des notifications
3. Tester la création de tâches avec différents rôles
4. Vérifier les permissions de visualisation et de modification des tâches
5. Tester les cas d'erreur (utilisateurs non autorisés, etc.)

## Prochaines étapes possibles

1. Interface de gestion des notifications in-app
2. Système de badges/compteurs pour les notifications non lues
3. Possibilité de modifier les rôles après création du module
4. Notifications push en temps réel
5. Rapports sur l'activité des modules par rôle