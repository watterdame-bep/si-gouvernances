# Guide de Test - Notification de Clôture de Module

## 🎯 Objectif

Tester que le responsable du projet reçoit bien une notification lorsqu'un module est clôturé par un responsable de module.

## 📋 Prérequis

1. ✅ Avoir deux comptes utilisateurs :
   - **Compte A** : Responsable principal du projet
   - **Compte B** : Responsable d'un module (mais pas responsable du projet)

2. ✅ Un projet avec au moins un module
3. ✅ Le module doit avoir des tâches terminées

## 🧪 Scénario 1: Notification Envoyée

### Étape 1: Préparation
1. Se connecter avec le **Compte A** (responsable du projet)
2. Créer ou vérifier qu'un projet existe
3. S'assurer d'être le responsable principal du projet
4. Affecter le **Compte B** comme responsable d'un module
5. Se déconnecter

### Étape 2: Clôture du Module
6. Se connecter avec le **Compte B** (responsable du module)
7. Aller dans "Mes Modules"
8. Vérifier qu'un module a toutes ses tâches terminées
9. Cliquer sur le bouton vert de clôture ✓
10. Confirmer dans la modale
11. Vérifier le message de succès
12. Se déconnecter

### Étape 3: Vérification de la Notification
13. Se connecter avec le **Compte A** (responsable du projet)
14. Regarder le badge de notification dans le header (🔔)

**Résultat attendu**:
- ✅ Badge de notification avec un chiffre (ex: 🔔 1)
- ✅ Cliquer sur le badge ouvre la liste des notifications
- ✅ Une notification "Module '{nom}' clôturé" est visible
- ✅ Le message indique qui a clôturé et quel module
- ✅ La notification n'est pas marquée comme lue (fond coloré)

**Contenu attendu**:
```
Titre: Module "Dashboard" clôturé

Message: Jean Dupont a clôturé le module "Dashboard" 
du projet "Système de gestion des pharmacies". 
Toutes les tâches ont été terminées.

Il y a X minutes
```

---

## 🧪 Scénario 2: Pas d'Auto-Notification

### Objectif
Vérifier qu'un responsable de projet qui clôture lui-même un module ne reçoit pas de notification.

### Étapes
1. Se connecter avec un compte qui est **à la fois** :
   - Responsable principal du projet
   - Responsable d'un module

2. Aller dans "Mes Modules"
3. Clôturer un module (toutes tâches terminées)
4. Vérifier le badge de notification

**Résultat attendu**:
- ✅ Pas de nouvelle notification
- ✅ Le badge ne s'incrémente pas
- ✅ Pas d'auto-notification (bonne pratique)

---

## 🧪 Scénario 3: Vérification des Boutons Réduits

### Objectif
Vérifier que les boutons d'action sont plus petits.

### Étapes
1. Se connecter avec n'importe quel compte
2. Aller dans "Mes Modules"
3. Observer la taille des boutons dans la colonne "Actions"

**Résultat attendu**:
- ✅ Boutons plus petits qu'avant (6x6 au lieu de 8x8)
- ✅ Icônes plus petites
- ✅ Lignes du tableau plus compactes
- ✅ Plus de modules visibles sans scroll

**Comparaison visuelle**:
```
Avant (8x8):        Après (6x6):
┌────────┐          ┌──────┐
│   📋   │          │  📋  │
└────────┘          └──────┘
  32px                24px
```

---

## 🧪 Scénario 4: Données Contextuelles

### Objectif
Vérifier que les données contextuelles sont bien enregistrées.

### Étapes (nécessite accès à la base de données)
1. Après avoir clôturé un module
2. Ouvrir la console Django ou l'admin
3. Chercher la notification créée

**Commande Django**:
```python
from core.models import NotificationModule

# Dernière notification de type MODULE_TERMINE
notif = NotificationModule.objects.filter(
    type_notification='MODULE_TERMINE'
).order_by('-date_creation').first()

print(notif.donnees_contexte)
```

**Résultat attendu**:
```json
{
    "projet_id": "uuid-du-projet",
    "module_id": 123,
    "date_cloture": "2026-02-11T14:30:00",
    "cloture_par": "Jean Dupont"
}
```

---

## 📊 Checklist de Test

### Tests Fonctionnels
- [ ] Notification envoyée au responsable du projet
- [ ] Pas d'auto-notification
- [ ] Badge de notification s'incrémente
- [ ] Titre de la notification correct
- [ ] Message de la notification informatif
- [ ] Émetteur correctement enregistré
- [ ] Données contextuelles présentes

### Tests Visuels
- [ ] Boutons réduits (6x6)
- [ ] Icônes plus petites (xs)
- [ ] Lignes du tableau plus compactes
- [ ] Notification bien formatée
- [ ] Badge de notification visible

### Tests de Permissions
- [ ] Seul le responsable principal reçoit la notification
- [ ] Pas de notification aux contributeurs
- [ ] Pas d'auto-notification

## 🐛 Problèmes Potentiels

### Problème 1: Pas de notification reçue
**Causes possibles**:
- Pas de responsable principal défini
- Responsable principal = personne qui clôture
- Erreur lors de la création de la notification

**Solution**:
- Vérifier qu'un responsable principal existe
- Vérifier les logs Django pour les erreurs
- Vérifier la base de données

### Problème 2: Notification vide
**Cause possible**: Erreur dans le template de notification

**Solution**:
- Vérifier le contenu de la notification dans la base
- Vérifier le template d'affichage des notifications

### Problème 3: Boutons toujours grands
**Cause possible**: Cache du navigateur

**Solution**:
- Vider le cache (Ctrl+F5)
- Vérifier le code source HTML (F12)

## ✅ Critères de Succès

Le test est réussi si:
1. ✅ Le responsable du projet reçoit la notification
2. ✅ Le message est clair et informatif
3. ✅ Pas d'auto-notification
4. ✅ Les boutons sont réduits
5. ✅ Les données contextuelles sont présentes
6. ✅ La notification est marquable comme lue

## 📝 Rapport de Test

**Date du test**: _______________

**Scénarios testés**:
- [ ] Scénario 1: Notification envoyée
- [ ] Scénario 2: Pas d'auto-notification
- [ ] Scénario 3: Boutons réduits
- [ ] Scénario 4: Données contextuelles

**Résultat global**: ⭕ Réussi / ❌ Échec

**Problèmes rencontrés**:
_________________________________
_________________________________

**Commentaires**:
_________________________________
_________________________________

---

**Bon test !** 🚀
