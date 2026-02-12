# Guide de Test - Système d'Alertes

## 🎯 Objectif

Vérifier que le système d'alertes fonctionne correctement et est bien séparé des notifications.

---

## ✅ Prérequis

1. Migration appliquée : `python manage.py migrate`
2. Serveur de développement lancé : `python manage.py runserver`
3. Au moins un projet avec une date de fin définie

---

## 🧪 Tests à effectuer

### Test 1 : Création manuelle d'une alerte J-7

**Objectif** : Vérifier que la commande crée bien des alertes

**Étapes** :

1. **Créer un projet de test**
   ```python
   # Dans le shell Django (python manage.py shell)
   from core.models import Projet, StatutProjet, Utilisateur
   from datetime import date, timedelta
   
   # Récupérer un utilisateur admin
   admin = Utilisateur.objects.filter(is_superuser=True).first()
   
   # Récupérer le statut EN_COURS
   statut = StatutProjet.objects.get(nom='EN_COURS')
   
   # Créer un projet qui se termine dans 7 jours
   projet = Projet.objects.create(
       nom="Projet Test Alerte J-7",
       description="Projet pour tester les alertes",
       client="Client Test",
       budget_previsionnel=10000,
       statut=statut,
       createur=admin,
       date_debut=date.today(),
       date_fin=date.today() + timedelta(days=7)
   )
   
   # Affecter l'admin comme responsable
   from core.models import Affectation, RoleProjet
   role_resp = RoleProjet.objects.get(nom='RESPONSABLE_PRINCIPAL')
   Affectation.objects.create(
       utilisateur=admin,
       projet=projet,
       role_projet=role_resp,
       est_responsable_principal=True
   )
   ```

2. **Exécuter la commande de vérification**
   ```bash
   python manage.py check_project_deadlines
   ```

3. **Vérifier la création de l'alerte**
   ```python
   # Dans le shell Django
   from core.models import AlerteProjet
   
   alertes = AlerteProjet.objects.filter(projet__nom="Projet Test Alerte J-7")
   print(f"Nombre d'alertes créées : {alertes.count()}")
   
   for alerte in alertes:
       print(f"- Type: {alerte.type_alerte}")
       print(f"  Niveau: {alerte.niveau}")
       print(f"  Titre: {alerte.titre}")
       print(f"  Destinataire: {alerte.destinataire.get_full_name()}")
   ```

**Résultat attendu** :
- Une alerte de type `ECHEANCE_J7` créée
- Niveau `WARNING`
- Destinataire = responsable du projet + admin

---

### Test 2 : Affichage du badge dans la sidebar

**Objectif** : Vérifier que le badge d'alertes s'affiche correctement

**Étapes** :

1. Se connecter avec l'utilisateur qui a reçu l'alerte
2. Observer la sidebar
3. Vérifier que le menu "Alertes" affiche un badge rouge avec le nombre d'alertes

**Résultat attendu** :
- Badge rouge visible avec le chiffre "1" (ou plus)
- Badge positionné à droite du texte "Alertes"

**Capture d'écran** :
```
Alertes [1]  ← Badge rouge
```

---

### Test 3 : Page des alertes

**Objectif** : Vérifier l'interface de consultation des alertes

**Étapes** :

1. Cliquer sur le menu "Alertes" dans la sidebar
2. Vérifier l'affichage de la page `/alertes/`

**Résultat attendu** :

**Header** :
- Titre "Alertes Système"
- Bouton "Tout marquer comme lu" visible

**Statistiques** (4 cartes) :
- Total : 1
- Non lues : 1 (orange)
- Critiques : 0 (rouge)
- Avertissements : 1 (jaune)

**Liste des alertes** :
- Une alerte affichée
- Badge "Nouveau" visible
- Badge "Avertissement" visible
- Icône d'horloge (fa-clock)
- Titre : "Projet proche de l'échéance"
- Message : "Le projet [Nom] arrive à échéance dans 7 jours..."
- Nom du projet affiché
- Temps écoulé affiché ("À l'instant" ou "Il y a X min")
- Bouton "Voir le projet" visible

---

### Test 4 : Marquer une alerte comme lue

**Objectif** : Vérifier que le marquage comme lu fonctionne

**Étapes** :

1. Sur la page `/alertes/`, cliquer sur "Voir le projet" d'une alerte
2. Vérifier la redirection vers la page du projet
3. Revenir sur `/alertes/`
4. Observer l'alerte

**Résultat attendu** :
- Redirection vers `/projets/<uuid>/detail/`
- Badge "Nouveau" disparu
- Fond de l'alerte changé (plus de fond orange clair)
- Statistiques mises à jour :
  - Non lues : 0
  - Badge dans la sidebar disparu

---

### Test 5 : Tout marquer comme lu

**Objectif** : Vérifier le marquage en masse

**Étapes** :

1. Créer plusieurs alertes (répéter Test 1 avec différentes dates)
2. Aller sur `/alertes/`
3. Vérifier que plusieurs alertes non lues sont affichées
4. Cliquer sur "Tout marquer comme lu"
5. Observer le résultat

**Résultat attendu** :
- Toutes les alertes marquées comme lues
- Badge "Nouveau" disparu de toutes les alertes
- Statistiques "Non lues" = 0
- Badge dans la sidebar disparu
- Bouton "Tout marquer comme lu" disparu

---

### Test 6 : Mise à jour automatique du badge

**Objectif** : Vérifier que le badge se met à jour automatiquement

**Étapes** :

1. Ouvrir deux onglets du navigateur
2. Se connecter avec le même utilisateur dans les deux onglets
3. Dans l'onglet 1 : rester sur le dashboard
4. Dans l'onglet 2 : créer une nouvelle alerte (via shell ou commande)
5. Attendre 60 secondes maximum
6. Observer l'onglet 1

**Résultat attendu** :
- Le badge dans la sidebar de l'onglet 1 se met à jour automatiquement
- Le nouveau nombre d'alertes s'affiche sans recharger la page

**Note** : Le JavaScript vérifie toutes les 60 secondes

---

### Test 7 : API du compteur d'alertes

**Objectif** : Vérifier que l'API fonctionne correctement

**Étapes** :

1. Se connecter avec un utilisateur
2. Ouvrir la console développeur du navigateur (F12)
3. Aller dans l'onglet "Network" (Réseau)
4. Recharger la page
5. Chercher la requête vers `/api/alertes/count/`
6. Vérifier la réponse

**Résultat attendu** :
```json
{
    "count": 1
}
```

**Vérification dans la console** :
```javascript
// Exécuter dans la console du navigateur
fetch('/api/alertes/count/')
    .then(r => r.json())
    .then(data => console.log('Alertes non lues:', data.count));
```

---

### Test 8 : Séparation Alertes / Notifications

**Objectif** : Vérifier que les alertes et notifications sont bien séparées

**Étapes** :

1. **Créer une alerte** (échéance projet)
   ```bash
   python manage.py check_project_deadlines
   ```

2. **Créer une notification** (terminer une tâche)
   - Aller sur un projet
   - Terminer une tâche d'étape

3. **Vérifier la séparation**
   - Aller sur `/alertes/` → Voir uniquement l'alerte d'échéance
   - Aller sur `/notifications/taches/` → Voir uniquement la notification de tâche

**Résultat attendu** :
- Les alertes n'apparaissent PAS dans `/notifications/taches/`
- Les notifications n'apparaissent PAS dans `/alertes/`
- Deux badges distincts dans la sidebar :
  - Badge "Notifications" (cloche jaune)
  - Badge "Alertes" (triangle orange)

---

### Test 9 : Différents types d'alertes

**Objectif** : Vérifier tous les types d'alertes

**Étapes** :

1. **Alerte J-7** (WARNING)
   ```python
   # Projet qui se termine dans 7 jours
   date_fin = date.today() + timedelta(days=7)
   ```

2. **Alerte J-3** (WARNING)
   ```python
   # Projet qui se termine dans 3 jours
   date_fin = date.today() + timedelta(days=3)
   ```

3. **Alerte J-1** (DANGER)
   ```python
   # Projet qui se termine dans 1 jour
   date_fin = date.today() + timedelta(days=1)
   ```

4. **Alerte dépassée** (DANGER)
   ```python
   # Projet qui devait se terminer hier
   date_fin = date.today() - timedelta(days=1)
   ```

5. Exécuter la commande pour chaque projet
   ```bash
   python manage.py check_project_deadlines
   ```

**Résultat attendu** :

| Type | Niveau | Icône | Couleur badge |
|------|--------|-------|---------------|
| J-7 | WARNING | fa-clock | Jaune |
| J-3 | WARNING | fa-exclamation-circle | Jaune |
| J-1 | DANGER | fa-exclamation-triangle | Rouge |
| Dépassée | DANGER | fa-times-circle | Rouge |

**Statistiques attendues** :
- Total : 4
- Non lues : 4
- Critiques : 2 (J-1 + Dépassée)
- Avertissements : 2 (J-7 + J-3)

---

### Test 10 : Éviter les doublons

**Objectif** : Vérifier qu'une seule alerte est créée par jour

**Étapes** :

1. Créer un projet qui se termine dans 7 jours
2. Exécuter la commande deux fois de suite
   ```bash
   python manage.py check_project_deadlines
   python manage.py check_project_deadlines
   ```
3. Vérifier le nombre d'alertes créées

**Résultat attendu** :
- Une seule alerte créée (pas de doublon)
- La commande détecte qu'une alerte existe déjà pour ce jour

---

## 🐛 Problèmes courants

### Le badge ne s'affiche pas

**Causes possibles** :
1. Aucune alerte non lue
2. JavaScript non chargé
3. Erreur dans la console

**Solution** :
1. Vérifier qu'il y a des alertes non lues : `/alertes/`
2. Ouvrir la console (F12) et chercher des erreurs
3. Vérifier que l'API répond : `/api/alertes/count/`

### Les alertes n'apparaissent pas

**Causes possibles** :
1. Migration non appliquée
2. Commande non exécutée
3. Projet sans date de fin

**Solution** :
1. Exécuter : `python manage.py migrate`
2. Exécuter : `python manage.py check_project_deadlines`
3. Vérifier que le projet a `date_fin` définie

### Le badge ne se met pas à jour

**Causes possibles** :
1. JavaScript désactivé
2. Erreur réseau
3. API non accessible

**Solution** :
1. Vérifier la console pour les erreurs
2. Tester l'API manuellement : `/api/alertes/count/`
3. Recharger la page

---

## 📊 Résultats attendus

### Checklist complète

- [ ] Test 1 : Alerte J-7 créée ✅
- [ ] Test 2 : Badge affiché dans la sidebar ✅
- [ ] Test 3 : Page des alertes fonctionnelle ✅
- [ ] Test 4 : Marquage comme lu fonctionne ✅
- [ ] Test 5 : Marquage en masse fonctionne ✅
- [ ] Test 6 : Mise à jour automatique du badge ✅
- [ ] Test 7 : API répond correctement ✅
- [ ] Test 8 : Séparation alertes/notifications ✅
- [ ] Test 9 : Tous les types d'alertes fonctionnent ✅
- [ ] Test 10 : Pas de doublons ✅

---

## 🎉 Validation finale

Si tous les tests passent, le système d'alertes est **opérationnel** et prêt pour la production.

**Prochaine étape** : Configurer le Planificateur de tâches Windows pour exécuter la commande quotidiennement (voir `GUIDE_PLANIFICATEUR_WINDOWS.md`).
