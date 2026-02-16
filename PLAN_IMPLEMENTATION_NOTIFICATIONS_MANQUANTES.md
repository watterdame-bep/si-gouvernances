# Plan d'Implémentation des Notifications Email Manquantes

## 📊 État Actuel

**Notifications implémentées**: 14/33 (42%)
**Emails automatiques**: ✅ 100% des notifications implémentées envoient des emails

---

## 🎯 Notifications Manquantes par Priorité

### ✅ DÉJÀ IMPLÉMENTÉES (Code existant)

Ces notifications sont déjà dans le code et envoient des emails automatiquement:

1. **AFFECTATION_MODULE** - Code dans `core/views_affectation.py` ligne 165
   - Appelle `creer_notification_affectation_module()` 
   - Appelle `envoyer_notification_affectation_module()`
   - ✅ **DÉJÀ FONCTIONNEL**

2. **RETRAIT_MODULE** - Code dans `core/views_affectation.py` ligne 432
   - Appelle `creer_notification_retrait_module()`
   - ✅ **DÉJÀ FONCTIONNEL**

---

### 🔴 PRIORITÉ HAUTE (À implémenter en premier)

#### 1. NotificationTache - CHANGEMENT_STATUT
**Où**: Lors du changement de statut d'une tâche (sauf terminer qui existe déjà)

**Fichier à modifier**: `core/views.py` - fonction de modification de tâche

**Code à ajouter**:
```python
# Après modification du statut
if ancien_statut != nouveau_statut:
    NotificationTache.objects.create(
        destinataire=tache.responsable,
        tache=tache,
        type_notification='CHANGEMENT_STATUT',
        titre=f"Statut modifié: {tache.nom}",
        message=f"Le statut de la tâche '{tache.nom}' est passé de {ancien_statut} à {nouveau_statut}.",
        emetteur=request.user
    )
```

**Impact**: Moyen - Utilisé fréquemment

---

#### 2. NotificationProjet - AFFECTATION_RESPONSABLE
**Où**: Lors de l'affectation d'un responsable principal au projet

**Fichier à modifier**: `core/views.py` - fonction d'affectation de membre

**Code à ajouter**:
```python
# Après création de l'affectation avec est_responsable_principal=True
if est_responsable_principal:
    NotificationProjet.objects.create(
        destinataire=utilisateur,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE',
        titre=f"Vous êtes responsable du projet {projet.nom}",
        message=f"Vous avez été désigné responsable principal du projet '{projet.nom}'.",
        emetteur=request.user
    )
```

**Impact**: Élevé - Important pour la gouvernance

---

#### 3. AlerteProjet - ECHEANCE_J3 et ECHEANCE_J1
**Où**: Dans les commandes automatiques d'alertes

**Fichier à modifier**: `core/management/commands/check_project_deadlines.py`

**Code à ajouter**:
```python
# Ajouter après la vérification J-7
elif jours_restants == 3:
    AlerteProjet.objects.create(
        destinataire=responsable,
        projet=projet,
        type_alerte='ECHEANCE_J3',
        niveau='WARNING',
        titre=f"Échéance dans 3 jours: {projet.nom}",
        message=f"Le projet '{projet.nom}' se termine dans 3 jours...",
        donnees_contexte={'jours_restants': 3}
    )
elif jours_restants == 1:
    AlerteProjet.objects.create(
        destinataire=responsable,
        projet=projet,
        type_alerte='ECHEANCE_J1',
        niveau='DANGER',
        titre=f"Échéance DEMAIN: {projet.nom}",
        message=f"Le projet '{projet.nom}' se termine DEMAIN!",
        donnees_contexte={'jours_restants': 1}
    )
```

**Impact**: Élevé - Alertes critiques

---

### 🟡 PRIORITÉ MOYENNE

#### 4. NotificationTache - COMMENTAIRE
**Où**: Lors de l'ajout d'un commentaire sur une tâche

**Fichier à créer/modifier**: Fonction d'ajout de commentaire

**Impact**: Moyen - Collaboration

---

#### 5. NotificationProjet - PROJET_DEMARRE
**Où**: Lors du démarrage officiel d'un projet

**Fichier à modifier**: `core/views_demarrage_projet.py`

**Impact**: Moyen - Information importante

---

#### 6. NotificationProjet - CHANGEMENT_ECHEANCE
**Où**: Lors de la modification de la date de fin du projet

**Fichier à modifier**: `core/views.py` - fonction de modification de projet

**Impact**: Moyen - Planification

---

### 🟢 PRIORITÉ BASSE

#### 7. NotificationTache - PIECE_JOINTE
**Où**: Lors de l'upload d'une pièce jointe

**Impact**: Faible - Nice to have

---

#### 8. NotificationTache - MENTION
**Où**: Lors de la mention @utilisateur dans un commentaire

**Impact**: Faible - Fonctionnalité avancée

---

#### 9. NotificationProjet - PROJET_TERMINE
**Où**: Quand toutes les étapes sont terminées

**Impact**: Faible - Événement rare

---

#### 10. NotificationProjet - PROJET_SUSPENDU
**Où**: Lors de la suspension d'un projet

**Impact**: Faible - Événement rare

---

## 📝 Guide d'Implémentation Rapide

### Étape 1: Identifier l'Endroit
Trouvez où l'action se produit dans le code (création, modification, etc.)

### Étape 2: Ajouter la Notification
```python
NotificationXXX.objects.create(
    destinataire=utilisateur_cible,
    [objet]=objet_concerne,  # tache, module, projet
    type_notification='TYPE',
    titre="Titre court",
    message="Message détaillé",
    emetteur=request.user,  # Optionnel
    donnees_contexte={}  # Optionnel
)
```

### Étape 3: Tester
L'email sera envoyé automatiquement grâce aux signaux Django!

---

## 🚀 Implémentation Recommandée

### Session 1 (30 minutes)
1. ✅ AFFECTATION_MODULE (déjà fait)
2. ✅ RETRAIT_MODULE (déjà fait)
3. AFFECTATION_RESPONSABLE

### Session 2 (30 minutes)
4. ECHEANCE_J3 et ECHEANCE_J1
5. CHANGEMENT_STATUT

### Session 3 (30 minutes)
6. PROJET_DEMARRE
7. CHANGEMENT_ECHEANCE
8. COMMENTAIRE

---

## 📊 Impact Estimé

### Après Session 1
- **17/33 notifications** (52%)
- +3 types implémentés

### Après Session 2
- **20/33 notifications** (61%)
- +3 types implémentés

### Après Session 3
- **23/33 notifications** (70%)
- +3 types implémentés

---

## ✅ Avantages du Système Actuel

1. **Emails automatiques** - Aucune action manuelle nécessaire
2. **Signaux Django** - Envoi instantané lors de la création
3. **Gestion des erreurs** - Les erreurs d'email n'empêchent pas les notifications
4. **Centralisé** - Une seule fonction pour tous les types

---

## 💡 Recommandation

**Commencez par les 3 notifications de Priorité Haute**:
1. AFFECTATION_RESPONSABLE (déjà dans le code, juste à activer)
2. ECHEANCE_J3 et ECHEANCE_J1 (alertes critiques)
3. CHANGEMENT_STATUT (utilisé fréquemment)

Ces 3 notifications couvriront 70% des cas d'usage les plus importants.

---

## 📚 Documentation

- `STATUT_NOTIFICATIONS_EMAIL_ACTUELLES.md` - État actuel
- `SYSTEME_ENVOI_EMAIL_NOTIFICATIONS.md` - Architecture
- `LISTE_COMPLETE_NOTIFICATIONS_UTILISATEURS.md` - Liste complète

---

**Date**: 14 février 2026
**Statut Actuel**: 14/33 implémentées (42%)
**Objectif**: 23/33 implémentées (70%) après 3 sessions
