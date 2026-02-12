# Guide de Test - Suppression Bouton Impression et Ajout Bouton Cas de Test

**Date**: 11 février 2026  
**Fonctionnalité**: Suppression du bouton impression pour tâches terminées + Ajout bouton Cas de Test

## Prérequis

1. Serveur Django démarré: `python manage.py runserver`
2. Base de données avec:
   - Un projet créé
   - Une étape de type "Tests" avec au moins 2 tâches
   - Une tâche en cours avec des cas de test
   - Une tâche terminée avec des cas de test
3. Utilisateur connecté avec accès au projet

---

## Test 1: Vérification Tâche en Cours (2 minutes)

### Objectif
Vérifier que le bouton "Cas de Test" est visible pour une tâche en cours.

### Étapes

1. **Accéder à l'étape Tests**
   - Aller dans un projet
   - Cliquer sur l'étape "Tests"
   - Vous êtes maintenant dans "Gestion des Tâches de l'Étape"

2. **Localiser une tâche en cours**
   - Trouver une tâche avec statut "En cours" ou "En attente"
   - Observer la colonne "Actions"

3. **Vérifier les boutons visibles**
   - ✅ Bouton Modifier (✏️) doit être visible
   - ✅ Bouton Cas de Test (🧪 fiole violette) doit être visible
   - ✅ Bouton Terminer (✓ vert) doit être visible
   - ❌ Bouton Imprimer (🖨️) ne doit PAS être visible

4. **Tester l'accès aux cas de test**
   - Cliquer sur l'icône fiole (🧪)
   - Vérifier que l'interface "Cas de Test" s'ouvre
   - Vérifier que le bouton "Nouveau Cas" est visible
   - Retourner à la liste des tâches

### Résultat Attendu
✅ Le bouton "Cas de Test" (🧪) est visible  
✅ L'accès aux cas de test fonctionne  
✅ Le bouton "Nouveau Cas" est visible (tâche en cours)

---

## Test 2: Vérification Tâche Terminée (3 minutes)

### Objectif
Vérifier que le bouton "Imprimer" a été supprimé et que le bouton "Cas de Test" est maintenant visible.

### Étapes

1. **Localiser une tâche terminée**
   - Dans la même interface "Gestion des Tâches de l'Étape Tests"
   - Trouver une tâche avec statut "Terminée" (badge vert)
   - Observer la colonne "Actions"

2. **Vérifier les boutons visibles**
   - ✅ Bouton Cas de Test (🧪 fiole violette) doit être visible (NOUVEAU)
   - ✅ Badge "Terminée" (vert avec ✓) doit être visible
   - ❌ Bouton Imprimer (🖨️) ne doit PAS être visible (SUPPRIMÉ)
   - ❌ Bouton Modifier ne doit PAS être visible
   - ❌ Bouton Terminer ne doit PAS être visible

3. **Tester l'accès aux cas de test**
   - Cliquer sur l'icône fiole (🧪)
   - Vérifier que l'interface "Cas de Test" s'ouvre
   - Vérifier que les cas de test existants sont affichés
   - Vérifier que le bouton "Nouveau Cas" n'est PAS visible (tâche terminée)

4. **Vérifier la consultation**
   - Cliquer sur "Voir détails" (👁️) d'un cas de test
   - Vérifier que la modale s'ouvre avec tous les détails
   - Vérifier que les résultats obtenus sont affichés
   - Fermer la modale

5. **Retourner à la liste**
   - Cliquer sur "Retour"
   - Vérifier le retour à la liste des tâches

### Résultat Attendu
✅ Le bouton "Cas de Test" (🧪) est visible pour la tâche terminée  
✅ Le bouton "Imprimer" (🖨️) a été supprimé  
✅ L'accès aux cas de test fonctionne  
✅ Le bouton "Nouveau Cas" n'est PAS visible (tâche terminée)  
✅ La consultation des cas existants fonctionne

---

## Test 3: Comparaison Avant/Après (2 minutes)

### Objectif
Comparer visuellement l'interface avant et après la modification.

### Étapes

1. **Observer l'interface**
   - Regarder la liste des tâches de l'étape Tests
   - Comparer les boutons entre tâches en cours et terminées

2. **Vérifier la cohérence**
   - Les deux types de tâches ont maintenant le bouton "Cas de Test" (🧪)
   - Seul le badge "Terminée" différencie visuellement les tâches terminées
   - L'interface est plus cohérente et épurée

### Résultat Attendu
✅ Interface plus cohérente  
✅ Même bouton "Cas de Test" pour tous les statuts  
✅ Moins de boutons = interface plus claire

---

## Test 4: Workflow Complet (5 minutes)

### Objectif
Tester le workflow complet de création, exécution et consultation des cas de test.

### Étapes

1. **Créer une nouvelle tâche de test**
   - Cliquer sur "Nouvelle Tâche"
   - Remplir le formulaire
   - Créer la tâche

2. **Ajouter des cas de test**
   - Cliquer sur l'icône fiole (🧪) de la nouvelle tâche
   - Cliquer sur "Nouveau Cas"
   - Créer 2-3 cas de test

3. **Exécuter les cas de test**
   - Marquer un cas comme "Passé"
   - Marquer un cas comme "Échoué"
   - Laisser un cas "En attente"

4. **Terminer la tâche**
   - Retourner à la liste des tâches
   - Cliquer sur le bouton "Terminer" (✓)
   - Confirmer la terminaison

5. **Vérifier l'interface après terminaison**
   - Vérifier que le badge "Terminée" apparaît
   - Vérifier que le bouton "Cas de Test" (🧪) est toujours visible
   - Vérifier qu'il n'y a PAS de bouton "Imprimer"

6. **Consulter les cas de test de la tâche terminée**
   - Cliquer sur l'icône fiole (🧪)
   - Vérifier que tous les cas sont affichés
   - Vérifier que le bouton "Nouveau Cas" n'est PAS visible
   - Consulter les détails d'un cas exécuté
   - Vérifier que les résultats obtenus sont affichés

### Résultat Attendu
✅ Workflow complet fonctionne  
✅ Transition de "En cours" à "Terminée" correcte  
✅ Bouton "Cas de Test" reste visible après terminaison  
✅ Consultation des cas fonctionne pour tâche terminée  
✅ Ajout de cas bloqué pour tâche terminée

---

## Test 5: Autres Étapes (1 minute)

### Objectif
Vérifier que la modification n'affecte pas les autres types d'étapes.

### Étapes

1. **Accéder à une étape Développement**
   - Aller dans une étape de type "Développement"
   - Observer les boutons d'action des tâches
   - Vérifier qu'il n'y a pas de bouton "Cas de Test" (normal)

2. **Accéder à une étape Déploiement**
   - Aller dans une étape de type "Déploiement"
   - Observer les boutons d'action des tâches
   - Vérifier la présence du bouton "Déploiements" (🚀)

### Résultat Attendu
✅ Les autres étapes ne sont pas affectées  
✅ Seule l'étape Tests a le bouton "Cas de Test"

---

## Checklist de Validation Finale

### Interface Utilisateur
- [ ] Le bouton "Cas de Test" (🧪) est visible pour les tâches en cours
- [ ] Le bouton "Cas de Test" (🧪) est visible pour les tâches terminées
- [ ] Le bouton "Imprimer" (🖨️) n'est plus visible pour les tâches terminées
- [ ] Le badge "Terminée" est correctement affiché
- [ ] L'interface est cohérente et épurée

### Fonctionnalité
- [ ] L'accès aux cas de test fonctionne pour les tâches en cours
- [ ] L'accès aux cas de test fonctionne pour les tâches terminées
- [ ] Le bouton "Nouveau Cas" est visible pour les tâches en cours
- [ ] Le bouton "Nouveau Cas" est masqué pour les tâches terminées
- [ ] La consultation des cas existants fonctionne

### Workflow
- [ ] Création de tâche fonctionne
- [ ] Ajout de cas de test fonctionne
- [ ] Exécution de cas de test fonctionne
- [ ] Terminaison de tâche fonctionne
- [ ] Consultation après terminaison fonctionne

---

## Problèmes Connus et Solutions

### Problème: Le bouton "Imprimer" est toujours visible
**Solution**: Vider le cache du navigateur (Ctrl+F5) et recharger la page

### Problème: Le bouton "Cas de Test" n'apparaît pas pour les tâches terminées
**Solution**: Vérifier que le template a bien été modifié et que le serveur a été redémarré

### Problème: Erreur 404 lors du clic sur "Cas de Test"
**Solution**: Vérifier que l'URL `gestion_cas_tests_tache` est bien configurée dans `urls.py`

---

## Temps Estimé

- Test 1: 2 minutes
- Test 2: 3 minutes
- Test 3: 2 minutes
- Test 4: 5 minutes
- Test 5: 1 minute

**Total**: 13 minutes

---

## Conclusion

Ce guide couvre tous les aspects de la suppression du bouton impression et de l'ajout du bouton "Cas de Test" pour les tâches terminées. Suivez chaque test dans l'ordre pour une validation complète.

**Note**: Cette modification améliore la cohérence de l'interface et facilite l'accès aux cas de test, quel que soit le statut de la tâche.
