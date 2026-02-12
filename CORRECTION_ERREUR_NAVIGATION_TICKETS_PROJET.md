# Correction Erreur Navigation : Tickets par Projet

**Date**: 12 février 2026  
**Statut**: ✅ Corrigé  
**Fichier modifié**: `templates/core/detail_ticket.html`

---

## ❌ ERREUR

```
NoReverseMatch at /projets/.../tickets/.../
Reverse for 'tickets_projet' with arguments '(UUID(...),)' not found. 
1 pattern(s) tried: ['tickets\\-projet/\\Z']
```

---

## 🔍 CAUSE

Dans `core/urls.py`, il existe deux routes distinctes :

```python
# Route SANS argument (liste des projets)
path('tickets-projet/', views_maintenance_v2.tickets_projet_view, name='tickets_projet'),

# Route AVEC argument projet_id (tickets d'un projet spécifique)
path('tickets-projet/<uuid:projet_id>/', views_maintenance_v2.tickets_projet_view, name='tickets_projet_detail'),
```

Le template utilisait `tickets_projet` avec un argument `projet.id`, mais cette route n'accepte pas d'argument.

---

## ✅ SOLUTION

Utiliser le bon nom de route : `tickets_projet_detail` au lieu de `tickets_projet`

**AVANT** (incorrect) :
```django
<a href="{% url 'tickets_projet' projet.id %}">
```

**APRÈS** (correct) :
```django
<a href="{% url 'tickets_projet_detail' projet.id %}">
```

---

## 📝 CODE CORRIGÉ

```django
{% elif request.GET.from == 'tickets_projet' %}
<a href="{% url 'tickets_projet_detail' projet.id %}" 
   class="ml-2 px-3 py-2 md:px-4 text-gray-600 hover:text-gray-900 transition flex items-center text-sm">
    <i class="fas fa-arrow-left mr-1 md:mr-2"></i> 
    <span class="hidden md:inline">Tickets du Projet</span>
</a>
{% endif %}
```

---

## 🎯 RÉSULTAT

Le bouton retour fonctionne maintenant correctement et ramène l'utilisateur vers la page "Tickets par projet" du projet concerné.

---

## 📊 ROUTES TICKETS

| Nom de la route | URL | Arguments | Description |
|----------------|-----|-----------|-------------|
| `mes_tickets` | `/mes-tickets/` | Aucun | Mes tickets assignés |
| `tickets_projet` | `/tickets-projet/` | Aucun | Liste des projets |
| `tickets_projet_detail` | `/tickets-projet/<projet_id>/` | projet_id | Tickets d'un projet |
| `tous_tickets` | `/tous-tickets/` | Aucun | Tous les tickets (Admin) |
| `gestion_tickets` | `/projets/<projet_id>/tickets/` | projet_id | Tickets de maintenance |
| `detail_ticket` | `/projets/<projet_id>/tickets/<ticket_id>/` | projet_id, ticket_id | Détails d'un ticket |

---

## ✅ CORRECTION APPLIQUÉE

La navigation intelligente fonctionne maintenant correctement pour tous les cas :
- ✅ Depuis "Mes Tickets"
- ✅ Depuis "Tickets par Projet" (corrigé)
- ✅ Depuis "Tous les Tickets"
- ✅ Depuis "Notifications"
- ✅ Depuis "Gestion Tickets" (défaut)
