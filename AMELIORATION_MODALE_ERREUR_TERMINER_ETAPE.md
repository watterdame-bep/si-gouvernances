# Amélioration : Modale d'Erreur pour Terminer Étape

## Problème Initial

Lorsqu'un utilisateur tentait de terminer une étape avec des tâches non terminées, l'erreur s'affichait dans un simple `alert()` JavaScript :

```
Erreur: ["Impossible de terminer l'étape. Les tâches suivantes ne sont pas terminées : Etape de test"]
```

Cette présentation était peu professionnelle et difficile à lire.

## Solution Implémentée

### 1. Modification de la Vue Backend

**Fichier** : `core/views.py` - Fonction `terminer_etape`

**Changement** : Détection spécifique des erreurs de tâches non terminées pour activer l'affichage en modale.

```python
except ValidationError as e:
    error_message = str(e)
    # Détecter si c'est une erreur de tâches non terminées
    if 'Impossible de terminer l\'étape' in error_message or 'ne sont pas terminées' in error_message:
        return JsonResponse({
            'success': False, 
            'error': error_message,
            'message': error_message,
            'show_modal': True  # Active l'affichage en modale
        })
    return JsonResponse({'success': False, 'error': error_message})
```

### 2. Amélioration de la Fonction JavaScript

**Fichier** : `templates/core/gestion_etapes.html` - Fonction `afficherModalErreur`

**Changements** :
- Ajout d'un paramètre `titre` pour personnaliser le titre de la modale
- Remplacement du titre fixe "Projet non démarré" par un titre dynamique
- Ajout d'un élément `<h3 id="titreErreurProjet">` pour mettre à jour le titre

**Avant** :
```javascript
function afficherModalErreur(message) {
    // ...
    <h3 class="...">Projet non démarré</h3>
    // ...
}
```

**Après** :
```javascript
function afficherModalErreur(message, titre = 'Erreur') {
    // ...
    <h3 id="titreErreurProjet" class="...">Erreur</h3>
    // ...
    document.getElementById('titreErreurProjet').textContent = titre;
    document.getElementById('messageErreurProjet').textContent = message;
    // ...
}
```

### 3. Mise à Jour de l'Appel

**Fichier** : `templates/core/gestion_etapes.html` - Fonction `confirmerTerminerEtape`

```javascript
if (data.show_modal) {
    afficherModalErreur(data.message || data.error, 'Impossible de terminer l\'étape');
} else {
    alert('Erreur: ' + data.error);
}
```

## Résultat

### Avant
- ❌ Message d'erreur dans un `alert()` JavaScript
- ❌ Format peu lisible avec des crochets et guillemets
- ❌ Pas de contexte visuel

### Après
- ✅ Modale professionnelle avec icône d'avertissement
- ✅ Titre clair : "Impossible de terminer l'étape"
- ✅ Message formaté et lisible
- ✅ Bouton "Fermer" avec icône
- ✅ Design cohérent avec le reste de l'application

## Exemple d'Affichage

Lorsqu'un utilisateur tente de terminer une étape avec des tâches non terminées :

**Modale affichée** :
```
┌─────────────────────────────────────┐
│         ⚠️ (icône rouge)            │
│                                     │
│  Impossible de terminer l'étape     │
│                                     │
│  Impossible de terminer l'étape.    │
│  Les tâches suivantes ne sont pas   │
│  terminées : Etape de test          │
│                                     │
│         [✕ Fermer]                  │
└─────────────────────────────────────┘
```

## Cas d'Usage

Cette amélioration s'applique à toutes les erreurs de validation lors de la terminaison d'une étape :

1. **Tâches non terminées** ✅
   - Message clair listant les tâches concernées
   - Modale avec titre explicite

2. **Projet non démarré** ✅
   - Déjà géré avec `show_modal: True`
   - Utilise la même modale

3. **Autres erreurs de validation**
   - Affichées en `alert()` par défaut
   - Peuvent être converties en modale si nécessaire

## Extensibilité

La fonction `afficherModalErreur` est maintenant générique et peut être utilisée pour d'autres types d'erreurs :

```javascript
// Exemple d'utilisation
afficherModalErreur('Message d\'erreur', 'Titre personnalisé');

// Avec titre par défaut
afficherModalErreur('Message d\'erreur'); // Titre = "Erreur"
```

## Fichiers Modifiés

1. **`core/views.py`**
   - Fonction `terminer_etape` : Détection des erreurs de tâches non terminées

2. **`templates/core/gestion_etapes.html`**
   - Fonction `afficherModalErreur` : Ajout du paramètre `titre`
   - Fonction `confirmerTerminerEtape` : Passage du titre personnalisé

## Test de Validation

### Scénario de Test

1. Créer un projet avec une étape en cours
2. Ajouter des tâches à l'étape
3. Laisser au moins une tâche non terminée
4. Tenter de terminer l'étape

**Résultat attendu** :
- ✅ Une modale s'affiche (pas un `alert()`)
- ✅ Le titre est "Impossible de terminer l'étape"
- ✅ Le message liste les tâches non terminées
- ✅ Un bouton "Fermer" permet de fermer la modale
- ✅ La modale se ferme en cliquant à l'extérieur ou avec Échap

### Vérification Visuelle

- ✅ Icône d'avertissement rouge
- ✅ Titre en gras et centré
- ✅ Message en gris et centré
- ✅ Bouton rouge avec icône
- ✅ Animation d'apparition fluide
- ✅ Fond semi-transparent

## Avantages

1. **Expérience utilisateur améliorée**
   - Interface professionnelle et cohérente
   - Messages d'erreur clairs et lisibles

2. **Maintenabilité**
   - Fonction générique réutilisable
   - Code centralisé et facile à modifier

3. **Accessibilité**
   - Modale accessible au clavier (Échap pour fermer)
   - Contraste visuel approprié

4. **Cohérence**
   - Même style que les autres modales de l'application
   - Design uniforme

## Date

12 février 2026
