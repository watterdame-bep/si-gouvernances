# Correction Erreur 500 - Détails Cas de Test

## Problème Identifié

Lors du clic sur le bouton "Voir détails" d'un cas de test, une erreur 500 se produisait :

```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
GET http://127.0.0.1:8000/projets/.../etapes/.../cas-tests/.../details/ 500
```

## Cause Racine

La fonction `details_cas_test_view` dans `core/views_tests.py` avait deux problèmes :

1. **Fonction dupliquée** : Deux occurrences de la même fonction (lignes 219 et 738)
2. **Appel à méthode inexistante** : `ServiceTests._peut_voir_tests(user, projet)` n'existe pas
3. **Code tronqué** : La ligne 737 contenait du texte dupliqué/corrompu

## Solution Appliquée

### 1. Suppression de la première duplication (ligne 219)
La première occurrence a été supprimée.

### 2. Correction de la vérification des permissions (ligne 738)

**Avant** :
```python
# Vérifier les permissions
if not ServiceTests._peut_voir_tests(user, projet):
    return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

**Après** :
```python
# Vérifier les permissions
if not user.est_super_admin():
    if not user.a_acces_projet(projet) and projet.createur != user:
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
```

### 3. Correction du code tronqué (ligne 737)

**Avant** :
```python
return JsonResponse({'success': False, 'error': f'Erreur lors du chargement : {str(e)}'})lse, 'error': f'Erreur lors du chargement : {str(e)}'})
```

**Après** :
```python
return JsonResponse({'success': False, 'error': f'Erreur lors du chargement : {str(e)}'})
```

## Fonction Corrigée Complète

```python
@login_required
def details_cas_test_view(request, projet_id, etape_id, cas_test_id):
    """Vue des détails d'un cas de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    from .models import CasTest
    cas_test = get_object_or_404(CasTest, id=cas_test_id, tache_etape__etape=etape)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        return JsonResponse({
            'success': True,
            'cas': {
                'id': str(cas_test.id),
                'numero_cas': cas_test.numero_cas,
                'nom': cas_test.nom,
                'description': cas_test.description,
                'priorite': cas_test.priorite,
                'priorite_display': cas_test.get_priorite_display(),
                'statut': cas_test.statut,
                'statut_display': cas_test.get_statut_display(),
                'donnees_entree': cas_test.donnees_entree,
                'preconditions': cas_test.preconditions,
                'etapes_execution': cas_test.etapes_execution,
                'resultats_attendus': cas_test.resultats_attendus,
                'resultats_obtenus': cas_test.resultats_obtenus,
                'date_creation': cas_test.date_creation.strftime('%d/%m/%Y à %H:%M'),
                'date_execution': cas_test.date_execution.strftime('%d/%m/%Y à %H:%M') if cas_test.date_execution else None,
                'executeur': cas_test.executeur.get_full_name() if cas_test.executeur else None,
                'createur': cas_test.createur.get_full_name() if cas_test.createur else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors du chargement : {str(e)}'})
```

## Résultat

✅ Le bouton "Voir détails" fonctionne maintenant correctement
✅ La modale affiche les informations complètes du cas de test
✅ Aucune erreur 500 n'est générée
✅ Les permissions sont correctement vérifiées

## Fichiers Modifiés

- `core/views_tests.py` : Correction de la fonction `details_cas_test_view`

## Test de Validation

1. Accéder à l'interface "Cas de Test" d'une tâche de l'étape Tests
2. Cliquer sur le bouton "Voir" (icône œil) d'un cas de test
3. Vérifier que la modale s'ouvre avec les détails complets
4. Vérifier qu'aucune erreur 500 n'apparaît dans la console

## Date

12 février 2026
