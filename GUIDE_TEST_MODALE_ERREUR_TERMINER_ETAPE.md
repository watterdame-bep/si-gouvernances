# Guide de Test : Modale d'Erreur Terminer Étape

## 🎯 Objectif du Test

Vérifier que lorsqu'un utilisateur tente de terminer une étape avec des tâches non terminées, une modale professionnelle s'affiche au lieu d'un simple `alert()` JavaScript.

## ✅ Prérequis

- Avoir un projet en cours
- Avoir au moins une étape en cours (ex: Analyse, Conception, Tests, etc.)
- Avoir les permissions pour terminer une étape (Super Admin, Créateur du projet, ou Responsable principal)

## 📋 Scénario de Test Principal

### Étape 1 : Préparer l'Environnement

1. Connectez-vous à l'application
2. Accédez à un projet en cours
3. Cliquez sur "Gestion des Étapes"
4. Identifiez l'étape en cours (badge bleu "En cours")

**Résultat attendu** : Vous voyez l'étape en cours avec un bouton "Terminer l'étape"

### Étape 2 : Créer des Tâches Non Terminées

1. Cliquez sur "Tâches de l'Étape" pour l'étape en cours
2. Créez au moins 2 tâches pour cette étape
3. Terminez seulement 1 tâche (laissez au moins 1 tâche non terminée)
4. Retournez à "Gestion des Étapes"

**Résultat attendu** : L'étape a des tâches, mais toutes ne sont pas terminées

### Étape 3 : Tenter de Terminer l'Étape

1. Dans "Gestion des Étapes", cliquez sur le bouton "Terminer l'étape"
2. Une modale de confirmation s'affiche
3. Lisez le message de confirmation
4. Cliquez sur "Confirmer"

**Résultat attendu** : 
- ✅ Une modale d'erreur s'affiche (PAS un `alert()` JavaScript)
- ✅ La modale a un fond semi-transparent
- ✅ La modale de confirmation se ferme

### Étape 4 : Vérifier le Contenu de la Modale

**Éléments visuels à vérifier** :

1. **Icône d'avertissement**
   - ✅ Icône triangle avec point d'exclamation (⚠️)
   - ✅ Couleur rouge
   - ✅ Fond rouge clair (cercle)
   - ✅ Centré en haut de la modale

2. **Titre**
   - ✅ Texte : "Impossible de terminer l'étape"
   - ✅ Police en gras
   - ✅ Couleur noire
   - ✅ Centré

3. **Message d'erreur**
   - ✅ Commence par "Impossible de terminer l'étape."
   - ✅ Liste les tâches non terminées
   - ✅ Format : "Les tâches suivantes ne sont pas terminées : [nom tâche 1], [nom tâche 2]"
   - ✅ Couleur grise
   - ✅ Centré
   - ✅ Lisible (pas de crochets ou guillemets parasites)

4. **Bouton Fermer**
   - ✅ Texte : "Fermer" avec icône ✕
   - ✅ Couleur rouge
   - ✅ Centré en bas de la modale
   - ✅ Effet hover (devient plus foncé au survol)

### Étape 5 : Tester les Interactions

1. **Fermer avec le bouton**
   - Cliquez sur "Fermer"
   - ✅ La modale se ferme
   - ✅ Le scroll de la page est restauré

2. **Fermer en cliquant à l'extérieur**
   - Rouvrez la modale (répétez les étapes 3)
   - Cliquez sur le fond semi-transparent (à l'extérieur de la modale)
   - ✅ La modale se ferme

3. **Fermer avec la touche Échap**
   - Rouvrez la modale
   - Appuyez sur la touche Échap
   - ✅ La modale se ferme

### Étape 6 : Vérifier la Console

1. Ouvrez la console du navigateur (F12)
2. Répétez l'étape 3 (tenter de terminer l'étape)
3. Vérifiez la console

**Résultat attendu** :
- ✅ Aucune erreur JavaScript
- ✅ Aucun `alert()` n'est déclenché
- ✅ La requête POST retourne un statut 200
- ✅ La réponse JSON contient `"success": false` et `"show_modal": true`

## 🧪 Scénarios de Test Additionnels

### Test 2 : Toutes les Tâches Terminées

1. Terminez toutes les tâches de l'étape
2. Tentez de terminer l'étape
3. Cliquez sur "Confirmer"

**Résultat attendu** :
- ✅ Aucune modale d'erreur
- ✅ Message de succès (notification verte en haut à droite)
- ✅ L'étape passe à "Terminée"
- ✅ L'étape suivante est activée automatiquement
- ✅ La page se recharge

### Test 3 : Étape Sans Tâches

1. Créez une nouvelle étape sans tâches
2. Activez cette étape
3. Tentez de la terminer immédiatement

**Résultat attendu** :
- ✅ L'étape se termine sans erreur (pas de tâches = toutes terminées)
- ✅ Message de succès

### Test 4 : Projet Non Démarré

1. Créez un nouveau projet (statut "Brouillon")
2. Tentez de terminer une étape

**Résultat attendu** :
- ✅ Une modale d'erreur s'affiche
- ✅ Titre : "Projet non démarré" (ou similaire)
- ✅ Message expliquant qu'il faut d'abord démarrer le projet

## 🔍 Points de Vérification Détaillés

### Apparence de la Modale

| Élément | Vérification | ✓ |
|---------|--------------|---|
| Fond semi-transparent | Noir avec opacité 50% | ☐ |
| Modale centrée | Au centre de l'écran | ☐ |
| Largeur modale | Max 28rem (448px) | ☐ |
| Coins arrondis | Arrondis (rounded-xl) | ☐ |
| Ombre | Ombre portée visible | ☐ |
| Padding | Espacement intérieur confortable | ☐ |

### Contenu de la Modale

| Élément | Vérification | ✓ |
|---------|--------------|---|
| Icône | Triangle d'avertissement rouge | ☐ |
| Titre | "Impossible de terminer l'étape" | ☐ |
| Message | Liste des tâches non terminées | ☐ |
| Bouton | "Fermer" avec icône ✕ | ☐ |

### Comportement

| Action | Résultat attendu | ✓ |
|--------|------------------|---|
| Clic sur "Fermer" | Modale se ferme | ☐ |
| Clic à l'extérieur | Modale se ferme | ☐ |
| Touche Échap | Modale se ferme | ☐ |
| Scroll bloqué | Pendant que modale ouverte | ☐ |
| Scroll restauré | Après fermeture | ☐ |

## ❌ Problèmes Potentiels

### Problème 1 : `alert()` s'affiche au lieu de la modale

**Cause possible** : Le backend ne retourne pas `show_modal: True`

**Solution** :
1. Vérifiez que `core/views.py` a été modifié
2. Vérifiez la réponse JSON dans la console (F12 > Network)
3. Redémarrez le serveur Django

### Problème 2 : La modale ne s'affiche pas

**Cause possible** : Erreur JavaScript

**Solution** :
1. Ouvrez la console (F12)
2. Cherchez des erreurs JavaScript
3. Vérifiez que la fonction `afficherModalErreur` existe

### Problème 3 : Le titre reste "Projet non démarré"

**Cause possible** : Le template n'a pas été mis à jour

**Solution** :
1. Vérifiez que `templates/core/gestion_etapes.html` a été modifié
2. Videz le cache du navigateur (Ctrl+Shift+R)
3. Rechargez la page

### Problème 4 : Le message contient des crochets `["..."]`

**Cause possible** : Le message n'est pas correctement extrait

**Solution** :
1. Vérifiez que le backend retourne `error_message = str(e)`
2. Le problème devrait être résolu avec les modifications

## ✅ Critères de Succès

Le test est réussi si :

- ✅ Une modale professionnelle s'affiche (pas un `alert()`)
- ✅ Le titre est "Impossible de terminer l'étape"
- ✅ Le message liste clairement les tâches non terminées
- ✅ Le message est lisible (pas de crochets ou guillemets parasites)
- ✅ La modale peut être fermée de 3 façons (bouton, clic extérieur, Échap)
- ✅ Aucune erreur dans la console
- ✅ Le design est cohérent avec le reste de l'application

## 📝 Rapport de Test

**Date du test** : _______________  
**Testeur** : _______________  
**Navigateur** : _______________  
**Résultat** : ☐ Réussi ☐ Échoué  

**Tâches non terminées testées** :
- Tâche 1 : _______________
- Tâche 2 : _______________

**Commentaires** : 
_______________________________________________
_______________________________________________

## 📚 Documentation Associée

- `AMELIORATION_MODALE_ERREUR_TERMINER_ETAPE.md` - Documentation technique

## 📅 Date

12 février 2026
