# Guide de Test - Clôture de Module depuis "Mes Modules"

## 🎯 Objectif du Test

Vérifier que les responsables de module peuvent clôturer leur module depuis l'interface "Mes Modules" uniquement lorsque toutes les tâches sont terminées.

## 📋 Prérequis

1. ✅ Avoir un compte utilisateur
2. ✅ Être responsable d'au moins un module
3. ✅ Le module doit avoir des tâches

## 🧪 Scénarios de Test

### Scénario 1: Module avec Toutes Tâches Terminées ✅

**Objectif**: Vérifier que le bouton de clôture est actif et fonctionne

**Étapes**:
1. Se connecter avec un compte responsable de module
2. Aller dans un projet où vous êtes responsable d'un module
3. Cliquer sur "Mes Modules" dans le menu du projet
4. Identifier un module où toutes les tâches sont terminées

**Résultat attendu**:
- ✅ Un bouton vert avec icône ✓ est visible à côté du bouton "Tâches"
- ✅ Le tooltip indique "Clôturer le module"
- ✅ Le bouton est cliquable

**Action**:
5. Cliquer sur le bouton vert de clôture

**Résultat attendu**:
- ✅ Une modale verte s'ouvre avec le titre "Confirmer la clôture"
- ✅ Le nom du module est affiché
- ✅ Un avertissement liste les restrictions après clôture
- ✅ Deux boutons: "Annuler" et "Clôturer"

**Action**:
6. Cliquer sur "Clôturer"

**Résultat attendu**:
- ✅ La modale se ferme
- ✅ Un message de succès vert s'affiche en haut à droite
- ✅ La page se recharge automatiquement après 1.5 secondes
- ✅ Un badge vert "Clôturé" apparaît à côté du nom du module
- ✅ Le bouton de clôture n'est plus visible

---

### Scénario 2: Module avec Tâches Restantes ⚠️

**Objectif**: Vérifier que le bouton est désactivé si des tâches ne sont pas terminées

**Étapes**:
1. Se connecter avec un compte responsable de module
2. Aller dans "Mes Modules"
3. Identifier un module où il reste des tâches non terminées

**Résultat attendu**:
- ✅ Un bouton gris avec icône ✓ est visible
- ✅ Le bouton a l'air désactivé (gris, pas de hover)
- ✅ Le curseur devient "interdit" au survol
- ✅ Le tooltip indique "Toutes les tâches doivent être terminées (X restante(s))"

**Action**:
4. Essayer de cliquer sur le bouton gris

**Résultat attendu**:
- ✅ Rien ne se passe (bouton désactivé)
- ✅ Pas de modale qui s'ouvre

---

### Scénario 3: Module Déjà Clôturé 🔒

**Objectif**: Vérifier l'affichage d'un module déjà clôturé

**Étapes**:
1. Se connecter avec un compte responsable de module
2. Aller dans "Mes Modules"
3. Identifier un module qui a été clôturé (badge vert "Clôturé")

**Résultat attendu**:
- ✅ Un badge vert "Clôturé" est affiché à côté du nom du module
- ✅ Le bouton de clôture n'est PAS visible
- ✅ Seul le bouton "Tâches" est présent
- ✅ Le bouton "Tâches" reste cliquable (consultation possible)

---

### Scénario 4: Contributeur (Non Responsable) 👤

**Objectif**: Vérifier que les contributeurs ne voient pas le bouton

**Étapes**:
1. Se connecter avec un compte contributeur (pas responsable)
2. Aller dans "Mes Modules"
3. Regarder les modules où vous êtes contributeur

**Résultat attendu**:
- ✅ Seul le bouton "Tâches" est visible
- ✅ Pas de bouton de clôture (ni actif, ni désactivé)
- ✅ Le badge "Contributeur" est affiché dans la colonne "Rôle"

---

### Scénario 5: Annulation de la Clôture ❌

**Objectif**: Vérifier que l'annulation fonctionne correctement

**Étapes**:
1. Se connecter comme responsable d'un module
2. Aller dans "Mes Modules"
3. Cliquer sur le bouton vert de clôture d'un module
4. La modale s'ouvre

**Action**:
5. Cliquer sur "Annuler"

**Résultat attendu**:
- ✅ La modale se ferme
- ✅ Rien n'est modifié
- ✅ Le module n'est pas clôturé
- ✅ Le bouton de clôture reste visible et actif

---

## 🎨 Éléments Visuels à Vérifier

### Bouton Actif (Vert)
```
┌─────────────────────────┐
│ [📋] [✓]                │
│  vert  vert             │
└─────────────────────────┘
```
- Couleur: Vert vif (`#059669`)
- Hover: Vert plus foncé
- Icône: Cercle avec check
- Taille: 8x8 (32px)

### Bouton Désactivé (Gris)
```
┌─────────────────────────┐
│ [📋] [✓]                │
│  vert  gris             │
└─────────────────────────┘
```
- Couleur: Gris clair (`#D1D5DB`)
- Pas de hover
- Curseur: Interdit
- Icône: Cercle avec check (gris)

### Badge Clôturé
```
┌──────────────────────────────┐
│ Module Dashboard [✓ Clôturé] │
└──────────────────────────────┘
```
- Couleur: Vert clair (`bg-green-100`)
- Texte: Vert foncé (`text-green-800`)
- Icône: Check circle
- Taille: Petit (xs)

### Modale de Confirmation
```
┌─────────────────────────────────────┐
│ ✓ Confirmer la clôture              │
│   Action définitive                 │
├─────────────────────────────────────┤
│                                     │
│ ⚠️ Important: Une fois clôturé...   │
│   • Ajouter de nouvelles tâches    │
│   • Supprimer le module            │
│   • Affecter de nouveaux membres   │
│                                     │
│ ✓ Vous pourrez toujours consulter  │
│                                     │
├─────────────────────────────────────┤
│              [Annuler] [✓ Clôturer] │
└─────────────────────────────────────┘
```

## 📊 Checklist de Test

### Tests Fonctionnels
- [ ] Bouton actif pour module avec toutes tâches terminées
- [ ] Bouton désactivé pour module avec tâches restantes
- [ ] Badge "Clôturé" affiché pour modules clôturés
- [ ] Bouton masqué pour contributeurs
- [ ] Modale s'ouvre au clic
- [ ] Modale se ferme sur "Annuler"
- [ ] Clôture réussie sur "Clôturer"
- [ ] Message de succès affiché
- [ ] Page rechargée automatiquement
- [ ] Badge "Clôturé" affiché après rechargement

### Tests Visuels
- [ ] Couleur verte pour bouton actif
- [ ] Couleur grise pour bouton désactivé
- [ ] Icône check-circle visible
- [ ] Tooltip informatif au survol
- [ ] Modale verte professionnelle
- [ ] Badge vert "Clôturé" bien visible
- [ ] Alignement correct des boutons
- [ ] Responsive sur mobile

### Tests de Permissions
- [ ] Responsable voit le bouton
- [ ] Contributeur ne voit pas le bouton
- [ ] Module clôturé ne montre pas le bouton
- [ ] Seuls les responsables peuvent clôturer

## 🐛 Problèmes Potentiels

### Problème 1: Bouton ne s'affiche pas
**Cause possible**: Pas responsable du module
**Solution**: Vérifier le rôle dans la colonne "Rôle"

### Problème 2: Bouton toujours gris
**Cause possible**: Des tâches ne sont pas terminées
**Solution**: Aller dans "Tâches" et vérifier les statuts

### Problème 3: Modale ne s'ouvre pas
**Cause possible**: Erreur JavaScript
**Solution**: Ouvrir la console (F12) et vérifier les erreurs

### Problème 4: Clôture ne fonctionne pas
**Cause possible**: Erreur serveur
**Solution**: Vérifier les logs Django et la console navigateur

## ✅ Critères de Succès

Le test est réussi si:
1. ✅ Le bouton s'affiche uniquement pour les responsables
2. ✅ Le bouton est actif seulement si toutes les tâches sont terminées
3. ✅ Le bouton est désactivé avec tooltip informatif si tâches restantes
4. ✅ La modale s'ouvre et se ferme correctement
5. ✅ La clôture fonctionne et le badge s'affiche
6. ✅ Les contributeurs ne voient pas le bouton
7. ✅ Les modules clôturés affichent le badge

## 📝 Rapport de Test

Après avoir effectué les tests, noter:

**Date du test**: _______________

**Scénarios testés**:
- [ ] Scénario 1: Module avec toutes tâches terminées
- [ ] Scénario 2: Module avec tâches restantes
- [ ] Scénario 3: Module déjà clôturé
- [ ] Scénario 4: Contributeur
- [ ] Scénario 5: Annulation

**Résultat global**: ⭕ Réussi / ❌ Échec

**Problèmes rencontrés**:
_________________________________
_________________________________
_________________________________

**Commentaires**:
_________________________________
_________________________________
_________________________________

---

**Bon test !** 🚀
