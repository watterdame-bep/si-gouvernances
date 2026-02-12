# Guide de Test - Blocage de l'Ajout de Cas de Test pour Tâche Terminée

**Date**: 11 février 2026  
**Fonctionnalité**: Empêcher l'ajout de cas de test à une tâche terminée

## Prérequis

1. Serveur Django démarré: `python manage.py runserver`
2. Base de données avec:
   - Un projet créé
   - Une étape de type "Tests" avec au moins 2 tâches
   - Des cas de test dans les tâches
3. Utilisateur connecté avec permissions (QA, Responsable projet, ou Responsable tâche)

---

## Scénario de Test 1: Tâche en Cours - Création Autorisée

### Objectif
Vérifier que le bouton "Nouveau Cas" est visible et fonctionnel pour une tâche en cours.

### Étapes

1. **Accéder à une tâche en cours**
   - Aller dans un projet
   - Cliquer sur l'étape "Tests"
   - Localiser une tâche avec statut "En cours" ou "En attente"
   - Cliquer sur le bouton "Cas de Test" ou l'icône fiole (🧪)

2. **Vérifier l'interface**
   - Vérifier que le bouton "Nouveau Cas" (violet) est visible en haut à droite
   - Vérifier que le bouton est actif (pas grisé)

3. **Créer un cas de test**
   - Cliquer sur "Nouveau Cas"
   - Remplir le formulaire:
     - Nom: "Test de connexion utilisateur"
     - Description: "Vérifier la connexion avec email valide"
     - Priorité: "Moyenne"
     - Étapes d'exécution: "1. Ouvrir la page\n2. Saisir email\n3. Cliquer connexion"
     - Résultats attendus: "Connexion réussie"
   - Cliquer sur "Créer"

4. **Vérifier la création**
   - Attendre le rechargement de la page
   - Vérifier qu'un message de succès s'affiche
   - Vérifier que le nouveau cas apparaît dans le tableau

### Résultat Attendu
✅ Le bouton "Nouveau Cas" est visible  
✅ La création de cas de test fonctionne  
✅ Le cas est ajouté au tableau

---

## Scénario de Test 2: Terminer une Tâche

### Objectif
Terminer une tâche de test pour préparer le test de blocage.

### Étapes

1. **Marquer tous les cas comme exécutés**
   - Dans l'interface "Cas de Test" de la tâche
   - Pour chaque cas de test non exécuté:
     - Cliquer sur le bouton vert (✓) "Marquer comme Passé"
     - Saisir des résultats obtenus
     - Confirmer

2. **Vérifier la progression**
   - Vérifier que tous les cas sont maintenant "Passé" ou "Échec"
   - Vérifier que la progression de la tâche est à 100%

3. **Retourner à la gestion des tâches**
   - Cliquer sur "Retour" pour revenir à la liste des tâches de l'étape
   - Localiser la tâche dans le tableau

4. **Terminer la tâche**
   - Cliquer sur le bouton "Terminer" de la tâche
   - Confirmer la terminaison
   - Vérifier que le statut passe à "Terminée" (badge vert)

### Résultat Attendu
✅ Tous les cas de test sont exécutés  
✅ La tâche passe au statut "Terminée"  
✅ Le badge de statut est vert

---

## Scénario de Test 3: Tâche Terminée - Création Bloquée

### Objectif
Vérifier que le bouton "Nouveau Cas" n'est plus visible pour une tâche terminée.

### Étapes

1. **Accéder à la tâche terminée**
   - Dans l'étape "Tests"
   - Localiser la tâche avec statut "Terminée"
   - Cliquer sur le bouton "Cas de Test" ou l'icône fiole (🧪)

2. **Vérifier l'interface**
   - Vérifier que le bouton "Nouveau Cas" n'est PAS visible
   - Vérifier que seul le bouton "Retour" est présent en haut à droite
   - Vérifier que les cas de test existants sont toujours affichés dans le tableau

3. **Vérifier la consultation**
   - Cliquer sur le bouton "Voir détails" (👁️) d'un cas de test
   - Vérifier que la modale s'ouvre correctement
   - Vérifier que tous les détails sont visibles
   - Fermer la modale

4. **Vérifier les statistiques**
   - Vérifier que les statistiques (Total, Passés, Échecs, etc.) sont toujours affichées
   - Vérifier que le pourcentage de réussite est calculé

### Résultat Attendu
✅ Le bouton "Nouveau Cas" n'est PAS visible  
✅ Les cas de test existants sont consultables  
✅ Les statistiques sont affichées  
✅ Aucune action de création n'est possible

---

## Scénario de Test 4: Tentative de Création via API (Test Avancé)

### Objectif
Vérifier que la création est bloquée au niveau backend même si on tente de contourner l'interface.

### Prérequis
- Outils de développement du navigateur (F12)
- Connaissance basique de JavaScript

### Étapes

1. **Ouvrir les outils de développement**
   - Appuyer sur F12
   - Aller dans l'onglet "Console"

2. **Récupérer les IDs nécessaires**
   - Dans l'interface "Cas de Test" de la tâche terminée
   - Regarder l'URL: `http://127.0.0.1:8000/projets/{projet_id}/etapes/{etape_id}/taches/{tache_id}/cas-tests/`
   - Noter les IDs

3. **Tenter une création via fetch**
   - Dans la console, exécuter:
   ```javascript
   fetch(window.location.pathname.replace('/cas-tests/', '/cas-tests/creer/'), {
       method: 'POST',
       headers: {
           'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
           'Content-Type': 'application/x-www-form-urlencoded',
       },
       body: 'nom=Test&description=Test&etapes_execution=Test&resultats_attendus=Test&priorite=MOYENNE'
   })
   .then(r => r.json())
   .then(data => console.log(data))
   ```

4. **Vérifier la réponse**
   - Observer la réponse dans la console
   - Vérifier qu'elle contient:
     ```json
     {
       "success": false,
       "error": "Impossible d'ajouter un cas de test à une tâche terminée"
     }
     ```

5. **Vérifier qu'aucun cas n'a été créé**
   - Recharger la page
   - Vérifier que le nombre de cas de test n'a pas changé

### Résultat Attendu
✅ La requête retourne une erreur  
✅ Le message d'erreur est explicite  
✅ Aucun cas de test n'est créé  
✅ La protection backend fonctionne

---

## Scénario de Test 5: Réouverture de Tâche

### Objectif
Vérifier que si une tâche est réouverte, la création de cas de test redevient possible.

### Étapes

1. **Accéder à la tâche terminée**
   - Dans l'étape "Tests"
   - Localiser la tâche avec statut "Terminée"

2. **Réouvrir la tâche** (si cette fonctionnalité existe)
   - Cliquer sur un bouton "Réouvrir" ou modifier le statut
   - Changer le statut de "Terminée" à "En cours"
   - Confirmer la modification

3. **Accéder aux cas de test**
   - Cliquer sur le bouton "Cas de Test"
   - Vérifier que le bouton "Nouveau Cas" est à nouveau visible

4. **Tester la création**
   - Cliquer sur "Nouveau Cas"
   - Créer un nouveau cas de test
   - Vérifier que la création réussit

### Résultat Attendu
✅ La tâche peut être réouverte  
✅ Le bouton "Nouveau Cas" redevient visible  
✅ La création de cas de test fonctionne à nouveau

---

## Scénario de Test 6: Permissions Multiples

### Objectif
Vérifier que le blocage s'applique à tous les utilisateurs, même les Super Admin.

### Étapes

1. **Tester avec QA**
   - Se connecter avec un compte QA
   - Accéder à une tâche terminée
   - Vérifier que le bouton "Nouveau Cas" n'est pas visible

2. **Tester avec Responsable Projet**
   - Se connecter avec le compte du responsable du projet
   - Accéder à une tâche terminée
   - Vérifier que le bouton "Nouveau Cas" n'est pas visible

3. **Tester avec Super Admin**
   - Se connecter avec un compte Super Admin
   - Accéder à une tâche terminée
   - Vérifier que le bouton "Nouveau Cas" n'est pas visible

### Résultat Attendu
✅ Le blocage s'applique à tous les utilisateurs  
✅ Même le Super Admin ne peut pas ajouter de cas  
✅ La règle métier est respectée pour tous

---

## Checklist de Validation Finale

### Interface Utilisateur
- [ ] Le bouton "Nouveau Cas" est visible pour les tâches en cours
- [ ] Le bouton "Nouveau Cas" est masqué pour les tâches terminées
- [ ] Les cas de test existants restent consultables
- [ ] Les statistiques sont toujours affichées
- [ ] Le bouton "Voir détails" fonctionne toujours

### Fonctionnalité
- [ ] La création de cas fonctionne pour les tâches en cours
- [ ] La création de cas est bloquée pour les tâches terminées
- [ ] Le message d'erreur backend est explicite
- [ ] La réouverture d'une tâche réactive la création

### Permissions
- [ ] Le blocage s'applique à tous les utilisateurs
- [ ] QA ne peut pas créer sur tâche terminée
- [ ] Responsable projet ne peut pas créer sur tâche terminée
- [ ] Super Admin ne peut pas créer sur tâche terminée

### Backend
- [ ] La protection backend fonctionne
- [ ] Les tentatives de contournement sont bloquées
- [ ] Le message d'erreur JSON est correct

---

## Problèmes Connus et Solutions

### Problème: Le bouton "Nouveau Cas" reste visible
**Solution**: Vérifier que le statut de la tâche est bien "TERMINEE" (en majuscules)

### Problème: La création fonctionne encore
**Solution**: Vider le cache du navigateur et recharger la page

### Problème: Erreur 500 lors de la tentative de création
**Solution**: Vérifier les logs Django pour identifier l'erreur exacte

---

## Temps Estimé

- Scénario 1: 3 minutes
- Scénario 2: 5 minutes
- Scénario 3: 2 minutes
- Scénario 4: 5 minutes (optionnel, pour utilisateurs avancés)
- Scénario 5: 3 minutes
- Scénario 6: 5 minutes

**Total**: 15-20 minutes (sans le scénario 4 optionnel)

---

## Conclusion

Ce guide couvre tous les aspects du blocage de l'ajout de cas de test pour les tâches terminées. Suivez chaque scénario dans l'ordre pour une validation complète de la fonctionnalité.
