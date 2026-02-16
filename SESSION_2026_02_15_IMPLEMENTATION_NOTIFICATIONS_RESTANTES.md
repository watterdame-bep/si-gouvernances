# Session 2026-02-15: Implémentation des Notifications Restantes

## 📊 État Initial

**Notifications implémentées**: 17/33 (51%)
- Avant cette session: 14/33 (42%)
- Ajoutées récemment: 3 notifications (AFFECTATION_RESPONSABLE, CHANGEMENT_STATUT, ECHEANCE_J3/J1)

---

## 🎯 Objectif de la Session

Implémenter les **16 notifications restantes** pour atteindre **100% de couverture**.

---

## 📋 Plan d'Implémentation

### Phase 1: Notifications de Projet (6 notifications)

#### 1.1 PROJET_DEMARRE ✅
- **Fichier**: `core/views_demarrage_projet.py`
- **Fonction**: `demarrer_projet()`
- **Destinataires**: Tous les membres de l'équipe
- **Priorité**: HAUTE

#### 1.2 CHANGEMENT_ECHEANCE
- **Fichier**: `core/views.py`
- **Fonction**: `modifier_projet()`
- **Destinataires**: Responsable + équipe
- **Priorité**: HAUTE

#### 1.3 PROJET_TERMINE
- **Fichier**: `core/views.py`
- **Fonction**: Lors de la terminaison de la dernière étape
- **Destinataires**: Équipe + admins
- **Priorité**: MOYENNE

#### 1.4 PROJET_SUSPENDU
- **Fichier**: `core/views.py`
- **Fonction**: `modifier_projet()` - changement de statut
- **Destinataires**: Équipe
- **Priorité**: MOYENNE

#### 1.5 ALERTE_FIN_PROJET (déjà implémenté comme ECHEANCE_J7)
- **Statut**: ✅ Déjà implémenté
- **Fichier**: `core/management/commands/check_project_deadlines.py`

---

### Phase 2: Notifications d'Étapes (5 notifications)

#### 2.1 ETAPE_TERMINEE
- **Fichier**: `core/views.py`
- **Fonction**: `terminer_etape()`
- **Destinataires**: Responsable projet + admins
- **Priorité**: HAUTE

#### 2.2 ETAPE_ACTIVEE
- **Fichier**: `core/views.py`
- **Fonction**: Lors de l'activation d'une étape
- **Destinataires**: Équipe projet
- **Priorité**: MOYENNE

#### 2.3 MODULES_DISPONIBLES
- **Fichier**: `core/views.py`
- **Fonction**: Lors de l'activation de l'étape DEVELOPPEMENT
- **Destinataires**: Développeurs
- **Priorité**: MOYENNE

#### 2.4 RETARD_ETAPE
- **Fichier**: Nouvelle commande ou ajout à `check_project_deadlines.py`
- **Destinataires**: Responsable projet
- **Priorité**: BASSE

#### 2.5 CHANGEMENT_STATUT (étape)
- **Fichier**: `core/views.py`
- **Fonction**: Modification du statut d'une étape
- **Destinataires**: Responsable projet
- **Priorité**: MOYENNE

---

### Phase 3: Notifications de Tâches (5 notifications)

#### 3.1 COMMENTAIRE
- **Fichier**: Nouvelle fonctionnalité à créer
- **Fonction**: Ajout de commentaire sur une tâche
- **Destinataires**: Responsable + créateur
- **Priorité**: BASSE

#### 3.2 MENTION
- **Fichier**: Système de mentions à créer
- **Fonction**: Mention @utilisateur dans un commentaire
- **Destinataires**: Utilisateur mentionné
- **Priorité**: BASSE

#### 3.3 PIECE_JOINTE
- **Fichier**: Fonctionnalité d'upload à créer
- **Fonction**: Upload de fichier sur une tâche
- **Destinataires**: Responsable + équipe
- **Priorité**: BASSE

#### 3.4 ECHEANCE (tâche)
- **Fichier**: Commande automatique
- **Fonction**: Alerte 2 jours avant échéance
- **Destinataires**: Responsable de la tâche
- **Priorité**: MOYENNE

#### 3.5 RETARD (tâche - déjà implémenté)
- **Statut**: ✅ Déjà implémenté
- **Fichier**: `core/management/commands/check_task_deadlines.py`

---

### Phase 4: Notifications de Modules (2 notifications)

#### 4.1 AFFECTATION_MODULE ✅
- **Statut**: ✅ Déjà implémenté
- **Fichier**: `core/views_affectation.py`

#### 4.2 RETRAIT_MODULE ✅
- **Statut**: ✅ Déjà implémenté
- **Fichier**: `core/views_affectation.py`

#### 4.3 CHANGEMENT_ROLE
- **Fichier**: `core/views_affectation.py`
- **Fonction**: Modification du rôle sur un module
- **Destinataires**: Utilisateur concerné
- **Priorité**: MOYENNE

---

### Phase 5: Alertes Système (2 alertes)

#### 5.1 BUDGET_DEPASSE
- **Fichier**: Nouvelle commande à créer
- **Fonction**: Vérification du budget
- **Destinataires**: Responsable + admins
- **Priorité**: BASSE

#### 5.2 ECHEANCE_J3 et ECHEANCE_J1 ✅
- **Statut**: ✅ Déjà implémenté dans le test
- **Fichier**: `core/management/commands/check_project_deadlines.py`

---

## 🚀 Ordre d'Implémentation Recommandé

### Batch 1: Notifications Critiques (30 min)
1. ✅ PROJET_DEMARRE
2. ETAPE_TERMINEE
3. CHANGEMENT_ECHEANCE

### Batch 2: Notifications Importantes (30 min)
4. ETAPE_ACTIVEE
5. MODULES_DISPONIBLES
6. CHANGEMENT_STATUT (étape)

### Batch 3: Notifications Complémentaires (30 min)
7. PROJET_TERMINE
8. PROJET_SUSPENDU
9. CHANGEMENT_ROLE (module)

### Batch 4: Alertes Automatiques (30 min)
10. ECHEANCE (tâche - alerte 2 jours avant)
11. RETARD_ETAPE
12. BUDGET_DEPASSE

### Batch 5: Fonctionnalités Avancées (optionnel)
13. COMMENTAIRE
14. MENTION
15. PIECE_JOINTE

---

## 📝 Template de Code

### Pour les Notifications Simples
```python
# Dans la vue appropriée
NotificationXXX.objects.create(
    destinataire=utilisateur,
    [objet]=objet_concerne,
    type_notification='TYPE',
    titre="Titre court",
    message="Message détaillé",
    emetteur=request.user,
    donnees_contexte={
        'key': 'value'
    }
)
```

### Pour les Notifications à Plusieurs Destinataires
```python
# Récupérer l'équipe
equipe = projet.get_equipe()

# Créer une notification pour chaque membre
for membre in equipe:
    if membre != request.user:  # Pas de notification pour l'émetteur
        NotificationProjet.objects.create(
            destinataire=membre,
            projet=projet,
            type_notification='TYPE',
            titre=f"Titre pour {membre.get_full_name()}",
            message="Message",
            emetteur=request.user
        )
```

---

## ✅ Checklist de Validation

Pour chaque notification implémentée:

- [ ] Code ajouté dans la bonne vue/fonction
- [ ] Type de notification correct
- [ ] Destinataires appropriés
- [ ] Message clair et informatif
- [ ] Données contexte ajoutées si nécessaire
- [ ] Test manuel effectué
- [ ] Email envoyé automatiquement (vérifier les logs)

---

## 📊 Progression

### Notifications Implémentées
- [x] AFFECTATION_RESPONSABLE (NotificationProjet)
- [x] CHANGEMENT_STATUT (NotificationModule)
- [x] ECHEANCE_J3 (AlerteProjet)
- [x] ECHEANCE_J1 (AlerteProjet)
- [ ] PROJET_DEMARRE (NotificationProjet)
- [ ] CHANGEMENT_ECHEANCE (NotificationProjet)
- [ ] ETAPE_TERMINEE (NotificationEtape)
- [ ] ETAPE_ACTIVEE (NotificationEtape)
- [ ] MODULES_DISPONIBLES (NotificationEtape)
- [ ] CHANGEMENT_STATUT (NotificationEtape)
- [ ] PROJET_TERMINE (NotificationProjet)
- [ ] PROJET_SUSPENDU (NotificationProjet)
- [ ] CHANGEMENT_ROLE (NotificationModule)
- [ ] ECHEANCE (NotificationTache - 2j avant)
- [ ] RETARD_ETAPE (NotificationEtape)
- [ ] BUDGET_DEPASSE (AlerteProjet)

**Total**: 4/16 (25%)

---

## 📁 Fichiers à Modifier

1. `core/views_demarrage_projet.py` - PROJET_DEMARRE
2. `core/views.py` - Plusieurs notifications d'étapes et projets
3. `core/views_affectation.py` - CHANGEMENT_ROLE
4. `core/management/commands/check_project_deadlines.py` - Alertes J3/J1
5. Nouvelle commande: `check_task_echeance.py` - Alerte 2j avant tâche
6. Nouvelle commande: `check_budget.py` - Alerte budget dépassé

---

**Date de début**: 15 février 2026
**Objectif**: 33/33 notifications (100%)
