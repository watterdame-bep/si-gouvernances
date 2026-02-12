# Guide de Test - Masquage des Boutons d'Action pour Cas de Test Exécutés

**Date**: 11 février 2026  
**Fonctionnalité**: Masquage des boutons d'action pour les cas de test déjà exécutés

## Prérequis

1. Serveur Django démarré: `python manage.py runserver`
2. Base de données avec:
   - Un projet créé
   - Une étape de type "Tests" avec des tâches
   - Au moins 2 cas de test dans une tâche (un non exécuté, un exécuté)
3. Utilisateur connecté avec permissions (QA, Responsable projet, ou Responsable tâche)

## Scénario de Test 1: Cas de Test Non Exécuté

### Objectif
Vérifier que tous les boutons d'action sont visibles pour un cas de test non exécuté.

### Étapes

1. **Accéder à l'interface Cas de Test**
   - Aller dans un projet
   - Cliquer sur l'étape "Tests"
   - Cliquer sur une tâche de test
   - Cliquer sur "Cas de Test" ou accéder via "Mes Tâches" → icône fiole (🧪)

2. **Vérifier l'affichage des boutons**
   - Localiser un cas de test avec statut "En Attente" ou "En Cours"
   - Dans la colonne "Actions", vérifier la présence de:
     - ✅ Bouton "Voir détails" (👁️ bleu)
     - ✅ Bouton "Marquer comme Passé" (✓ vert)
     - ✅ Bouton "Marquer comme Échoué" (✗ rouge)

3. **Tester le bouton "Voir détails"**
   - Cliquer sur l'icône œil (👁️)
   - Vérifier que la modale s'ouvre
   - Vérifier que les sections suivantes sont affichées:
     - Numéro du cas
     - Nom et description
     - Statut et priorité
     - Étapes d'exécution
     - Résultats attendus
     - Date de création et créateur
   - Vérifier que la section "Résultats obtenus" n'est PAS affichée (cas non exécuté)
   - Fermer la modale

### Résultat Attendu
✅ Les 3 boutons d'action sont visibles  
✅ La modale de détails s'ouvre correctement  
✅ Pas de section "Résultats obtenus" pour un cas non exécuté

---

## Scénario de Test 2: Exécution d'un Cas de Test

### Objectif
Exécuter un cas de test et vérifier que les boutons d'action disparaissent après exécution.

### Étapes

1. **Marquer un cas comme Passé**
   - Localiser un cas de test avec statut "En Attente"
   - Cliquer sur le bouton vert "Marquer comme Passé" (✓)
   - Vérifier que la modale d'exécution s'ouvre avec:
     - En-tête vert
     - Icône de succès (✓)
     - Message "Marquer ce cas de test comme réussi ?"
     - Champ "Résultats obtenus" (obligatoire)

2. **Saisir les résultats**
   - Dans le champ "Résultats obtenus", saisir:
     ```
     Test exécuté avec succès.
     - Connexion réussie
     - Redirection vers le dashboard
     - Aucune erreur détectée
     ```
   - Cliquer sur "Confirmer"

3. **Vérifier la mise à jour**
   - Attendre le rechargement de la page
   - Vérifier que le statut du cas est maintenant "Passé" (badge vert)
   - Vérifier que dans la colonne "Actions":
     - ✅ Bouton "Voir détails" (👁️) toujours visible
     - ❌ Bouton "Marquer comme Passé" (✓) disparu
     - ❌ Bouton "Marquer comme Échoué" (✗) disparu

### Résultat Attendu
✅ Le cas de test passe au statut "Passé"  
✅ Seul le bouton "Voir détails" reste visible  
✅ Les boutons d'action (✓ et ✗) ont disparu

---

## Scénario de Test 3: Consultation des Résultats

### Objectif
Vérifier que les résultats obtenus sont bien affichés dans la modale de détails.

### Étapes

1. **Ouvrir les détails d'un cas exécuté**
   - Localiser le cas de test marqué comme "Passé" dans le scénario précédent
   - Cliquer sur le bouton "Voir détails" (👁️)

2. **Vérifier le contenu de la modale**
   - Vérifier la présence de toutes les sections:
     - ✅ Numéro du cas et nom
     - ✅ Statut "Passé" (badge vert)
     - ✅ Priorité
     - ✅ Description
     - ✅ Étapes d'exécution
     - ✅ Résultats attendus
     - ✅ **Résultats obtenus** (nouvelle section)
     - ✅ Date de création
     - ✅ Date d'exécution
     - ✅ Nom de l'exécuteur

3. **Vérifier les résultats obtenus**
   - Localiser la section "Résultats obtenus" avec icône orange (📋)
   - Vérifier que le texte saisi précédemment est bien affiché:
     ```
     Test exécuté avec succès.
     - Connexion réussie
     - Redirection vers le dashboard
     - Aucune erreur détectée
     ```

4. **Vérifier les métadonnées d'exécution**
   - Vérifier que la date d'exécution est affichée (format: JJ/MM/AAAA à HH:MM)
   - Vérifier que le nom de l'exécuteur est affiché

### Résultat Attendu
✅ La section "Résultats obtenus" est affichée  
✅ Les résultats saisis sont correctement affichés  
✅ La date d'exécution et l'exécuteur sont visibles

---

## Scénario de Test 4: Cas de Test Échoué

### Objectif
Vérifier le comportement pour un cas de test marqué comme échoué.

### Étapes

1. **Marquer un cas comme Échoué**
   - Localiser un autre cas de test avec statut "En Attente"
   - Cliquer sur le bouton rouge "Marquer comme Échoué" (✗)
   - Vérifier que la modale d'exécution s'ouvre avec:
     - En-tête rouge
     - Icône d'échec (✗)
     - Message "Marquer ce cas de test comme échoué ?"

2. **Saisir les résultats d'échec**
   - Dans le champ "Résultats obtenus", saisir:
     ```
     Test échoué.
     - Erreur 500 lors de la connexion
     - Message d'erreur: "Invalid credentials"
     - Pas de redirection
     ```
   - Cliquer sur "Confirmer"

3. **Vérifier la mise à jour**
   - Attendre le rechargement de la page
   - Vérifier que le statut du cas est maintenant "Échec" (badge rouge)
   - Vérifier que dans la colonne "Actions":
     - ✅ Bouton "Voir détails" (👁️) toujours visible
     - ❌ Bouton "Marquer comme Passé" (✓) disparu
     - ❌ Bouton "Marquer comme Échoué" (✗) disparu

4. **Consulter les détails du cas échoué**
   - Cliquer sur "Voir détails" (👁️)
   - Vérifier que la section "Résultats obtenus" affiche bien les résultats d'échec
   - Vérifier que le statut "Échec" est affiché avec un badge rouge

### Résultat Attendu
✅ Le cas de test passe au statut "Échec"  
✅ Seul le bouton "Voir détails" reste visible  
✅ Les résultats d'échec sont correctement affichés dans la modale

---

## Scénario de Test 5: Notification au Responsable du Projet

### Objectif
Vérifier que le responsable du projet reçoit une notification quand un cas de test est marqué comme passé.

### Étapes

1. **Se connecter en tant que responsable du projet**
   - Se déconnecter de l'utilisateur actuel
   - Se connecter avec le compte du responsable du projet

2. **Vérifier les notifications**
   - Cliquer sur l'icône de notifications (🔔) dans la barre de navigation
   - Vérifier la présence d'une notification avec:
     - Titre: "Cas de test passé : [NUMERO_CAS]"
     - Message: "Le cas de test "[NOM]" de la tâche "[TACHE]" a été marqué comme passé par [EXECUTEUR]."
     - Type: Notification de cas de test (icône fiole 🧪)

3. **Cliquer sur la notification**
   - Cliquer sur la notification
   - Vérifier la redirection vers l'étape ou le projet concerné

### Résultat Attendu
✅ Le responsable du projet reçoit une notification  
✅ La notification contient les bonnes informations  
✅ La notification est cliquable et redirige correctement

---

## Scénario de Test 6: Permissions

### Objectif
Vérifier que seuls les utilisateurs autorisés peuvent voir et exécuter les cas de test.

### Étapes

1. **Tester avec un utilisateur QA**
   - Se connecter avec un compte QA
   - Accéder à l'interface Cas de Test
   - Vérifier que tous les boutons sont visibles (pour cas non exécutés)
   - ✅ Peut créer, exécuter et consulter les cas de test

2. **Tester avec le responsable du projet**
   - Se connecter avec le compte du responsable du projet
   - Accéder à l'interface Cas de Test
   - Vérifier que tous les boutons sont visibles (pour cas non exécutés)
   - ✅ Peut créer, exécuter et consulter les cas de test

3. **Tester avec le responsable de la tâche**
   - Se connecter avec le compte du responsable de la tâche
   - Accéder à l'interface Cas de Test
   - Vérifier que tous les boutons sont visibles (pour cas non exécutés)
   - ✅ Peut créer, exécuter et consulter les cas de test

4. **Tester avec un utilisateur sans permissions**
   - Se connecter avec un compte développeur non assigné au projet
   - Tenter d'accéder à l'interface Cas de Test
   - ❌ Devrait être redirigé avec un message d'erreur

### Résultat Attendu
✅ QA, Responsable projet et Responsable tâche ont accès complet  
✅ Les utilisateurs sans permissions sont bloqués

---

## Checklist de Validation Finale

### Interface Utilisateur
- [ ] Les boutons d'action sont visibles pour les cas non exécutés
- [ ] Les boutons d'action sont masqués pour les cas exécutés (PASSÉ ou ÉCHOUÉ)
- [ ] Le bouton "Voir détails" est toujours visible
- [ ] Les badges de statut sont correctement colorés
- [ ] Les icônes sont cohérentes et lisibles

### Modale de Détails
- [ ] La modale s'ouvre correctement
- [ ] Tous les champs sont affichés
- [ ] La section "Résultats obtenus" apparaît seulement pour les cas exécutés
- [ ] Les résultats obtenus sont correctement formatés
- [ ] La date d'exécution et l'exécuteur sont affichés

### Fonctionnalité
- [ ] L'exécution d'un cas de test fonctionne (PASSÉ)
- [ ] L'exécution d'un cas de test fonctionne (ÉCHOUÉ)
- [ ] Les résultats obtenus sont sauvegardés en base de données
- [ ] Le statut du cas est mis à jour
- [ ] La page se recharge après exécution

### Notifications
- [ ] Le responsable du projet reçoit une notification (cas PASSÉ)
- [ ] La notification contient les bonnes informations
- [ ] La notification est cliquable

### Permissions
- [ ] QA peut créer et exécuter les cas de test
- [ ] Responsable projet peut créer et exécuter les cas de test
- [ ] Responsable tâche peut créer et exécuter les cas de test
- [ ] Les utilisateurs sans permissions sont bloqués

---

## Problèmes Connus et Solutions

### Problème: Les boutons ne disparaissent pas après exécution
**Solution**: Vérifier que la page se recharge bien après l'exécution (`location.reload()` dans le JavaScript)

### Problème: La section "Résultats obtenus" n'apparaît pas
**Solution**: Vérifier que le champ `resultats_obtenus` est bien rempli lors de l'exécution et que la vue `details_cas_test_view` le retourne

### Problème: Erreur 403 lors de l'exécution
**Solution**: Vérifier que l'utilisateur a les permissions nécessaires (QA, Responsable projet, ou Responsable tâche)

---

## Conclusion

Ce guide couvre tous les aspects de la fonctionnalité de masquage des boutons d'action pour les cas de test exécutés. Suivez chaque scénario dans l'ordre pour une validation complète.

**Temps estimé**: 15-20 minutes pour tous les scénarios
