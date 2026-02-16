# 🧪 GUIDE DE TEST - EMAILS HTML PROFESSIONNELS

## ⚠️ IMPORTANT: NE PAS REGARDER LES ANCIENS EMAILS!

Les emails reçus AVANT le redémarrage du serveur (il y a 44 minutes) sont en texte brut.
Vous devez tester avec une NOUVELLE action pour voir les emails HTML.

---

## 🎯 TEST RAPIDE (5 minutes)

### Option 1: Créer un Nouveau Projet

1. Se connecter à l'application: http://localhost:8000
2. Aller dans "Projets" → "Créer un projet"
3. Remplir le formulaire:
   - Nom: "Test Email HTML"
   - Client: "Test Client"
   - Responsable: Sélectionner un utilisateur avec email
   - Budget: 10000
   - Statut: "Planifié"
4. Cliquer sur "Créer"
5. **Vérifier l'email du responsable** (dans les 2 minutes)

### Option 2: Assigner un Responsable à un Projet Existant

1. Aller dans "Projets"
2. Cliquer sur un projet existant
3. Aller dans "Paramètres" ou "Modifier"
4. Changer le responsable principal
5. Sauvegarder
6. **Vérifier l'email du nouveau responsable**

### Option 3: Créer un Nouveau Compte Utilisateur

1. Aller dans "Administration" → "Gestion des comptes"
2. Cliquer sur "Créer un compte"
3. Remplir le formulaire avec un email valide
4. Cliquer sur "Créer"
5. **Vérifier l'email d'activation**

---

## 📧 À QUOI RESSEMBLE L'EMAIL HTML?

### Vous devriez voir:

✅ **En-tête avec gradient violet/bleu**
```
┌─────────────────────────────────┐
│   [LOGO J-CONSULT MY]           │
│                                 │
│   SI-Gouvernance                │
│   Système de Gestion de Projets │
└─────────────────────────────────┘
```

✅ **Corps du message avec design moderne**
- Texte bien formaté
- Carte d'information avec bordure violette
- Détails du projet/tâche/alerte

✅ **Bouton d'action cliquable**
```
┌─────────────────────────┐
│  🚀 Accéder au Projet   │
└─────────────────────────┘
```

✅ **Footer professionnel**
```
J-CONSULT MY
Système de Gouvernance et Gestion de Projets

Accueil | Aide | Contact

© 2026 J-Consult MY. Tous droits réservés.
```

---

## ❌ SI VOUS VOYEZ ENCORE DU TEXTE BRUT

### Vérification 1: Est-ce un NOUVEL email?

- ❌ Email reçu il y a 1 heure → ANCIEN (texte brut)
- ✅ Email reçu il y a 2 minutes → NOUVEAU (HTML)

### Vérification 2: Paramètres Gmail

1. Ouvrir Gmail
2. Cliquer sur l'engrenage ⚙️ → "Voir tous les paramètres"
3. Onglet "Général"
4. Chercher "Images"
5. Cocher "Toujours afficher les images externes"
6. Sauvegarder

### Vérification 3: Voir le Code Source

1. Ouvrir l'email
2. Cliquer sur les 3 points (⋮)
3. Sélectionner "Afficher l'original"
4. Chercher cette ligne:
   ```
   Content-Type: text/html; charset="utf-8"
   ```
5. Si présent → L'email EST en HTML, Gmail le bloque
6. Si absent → Contacter le support

---

## 🔍 DIAGNOSTIC AVANCÉ

### Commande de Vérification Complète

Exécuter dans le terminal:

```bash
docker exec si_gouvernance_web python verifier_code_email.py
```

Cette commande vérifie:
- ✅ Configuration email
- ✅ Templates HTML
- ✅ Code d'envoi
- ✅ Signaux Django
- ✅ Envoie un email de test

### Résultat Attendu

```
================================================================================
✓ TOUT EST CONFIGURÉ CORRECTEMENT!
================================================================================

📧 VÉRIFIEZ VOTRE BOÎTE EMAIL: watterdame70@gmail.com
   Sujet: [SI-Gouvernance] Nouveau Responsable: ...
   L'email devrait être en HTML avec:
   - Logo J-Consult MY
   - Design moderne avec gradient violet/bleu
   - Bouton 'Accéder au Projet'
   - Footer avec copyright © 2026 J-Consult MY
```

---

## 📊 EMAILS DISPONIBLES

### 1. Responsable de Projet
**Quand:** Assignation d'un responsable principal
**Contenu:**
- Détails du projet (nom, client, budget)
- Liste des responsabilités
- Bouton "Accéder au Projet"

### 2. Activation de Compte
**Quand:** Création d'un nouveau compte utilisateur
**Contenu:**
- Lien d'activation sécurisé (48h)
- Informations du compte
- Bouton "Activer Mon Compte"

### 3. Assignation de Tâche
**Quand:** Assignation d'une tâche à un utilisateur
**Contenu:**
- Détails de la tâche
- Projet et étape associés
- Bouton "Voir la Tâche"

### 4. Alerte de Projet
**Quand:** Projet en retard, budget dépassé, contrat expiré
**Contenu:**
- Type et niveau d'alerte
- Détails contextuels
- Bouton "Consulter le Projet"

---

## ✅ CHECKLIST DE TEST

Cocher après avoir testé:

- [ ] J'ai effectué une NOUVELLE action dans l'application
- [ ] J'ai attendu 2 minutes
- [ ] J'ai rafraîchi ma boîte email
- [ ] J'ai ouvert le NOUVEL email (pas un ancien)
- [ ] Je vois le logo J-Consult MY
- [ ] Je vois le gradient violet/bleu
- [ ] Je vois le bouton d'action
- [ ] Je vois le footer avec copyright

Si tous les points sont cochés → ✅ **ÇA FONCTIONNE!**

Si certains points ne sont pas cochés:
1. Vérifier les paramètres Gmail (images)
2. Voir le code source de l'email
3. Exécuter `verifier_code_email.py`

---

## 🆘 SUPPORT

### Si le Problème Persiste

1. **Vérifier que c'est bien un NOUVEL email**
   - Date de réception < 1 heure
   - Après le redémarrage du serveur

2. **Exécuter le diagnostic**
   ```bash
   docker exec si_gouvernance_web python verifier_code_email.py
   ```

3. **Vérifier les logs**
   ```bash
   docker logs si_gouvernance_web --tail 50
   ```

4. **Contacter le support avec:**
   - Capture d'écran de l'email
   - Code source de l'email (Afficher l'original)
   - Résultat de `verifier_code_email.py`

---

## 🎉 CONFIRMATION

Une fois que vous voyez l'email HTML professionnel:

1. ✅ Le système fonctionne correctement
2. ✅ Tous les futurs emails seront en HTML
3. ✅ Le design est professionnel et moderne
4. ✅ Prêt pour la production

**Félicitations! Le système d'emails HTML est opérationnel! 🚀**

---

**Date:** 16/02/2026
**Version:** 1.0
**Statut:** ✅ Système Fonctionnel
