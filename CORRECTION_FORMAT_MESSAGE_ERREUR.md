# Correction : Format du Message d'Erreur

## Problème

Le message d'erreur s'affichait avec des crochets et guillemets, révélant le format JSON/Python :

```
["Impossible de terminer l'étape. Il reste 3 tâches non terminées..."]
```

Cela expose des détails techniques inutiles et peu professionnels.

## Cause

La `ValidationError` de Django est convertie en liste par défaut, et `str(e)` retourne la représentation brute avec crochets.

## Solution

Extraction propre du message d'erreur sans les caractères de formatage :

**Fichier** : `core/views.py` - Fonction `terminer_etape`

### Avant

```python
except ValidationError as e:
    error_message = str(e)  # Retourne ["message"]
    # ...
```

### Après

```python
except ValidationError as e:
    # Extraire le message proprement (sans crochets ni guillemets)
    if hasattr(e, 'message'):
        error_message = e.message
    elif hasattr(e, 'messages') and e.messages:
        error_message = e.messages[0] if isinstance(e.messages, list) else str(e.messages)
    else:
        error_message = str(e).strip("[]'\"")
    
    # Détecter si c'est une erreur de tâches non terminées
    if 'Impossible de terminer l\'étape' in error_message:
        return JsonResponse({
            'success': False,
            'message': error_message,
            'show_modal': True
        })
```

## Résultat

### Avant ❌
```
["Impossible de terminer l'étape. Il reste 3 tâches non terminées. Veuillez terminer toutes les tâches avant de clôturer l'étape."]
```

### Après ✅
```
Impossible de terminer l'étape. Il reste 3 tâches non terminées. Veuillez terminer toutes les tâches avant de clôturer l'étape.
```

## Avantages

1. **Sécurité** : Ne révèle pas le langage de programmation utilisé
2. **Professionnalisme** : Message propre et lisible
3. **Expérience utilisateur** : Texte naturel sans artefacts techniques
4. **Confidentialité** : Masque les détails d'implémentation

## Logique d'Extraction

La fonction essaie plusieurs méthodes pour extraire le message :

1. **`e.message`** : Attribut direct (si disponible)
2. **`e.messages[0]`** : Premier message de la liste
3. **`str(e).strip("[]'\"")`** : Conversion en chaîne et suppression des caractères parasites

Cette approche garantit un message propre dans tous les cas.

## Test

Pour vérifier :
1. Créer une étape avec des tâches non terminées
2. Tenter de terminer l'étape
3. ✅ Le message dans la modale ne contient pas de crochets `[]`
4. ✅ Le message ne contient pas de guillemets `"` ou `'`
5. ✅ Le texte est propre et naturel

## Fichier Modifié

- `core/views.py` - Fonction `terminer_etape` : Extraction propre du message d'erreur

## Date

12 février 2026
