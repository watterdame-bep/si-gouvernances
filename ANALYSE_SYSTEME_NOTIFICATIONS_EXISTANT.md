# 📬 ANALYSE DU SYSTÈME DE NOTIFICATIONS EXISTANT

## ✅ MODÈLES DE NOTIFICATIONS IMPLÉMENTÉS

### 1. **NotificationTache** (Tâches d'Étape)
**Types de notifications:**
- `ASSIGNATION` - Assignation de tâche
- `CHANGEMENT_STATUT` - Changement de statut
- `COMMENTAIRE` - Nouveau commentaire
- `MENTION` - Mention dans un commentaire
- `ECHEANCE` - Échéance approchante
- `RETARD` - Tâche en retard
- `PIECE_JOINTE` - Nouvelle pièce jointe

**Champs:**
- destinataire (Utilisateur)
- tache (TacheEtape)
- type_notification
- titre, message
- lue (boolean), date_lecture
- emetteur (Utilisateur)
- donnees_contexte (JSON)

---

### 2. **NotificationEtape** (Étapes de Projet)
**Types de notifications:**
- `ETAPE_TERMINEE` - Étape terminée ✅
- `ETAPE_ACTIVEE` - Étape activée
- `MODULES_DISPONIBLES` - Modules disponibles
- `RETARD_ETAPE` - Retard d'étape
- `CHANGEMENT_STATUT` - Changement de statut

**Champs:**
- destinataire (Utilisateur)
- etape (EtapeProjet)
- cas_test (CasTest) - optionnel
- type_notification
- titre, message
- lue (boolean), date_lecture
- emetteur (Utilisateur)
- donnees_contexte (JSON)

---

### 3. **NotificationModule** (Modules de Projet)
**Types de notifications:**
- `AFFECTATION_MODULE` - Affectation au module
- `RETRAIT_MODULE` - Retrait du module
- `NOUVELLE_TACHE` - Nouvelle tâche assignée
- `TACHE_TERMINEE` - Tâche terminée
- `CHANGEMENT_ROLE` - Changement de rôle
- `MODULE_TERMINE` - Module terminé

**Champs:**
- destinataire (Utilisateur)
- module (ModuleProjet)
- type_notification
- titre, message
- lue (boolean), date_lecture
- emetteur (Utilisateur)
- donnees_contexte (JSON)

---

## ✅ NOTIFICATIONS DÉJÀ FONCTIONNELLES

### **1. Étape Terminée** ✅
**Fichier:** `core/models.py` - fonction `terminer_etape()`
**Fichier:** `core/utils.py` - fonction `envoyer_notification_etape_terminee()`

**Destinataires actuels:**
- ✅ Tous les super admins (is_superuser=True)
- ✅ Tous les chefs de projet système (role_systeme='CHEF_PROJET')

**Fonctionnement:**
- Envoi d'email
- Création de NotificationEtape
- Informations sur l'étape suivante activée

**Code:**
```python
def terminer_etape(self, utilisateur):
    # ...
    self.statut = 'TERMINEE'
    self.date_fin_reelle = timezone.now()
    self.save()
    
    # Envoyer les notifications
    envoyer_notification_etape_terminee(self, utilisateur)
    
    # Activer l'étape suivante
    if etape_suivante:
        etape_suivante.statut = 'EN_COURS'
        etape_suivante.save()
```

---

### **2. Tâche Terminée** ✅
**Fichier:** `core/views.py` - fonction `terminer_tache_etape()`

**Destinataires actuels:**
- ✅ Responsable principal du projet
- ✅ Responsable de la tâche (si différent)
- ✅ Tous les administrateurs

**Fonctionnement:**
- Création de NotificationTache
- Type: 'CHANGEMENT_STATUT'
- Notification pour chaque destinataire

**Code:**
```python
def terminer_tache_etape(request, projet_id, etape_id, tache_id):
    # ...
    tache.statut = 'TERMINEE'
    tache.save()
    
    # Notification au responsable principal
    if responsable_principal:
        NotificationTache.objects.create(
            destinataire=responsable_principal,
            tache=tache,
            type_notification='CHANGEMENT_STATUT',
            titre=f'Tâche terminée: {tache.nom}',
            message=f'La tâche "{tache.nom}" a été terminée',
            emetteur=user
        )
    
    # Notification au responsable de la tâche
    if tache.responsable:
        NotificationTache.objects.create(...)
    
    # Notification aux administrateurs
    for admin in administrateurs:
        NotificationTache.objects.create(...)
```

---

### **3. Changement de Statut de Tâche** ✅
**Fichier:** `core/models.py` - fonction `_creer_notifications_changement_statut()`

**Destinataires actuels:**
- ✅ Responsable de la tâche
- ✅ Créateur de la tâche
- ✅ Responsable principal du projet

**Fonctionnement:**
- Notification automatique via la méthode du modèle
- Évite les doublons (set de destinataires)

---

### **4. Tâche Module Terminée** ⚠️ PARTIEL
**Fichier:** `core/views_taches_module.py`

**Problème:** Les notifications utilisent un ancien champ `utilisateur` au lieu de `destinataire`

**Code actuel (INCORRECT):**
```python
NotificationModule.objects.create(
    utilisateur=responsable,  # ❌ Devrait être 'destinataire'
    type_notification='TACHE_ASSIGNEE',
    ...
)
```

---

## ❌ NOTIFICATIONS MANQUANTES

### **1. Étape Terminée - Responsable Projet**
**Besoin:** Notifier le responsable principal du projet quand une étape est terminée
**Actuellement:** Seulement les admins et chefs de projet système

### **2. Tâche Module Terminée - Responsable Équipe**
**Besoin:** Notifier le responsable de l'équipe du module
**Actuellement:** Notifications cassées (mauvais champ)

### **3. Sous-tâche Terminée - Responsable**
**Besoin:** Notifier le responsable quand une sous-tâche est terminée
**Actuellement:** Pas implémenté

### **4. Paramètre Projet - Notifications Admin**
**Besoin:** Bouton dans les paramètres du projet pour activer/désactiver les notifications admin
**Actuellement:** Pas implémenté

---

## 🔧 CORRECTIONS NÉCESSAIRES

### **1. Corriger NotificationModule**
Remplacer `utilisateur` par `destinataire` dans:
- `core/views_taches_module.py` (3 occurrences)
- `core/utils.py` (2 occurrences)

### **2. Ajouter Champ au Modèle Projet**
```python
class Projet(models.Model):
    # ...
    notifications_admin_activees = models.BooleanField(
        default=False,
        help_text="L'administrateur reçoit les notifications de ce projet"
    )
```

### **3. Améliorer Logique Notifications Étape**
```python
def envoyer_notification_etape_terminee(etape, utilisateur):
    destinataires = []
    
    # 1. Responsable principal du projet (TOUJOURS)
    responsable = etape.projet.get_responsable_principal()
    if responsable:
        destinataires.append(responsable)
    
    # 2. Administrateurs (SI activé dans paramètres)
    if etape.projet.notifications_admin_activees:
        admins = Utilisateur.objects.filter(is_superuser=True)
        destinataires.extend(admins)
```

### **4. Améliorer Notifications Tâche Module**
```python
def terminer_tache_module(request, module_id, tache_id):
    # ...
    tache.statut = 'TERMINEE'
    tache.save()
    
    # Notifier le responsable de l'équipe
    responsable_equipe = module.get_responsable()
    if responsable_equipe:
        NotificationModule.objects.create(
            destinataire=responsable_equipe,  # ✅ Correct
            module=module,
            type_notification='TACHE_TERMINEE',
            titre=f'Tâche terminée: {tache.nom}',
            message=f'La tâche "{tache.nom}" du module "{module.nom}" a été terminée',
            emetteur=request.user
        )
```

---

## 📊 RÉSUMÉ

| Fonctionnalité | Statut | Destinataires | Action |
|----------------|--------|---------------|--------|
| Étape terminée | ✅ Partiel | Admins + Chefs projet | Ajouter responsable projet |
| Tâche étape terminée | ✅ OK | Responsable projet + tâche + admins | OK |
| Tâche module terminée | ❌ Cassé | Aucun (bug) | Corriger champ |
| Sous-tâche terminée | ❌ Manquant | - | À implémenter |
| Paramètre notifications admin | ❌ Manquant | - | À implémenter |

---

## 🎯 PLAN D'ACTION

1. ✅ **Analyser l'existant** (FAIT)
2. ⏳ **Corriger NotificationModule** (champ destinataire)
3. ⏳ **Ajouter champ notifications_admin_activees au modèle Projet**
4. ⏳ **Modifier logique notifications étape terminée**
5. ⏳ **Implémenter notifications tâche module terminée**
6. ⏳ **Implémenter notifications sous-tâche terminée**
7. ⏳ **Ajouter interface paramètres notifications dans projet**

---

**Date:** 09/02/2026  
**Statut:** ✅ ANALYSE COMPLÈTE
