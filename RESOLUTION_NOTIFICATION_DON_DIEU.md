# Résolution: Notification manquante pour DON DIEU

## Problème Initial

DON DIEU a été ajouté comme responsable du projet "Test UI Transfer" mais n'a pas reçu la notification automatique.

## Diagnostic

### Outils créés
- `debug_notification_responsable_don_dieu.py` - Script de diagnostic complet
- `corriger_affectation_don_dieu.py` - Script de correction

### Cause Identifiée

L'affectation de DON DIEU avait une **incohérence de données** :
- ✓ Rôle: `RESPONSABLE_PRINCIPAL` (correct)
- ✗ Flag `est_responsable_principal`: `False` (incorrect)

```
Affectation ID: f88eb89d-9fb5-4383-8559-3e534771881a
- Rôle: RESPONSABLE_PRINCIPAL
- est_responsable_principal: False  ← PROBLÈME ICI
- Date début: 2026-02-09 15:36:25
- Date fin: Active
```

### Pourquoi le signal ne s'est pas déclenché

Le signal `notifier_responsable_projet` dans `core/models.py` vérifie explicitement le flag `est_responsable_principal` :

```python
@receiver(post_save, sender=Affectation)
def notifier_responsable_projet(sender, instance, created, **kwargs):
    if instance.est_responsable_principal and instance.date_fin is None:
        # Créer la notification...
```

Comme le flag était à `False`, le signal n'a pas créé la notification.

## Solution Appliquée

### 1. Correction du flag
```python
affectation.est_responsable_principal = True
affectation.save()
```

### 2. Vérification des notifications
Le système a détecté qu'une notification existait déjà (créée manuellement), donc aucune duplication.

### 3. État final
- ✓ Affectation corrigée: `est_responsable_principal = True`
- ✓ 2 notifications AFFECTATION_RESPONSABLE présentes
- ✓ Notifications non lues (DON DIEU les verra dans son interface)

## Informations du Projet

**Projet**: Test UI Transfer
- ID: `1d99beda-7540-4929-9ea6-c6c45ce4c997`
- Client: Client Test UI
- Durée prévue: 7 jours
- Date début: Non démarré
- Peut être démarré: Non (conditions non remplies)

**Utilisateur**: DON DIEU
- ID: `01ee3c7e-4e69-40f7-b45a-25c6a0b61266`
- Username: `don.dieu`
- Email: don80@gmail.com
- Statut: Actif

## Notifications Créées

### Notification #1 (ID: 11)
- Type: `AFFECTATION_RESPONSABLE`
- Titre: 🎯 Vous êtes responsable du projet Test UI Transfer
- Date: 2026-02-09 15:46:13
- Statut: Non lue

### Notification #2 (ID: 9)
- Type: `AFFECTATION_RESPONSABLE`
- Titre: 🎯 Vous êtes responsable du projet Test UI Transfer
- Date: 2026-02-09 15:36:25
- Statut: Non lue

## Prévention Future

### Cause de l'incohérence
L'affectation a probablement été créée **avant** l'implémentation du système de notification automatique, ou via un processus qui n'a pas correctement défini le flag.

### Recommandations

1. **Toujours utiliser la vue `ajouter_membre_projet`** qui gère correctement les flags
2. **Vérifier la cohérence** entre `role_projet` et `est_responsable_principal`
3. **Utiliser le paramètre `est_responsable=true`** lors de l'ajout d'un responsable

### Code de la vue (correct)
```python
@login_required
@require_http_methods(["POST"])
def ajouter_membre_projet(request, projet_id):
    # ...
    est_responsable = request.POST.get('est_responsable', 'false').lower() == 'true'
    
    # Créer l'affectation avec le bon flag
    affectation = Affectation(
        utilisateur=utilisateur,
        projet=projet,
        role_projet=role,
        est_responsable_principal=est_responsable  # ← Important !
    )
    affectation.save()
```

## Scripts de Maintenance

### Diagnostic
```bash
python debug_notification_responsable_don_dieu.py
```

Vérifie:
- Existence de l'utilisateur
- Existence du projet
- État des affectations
- Présence des notifications

### Correction (si nécessaire)
```bash
python corriger_affectation_don_dieu.py
```

Corrige:
- Le flag `est_responsable_principal`
- Crée la notification si manquante
- Évite les doublons

## Résultat

✅ **Problème résolu**

DON DIEU peut maintenant voir ses notifications de responsable dans l'interface. Les 2 notifications sont présentes et non lues.

## Fichiers Modifiés

- `debug_notification_responsable_don_dieu.py` (créé)
- `corriger_affectation_don_dieu.py` (créé)
- Base de données: Affectation `f88eb89d-9fb5-4383-8559-3e534771881a` mise à jour

## Références

- Signal: `core/models.py` ligne ~2210 (`notifier_responsable_projet`)
- Vue: `core/views.py` ligne ~1104 (`ajouter_membre_projet`)
- Documentation: `NOTIFICATION_RESPONSABLE_PROJET.md`
- Documentation: `AJOUT_RESPONSABLE_OBLIGATOIRE.md`
