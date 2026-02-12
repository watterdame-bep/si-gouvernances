# Guide de Test : Correction Erreur 500 - Détails Cas de Test

## 🎯 Objectif du Test

Vérifier que le bouton "Voir détails" d'un cas de test fonctionne correctement sans générer d'erreur 500.

## ✅ Prérequis

- Avoir un projet avec une étape Tests
- Avoir au moins une tâche dans l'étape Tests
- Avoir au moins un cas de test créé pour cette tâche
- Être connecté avec un compte ayant accès au projet

## 📋 Scénario de Test

### Étape 1 : Accéder à l'Interface Cas de Test

1. Connectez-vous à l'application
2. Accédez à un projet
3. Cliquez sur l'étape "Tests"
4. Cliquez sur "Tâches de l'Étape"
5. Cliquez sur l'icône fiole (🧪) d'une tâche pour accéder aux cas de test

**Résultat attendu** : L'interface "Gestion des Cas de Test" s'affiche

### Étape 2 : Tester le Bouton "Voir Détails"

1. Dans la liste des cas de test, repérez un cas de test
2. Dans la colonne "Actions", cliquez sur l'icône œil (👁️) "Voir détails"

**Résultat attendu** :
- ✅ Aucune erreur 500 dans la console du navigateur
- ✅ Une modale s'ouvre avec le titre "Détails du Cas de Test"
- ✅ Un indicateur de chargement apparaît brièvement

### Étape 3 : Vérifier le Contenu de la Modale

Une fois la modale chargée, vérifiez que les informations suivantes s'affichent :

**Informations de base** :
- ✅ Numéro du cas (ex: CT-001)
- ✅ Nom du cas de test
- ✅ Badge de statut (En Attente, En Cours, Passé, Échec, Bloqué)
- ✅ Badge de priorité (Critique, Haute, Moyenne, Basse)

**Détails du test** :
- ✅ Description
- ✅ Étapes d'exécution
- ✅ Résultats attendus
- ✅ Données d'entrée (si renseignées)
- ✅ Préconditions (si renseignées)

**Résultats (si le cas a été exécuté)** :
- ✅ Résultats obtenus
- ✅ Date d'exécution
- ✅ Nom de l'exécuteur

**Métadonnées** :
- ✅ Date de création
- ✅ Nom du créateur

### Étape 4 : Fermer la Modale

1. Cliquez sur le bouton "Fermer" en bas de la modale
   OU
2. Cliquez sur le X en haut à droite
   OU
3. Appuyez sur la touche Échap

**Résultat attendu** : La modale se ferme correctement

### Étape 5 : Test avec Différents Statuts

Répétez les étapes 2-4 avec des cas de test ayant différents statuts :
- ✅ Cas en attente
- ✅ Cas en cours
- ✅ Cas passé (avec résultats obtenus)
- ✅ Cas échoué (avec résultats obtenus)

## 🔍 Vérifications Techniques

### Console du Navigateur (F12)

Ouvrez la console du navigateur et vérifiez :

**Avant la correction** (ne devrait plus se produire) :
- ❌ `Failed to load resource: the server responded with a status of 500`
- ❌ `GET .../cas-tests/.../details/ 500 (Internal Server Error)`

**Après la correction** :
- ✅ `GET .../cas-tests/.../details/ 200 (OK)`
- ✅ Aucune erreur JavaScript
- ✅ Réponse JSON valide

### Onglet Réseau (Network)

1. Ouvrez l'onglet Réseau (F12 > Network)
2. Cliquez sur "Voir détails" d'un cas de test
3. Cherchez la requête vers `.../details/`

**Vérifications** :
- ✅ Status Code : 200 OK (pas 500)
- ✅ Response Type : application/json
- ✅ Response contient `"success": true`
- ✅ Response contient l'objet `"cas"` avec toutes les données

## 🧪 Tests de Permissions

Testez avec différents types d'utilisateurs :

### Super Admin
- ✅ Peut voir les détails de tous les cas de test

### Membre de l'Équipe du Projet
- ✅ Peut voir les détails des cas de test du projet

### Créateur du Projet
- ✅ Peut voir les détails des cas de test de son projet

### Utilisateur Sans Accès
- ✅ Reçoit un message "Permissions insuffisantes"

## ❌ Problèmes Potentiels

Si la modale ne s'ouvre pas :
1. Vérifiez la console pour des erreurs JavaScript
2. Vérifiez que l'URL de la requête est correcte
3. Vérifiez que le CSRF token est présent

Si une erreur 500 persiste :
1. Vérifiez que `core/views_tests.py` a été correctement modifié
2. Vérifiez qu'il n'y a qu'une seule fonction `details_cas_test_view`
3. Redémarrez le serveur Django

## ✅ Critères de Succès

Le test est réussi si :
- ✅ Aucune erreur 500 n'est générée
- ✅ La modale s'ouvre correctement
- ✅ Toutes les informations du cas de test s'affichent
- ✅ La modale se ferme correctement
- ✅ Les permissions sont respectées

## 📝 Rapport de Test

**Date du test** : _______________  
**Testeur** : _______________  
**Résultat** : ☐ Réussi ☐ Échoué  
**Commentaires** : _______________

---

## 📚 Documentation Associée

- `CORRECTION_ERREUR_500_DETAILS_CAS_TEST.md` - Documentation technique
- `RECAP_FINAL_CORRECTION_ERREUR_500.md` - Récapitulatif
- `SESSION_2026_02_11_CAS_TEST_COMPLET.md` - Vue d'ensemble complète

## 📅 Date

12 février 2026
