# Guide de Test - Système de Réinitialisation de Mot de Passe

## 🎯 Objectif

Tester le système complet de réinitialisation de mot de passe avec toutes ses fonctionnalités de sécurité.

## ✅ Prérequis

- ✅ Serveur Docker démarré (`docker-compose up -d`)
- ✅ Configuration email validée (Gmail SMTP)
- ✅ Au moins un utilisateur actif dans la base
- ✅ Accès à la boîte email de test

## 🧪 Tests à effectuer

### TEST 1: Accès à la page de réinitialisation

**Action:**
1. Ouvrir http://localhost:8000/login/
2. Vérifier la présence du lien "Mot de passe oublié ?"
3. Cliquer sur le lien

**Résultat attendu:**
- ✅ Lien visible avec icône clé
- ✅ Redirection vers `/password-reset/`
- ✅ Page professionnelle avec logo
- ✅ Formulaire avec champ email
- ✅ Bouton "Envoyer le lien de réinitialisation"
- ✅ Lien retour vers connexion
- ✅ Informations de sécurité affichées

### TEST 2: Demande avec email valide

**Action:**
1. Entrer un email d'utilisateur actif
2. Cliquer sur "Envoyer le lien"

**Résultat attendu:**
- ✅ Redirection vers `/password-reset/done/`
- ✅ Message générique affiché
- ✅ Icône de succès animée
- ✅ Instructions claires
- ✅ Avertissements (expiration, spam)
- ✅ Bouton retour vers connexion

### TEST 3: Réception de l'email

**Action:**
1. Vérifier la boîte email
2. Ouvrir l'email reçu

**Résultat attendu:**
- ✅ Email reçu en quelques secondes
- ✅ Sujet: "[SI-Gouvernance] Réinitialisation de votre mot de passe"
- ✅ Design HTML professionnel
- ✅ Logo JCONSULT MY visible
- ✅ Nom complet de l'utilisateur
- ✅ Bouton CTA "Réinitialiser mon mot de passe"
- ✅ Lien alternatif fonctionnel
- ✅ Avertissement d'expiration (10 minutes)
- ✅ Message de sécurité
- ✅ Informations du compte (email, date, IP)

### TEST 4: Clic sur le lien de réinitialisation

**Action:**
1. Cliquer sur le bouton dans l'email
2. OU copier/coller le lien alternatif

**Résultat attendu:**
- ✅ Redirection vers `/password-reset-confirm/<uidb64>/<token>/`
- ✅ Page de création de nouveau mot de passe
- ✅ 2 champs: nouveau MDP + confirmation
- ✅ Boutons toggle password (afficher/masquer)
- ✅ Exigences du mot de passe affichées
- ✅ Design professionnel et responsive

### TEST 5: Validation du mot de passe

**Action:**
Tester différents mots de passe:

1. **Trop court:** `Test1`
2. **Trop commun:** `password`
3. **Entièrement numérique:** `12345678`
4. **Valide:** `MonNouveauMDP2024!`

**Résultat attendu:**
- ✅ Mots de passe invalides rejetés avec messages clairs
- ✅ Mot de passe valide accepté
- ✅ Messages d'erreur en français
- ✅ Validation côté serveur

### TEST 6: Confirmation du nouveau mot de passe

**Action:**
1. Entrer un mot de passe valide
2. Confirmer le même mot de passe
3. Cliquer sur "Réinitialiser le mot de passe"

**Résultat attendu:**
- ✅ Redirection vers `/password-reset-complete/`
- ✅ Page de succès avec animation
- ✅ Message de confirmation
- ✅ Informations de sécurité (sessions fermées)
- ✅ Bouton "Se connecter maintenant"
- ✅ Redirection automatique après 5 secondes
- ✅ Conseils de sécurité affichés

### TEST 7: Email de confirmation

**Action:**
1. Vérifier la boîte email
2. Ouvrir l'email de confirmation

**Résultat attendu:**
- ✅ Email reçu immédiatement
- ✅ Sujet: "[SI-Gouvernance] Votre mot de passe a été modifié"
- ✅ Design HTML professionnel
- ✅ Confirmation du changement
- ✅ Mesures de sécurité listées
- ✅ Avertissement si non autorisé
- ✅ Informations du changement (date, IP)
- ✅ Conseils de sécurité

### TEST 8: Connexion avec nouveau mot de passe

**Action:**
1. Aller sur `/login/`
2. Entrer email + nouveau mot de passe
3. Se connecter

**Résultat attendu:**
- ✅ Connexion réussie
- ✅ Redirection vers dashboard
- ✅ Session active

### TEST 9: Invalidation des sessions

**Action:**
1. Avant la réinitialisation: se connecter sur 2 navigateurs différents
2. Effectuer la réinitialisation
3. Vérifier les 2 navigateurs

**Résultat attendu:**
- ✅ Les 2 sessions sont fermées
- ✅ Reconnexion obligatoire sur les 2 navigateurs
- ✅ Ancien mot de passe ne fonctionne plus

### TEST 10: Sécurité - Email inexistant

**Action:**
1. Demander réinitialisation avec email inexistant
2. Observer le comportement

**Résultat attendu:**
- ✅ Même message générique affiché
- ✅ Pas de révélation que l'email n'existe pas
- ✅ Aucun email envoyé
- ✅ Log d'audit créé

### TEST 11: Sécurité - Token expiré

**Action:**
1. Demander réinitialisation
2. Attendre 11 minutes
3. Cliquer sur le lien

**Résultat attendu:**
- ✅ Message "Lien invalide ou expiré"
- ✅ Explication des raisons possibles
- ✅ Bouton "Demander un nouveau lien"
- ✅ Bouton retour vers connexion

### TEST 12: Sécurité - Réutilisation du token

**Action:**
1. Utiliser un lien de réinitialisation
2. Compléter la réinitialisation
3. Essayer de réutiliser le même lien

**Résultat attendu:**
- ✅ Message "Lien invalide"
- ✅ Token invalidé après première utilisation
- ✅ Impossible de réutiliser

### TEST 13: Audit et logs

**Action:**
```bash
python test_password_reset.py
```

**Résultat attendu:**
- ✅ Tous les tests passent
- ✅ Logs créés dans AuditLog
- ✅ Type d'action: DEMANDE_RESET_PASSWORD
- ✅ Type d'action: RESET_PASSWORD_SUCCESS
- ✅ IP enregistrée
- ✅ Timestamp précis

### TEST 14: Responsive design

**Action:**
1. Tester sur mobile (DevTools)
2. Tester sur tablet
3. Tester sur desktop

**Résultat attendu:**
- ✅ Toutes les pages responsive
- ✅ Formulaires utilisables sur mobile
- ✅ Boutons accessibles
- ✅ Texte lisible
- ✅ Images adaptées

### TEST 15: Accessibilité

**Action:**
1. Navigation au clavier (Tab)
2. Lecteur d'écran (si disponible)
3. Contraste des couleurs

**Résultat attendu:**
- ✅ Navigation au clavier fluide
- ✅ Focus visible
- ✅ Labels appropriés
- ✅ Contraste suffisant
- ✅ Messages d'erreur clairs

## 📊 Checklist de validation

### Fonctionnalités
- [ ] Lien "Mot de passe oublié ?" visible
- [ ] Formulaire de demande fonctionnel
- [ ] Email de réinitialisation reçu
- [ ] Lien de réinitialisation fonctionnel
- [ ] Validation du mot de passe active
- [ ] Nouveau mot de passe accepté
- [ ] Email de confirmation reçu
- [ ] Connexion avec nouveau MDP réussie

### Sécurité
- [ ] Token expire après 10 minutes
- [ ] Token usage unique
- [ ] Sessions invalidées
- [ ] Pas de révélation d'email inexistant
- [ ] IP enregistrée
- [ ] Audit complet
- [ ] Validateurs de MDP actifs
- [ ] CSRF protection active

### Design
- [ ] Interface professionnelle
- [ ] Responsive (mobile/tablet/desktop)
- [ ] Emails HTML professionnels
- [ ] Animations fluides
- [ ] Messages clairs
- [ ] Icônes appropriées
- [ ] Couleurs cohérentes
- [ ] Logo visible

### Performance
- [ ] Email envoyé rapidement (< 5s)
- [ ] Pages chargent rapidement
- [ ] Pas d'erreurs console
- [ ] Pas de requêtes inutiles

## 🐛 Problèmes courants

### Email non reçu

**Solutions:**
1. Vérifier dossier spam
2. Vérifier configuration SMTP dans `.env`
3. Tester avec `python test_password_reset.py`
4. Vérifier les logs Django

### Token invalide immédiatement

**Solutions:**
1. Vérifier `PASSWORD_RESET_TIMEOUT` dans settings
2. Vérifier l'heure du serveur
3. Vérifier que le lien est complet
4. Demander un nouveau lien

### Erreur 500

**Solutions:**
1. Vérifier les logs Django
2. Vérifier la configuration email
3. Vérifier les migrations
4. Redémarrer le serveur

### Sessions non invalidées

**Solutions:**
1. Vérifier le code dans `CustomPasswordResetConfirmView`
2. Vérifier les logs
3. Tester manuellement la déconnexion

## 📝 Rapport de test

### Template de rapport

```
Date: __/__/____
Testeur: ___________
Version: 1.0.0

RÉSULTATS:
- Tests fonctionnels: __/8 ✅
- Tests sécurité: __/5 ✅
- Tests design: __/4 ✅
- Tests performance: __/4 ✅

TOTAL: __/21 ✅

PROBLÈMES IDENTIFIÉS:
1. _______________
2. _______________

RECOMMANDATIONS:
1. _______________
2. _______________

CONCLUSION:
[ ] Système prêt pour production
[ ] Corrections nécessaires
```

## 🎉 Validation finale

Si tous les tests passent:
- ✅ Le système est prêt pour la production
- ✅ La sécurité est conforme aux standards
- ✅ L'expérience utilisateur est optimale
- ✅ L'audit est complet

---

**Date:** 17 février 2026
**Version:** 1.0.0
**Status:** Prêt pour les tests
