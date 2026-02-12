# Simplification du Message d'Erreur - Tâches Non Terminées

## Problème

Le message d'erreur listait toutes les tâches non terminées, ce qui pouvait rendre la modale très longue :

```
Impossible de terminer l'étape. Les tâches suivantes ne sont pas terminées : 
Tâche 1, Tâche 2, Tâche 3, Tâche 4, Tâche 5, Tâche 6...
```

## Solution

Le message a été simplifié pour afficher seulement le nombre de tâches non terminées :

```
Impossible de terminer l'étape. Il reste 6 tâches non terminées. 
Veuillez terminer toutes les tâches avant de clôturer l'étape.
```

## Modification

**Fichier** : `core/models.py`  
**Méthode** : `EtapeProjet.terminer_etape()`

### Avant

```python
taches_non_terminees = self.taches_etape.exclude(statut='TERMINEE')
if taches_non_terminees.exists():
    noms_taches = list(taches_non_terminees.values_list('nom', flat=True))
    raise ValidationError(
        f'Impossible de terminer l\'étape. Les tâches suivantes ne sont pas terminées : {", ".join(noms_taches)}'
    )
```

### Après

```python
taches_non_terminees = self.taches_etape.exclude(statut='TERMINEE')
if taches_non_terminees.exists():
    nombre_taches = taches_non_terminees.count()
    raise ValidationError(
        f'Impossible de terminer l\'étape. Il reste {nombre_taches} tâche{"s" if nombre_taches > 1 else ""} non terminée{"s" if nombre_taches > 1 else ""}. Veuillez terminer toutes les tâches avant de clôturer l\'étape.'
    )
```

## Avantages

1. **Message plus court** : La modale reste compacte même avec beaucoup de tâches
2. **Information claire** : L'utilisateur sait combien de tâches restent à terminer
3. **Grammaire correcte** : Gestion du singulier/pluriel automatique
4. **Meilleure UX** : Pas de liste interminable dans la modale

## Exemples de Messages

### 1 tâche non terminée
```
Impossible de terminer l'étape. Il reste 1 tâche non terminée. 
Veuillez terminer toutes les tâches avant de clôturer l'étape.
```

### Plusieurs tâches non terminées
```
Impossible de terminer l'étape. Il reste 5 tâches non terminées. 
Veuillez terminer toutes les tâches avant de clôturer l'étape.
```

## Affichage dans la Modale

```
┌─────────────────────────────────────┐
│         ⚠️ (icône rouge)            │
│                                     │
│  Impossible de terminer l'étape     │
│                                     │
│  Impossible de terminer l'étape.    │
│  Il reste 3 tâches non terminées.   │
│  Veuillez terminer toutes les       │
│  tâches avant de clôturer l'étape.  │
│                                     │
│         [✕ Fermer]                  │
└─────────────────────────────────────┘
```

## Test

Pour tester :
1. Créer une étape avec plusieurs tâches (ex: 5 tâches)
2. Laisser au moins 2 tâches non terminées
3. Tenter de terminer l'étape
4. ✅ Le message affiche "Il reste 2 tâches non terminées"
5. ✅ La modale reste compacte et lisible

## Fichier Modifié

- `core/models.py` - Méthode `EtapeProjet.terminer_etape()`

## Date

12 février 2026
