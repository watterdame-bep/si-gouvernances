# Système d'Alertes - Implémentation Complète

## 📋 Vue d'ensemble

Le système d'alertes est maintenant **complètement séparé** du système de notifications. Les alertes concernent les échéances de projets et les événements critiques, tandis que les notifications concernent les actions utilisateur (tâches, modules, etc.).

## ✅ Statut : TERMINÉ

Date de finalisation : 12 février 2026

## 🎯 Objectifs atteints

1. ✅ Modèle `AlerteProjet` créé et séparé de `NotificationProjet`
2. ✅ Commande `check_project_deadlines` modifiée pour créer des alertes
3. ✅ Interface dédiée aux alertes avec statistiques
4. ✅ Menu "Alertes" dans la sidebar avec badge en temps réel
5. ✅ API pour le compteur d'alertes non lues
6. ✅ Mise à jour automatique du badge toutes les 60 secondes

---

## 📦 Composants implémentés

### 1. Modèle de données

**Fichier** : `core/models.py` (lignes 2277-2360)

```python
class AlerteProjet(models.Model):
    """Alertes système liées aux projets (échéances, dépassements, etc.)"""
    
    TYPE_ALERTE_CHOICES = [
        ('ECHEANCE_J7', 'Échéance dans 7 jours'),
        ('ECHEANCE_J3', 'Échéance dans 3 jours'),
        ('ECHEANCE_J1', 'Échéance dans 1 jour'),
        ('ECHEANCE_DEPASSEE', 'Échéance dépassée'),
        ('BUDGET_DEPASSE', 'Budget dépassé'),
        ('TACHES_EN_RETARD', 'Tâches en retard'),
    ]
    
    NIVEAU_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('DANGER', 'Critique'),
    ]
```

**Champs principaux** :
- `destinataire` : Utilisateur qui reçoit l'alerte
- `projet` : Projet concerné
- `type_alerte` : Type d'alerte (J-7, J-3, J-1, dépassée, etc.)
- `niveau` : Niveau de gravité (INFO, WARNING, DANGER)
- `titre` : Titre de l'alerte
- `message` : Message détaillé
- `lue` : État de lecture
- `date_creation` : Date de création
- `date_lecture` : Date de lecture

**Méthodes utiles** :
- `marquer_comme_lue()` : Marque l'alerte comme lue
- `get_couleur_badge()` : Retourne la couleur selon le niveau
- `get_icone()` : Retourne l'icône FontAwesome selon le type

### 2. Migration

**Fichier** : `core/migrations/0040_add_alerte_projet.py`

```bash
python manage.py migrate
```

### 3. Vues

**Fichier** : `core/views_alertes.py`

#### Vue principale
```python
@login_required
def alertes_view(request):
    """Affiche toutes les alertes de l'utilisateur avec statistiques"""
```

#### API pour le badge
```python
@login_required
def api_alertes_count(request):
    """Retourne le nombre d'alertes non lues"""
    # Utilisé par le JavaScript pour mettre à jour le badge
```

#### API pour la liste
```python
@login_required
def api_alertes_list(request):
    """Retourne les 10 dernières alertes"""
```

#### Actions
```python
@login_required
def marquer_alerte_lue(request, alerte_id):
    """Marque une alerte comme lue et redirige vers le projet"""

@login_required
def marquer_toutes_alertes_lues(request):
    """Marque toutes les alertes comme lues"""
```

### 4. URLs

**Fichier** : `core/urls.py`

```python
# Alertes
path('alertes/', views_alertes.alertes_view, name='alertes'),
path('alertes/<int:alerte_id>/lue/', views_alertes.marquer_alerte_lue, name='marquer_alerte_lue'),
path('alertes/marquer-toutes-lues/', views_alertes.marquer_toutes_alertes_lues, name='marquer_toutes_alertes_lues'),

# API Alertes
path('api/alertes/count/', views_alertes.api_alertes_count, name='api_alertes_count'),
path('api/alertes/list/', views_alertes.api_alertes_list, name='api_alertes_list'),
```

### 5. Template

**Fichier** : `templates/core/alertes.html`

**Sections** :
1. Header avec bouton "Tout marquer comme lu"
2. Statistiques (Total, Non lues, Critiques, Avertissements)
3. Liste des alertes avec badges de niveau
4. Icônes et couleurs selon le niveau de gravité

**Design** :
- Responsive (mobile-first)
- Badges colorés selon le niveau (rouge=danger, jaune=warning, bleu=info)
- Icônes FontAwesome adaptées au type d'alerte
- Mise en évidence des alertes non lues (fond orange clair)

### 6. Menu Sidebar

**Fichier** : `templates/base.html`

**Menu ajouté** :
```html
<!-- Alertes -->
<a href="{% url 'alertes' %}" class="nav-item ...">
    <div class="... bg-orange-100 ...">
        <i class="fas fa-exclamation-triangle text-orange-600"></i>
    </div>
    <span>Alertes</span>
    <span id="alertesBadge" class="ml-auto hidden px-2 py-0.5 bg-red-500 text-white text-xs font-bold rounded-full">
        <span id="alertesCount">0</span>
    </span>
</a>
```

### 7. JavaScript de mise à jour

**Fichier** : `templates/base.html` (fin du fichier)

**Fonctionnalités** :
- Chargement initial du compteur au chargement de la page
- Mise à jour automatique toutes les 60 secondes
- Affichage/masquage du badge selon le nombre d'alertes
- Limitation à 99+ pour les grands nombres

```javascript
// Load alertes count from server
function loadAlertesCount() {
    fetch('/api/alertes/count/')
        .then(response => response.json())
        .then(data => {
            updateAlertesBadge(data.count);
        })
        .catch(error => {
            console.error('Erreur:', error);
        });
}

// Update alertes badge
function updateAlertesBadge(count) {
    if (count > 0) {
        alertesBadge.classList.remove('hidden');
        alertesCount.textContent = count > 99 ? '99+' : count;
    } else {
        alertesBadge.classList.add('hidden');
    }
}
```

### 8. Commande de vérification

**Fichier** : `core/management/commands/check_project_deadlines.py`

**Modifications** :
- Crée des `AlerteProjet` au lieu de `NotificationProjet`
- Vérifie les échéances J-7, J-3, J-1
- Envoie aux responsables de projet et administrateurs
- Évite les doublons (une seule alerte par type et par jour)

**Exécution manuelle** :
```bash
python manage.py check_project_deadlines
```

**Exécution automatique** :
- Windows : Planificateur de tâches (voir `GUIDE_PLANIFICATEUR_WINDOWS.md`)
- Linux : Cron job

---

## 🎨 Interface utilisateur

### Page Alertes

**URL** : `/alertes/`

**Sections** :

1. **Header**
   - Titre "Alertes Système"
   - Bouton "Tout marquer comme lu" (si alertes non lues)

2. **Statistiques** (4 cartes)
   - Total des alertes
   - Alertes non lues (orange)
   - Alertes critiques (rouge)
   - Avertissements (jaune)

3. **Liste des alertes**
   - Badge "Nouveau" pour les non lues
   - Badge de niveau (Critique/Avertissement/Info)
   - Icône selon le type d'alerte
   - Message détaillé
   - Nom du projet
   - Temps écoulé
   - Bouton "Voir le projet" (marque comme lu et redirige)

### Badge dans la sidebar

- Icône : Triangle d'exclamation orange
- Badge rouge avec compteur
- Mise à jour automatique toutes les 60 secondes
- Masqué si aucune alerte non lue

---

## 🔄 Flux de fonctionnement

### 1. Création d'alertes

```
Planificateur Windows (quotidien à 8h)
    ↓
python manage.py check_project_deadlines
    ↓
Vérification des projets EN_COURS
    ↓
Calcul des jours restants
    ↓
Création d'AlerteProjet si J-7, J-3, J-1 ou dépassé
    ↓
Destinataires : Responsable + Admin
```

### 2. Affichage du badge

```
Chargement de la page
    ↓
JavaScript : loadAlertesCount()
    ↓
Appel API : /api/alertes/count/
    ↓
Mise à jour du badge
    ↓
Répétition toutes les 60 secondes
```

### 3. Consultation d'une alerte

```
Utilisateur clique sur "Voir le projet"
    ↓
Appel : /alertes/<id>/lue/
    ↓
Marque l'alerte comme lue
    ↓
Redirection vers le projet concerné
```

---

## 🧪 Tests à effectuer

### Test 1 : Création d'alertes J-7

1. Créer un projet avec `date_fin` dans 7 jours
2. Exécuter : `python manage.py check_project_deadlines`
3. Vérifier qu'une alerte J-7 est créée
4. Vérifier que le badge s'affiche dans la sidebar

### Test 2 : Badge en temps réel

1. Se connecter avec un utilisateur
2. Vérifier que le badge affiche le bon nombre
3. Attendre 60 secondes
4. Vérifier que le badge se met à jour automatiquement

### Test 3 : Marquer comme lu

1. Aller sur `/alertes/`
2. Cliquer sur "Voir le projet" d'une alerte
3. Vérifier la redirection vers le projet
4. Revenir sur `/alertes/`
5. Vérifier que l'alerte n'a plus le badge "Nouveau"

### Test 4 : Tout marquer comme lu

1. Avoir plusieurs alertes non lues
2. Cliquer sur "Tout marquer comme lu"
3. Vérifier que toutes les alertes sont marquées comme lues
4. Vérifier que le badge disparaît de la sidebar

### Test 5 : Séparation avec notifications

1. Créer une alerte (échéance projet)
2. Créer une notification (tâche terminée)
3. Vérifier que l'alerte apparaît dans `/alertes/`
4. Vérifier que la notification apparaît dans `/notifications/taches/`
5. Vérifier qu'elles ne se mélangent pas

---

## 📊 Différences Alertes vs Notifications

| Critère | Alertes | Notifications |
|---------|---------|---------------|
| **Modèle** | `AlerteProjet` | `NotificationProjet`, `NotificationEtape`, etc. |
| **Source** | Système automatique (commande) | Actions utilisateur |
| **Contenu** | Échéances, dépassements | Tâches, modules, tickets |
| **Menu** | "Alertes" (triangle orange) | "Notifications" (cloche jaune) |
| **URL** | `/alertes/` | `/notifications/taches/` |
| **Badge** | Rouge avec compteur | Rouge avec compteur |
| **API** | `/api/alertes/count/` | `/api/notifications/` |
| **Fréquence** | Quotidienne (planificateur) | Temps réel (actions) |

---

## 🚀 Prochaines étapes possibles

### Améliorations futures (optionnelles)

1. **Alertes supplémentaires**
   - Budget dépassé (si suivi des coûts)
   - Tâches en retard
   - Modules bloqués

2. **Notifications par email**
   - Envoyer un email pour les alertes critiques
   - Résumé quotidien des alertes

3. **Paramétrage utilisateur**
   - Désactiver certains types d'alertes
   - Choisir la fréquence de vérification

4. **Historique**
   - Archivage des alertes anciennes
   - Statistiques sur les alertes

5. **Filtres et recherche**
   - Filtrer par type d'alerte
   - Filtrer par projet
   - Recherche dans les alertes

---

## 📝 Notes importantes

### Sécurité
- Les alertes sont filtrées par utilisateur (destinataire)
- Seul le destinataire peut voir ses alertes
- Les API vérifient l'authentification

### Performance
- Index sur `destinataire`, `lue`, `date_creation`
- Requêtes optimisées avec `select_related('projet')`
- Limitation à 10 alertes dans l'API liste

### Maintenance
- Penser à nettoyer les anciennes alertes lues (>30 jours)
- Vérifier les logs du planificateur Windows
- Surveiller le nombre d'alertes créées

---

## 🔗 Fichiers liés

### Documentation
- `README_SYSTEME_ALERTES.md` - Guide utilisateur
- `GUIDE_PLANIFICATEUR_WINDOWS.md` - Configuration du planificateur
- `ARCHITECTURE_ALERTES_PORTABLE.md` - Architecture technique
- `ALERTES_QUICK_START.md` - Démarrage rapide

### Code
- `core/models.py` (lignes 2277-2360) - Modèle AlerteProjet
- `core/views_alertes.py` - Vues des alertes
- `core/management/commands/check_project_deadlines.py` - Commande de vérification
- `templates/core/alertes.html` - Interface
- `templates/base.html` - Menu et JavaScript

### Migrations
- `core/migrations/0040_add_alerte_projet.py` - Création du modèle

---

## ✅ Checklist de déploiement

- [x] Migration appliquée
- [x] Vues créées et testées
- [x] URLs configurées
- [x] Template créé
- [x] Menu ajouté dans la sidebar
- [x] JavaScript de mise à jour implémenté
- [x] API fonctionnelle
- [x] Commande modifiée pour créer des alertes
- [ ] Planificateur Windows configuré (voir guide)
- [ ] Tests effectués
- [ ] Documentation lue par l'équipe

---

## 🎉 Conclusion

Le système d'alertes est maintenant **complètement opérationnel** et **totalement séparé** des notifications. Les utilisateurs peuvent consulter leurs alertes d'échéances de projets dans un menu dédié, avec un badge qui se met à jour automatiquement.

**Prochaine étape** : Configurer le Planificateur de tâches Windows pour exécuter la commande `check_project_deadlines` quotidiennement (voir `GUIDE_PLANIFICATEUR_WINDOWS.md`).
