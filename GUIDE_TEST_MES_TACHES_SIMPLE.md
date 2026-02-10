# Guide de Test - Interface "Mes Tâches" Simple

## 🎯 Objectif

Tester la nouvelle interface "Mes Tâches" avec tableau simple et actions rapides via icônes FontAwesome.

## 📋 Prérequis

1. Serveur Django redémarré
2. Au moins un projet avec des tâches
3. Un utilisateur avec des tâches assignées

## 🧪 Scénarios de Test

### Test 1: Redirection depuis une Notification

**Étapes**:
1. Se connecter avec un utilisateur
2. Assigner une tâche à cet utilisateur (depuis un autre compte admin)
3. Vérifier qu'une notification apparaît (icône cloche en haut à droite)
4. Cliquer sur la notification
5. **Résultat attendu**: Redirection vers `/projets/{projet_id}/mes-taches/`

**Validation**:
- ✅ URL correcte: `/projets/{uuid}/mes-taches/`
- ✅ Titre de la page: "Mes Tâches - [Nom du projet]"
- ✅ Affichage du tableau simple

---

### Test 2: Affichage du Tableau

**Étapes**:
1. Accéder à `/projets/{projet_id}/mes-taches/`
2. Observer l'interface

**Validation**:
- ✅ Statistiques affichées en haut:
  - Total
  - En cours
  - Terminées
  - Bloquées
- ✅ Tableau avec colonnes:
  - Tâche (nom + description)
  - Contexte (étape ou module)
  - Statut (badge coloré)
  - Priorité (badge coloré)
  - Échéance (date)
  - Actions (boutons)
- ✅ Pas de barre de progression
- ✅ Design moderne et épuré

---

### Test 3: Bouton "En cours" (Orange)

**Étapes**:
1. Trouver une tâche avec statut "À faire"
2. Cliquer sur le bouton orange avec icône `fa-play-circle`
3. Confirmer l'action dans la popup

**Validation**:
- ✅ Popup de confirmation s'affiche
- ✅ Après confirmation, la page se recharge
- ✅ Le statut de la tâche passe à "En cours"
- ✅ Le badge devient orange
- ✅ Les statistiques se mettent à jour

**Vérification technique**:
```javascript
// Requête envoyée
POST /projets/{projet_id}/taches/{tache_id}/changer-statut/{type_tache}/
Body: statut=EN_COURS
```

---

### Test 4: Bouton "Terminer" (Vert)

**Étapes**:
1. Trouver une tâche avec statut "En cours" ou "À faire"
2. Cliquer sur le bouton vert avec icône `fa-check-circle`
3. Confirmer l'action dans la popup

**Validation**:
- ✅ Popup de confirmation s'affiche
- ✅ Après confirmation, la page se recharge
- ✅ Le statut de la tâche passe à "Terminée"
- ✅ Le badge devient vert
- ✅ Les boutons d'action sont désactivés (grisés)
- ✅ Les statistiques se mettent à jour

**Vérification technique**:
```javascript
// Requête envoyée
POST /projets/{projet_id}/taches/{tache_id}/terminer/{type_tache}/
```

---

### Test 5: Tâches Déjà Terminées

**Étapes**:
1. Trouver une tâche avec statut "Terminée"
2. Observer les boutons d'action

**Validation**:
- ✅ Les boutons sont désactivés (grisés)
- ✅ Icône `fa-check-circle` affichée en gris
- ✅ Pas de possibilité de cliquer

---

### Test 6: Affichage des Tâches d'Étapes et de Modules

**Étapes**:
1. Assigner des tâches d'étapes à l'utilisateur
2. Assigner des tâches de modules à l'utilisateur
3. Accéder à "Mes Tâches"

**Validation**:
- ✅ Les tâches d'étapes s'affichent avec icône `fa-layer-group`
- ✅ Les tâches de modules s'affichent avec icône `fa-puzzle-piece`
- ✅ Toutes les tâches sont dans le même tableau
- ✅ Le contexte (étape ou module) est clairement indiqué

---

### Test 7: Statistiques

**Étapes**:
1. Noter les statistiques initiales
2. Marquer une tâche "En cours"
3. Vérifier les statistiques
4. Terminer une tâche
5. Vérifier les statistiques

**Validation**:
- ✅ Total reste constant
- ✅ "En cours" augmente quand on marque une tâche en cours
- ✅ "Terminées" augmente quand on termine une tâche
- ✅ Les compteurs sont cohérents

---

### Test 8: Responsive Design

**Étapes**:
1. Accéder à "Mes Tâches" sur desktop
2. Réduire la fenêtre du navigateur
3. Accéder depuis un mobile (ou mode responsive)

**Validation**:
- ✅ Le tableau s'adapte à la largeur de l'écran
- ✅ Les statistiques passent en colonne sur mobile
- ✅ Les boutons restent cliquables
- ✅ Le texte reste lisible

---

### Test 9: Aucune Tâche Assignée

**Étapes**:
1. Se connecter avec un utilisateur sans tâches
2. Accéder à "Mes Tâches"

**Validation**:
- ✅ Message affiché: "Aucune tâche assignée"
- ✅ Icône `fa-tasks` affichée
- ✅ Texte explicatif: "Vous n'avez aucune tâche dans ce projet pour le moment."
- ✅ Statistiques à 0

---

### Test 10: Bouton "Retour au projet"

**Étapes**:
1. Accéder à "Mes Tâches"
2. Cliquer sur le bouton "Retour au projet" en haut à droite

**Validation**:
- ✅ Redirection vers `/projets/{projet_id}/`
- ✅ Affichage de la page de détail du projet

---

## 🐛 Problèmes Potentiels

### Problème 1: Erreur 404 sur les actions

**Symptôme**: Clic sur bouton → Erreur 404

**Vérification**:
```python
# Dans core/urls.py, vérifier que ces routes existent:
path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/terminer/<str:type_tache>/', 
     views.terminer_tache_view, name='terminer_tache')

path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/changer-statut/<str:type_tache>/', 
     views.changer_statut_ma_tache_view, name='changer_statut_ma_tache')
```

### Problème 2: CSRF Token manquant

**Symptôme**: Erreur 403 Forbidden

**Solution**: Vérifier que `{{ csrf_token }}` est présent dans le template

### Problème 3: Statistiques incorrectes

**Symptôme**: Les compteurs ne correspondent pas

**Vérification**: Vérifier la logique dans `mes_taches_view()` ligne ~4254

---

## 📊 Checklist de Validation

- [ ] Redirection depuis notification fonctionne
- [ ] Tableau simple s'affiche correctement
- [ ] Statistiques sont correctes
- [ ] Bouton "En cours" fonctionne
- [ ] Bouton "Terminer" fonctionne
- [ ] Tâches terminées sont désactivées
- [ ] Tâches d'étapes et de modules s'affichent
- [ ] Design responsive fonctionne
- [ ] Message "Aucune tâche" s'affiche si vide
- [ ] Bouton "Retour au projet" fonctionne

---

## 🚀 Commandes Utiles

### Redémarrer le serveur
```bash
python manage.py runserver
```

### Créer un utilisateur de test
```bash
python manage.py shell
from core.models import Utilisateur
user = Utilisateur.objects.create_user(
    username='test_user',
    email='test@example.com',
    password='test123',
    first_name='Test',
    last_name='User'
)
```

### Assigner une tâche de test
```python
from core.models import TacheEtape, Utilisateur, EtapeProjet

user = Utilisateur.objects.get(email='test@example.com')
etape = EtapeProjet.objects.first()
tache = TacheEtape.objects.create(
    nom='Tâche de test',
    description='Description de test',
    etape=etape,
    statut='A_FAIRE',
    priorite='MOYENNE'
)
tache.assigner_responsable(user, user)
```

---

## 📝 Rapport de Test

**Date**: ___________  
**Testeur**: ___________  
**Version**: 2026-02-10  

| Test | Statut | Commentaires |
|------|--------|--------------|
| Test 1: Redirection | ⬜ | |
| Test 2: Affichage | ⬜ | |
| Test 3: Bouton "En cours" | ⬜ | |
| Test 4: Bouton "Terminer" | ⬜ | |
| Test 5: Tâches terminées | ⬜ | |
| Test 6: Étapes et modules | ⬜ | |
| Test 7: Statistiques | ⬜ | |
| Test 8: Responsive | ⬜ | |
| Test 9: Aucune tâche | ⬜ | |
| Test 10: Retour projet | ⬜ | |

**Résultat global**: ⬜ Réussi / ⬜ Échec partiel / ⬜ Échec

**Notes**:
_______________________________________
_______________________________________
_______________________________________

---

**Prêt pour les tests!** 🚀
