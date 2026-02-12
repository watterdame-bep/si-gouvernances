# Guide de Test : Menu Tickets dans la Sidebar

## 📅 Date : 12 février 2026

## 🎯 Objectif

Tester le système de navigation des tickets de maintenance pour vérifier :
- ✅ Fonctionnalités
- ✅ Sécurité et permissions
- ✅ Interface responsive
- ✅ Navigation

## 🧪 Tests à Effectuer

### 1️⃣ Test : Mes Tickets

#### Prérequis
- Utilisateur connecté (développeur ou autre)
- Au moins 1 ticket assigné à l'utilisateur

#### Étapes
1. Cliquer sur "Tickets" dans la sidebar
2. Le sous-menu s'ouvre automatiquement
3. Cliquer sur "Mes tickets"
4. Vérifier l'affichage de la page

#### Résultats Attendus
✅ Page `/mes-tickets/` s'affiche
✅ Statistiques affichées : Total, Ouverts, Résolus
✅ Liste des tickets assignés à l'utilisateur uniquement
✅ Badges de priorité colorés (Critique, Haute, Normale, Basse)
✅ Icônes de statut (Ouvert, En cours, Résolu, Fermé)
✅ Filtres fonctionnels (statut, priorité)
✅ Clic sur un ticket redirige vers les détails

#### Test de Sécurité
- Vérifier qu'on ne voit QUE ses propres tickets
- Essayer de modifier l'URL pour voir les tickets d'un autre utilisateur
- ❌ Doit être impossible

---

### 2️⃣ Test : Tickets du Projet

#### Prérequis
- Utilisateur connecté
- Utilisateur membre d'au moins 1 projet (affectation active)

#### Étapes
1. Cliquer sur "Tickets" dans la sidebar
2. Cliquer sur "Tickets du projet"
3. Vérifier l'affichage de la liste des projets
4. Sélectionner un projet dans le dropdown
5. Vérifier l'affichage des tickets du projet

#### Résultats Attendus
✅ Page `/tickets-projet/` s'affiche
✅ Liste des projets accessibles (où l'utilisateur a une affectation active)
✅ Sélection d'un projet → URL change vers `/tickets-projet/<projet_id>/`
✅ Statistiques du projet : Total, Ouverts, Résolus
✅ Liste des tickets du projet sélectionné
✅ Filtres fonctionnels (statut, priorité)
✅ Clic sur un ticket redirige vers les détails

#### Test de Sécurité
- Essayer d'accéder à `/tickets-projet/<projet_id>/` d'un projet où l'utilisateur n'est PAS membre
- ❌ Doit rediriger vers `/tickets-projet/` avec message d'erreur
- Vérifier qu'on ne voit QUE les projets où on a une affectation active

#### Test avec Différents Rôles
- **Membre** : Voit les tickets du projet
- **Responsable** : Voit les tickets du projet
- **Admin** : Voit tous les projets

---

### 3️⃣ Test : Tous les Tickets (Admin)

#### Prérequis
- Utilisateur connecté avec rôle **Administrateur**

#### Étapes
1. Cliquer sur "Tickets" dans la sidebar
2. Vérifier que "Tous les tickets" est visible
3. Cliquer sur "Tous les tickets"
4. Vérifier l'affichage de la page

#### Résultats Attendus
✅ Page `/tous-tickets/` s'affiche
✅ Statistiques globales : Total, Ouverts, Résolus, Critiques
✅ Liste de TOUS les tickets (tous projets confondus)
✅ Filtres avancés : projet, statut, priorité
✅ Clic sur un ticket redirige vers les détails

#### Test de Sécurité (Utilisateur Normal)
- Se connecter avec un utilisateur NON admin
- Vérifier que "Tous les tickets" n'est PAS visible dans le menu
- Essayer d'accéder directement à `/tous-tickets/`
- ❌ Doit rediriger vers `/mes-tickets/` avec message d'erreur

---

### 4️⃣ Test : Navigation Sidebar

#### Étapes
1. Cliquer sur "Tickets" dans la sidebar
2. Vérifier l'ouverture du sous-menu
3. Cliquer à nouveau sur "Tickets"
4. Vérifier la fermeture du sous-menu

#### Résultats Attendus
✅ Clic 1 : Sous-menu s'ouvre avec animation
✅ Chevron tourne (rotate-180)
✅ Sous-menu affiche les 3 options (ou 2 si non-admin)
✅ Clic 2 : Sous-menu se ferme
✅ Chevron revient à la position initiale

#### Test Auto-Ouverture
1. Naviguer vers `/mes-tickets/`
2. Recharger la page
3. Vérifier que le sous-menu "Tickets" est automatiquement ouvert

✅ Sous-menu ouvert automatiquement
✅ Page active mise en évidence

---

### 5️⃣ Test : Responsive Mobile

#### Prérequis
- Navigateur avec DevTools (F12)
- Mode responsive activé

#### Étapes
1. Ouvrir DevTools (F12)
2. Activer le mode responsive
3. Tester avec différentes tailles d'écran :
   - Mobile : 375px
   - Tablette : 768px
   - Desktop : 1024px

#### Résultats Attendus

**Mobile (< 768px)** :
✅ Padding réduit (px-3 py-4)
✅ Textes plus petits (text-xs, text-sm)
✅ Icônes : text-lg
✅ Statistiques : 3 colonnes
✅ Filtres : empilés verticalement
✅ Cartes : pleine largeur
✅ Textes tronqués si trop longs

**Tablette (≥ 768px)** :
✅ Padding normal (px-4 py-6)
✅ Textes standards (text-sm, text-base)
✅ Statistiques : 3 colonnes
✅ Filtres : en ligne

**Desktop (≥ 1024px)** :
✅ Padding généreux (px-4 py-8)
✅ Textes standards
✅ Statistiques : 4 colonnes
✅ Filtres : en ligne
✅ Cartes : largeur optimale

---

### 6️⃣ Test : Filtres

#### Test Filtre Statut
1. Aller sur "Mes tickets"
2. Sélectionner "Ouvert" dans le filtre statut
3. Vérifier que seuls les tickets ouverts s'affichent
4. Sélectionner "Résolu"
5. Vérifier que seuls les tickets résolus s'affichent

✅ Filtrage fonctionne correctement
✅ URL mise à jour avec le paramètre `?statut=OUVERT`
✅ Statistiques restent globales (pas filtrées)

#### Test Filtre Priorité
1. Sélectionner "Critique" dans le filtre priorité
2. Vérifier que seuls les tickets critiques s'affichent
3. Sélectionner "Normale"
4. Vérifier que seuls les tickets normaux s'affichent

✅ Filtrage fonctionne correctement
✅ URL mise à jour avec le paramètre `?priorite=CRITIQUE`

#### Test Filtres Combinés
1. Sélectionner "Ouvert" + "Critique"
2. Vérifier que seuls les tickets ouverts ET critiques s'affichent

✅ Filtres combinés fonctionnent
✅ URL : `?statut=OUVERT&priorite=CRITIQUE`

---

### 7️⃣ Test : Statistiques

#### Étapes
1. Aller sur "Mes tickets"
2. Noter les statistiques affichées
3. Créer un nouveau ticket et l'assigner à soi-même
4. Recharger la page
5. Vérifier que les statistiques sont mises à jour

#### Résultats Attendus
✅ Total augmente de 1
✅ Ouverts augmente de 1
✅ Statistiques exactes et cohérentes

---

### 8️⃣ Test : Clic sur Ticket

#### Étapes
1. Aller sur "Mes tickets"
2. Cliquer sur une carte de ticket
3. Vérifier la redirection

#### Résultats Attendus
✅ Redirection vers `/projets/<projet_id>/tickets/<ticket_id>/`
✅ Page de détails du ticket s'affiche
✅ Informations complètes du ticket visibles

---

### 9️⃣ Test : Icônes et Badges

#### Vérifications Visuelles

**Icônes de Type** :
✅ Bug : `fa-bug` (rouge)
✅ Amélioration : `fa-star` (jaune)
✅ Question : `fa-question-circle` (bleu)
✅ Autre : `fa-file-alt` (gris)

**Icônes de Statut** :
✅ Ouvert : `fa-folder-open` (bleu)
✅ En cours : `fa-spinner` (indigo)
✅ Résolu : `fa-check-circle` (vert)
✅ Fermé : `fa-lock` (gris)
✅ Rejeté : `fa-times-circle` (rouge)

**Badges de Priorité** :
✅ Critique : fond rouge, texte rouge foncé
✅ Haute : fond orange, texte orange foncé
✅ Normale : fond bleu, texte bleu foncé
✅ Basse : fond gris, texte gris foncé

---

## 📊 Checklist Complète

### Fonctionnalités
- [ ] Mes tickets affiche uniquement les tickets assignés
- [ ] Tickets du projet affiche les projets accessibles
- [ ] Tous les tickets affiche tous les tickets (Admin)
- [ ] Filtres fonctionnent correctement
- [ ] Statistiques sont exactes
- [ ] Clic sur ticket redirige vers détails

### Sécurité
- [ ] Utilisateur normal ne voit que ses tickets
- [ ] Utilisateur normal ne voit que ses projets
- [ ] Utilisateur normal ne peut pas accéder à "Tous les tickets"
- [ ] Accès direct par URL bloqué si non autorisé
- [ ] Messages d'erreur appropriés

### Interface
- [ ] Design responsive (mobile, tablette, desktop)
- [ ] Icônes FontAwesome affichées correctement
- [ ] Badges colorés selon priorité/statut
- [ ] Textes lisibles et bien dimensionnés
- [ ] Espacement cohérent

### Navigation
- [ ] Menu "Tickets" dans la sidebar
- [ ] Sous-menu s'ouvre/ferme au clic
- [ ] Chevron animé (rotate-180)
- [ ] Auto-ouverture sur pages tickets
- [ ] Page active mise en évidence

### Performance
- [ ] Chargement rapide des pages
- [ ] Requêtes optimisées (select_related, prefetch_related)
- [ ] Pas de requêtes N+1
- [ ] Utilisation de distinct() pour éviter doublons

---

## 🎯 Résultats Attendus Globaux

Après tous les tests, le système doit :
- ✅ Fonctionner sans erreur
- ✅ Respecter toutes les permissions
- ✅ Être responsive sur tous les écrans
- ✅ Offrir une navigation intuitive
- ✅ Afficher des données exactes
- ✅ Être sécurisé contre les accès non autorisés

---

## 🐛 Problèmes Potentiels

### Si "Mes tickets" est vide
- Vérifier qu'il existe des tickets assignés à l'utilisateur
- Créer un ticket et l'assigner à l'utilisateur de test

### Si "Tickets du projet" est vide
- Vérifier que l'utilisateur a une affectation active sur au moins un projet
- Créer une affectation : `Affectation.objects.create(utilisateur=user, projet=projet, date_fin=None)`

### Si "Tous les tickets" n'est pas visible
- Vérifier que l'utilisateur est bien Admin : `user.is_superuser = True`

### Si les filtres ne fonctionnent pas
- Vérifier les paramètres GET dans l'URL
- Vérifier la logique de filtrage dans la vue

---

## ✅ Validation Finale

Une fois tous les tests passés :
- ✅ Le système de navigation des tickets est opérationnel
- ✅ La sécurité est garantie
- ✅ L'interface est professionnelle et responsive
- ✅ L'expérience utilisateur est optimale

**Le système est prêt pour la production !**

