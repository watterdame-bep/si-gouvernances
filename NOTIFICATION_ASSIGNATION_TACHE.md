# Notification d'assignation de tâche

## Fonctionnalité implémentée

Lorsqu'une tâche est assignée à un membre de l'équipe, ce membre reçoit maintenant une notification automatique.

## Modifications apportées

### 1. Méthode assigner_responsable - TacheModule (core/models.py)

Ajout de la création de notification lors de l'assignation:

```python
def assigner_responsable(self, responsable, utilisateur_assigneur):
    """Assigne un responsable à la tâche avec audit et notification"""
    ancien_responsable = self.responsable
    self.responsable = responsable
    self.save()
    
    # Créer une notification pour le nouveau responsable
    if responsable and responsable != utilisateur_assigneur:
        from .models import NotificationTache
        NotificationTache.objects.create(
            destinataire=responsable,
            tache=self,
            type_notification='ASSIGNATION',
            message=f'La tâche "{self.nom}" du module "{self.module.nom}" vous a été assignée...'
        )
    
    # Audit...
```

### 2. Méthode assigner_responsable - TacheEtape (core/models.py)

Même logique pour les tâches d'étape:

```python
def assigner_responsable(self, responsable, utilisateur_assigneur):
    """Assigne un responsable à la tâche avec audit et notification"""
    # ... même logique avec message adapté pour les étapes
```

## Types de tâches concernées

### 1. Tâches de module (TacheModule)
- Tâches créées dans un module de développement
- Message: "La tâche '[Nom]' du module '[Module]' vous a été assignée par [Assigneur]"

### 2. Tâches d'étape (TacheEtape)
- Tâches créées directement dans une étape
- Message: "La tâche '[Nom]' de l'étape '[Étape]' vous a été assignée par [Assigneur]"

## Comportement

### Quand une tâche est assignée:

1. ✅ Tâche assignée au responsable
2. ✅ Notification créée automatiquement avec:
   - Type: `ASSIGNATION`
   - Destinataire: Le membre assigné
   - Message: Description de la tâche et qui l'a assignée
3. ✅ Notification visible dans l'interface
4. ✅ Audit enregistré

### Cas particuliers:

- ❌ **Pas de notification** si l'utilisateur s'assigne lui-même la tâche
- ❌ **Pas de notification** si le responsable est `None`
- ✅ **Notification** dans tous les autres cas

## Contenu de la notification

### Pour une tâche de module:
**Message**: La tâche "[Nom de la tâche]" du module "[Nom du module]" vous a été assignée par [Nom de l'assigneur].

### Pour une tâche d'étape:
**Message**: La tâche "[Nom de la tâche]" de l'étape "[Nom de l'étape]" vous a été assignée par [Nom de l'assigneur].

## Qui peut assigner des tâches

1. **Administrateur** (est_super_admin)
2. **Créateur du projet**
3. **Responsable du projet**
4. **Responsable du module** (pour les tâches de module)
5. **Créateur de la tâche**

## Affichage de la notification

La notification s'affiche dans:
- ✅ Badge de notification (icône cloche)
- ✅ Dropdown des notifications
- ✅ Page complète des notifications

Clic sur la notification → Redirection vers la page de la tâche

## Modèle NotificationTache existant

Le modèle `NotificationTache` existe déjà avec les types:
- `ASSIGNATION` - Assignation de tâche ✅ (utilisé)
- `CHANGEMENT_STATUT` - Changement de statut
- `COMMENTAIRE` - Nouveau commentaire
- `MENTION` - Mention dans un commentaire
- `ECHEANCE_PROCHE` - Échéance proche

## Test de la fonctionnalité

### Étapes pour tester:

1. **Se connecter en tant qu'administrateur ou responsable**
   ```
   Email: jovi80@gmail.com
   Mot de passe: admin123
   ```

2. **Aller dans un projet avec des tâches**
   - Projet → Étapes → Tâches
   - OU Projet → Modules → Tâches

3. **Assigner une tâche à un membre**
   - Cliquer sur "Assigner" pour une tâche
   - Sélectionner un membre de l'équipe
   - Valider

4. **Se connecter avec le membre assigné**
   - Vérifier le badge de notification
   - Cliquer sur l'icône de notification
   - Voir la notification d'assignation

5. **Cliquer sur la notification**
   - Devrait rediriger vers la page de la tâche
   - La notification devrait être marquée comme lue

## Fichiers modifiés

- `core/models.py`:
  - Méthode `assigner_responsable()` de `TacheModule` (ligne ~1365)
  - Méthode `assigner_responsable()` de `TacheEtape` (ligne ~1536)

## Statut

✅ **Implémenté**  
✅ **Prêt pour test**  
⏳ **Nécessite redémarrage du serveur**

## Action requise

Redémarrer le serveur Django:
```bash
python manage.py runserver
```

## Notes importantes

- Les notifications utilisent le modèle `NotificationTache` existant
- Le type `ASSIGNATION` était déjà défini mais pas utilisé
- Pas besoin de migration car on utilise un modèle existant
- La notification n'est créée que si le responsable est différent de l'assigneur

---

**Date**: 2026-02-10  
**Fonctionnalité**: Notification d'assignation de tâche  
**Type**: Amélioration UX
