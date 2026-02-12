# Règles de Gouvernance : Tickets de Maintenance

**Date**: 12 février 2026  
**Statut**: ✅ Documenté  

---

## 🔒 RÈGLE FONDAMENTALE

**LE CLIENT N'EST PAS DANS LE SYSTÈME**

Le client est externe au système SI-Gouvernance. Il ne peut ni se connecter, ni créer de tickets, ni voir l'interface.

---

## 👥 ACTEURS DU SYSTÈME

### 1. CLIENT (Externe)
**Rôle** : Utilisateur final du logiciel développé

**Ce qu'il PEUT faire** :
- Signaler des problèmes par email, téléphone, ou autre canal externe
- Demander des améliorations
- Tester les solutions proposées
- Valider que les corrections fonctionnent

**Ce qu'il NE PEUT PAS faire** :
- ❌ Se connecter au système SI-Gouvernance
- ❌ Créer des tickets directement
- ❌ Voir l'état des tickets
- ❌ Accéder à l'interface de maintenance

### 2. ADMINISTRATEUR (Interne)
**Rôle** : Gestionnaire du système et de la maintenance

**Permissions** :
- ✅ Créer des tickets (suite aux demandes clients)
- ✅ Assigner des développeurs
- ✅ Voir tous les tickets
- ✅ Valider et fermer les tickets
- ✅ Rejeter les tickets
- ✅ Gérer les contrats de garantie

### 3. RESPONSABLE DE PROJET (Interne)
**Rôle** : Gestionnaire d'un projet spécifique

**Permissions** :
- ✅ Créer des tickets pour son projet
- ✅ Assigner des développeurs de son équipe
- ✅ Voir les tickets de son projet
- ✅ Valider et fermer les tickets de son projet
- ✅ Rejeter les tickets de son projet

### 4. DÉVELOPPEUR (Interne)
**Rôle** : Résout les problèmes techniques

**Permissions** :
- ✅ Voir les tickets qui lui sont assignés
- ✅ Résoudre les tickets assignés
- ✅ Ajouter du temps passé
- ❌ Créer des tickets
- ❌ Assigner des tickets
- ❌ Fermer ou rejeter des tickets

---

## 🔄 WORKFLOW RÉEL

### Étape 1 : Signalement Client (Externe)
```
CLIENT → Email/Téléphone → ADMINISTRATEUR ou RESPONSABLE
```

**Exemple** :
- Client envoie un email : "Le bouton de connexion ne fonctionne pas"
- Administrateur reçoit l'email

### Étape 2 : Création du Ticket (Interne)
```
ADMINISTRATEUR/RESPONSABLE → Crée le ticket dans SI-Gouvernance
```

**Actions** :
1. Se connecte au système
2. Va dans "Tickets de Maintenance"
3. Clique sur "Créer un ticket"
4. Remplit :
   - Titre : "Bouton de connexion ne fonctionne pas"
   - Description : Détails du problème signalé par le client
   - Type : Bug
   - Priorité : Haute
   - Contrat de garantie : Sélectionne le contrat actif
5. Assigne un ou plusieurs développeurs
6. Le ticket est créé avec statut EN_COURS

### Étape 3 : Résolution (Interne)
```
DÉVELOPPEUR → Corrige le problème → Marque comme RESOLU
```

**Actions** :
1. Développeur reçoit une notification
2. Travaille sur le problème
3. Corrige le bug
4. Remplit le formulaire de résolution :
   - Solution : "Correction du gestionnaire d'événements"
   - Fichiers modifiés : "src/components/LoginButton.js"
   - Temps passé : 1.5h
5. Clique sur "Marquer comme résolu"

### Étape 4 : Validation Client (Externe)
```
ADMINISTRATEUR/RESPONSABLE → Contacte le client → Client teste
```

**Actions** :
1. Administrateur reçoit une notification (ticket résolu)
2. Contacte le client par email/téléphone
3. Demande au client de tester la correction
4. Client teste et confirme que ça fonctionne

### Étape 5 : Fermeture (Interne)
```
ADMINISTRATEUR/RESPONSABLE → Valide et ferme le ticket
```

**Actions** :
1. Administrateur se connecte
2. Va dans les détails du ticket
3. Clique sur "Valider et fermer"
4. Le ticket passe au statut FERME

---

## 📋 PERMISSIONS DÉTAILLÉES

| Action | Admin | Responsable | Développeur | Client |
|--------|-------|-------------|-------------|--------|
| Créer ticket | ✅ | ✅ (son projet) | ❌ | ❌ |
| Voir tickets | ✅ Tous | ✅ Son projet | ✅ Assignés | ❌ |
| Assigner | ✅ | ✅ (son projet) | ❌ | ❌ |
| Résoudre | ✅ | ✅ (son projet) | ✅ (assignés) | ❌ |
| Fermer | ✅ | ✅ (son projet) | ❌ | ❌ |
| Rejeter | ✅ | ✅ (son projet) | ❌ | ❌ |

---

## 🎯 POURQUOI LE CLIENT EST EXTERNE ?

### Raisons de Sécurité
- Le système SI-Gouvernance contient des informations sensibles sur le développement
- Les clients n'ont pas besoin de voir les détails techniques
- Évite la multiplication des comptes utilisateurs

### Raisons Pratiques
- Le client n'a pas besoin d'apprendre un nouveau système
- Communication plus directe et personnalisée
- Flexibilité dans la gestion des demandes

### Raisons de Gouvernance
- Contrôle total sur les tickets créés
- Filtrage des demandes (garantie, priorité, etc.)
- Traçabilité interne complète

---

## 💬 COMMUNICATION CLIENT

### Canaux de Communication
1. **Email** : Principal moyen de communication
2. **Téléphone** : Pour les urgences
3. **Réunions** : Pour les demandes complexes
4. **Support externe** : Si système de ticketing client séparé

### Informations à Collecter
Lors de la création d'un ticket suite à une demande client :
- Description détaillée du problème
- Étapes pour reproduire (si bug)
- Environnement (navigateur, OS, etc.)
- Urgence/Impact business
- Coordonnées du contact client

### Retour au Client
Après résolution :
- Email avec description de la correction
- Instructions de test si nécessaire
- Demande de confirmation
- Numéro de ticket pour référence (ex: MAINT-00002)

---

## 📊 EXEMPLE COMPLET

### Scénario : Bug Signalé par le Client

**1. Client → Administrateur** (Email)
```
De: client@entreprise.com
À: admin@si-gouvernance.com
Sujet: Problème de connexion

Bonjour,
Depuis ce matin, le bouton "Se connecter" ne répond plus.
Nous ne pouvons plus accéder à l'application.
Urgent !

Cordialement,
Jean Dupont
```

**2. Administrateur → Système** (Création ticket)
```
Ticket: MAINT-00003
Titre: Bouton de connexion ne répond plus
Type: Bug
Priorité: CRITIQUE
Description: Le client signale que le bouton "Se connecter" ne fonctionne plus 
depuis ce matin. Impact: Blocage complet de l'accès à l'application.
Assigné à: DON DIEU, Eraste Butela
```

**3. Développeur → Système** (Résolution)
```
Solution: Correction d'un conflit JavaScript introduit dans le dernier déploiement.
Le gestionnaire d'événements du bouton était écrasé.
Fichiers modifiés: src/components/LoginButton.js, src/utils/eventHandlers.js
Temps passé: 2h
```

**4. Administrateur → Client** (Email)
```
De: admin@si-gouvernance.com
À: client@entreprise.com
Sujet: RE: Problème de connexion - RÉSOLU (MAINT-00003)

Bonjour Jean,

Le problème a été identifié et corrigé. Il s'agissait d'un conflit JavaScript.
La correction a été déployée.

Pourriez-vous tester et confirmer que tout fonctionne ?

Référence: MAINT-00003

Cordialement,
L'équipe SI-Gouvernance
```

**5. Client → Administrateur** (Email)
```
De: client@entreprise.com
À: admin@si-gouvernance.com
Sujet: RE: Problème de connexion - RÉSOLU (MAINT-00003)

Bonjour,

Testé et validé. Tout fonctionne parfaitement maintenant.
Merci pour la rapidité !

Cordialement,
Jean Dupont
```

**6. Administrateur → Système** (Fermeture)
```
Action: Valider et fermer
Statut: FERME
Note: Client a confirmé que la correction fonctionne
```

---

## ✅ RÉSUMÉ

Le système de tickets de maintenance de SI-Gouvernance est un **outil interne** :
- ✅ Les clients signalent les problèmes par des canaux externes
- ✅ L'administrateur ou le responsable crée les tickets dans le système
- ✅ Les développeurs résolvent les tickets
- ✅ L'administrateur valide avec le client et ferme les tickets
- ✅ Toute la traçabilité et la gestion sont internes

Cette approche garantit sécurité, contrôle et professionnalisme dans la gestion de la maintenance.
