# Workflow et Statuts des Tickets de Maintenance

**Date**: 12 février 2026  
**Statut**: ✅ Documenté  

---

## 📊 CYCLE DE VIE D'UN TICKET

```
OUVERT → EN_COURS → RESOLU → FERME
   ↓         ↓          ↓
   └─────────┴──────────┴─→ REJETE
```

---

## 🔄 STATUTS DÉTAILLÉS

### 1. OUVERT (🆕)
**Description** : Ticket créé, en attente d'assignation

**Actions possibles** :
- Assigner à un ou plusieurs développeurs
- Rejeter (si invalide ou hors garantie)

**Qui peut agir** :
- Administrateur
- Responsable du projet

---

### 2. EN_COURS (🔵)
**Description** : Ticket assigné, travail en cours

**Transition automatique** : Dès qu'un développeur est assigné

**Actions possibles** :
- Marquer comme résolu (avec solution)
- Rejeter (si finalement invalide)

**Qui peut agir** :
- Développeurs assignés
- Responsable du projet
- Administrateur

---

### 3. RESOLU (✅)
**Description** : Solution fournie, en attente de validation

**Ce qui se passe** :
- Le développeur a corrigé le problème
- Une solution est documentée
- Les fichiers modifiés sont listés
- Une notification est envoyée à l'administrateur

**Actions possibles** :
- **Valider et fermer** : Confirme que la solution fonctionne (action normale)
- ~~Rejeter~~ : Supprimé car n'a pas de sens après résolution

**Qui peut agir** :
- Administrateur
- Responsable du projet

**Pourquoi ne pas rejeter un ticket résolu ?**
- Si la solution ne convient pas, il faut rouvrir le ticket (pas encore implémenté)
- Le rejet est pour les tickets invalides AVANT résolution

---

### 4. FERME (🔒)
**Description** : Ticket validé et archivé

**Ce qui se passe** :
- Le client/responsable a testé et validé la solution
- Le ticket est considéré comme terminé
- Plus aucune action possible

**Actions possibles** : Aucune (état final)

---

### 5. REJETE (❌)
**Description** : Ticket refusé, ne sera pas traité

**Raisons courantes** :
- Demande hors garantie
- Ticket doublon
- Demande invalide ou non pertinente
- Problème non reproductible

**Quand rejeter** :
- Statut OUVERT : Ticket invalide dès le départ
- Statut EN_COURS : Découverte que le ticket est invalide pendant l'analyse
- ~~Statut RESOLU~~ : Ne devrait pas être rejeté à ce stade

**Actions possibles** : Aucune (état final)

---

## 🎯 WORKFLOW NORMAL

### Scénario 1 : Ticket Traité avec Succès

1. **Signalement Client** (Externe)
   - Client signale un problème par email/téléphone
   - Administrateur ou Responsable reçoit la demande

2. **Création** (OUVERT → EN_COURS)
   - Administrateur/Responsable crée le ticket dans le système
   - Décrit le problème signalé par le client
   - Assigne un développeur
   - Statut passe automatiquement à EN_COURS

3. **Résolution** (RESOLU)
   - Développeur corrige le problème
   - Fournit la solution et les fichiers modifiés
   - Notification envoyée à l'administrateur

4. **Validation Client** (Externe)
   - Administrateur contacte le client
   - Client teste la correction
   - Client confirme que ça fonctionne

5. **Fermeture** (FERME)
   - Administrateur/Responsable clique sur "Valider et fermer"
   - Ticket archivé

### Scénario 2 : Ticket Invalide

1. **Création** (OUVERT)
   - Responsable crée un ticket

2. **Analyse** (EN_COURS ou OUVERT)
   - Découverte que le ticket est invalide

3. **Rejet** (REJETE)
   - Administrateur/Responsable rejette avec raison
   - Ticket archivé

---

## 🔧 MODIFICATIONS APPORTÉES

### 1. Suppression de l'Avancement Basé sur le Temps

**AVANT** :
```
Avancement: 125% (temps passé / temps estimé)
Barre de progression: 100% (plafonnée)
```

**PROBLÈME** : Le temps passé peut dépasser l'estimation, rendant le calcul incorrect

**APRÈS** :
```
Temps estimé: 2h
Temps passé: 2.5h
(Pas de pourcentage d'avancement)
```

**RAISON** : L'avancement d'un ticket n'est pas linéaire par rapport au temps. Un ticket est soit en cours, soit résolu.

### 2. Simplification des Actions

**AVANT** :
- Ticket RESOLU : Boutons "Fermer" ET "Rejeter"

**APRÈS** :
- Ticket RESOLU : Bouton "Valider et fermer" uniquement
- Ticket OUVERT/EN_COURS : Bouton "Rejeter" uniquement

**RAISON** : 
- Un ticket résolu ne devrait pas être rejeté
- Si la solution ne convient pas, il faudrait le rouvrir (fonctionnalité future)
- Clarification du workflow pour l'utilisateur

---

## 📋 PERMISSIONS

| Action | OUVERT | EN_COURS | RESOLU | FERME | REJETE |
|--------|--------|----------|--------|-------|--------|
| Assigner | Admin, Resp | Admin, Resp | - | - | - |
| Résoudre | - | Assigné, Admin, Resp | - | - | - |
| Fermer | - | - | Admin, Resp | - | - |
| Rejeter | Admin, Resp | Admin, Resp | - | - | - |

**Légende** :
- Admin : Administrateur
- Resp : Responsable du projet
- Assigné : Développeur assigné au ticket

---

## 💡 BONNES PRATIQUES

### Pour les Responsables de Projet
1. Créer des tickets clairs avec description détaillée
2. Assigner rapidement aux bons développeurs
3. Valider les solutions avant de fermer
4. Rejeter uniquement les tickets vraiment invalides

### Pour les Développeurs
1. Fournir une solution détaillée lors de la résolution
2. Lister tous les fichiers modifiés
3. Indiquer le temps réel passé
4. Tester la solution avant de marquer comme résolu

### Pour les Administrateurs
1. Surveiller les notifications de tickets résolus
2. Valider et fermer rapidement après test
3. Gérer les contrats de garantie
4. Suivre les statistiques de maintenance

---

## ✅ RÉSULTAT

Le workflow des tickets est maintenant plus clair et logique :
- ✅ Suppression de l'avancement basé sur le temps (incorrect)
- ✅ Simplification des actions selon le statut
- ✅ Workflow cohérent : OUVERT → EN_COURS → RESOLU → FERME
- ✅ Rejet possible uniquement avant résolution
- ✅ Validation claire avec "Valider et fermer"
