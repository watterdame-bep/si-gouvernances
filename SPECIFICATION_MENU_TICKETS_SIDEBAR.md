# Spécification : Menu Tickets dans la Sidebar

## 📅 Date : 12 février 2026

## 🎯 Objectif

Ajouter un système de navigation professionnel pour les tickets de maintenance dans la sidebar, avec une gestion basée sur les rôles et permissions, inspiré de Jira.

## 📋 Structure du Menu

```
📋 Tickets
   ├── 👤 Mes tickets (badge: X)
   ├── 📁 Tickets du projet (si membre)
   └── 🌐 Tous les tickets (Admin uniquement)
```

## 🔐 Règles de Sécurité et Permissions

### 1️⃣ Mes Tickets

**Affichage** : Tous les utilisateurs connectés

**Logique Backend** :
```python
tickets = TicketMaintenance.objects.filter(
    assignes_a=request.user
).select_related('projet', 'cree_par').order_by('-date_creation')
```

**Données affichées** :
- Numéro du ticket
- Titre
- Priorité (badge coloré)
- Statut (badge avec icône)
- Projet lié
- Date de création
- Date limite (si existe)

**Badge compteur** : Nombre de tickets assignés non fermés

### 2️⃣ Tickets du Projet

**Affichage** : Conditionnel

**Logique de visibilité** :
```python
# L'utilisateur peut voir les tickets d'un projet si :
- Il est membre du projet (dans l'équipe)
- OU il est responsable du projet
- OU il est Administrateur
```

**Logique Backend** :
```python
# Récupérer les projets accessibles
projets_accessibles = []

if user.est_super_admin():
    projets_accessibles = Projet.objects.all()
else:
    # Projets où l'utilisateur est membre
    projets_membre = Projet.objects.filter(
        membres__utilisateur=user
    )
    
    # Projets où l'utilisateur est responsable
    projets_responsable = Projet.objects.filter(
        affectations__utilisateur=user,
        affectations__role__nom='RESPONSABLE_PROJET'
    )
    
    projets_accessibles = (projets_membre | projets_responsable).distinct()

# Récupérer les tickets de ces projets
tickets = TicketMaintenance.objects.filter(
    projet__in=projets_accessibles
).select_related('projet', 'cree_par').prefetch_related('assignes_a')
```

**Interface** :
- Sélecteur de projet (dropdown)
- Liste des tickets du projet sélectionné
- Filtres par statut

### 3️⃣ Tous les Tickets

**Affichage** : Administrateur uniquement

**Logique Backend** :
```python
if not user.est_super_admin():
    return redirect('mes_tickets')  # Ou 403 Forbidden

tickets = TicketMaintenance.objects.all().select_related(
    'projet', 'cree_par'
).prefetch_related('assignes_a').order_by('-date_creation')
```

**Fonctionnalités** :
- Vue globale de tous les tickets
- Filtres avancés (projet, statut, priorité, assigné)
- Statistiques globales

## 🛡️ Sécurité Backend

### Décorateurs de Permission

```python
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def ticket_access_required(view_func):
    """Vérifie que l'utilisateur a accès au ticket"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        ticket_id = kwargs.get('ticket_id')
        ticket = get_object_or_404(TicketMaintenance, id=ticket_id)
        user = request.user
        
        # Admin : accès total
        if user.est_super_admin():
            return view_func(request, *args, **kwargs)
        
        # Assigné au ticket
        if user in ticket.assignes_a.all():
            return view_func(request, *args, **kwargs)
        
        # Membre ou responsable du projet
        if user.a_acces_projet(ticket.projet):
            return view_func(request, *args, **kwargs)
        
        # Accès refusé
        messages.error(request, 'Vous n\'avez pas accès à ce ticket.')
        return redirect('mes_tickets')
    
    return wrapper
```

### Vérifications Systématiques

**Chaque vue doit** :
1. Vérifier l'authentification (`@login_required`)
2. Vérifier les permissions spécifiques
3. Filtrer les données selon le rôle
4. Bloquer les accès directs par URL

**Exemple** :
```python
@login_required
def mes_tickets_view(request):
    user = request.user
    
    # Filtrage strict côté backend
    tickets = TicketMaintenance.objects.filter(
        assignes_a=user
    ).select_related('projet', 'cree_par')
    
    # Impossible de voir les tickets des autres
    # même en modifiant l'URL
    
    return render(request, 'core/mes_tickets.html', {'tickets': tickets})
```

## 🎨 Interface Professionnelle

### Badges de Priorité

```html
<!-- Critique -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
    <i class="fas fa-exclamation-circle"></i> Critique
</span>

<!-- Haute -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
    <i class="fas fa-arrow-up"></i> Haute
</span>

<!-- Normale -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
    <i class="fas fa-minus"></i> Normale
</span>

<!-- Basse -->
<span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
    <i class="fas fa-arrow-down"></i> Basse
</span>
```

### Badges de Statut

```html
<!-- Ouvert -->
<span class="inline-flex items-center">
    <i class="fas fa-folder-open text-blue-600"></i>
</span>

<!-- En cours -->
<span class="inline-flex items-center">
    <i class="fas fa-spinner text-indigo-600"></i>
</span>

<!-- Résolu -->
<span class="inline-flex items-center">
    <i class="fas fa-check-circle text-green-600"></i>
</span>

<!-- Fermé -->
<span class="inline-flex items-center">
    <i class="fas fa-lock text-gray-600"></i>
</span>
```

### Compteur dans la Sidebar

```html
<a href="{% url 'mes_tickets' %}" class="flex items-center justify-between">
    <span>
        <i class="fas fa-ticket-alt mr-2"></i>
        Mes tickets
    </span>
    {% if tickets_count > 0 %}
    <span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-500 text-white">
        {{ tickets_count }}
    </span>
    {% endif %}
</a>
```

### Filtres

```html
<div class="flex items-center space-x-4 mb-6">
    <!-- Filtre Statut -->
    <select name="statut" class="px-3 py-2 border rounded-lg">
        <option value="">Tous les statuts</option>
        <option value="OUVERT">Ouvert</option>
        <option value="EN_COURS">En cours</option>
        <option value="RESOLU">Résolu</option>
        <option value="FERME">Fermé</option>
    </select>
    
    <!-- Filtre Priorité -->
    <select name="priorite" class="px-3 py-2 border rounded-lg">
        <option value="">Toutes les priorités</option>
        <option value="CRITIQUE">Critique</option>
        <option value="HAUTE">Haute</option>
        <option value="NORMALE">Normale</option>
        <option value="BASSE">Basse</option>
    </select>
</div>
```

## 📁 Structure des Fichiers

### Vues (core/views_maintenance_v2.py)

```python
# Ajouter ces vues :

@login_required
def mes_tickets_view(request):
    """Mes tickets assignés"""
    pass

@login_required
def tickets_projet_view(request, projet_id=None):
    """Tickets d'un projet spécifique"""
    pass

@login_required
def tous_tickets_view(request):
    """Tous les tickets (Admin uniquement)"""
    pass
```

### URLs (core/urls.py)

```python
# Ajouter ces routes :

path('mes-tickets/', views_maintenance_v2.mes_tickets_view, name='mes_tickets'),
path('tickets-projet/', views_maintenance_v2.tickets_projet_view, name='tickets_projet'),
path('tickets-projet/<uuid:projet_id>/', views_maintenance_v2.tickets_projet_view, name='tickets_projet_detail'),
path('tous-tickets/', views_maintenance_v2.tous_tickets_view, name='tous_tickets'),
```

### Templates

```
templates/core/
├── mes_tickets.html           # Mes tickets assignés
├── tickets_projet.html        # Tickets d'un projet
└── tous_tickets.html          # Tous les tickets (Admin)
```

### Sidebar (templates/base.html)

Ajouter le menu dans la sidebar existante.

## 🔄 Flux de Navigation

```
Sidebar
  │
  ├─→ Mes tickets
  │     └─→ Liste des tickets assignés
  │           └─→ Clic sur ticket → Détails du ticket
  │
  ├─→ Tickets du projet
  │     ├─→ Sélection du projet (dropdown)
  │     └─→ Liste des tickets du projet
  │           └─→ Clic sur ticket → Détails du ticket
  │
  └─→ Tous les tickets (Admin)
        └─→ Liste globale avec filtres
              └─→ Clic sur ticket → Détails du ticket
```

## ✅ Checklist d'Implémentation

### Phase 1 : Backend
- [ ] Créer les 3 vues dans `views_maintenance_v2.py`
- [ ] Ajouter les routes dans `urls.py`
- [ ] Implémenter les vérifications de permissions
- [ ] Créer le décorateur `@ticket_access_required`
- [ ] Tester les accès directs par URL

### Phase 2 : Templates
- [ ] Créer `mes_tickets.html`
- [ ] Créer `tickets_projet.html`
- [ ] Créer `tous_tickets.html`
- [ ] Ajouter le menu dans la sidebar (`base.html`)
- [ ] Implémenter les badges et filtres

### Phase 3 : Sécurité
- [ ] Vérifier toutes les permissions backend
- [ ] Tester les accès non autorisés
- [ ] Valider les filtres de données
- [ ] Tester avec différents rôles

### Phase 4 : UX
- [ ] Ajouter les compteurs de badges
- [ ] Implémenter les filtres dynamiques
- [ ] Optimiser pour mobile
- [ ] Ajouter les transitions et animations

## 🎯 Résultat Attendu

Un système de navigation professionnel pour les tickets de maintenance :
- ✅ Sécurisé (vérifications backend)
- ✅ Basé sur les rôles et permissions
- ✅ Interface moderne et intuitive
- ✅ Compteurs en temps réel
- ✅ Filtres efficaces
- ✅ Compatible mobile
- ✅ Inspiré de Jira

## 📊 Exemple de Données

### Mes Tickets
```
┌─────────────┬──────────┬────────┬─────────────┬──────────┐
│ Ticket      │ Priorité │ Statut │ Projet      │ Date     │
├─────────────┼──────────┼────────┼─────────────┼──────────┤
│ MAINT-001   │ Critique │ 🔵     │ Projet A    │ 12/02/26 │
│ MAINT-005   │ Haute    │ 🟢     │ Projet B    │ 11/02/26 │
│ MAINT-012   │ Normale  │ 🔵     │ Projet A    │ 10/02/26 │
└─────────────┴──────────┴────────┴─────────────┴──────────┘
```

### Sidebar avec Compteur
```
📋 Tickets
   👤 Mes tickets (3)
   📁 Tickets du projet
   🌐 Tous les tickets
```

## 🚀 Prochaines Étapes

1. Valider cette spécification
2. Implémenter phase par phase
3. Tester avec différents rôles
4. Déployer progressivement

Cette implémentation garantit une gestion professionnelle, sécurisée et intuitive des tickets de maintenance !
