# 🚀 GUIDE RAPIDE - ACCÈS AU SYSTÈME DE MAINTENANCE

## 📍 COMMENT ACCÉDER À LA MAINTENANCE

### Méthode 1: Depuis le Dashboard Projet

```
1. Accédez à votre projet
   http://localhost:8000/projets/<projet_id>/

2. Cliquez sur "Gestion des Étapes"
   ou
   http://localhost:8000/projets/<projet_id>/etapes/

3. Trouvez l'étape "MAINTENANCE" et cliquez dessus

4. L'interface spéciale MAINTENANCE s'affiche! 🎉
```

### Méthode 2: URL Directe

```
http://localhost:8000/projets/<projet_id>/etapes/<etape_maintenance_id>/
```

---

## 🖼️ CE QUE VOUS VERREZ

### Interface Spéciale MAINTENANCE

```
┌─────────────────────────────────────────────────────────────┐
│  🔧 SYSTÈME DE MAINTENANCE                                  │
│  Gestion des contrats, tickets et interventions             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 STATISTIQUES                                             │
│  ┌──────────────────────┬──────────────────────┐           │
│  │ 📋 Contrats Actifs   │ 🎫 Tickets Ouverts   │           │
│  │        0             │         0            │           │
│  │ Garanties en cours   │ En attente           │           │
│  └──────────────────────┴──────────────────────┘           │
│                                                              │
│  🎯 ACTIONS                                                  │
│  ┌──────────────────────┬──────────────────────┐           │
│  │ 📋 Contrats          │ 🎫 Tickets           │           │
│  │ de Garantie          │ de Maintenance       │           │
│  │                      │                      │           │
│  │ Gérez les contrats   │ Créez et suivez     │           │
│  │ de garantie...       │ les tickets...      │           │
│  │                      │                      │           │
│  │ [Gérer les Contrats] │ [Gérer les Tickets] │           │
│  └──────────────────────┴──────────────────────┘           │
│                                                              │
│  🔄 WORKFLOW                                                 │
│  ① Contrat → ② Ticket → ③ Billet → ④ Intervention → ⑤ Statut│
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 ACTIONS DISPONIBLES

### 1. Gérer les Contrats de Garantie

**Cliquez sur:** `[Gérer les Contrats]`

**Vous serez redirigé vers:**
```
http://localhost:8000/projets/<projet_id>/contrats/
```

**Vous pourrez:**
- ✅ Voir tous les contrats de garantie
- ✅ Créer un nouveau contrat
- ✅ Voir les contrats actifs vs expirés
- ✅ Définir les conditions de maintenance gratuite

### 2. Gérer les Tickets de Maintenance

**Cliquez sur:** `[Gérer les Tickets]`

**Vous serez redirigé vers:**
```
http://localhost:8000/projets/<projet_id>/tickets/
```

**Vous pourrez:**
- ✅ Voir tous les tickets de maintenance
- ✅ Créer un nouveau ticket
- ✅ Filtrer par statut et gravité
- ✅ Voir les statistiques
- ✅ Émettre des billets d'intervention

---

## 🔄 WORKFLOW COMPLET

### Étape par Étape

```
1️⃣ CONTRAT DE GARANTIE
   ↓
   Créez un contrat qui définit:
   - Type: CORRECTIVE ou EVOLUTIVE
   - Période: Date début → Date fin
   - SLA: Temps de réponse (heures)
   - Couverture: Ce qui est inclus
   - Exclusions: Ce qui n'est pas inclus

2️⃣ TICKET DE MAINTENANCE
   ↓
   Créez un ticket pour un incident:
   - Titre et description
   - Gravité: MINEUR / MAJEUR / CRITIQUE
   - Origine: CLIENT / MONITORING / INTERNE
   - Contrat associé (si disponible)
   → Vérification automatique: Gratuit ou Payant?

3️⃣ BILLET D'INTERVENTION
   ↓
   Chef projet émet un billet:
   - Développeur autorisé
   - Type: ANALYSE / CORRECTION / DEPLOIEMENT
   - Durée estimée
   - Instructions spécifiques

4️⃣ INTERVENTION TECHNIQUE
   ↓
   Développeur enregistre son intervention:
   - Description des actions
   - Temps passé
   - Correctif appliqué
   - Fichiers modifiés

5️⃣ STATUT TECHNIQUE
   ↓
   Développeur rédige le rapport:
   - Problème initial
   - Cause réelle (Root Cause)
   - Solution apportée
   - Impact système
   - Risques futurs
   - Recommandations
   → Chef projet valide
   → Ticket automatiquement RÉSOLU
```

---

## 💡 CONSEILS

### Premier Démarrage

1. **Créez d'abord un Contrat de Garantie**
   - Cela permettra de traiter les tickets gratuitement
   - Sans contrat, les tickets seront marqués PAYANT

2. **Créez ensuite des Tickets**
   - Décrivez les incidents ou demandes
   - Le système vérifiera automatiquement la garantie

3. **Suivez le Workflow**
   - Billet → Intervention → Statut → Résolution

### Rechargement Cache

Si vous ne voyez pas les changements:
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

---

## 🎨 DIFFÉRENCES AVEC LES AUTRES ÉTAPES

### Étapes Classiques (ANALYSE, CONCEPTION, etc.)
```
┌─────────────────────────────────────┐
│ 📋 Tâches de l'étape                │
│ [+ Nouvelle tâche] [⚙️ Gérer]       │
│                                     │
│ Liste des tâches...                 │
└─────────────────────────────────────┘
```
- Gestion de tâches classiques (TacheEtape)
- Création et assignation de tâches
- Suivi de progression

### Étape MAINTENANCE (Spéciale)
```
┌─────────────────────────────────────┐
│ 🔧 SYSTÈME DE MAINTENANCE           │
│ [Contrats] [Tickets]                │
│                                     │
│ Workflow: Contrat → Ticket → ...   │
└─────────────────────────────────────┘
```
- Gestion de contrats et tickets
- Workflow spécifique maintenance
- Pas de tâches classiques

---

## 📊 EXEMPLE CONCRET

### Projet: "Gestion de Stock"

**Scénario:**
1. Le projet est déployé en production
2. L'étape MAINTENANCE est activée
3. Un contrat de garantie de 6 mois est créé
4. Un client signale un bug critique
5. Un ticket est créé (automatiquement gratuit car sous garantie)
6. Le chef projet émet un billet pour un développeur
7. Le développeur corrige le bug et enregistre son intervention
8. Le développeur rédige le statut technique
9. Le chef projet valide
10. Le ticket est automatiquement résolu

**Navigation:**
```
Dashboard Projet "Gestion de Stock"
  ↓
Gestion des Étapes
  ↓
Cliquer sur "MAINTENANCE"
  ↓
Interface spéciale s'affiche
  ↓
[Gérer les Tickets]
  ↓
Liste des tickets avec le bug critique
```

---

## ❓ FAQ

### Q: Je ne vois pas l'interface spéciale MAINTENANCE
**R:** Vérifiez que:
- Vous êtes bien sur l'étape MAINTENANCE (pas une autre étape)
- Vous avez rechargé le cache (Ctrl + Shift + R)
- Le serveur Django est redémarré

### Q: Les statistiques affichent 0
**R:** C'est normal si:
- Aucun contrat n'a été créé
- Aucun ticket n'a été créé
- Créez votre premier contrat et ticket pour voir les statistiques

### Q: Je ne peux pas créer de tâches dans MAINTENANCE
**R:** C'est normal! MAINTENANCE ne fonctionne pas avec des tâches classiques. Utilisez les contrats et tickets à la place.

### Q: Comment créer un contrat?
**R:** 
1. Cliquez sur "Gérer les Contrats"
2. Cliquez sur "Nouveau Contrat"
3. Remplissez le formulaire
4. Créez

### Q: Comment créer un ticket?
**R:**
1. Cliquez sur "Gérer les Tickets"
2. Cliquez sur "Nouveau Ticket"
3. Remplissez le formulaire
4. Créez

---

## 🎉 VOUS ÊTES PRÊT!

L'interface MAINTENANCE est maintenant accessible et fonctionnelle.

**Prochaines étapes:**
1. ✅ Accédez à l'étape MAINTENANCE
2. ✅ Créez votre premier contrat de garantie
3. ✅ Créez votre premier ticket
4. ✅ Suivez le workflow complet

**Besoin d'aide?**
- Consultez `SYSTEME_MAINTENANCE_COMPLET.md` pour la documentation complète
- Consultez `MAINTENANCE_INTERFACE_VISUEL.md` pour l'aperçu visuel

---

**Date:** 06/02/2026  
**Version:** 1.0  
**Statut:** ✅ PRÊT À UTILISER

**Bon travail avec le système de maintenance! 🚀**
