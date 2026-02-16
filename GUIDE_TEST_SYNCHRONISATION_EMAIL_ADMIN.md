# Guide de Test - Synchronisation Email Admin

## 🎯 Objectif
Tester la fonctionnalité de modification d'email pour les administrateurs avec synchronisation automatique vers le compte de connexion.

---

## ✅ Prérequis

- Être connecté en tant qu'administrateur
- Avoir un profil membre associé au compte admin
- Accès à l'interface de profil

---

## 🧪 Test de la Fonctionnalité

### Étape 1 : Accéder au Profil

1. Connectez-vous en tant qu'administrateur
2. Cliquez sur votre nom en haut à droite
3. Sélectionnez "Mon Profil"

**Résultat attendu** :
- ✅ Page de profil s'affiche
- ✅ Section "Profil RH" visible

---

### Étape 2 : Vérifier l'Interface Admin

Dans la section "Profil RH", vérifiez :

**Pour un administrateur** :
- ✅ Le champ "Email personnel" a un fond bleu clair
- ✅ Le label affiche "(Éditable - Admin)" en bleu
- ✅ Le champ est éditable (pas disabled)
- ✅ Message d'information : "Cet email sera synchronisé avec votre compte de connexion"
- ✅ Bouton "Sauvegarder l'email" visible en bas de la section
- ✅ Note informative adaptée pour les admins

**Pour un utilisateur non-admin** :
- ✅ Le champ "Email personnel" a un fond gris
- ✅ Le champ est désactivé (disabled)
- ✅ Pas de bouton "Sauvegarder l'email"
- ✅ Note informative standard

---

### Étape 3 : Modifier l'Email

1. Dans le champ "Email personnel", modifiez l'email
   - Exemple : `admin.nouveau@example.com`
2. Cliquez sur le bouton "Sauvegarder l'email"

**Résultat attendu** :
- ✅ Modale de confirmation s'affiche
- ✅ Message : "Êtes-vous sûr de vouloir modifier votre email ?"
- ✅ Affiche le nouvel email dans la confirmation
- ✅ Mention : "Cet email sera utilisé pour vous connecter au système"

---

### Étape 4 : Confirmer la Modification

1. Cliquez sur "OK" dans la modale de confirmation

**Résultat attendu** :
- ✅ Message de succès vert apparaît en haut à droite
- ✅ Texte : "Email modifié avec succès !"
- ✅ Après 1.5 secondes, message bleu : "Votre email de connexion a été mis à jour"
- ✅ Le champ "Email" dans la section "Informations du compte" est mis à jour
- ✅ Pas de rechargement de page

---

### Étape 5 : Vérifier la Synchronisation

1. Notez le nouvel email affiché
2. Déconnectez-vous
3. Essayez de vous connecter avec l'ancien email

**Résultat attendu** :
- ✅ Connexion échoue avec l'ancien email
- ✅ Message d'erreur approprié

4. Essayez de vous connecter avec le nouvel email

**Résultat attendu** :
- ✅ Connexion réussit avec le nouvel email
- ✅ Accès au système normal

---

### Étape 6 : Vérifier l'Audit

1. Connectez-vous en tant qu'admin
2. Accédez à la page "Audit"
3. Recherchez l'action "MODIFICATION_EMAIL_ADMIN"

**Résultat attendu** :
- ✅ Entrée d'audit créée
- ✅ Type d'action : "MODIFICATION_EMAIL_ADMIN"
- ✅ Description : "Modification de l'email par l'administrateur [Nom]"
- ✅ Données avant : ancien email (membre et user)
- ✅ Données après : nouvel email (membre et user)
- ✅ Date et heure correctes
- ✅ Adresse IP enregistrée

---

## 🔒 Tests de Sécurité

### Test 1 : Validation du Format Email

1. Entrez un email invalide : `admin@invalide`
2. Cliquez sur "Sauvegarder l'email"

**Résultat attendu** :
- ✅ Message d'erreur : "Format d'email invalide"
- ✅ Pas de modification effectuée

---

### Test 2 : Email Vide

1. Effacez complètement le champ email
2. Cliquez sur "Sauvegarder l'email"

**Résultat attendu** :
- ✅ Message d'erreur : "L'email ne peut pas être vide"
- ✅ Pas de modification effectuée

---

### Test 3 : Email Déjà Utilisé (Membre)

1. Entrez un email déjà utilisé par un autre membre
2. Cliquez sur "Sauvegarder l'email"

**Résultat attendu** :
- ✅ Message d'erreur : "Cet email est déjà utilisé par un autre membre"
- ✅ Pas de modification effectuée

---

### Test 4 : Email Déjà Utilisé (Utilisateur)

1. Entrez un email déjà utilisé par un autre compte utilisateur
2. Cliquez sur "Sauvegarder l'email"

**Résultat attendu** :
- ✅ Message d'erreur : "Cet email est déjà utilisé par un autre compte utilisateur"
- ✅ Pas de modification effectuée

---

### Test 5 : Accès Non-Admin

1. Connectez-vous en tant qu'utilisateur non-admin
2. Accédez à votre profil
3. Tentez de modifier l'email via l'API (avec curl ou Postman)

**Résultat attendu** :
- ✅ Erreur 403 Forbidden
- ✅ Message : "Seuls les administrateurs peuvent modifier leur email"
- ✅ Pas de modification effectuée

---

### Test 6 : Sans Profil Membre

1. Créez un compte admin sans profil membre associé
2. Tentez de modifier l'email via l'API

**Résultat attendu** :
- ✅ Erreur 400 Bad Request
- ✅ Message : "Vous n'avez pas de profil membre associé"
- ✅ Pas de modification effectuée

---

## 🎨 Tests d'Interface

### Test 1 : Responsive Mobile

1. Ouvrez le profil sur un mobile (ou mode responsive)
2. Vérifiez l'affichage du champ email

**Résultat attendu** :
- ✅ Champ email visible et éditable
- ✅ Bouton "Sauvegarder l'email" accessible
- ✅ Messages de succès/erreur visibles
- ✅ Modale de confirmation adaptée au mobile

---

### Test 2 : Animations

1. Modifiez l'email et sauvegardez
2. Observez les animations

**Résultat attendu** :
- ✅ Message de succès glisse depuis la droite
- ✅ Animation fluide (300ms)
- ✅ Message disparaît après 4 secondes
- ✅ Transition de disparition fluide

---

### Test 3 : Indicateurs Visuels

Vérifiez les indicateurs visuels :

**Champ éditable (Admin)** :
- ✅ Fond bleu clair (`bg-blue-50`)
- ✅ Bordure bleue (`border-blue-300`)
- ✅ Focus ring bleu
- ✅ Texte noir (pas gris)

**Champ désactivé (Non-admin)** :
- ✅ Fond gris (`bg-gray-50`)
- ✅ Bordure grise
- ✅ Texte gris
- ✅ Curseur "not-allowed"

---

## 📊 Tests de Cohérence

### Test 1 : Cohérence Membre ↔ Utilisateur

1. Modifiez l'email via le profil
2. Vérifiez dans la base de données :

```sql
SELECT 
    u.email as email_user,
    m.email_personnel as email_membre
FROM core_utilisateur u
JOIN core_membre m ON u.membre_id = m.id
WHERE u.is_superuser = 1;
```

**Résultat attendu** :
- ✅ `email_user` = `email_membre`
- ✅ Les deux emails sont identiques

---

### Test 2 : Transaction Atomique

1. Simulez une erreur pendant la sauvegarde (ex: contrainte DB)
2. Vérifiez que rien n'a été modifié

**Résultat attendu** :
- ✅ Rollback automatique
- ✅ Email membre non modifié
- ✅ Email utilisateur non modifié
- ✅ Message d'erreur affiché

---

## 🐛 Tests d'Erreurs

### Test 1 : Erreur Réseau

1. Coupez la connexion réseau
2. Tentez de modifier l'email

**Résultat attendu** :
- ✅ Message d'erreur : "Une erreur est survenue lors de la sauvegarde"
- ✅ Pas de modification effectuée
- ✅ Interface reste fonctionnelle

---

### Test 2 : Timeout Serveur

1. Simulez un timeout serveur (>30s)
2. Tentez de modifier l'email

**Résultat attendu** :
- ✅ Message d'erreur après timeout
- ✅ Pas de modification effectuée
- ✅ Possibilité de réessayer

---

## ✅ Checklist Complète

- [ ] Interface admin affichée correctement
- [ ] Champ email éditable pour admin uniquement
- [ ] Indicateurs visuels corrects (bleu pour admin)
- [ ] Bouton "Sauvegarder l'email" visible pour admin
- [ ] Modale de confirmation s'affiche
- [ ] Validation du format email
- [ ] Vérification d'unicité de l'email
- [ ] Synchronisation membre → utilisateur
- [ ] Messages de succès animés
- [ ] Mise à jour dynamique de l'affichage
- [ ] Connexion fonctionne avec le nouvel email
- [ ] Audit enregistré correctement
- [ ] Tests de sécurité passés
- [ ] Interface responsive (mobile/tablette)
- [ ] Animations fluides
- [ ] Gestion des erreurs appropriée
- [ ] Transaction atomique fonctionnelle

---

## 📝 Notes Importantes

### Sécurité
- Seuls les administrateurs peuvent modifier leur email
- Validation stricte du format email
- Vérification d'unicité (membre et utilisateur)
- Transaction atomique pour garantir la cohérence
- Audit complet de toutes les modifications

### Expérience Utilisateur
- Confirmation avant modification
- Messages clairs et informatifs
- Animations fluides
- Pas de rechargement de page
- Feedback visuel immédiat

### Technique
- Transaction atomique (rollback en cas d'erreur)
- Synchronisation bidirectionnelle
- Validation côté client et serveur
- Gestion des erreurs robuste
- Audit complet

---

**Date** : 2026-02-16  
**Statut** : ✅ Prêt pour les tests  
**Fonctionnalité** : Synchronisation email admin
