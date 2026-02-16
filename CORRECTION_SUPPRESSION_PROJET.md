# Correction: Suppression de Projet Bloquée par ActionAudit

## Problème Rencontré

Lors de la tentative de suppression d'un projet, l'erreur suivante apparaissait:

```
Erreur lors de la suppression : ("Cannot delete some instances of model 'Projet' 
because they are referenced through protected foreign keys: 'ActionAudit.projet'.", 
{<ActionAudit: 16/02/2026 10:56 - - Création de projet>, ...})
```

## Cause

Le modèle `ActionAudit` avait une clé étrangère vers `Projet` avec `on_delete=models.PROTECT`, ce qui empêchait la suppression d'un projet ayant des entrées d'audit associées.

```python
# AVANT (ligne 844 de core/models.py)
projet = models.ForeignKey(Projet, on_delete=models.PROTECT, null=True, blank=True, related_name='actions_audit')
```

## Solution Appliquée

Changement de `on_delete=models.PROTECT` vers `on_delete=models.SET_NULL` pour permettre la suppression du projet tout en conservant l'historique d'audit.

```python
# APRÈS (ligne 844 de core/models.py)
projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True, related_name='actions_audit')
```

## Avantages de cette Solution

1. **Suppression possible**: Les projets peuvent maintenant être supprimés sans erreur
2. **Conservation de l'audit**: L'historique d'audit est préservé pour la traçabilité
3. **Conformité**: Les audits restent accessibles même après suppression du projet
4. **Intégrité**: Le champ `projet` est déjà nullable, donc compatible avec SET_NULL

## Migration Créée

```bash
docker-compose exec web python manage.py makemigrations --name fix_audit_projet_deletion
docker-compose exec web python manage.py migrate
```

Fichier: `core/migrations/0046_fix_audit_projet_deletion.py`

## Test de Validation

Script de test créé: `test_suppression_projet.py`

Résultat du test:
```
✅ Projet supprimé avec succès!
✅ Audits conservés avec projet=NULL
✅ Confirmation: Le projet n'existe plus dans la base
```

## Comportement Après Correction

Quand un projet est supprimé:
- Le projet est supprimé de la base de données
- Les audits associés restent dans la base avec `projet=NULL`
- L'historique d'audit reste consultable pour la traçabilité
- Aucune perte de données d'audit

## Fichiers Modifiés

1. `core/models.py` - Ligne 844: Changement de PROTECT vers SET_NULL
2. `core/migrations/0046_fix_audit_projet_deletion.py` - Migration créée
3. `test_suppression_projet.py` - Script de test

## Date de Correction

16 février 2026

## Statut

✅ **RÉSOLU** - La suppression de projets fonctionne correctement
