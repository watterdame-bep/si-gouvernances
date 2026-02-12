# Règles de Gouvernance - Contrats et Tickets de Maintenance

## 🎯 Objectif

Implémenter des règles strictes de gouvernance pour la gestion des contrats de maintenance et des tickets, avec des contrôles de sécurité côté backend.

---

## 1️⃣ CONTRAT DE MAINTENANCE

### 🔒 Règles d'Accès

**Seul l'Administrateur peut** :
- ✅ Créer un contrat de maintenance
- ✅ Modifier un contrat
- ✅ Activer / Suspendre / Clôturer un contrat

**Le Responsable du projet NE PEUT PAS** :
- ❌ Créer un contrat
- ❌ Modifier un contrat

### 📌 Implémentation Backend

**Fichier** : `core/views_maintenance.py`

#### Vue `gestion_contrats_view`
```python
# RÈGLE DE GOUVERNANCE : Seul l'Admin peut créer/modifier des contrats
peut_creer_contrat = user.est_super_admin()

context = {
    'peut_creer': peut_creer_contrat,  # Contrôle l'affichage du bouton
}
```

#### Vue `creer_contrat_view`
```python
# RÈGLE DE GOUVERNANCE : Seul l'Administrateur peut créer un contrat
if not user.est_super_admin():
    messages.error(request, 'Permissions insuffisantes. Seul l\'Administrateur peut créer un contrat de maintenance.')
    return redirect('gestion_contrats', projet_id=projet.id)
```

### ✅ Sécurité

- ✅ Vérification côté backend (pas seulement en interface)
- ✅ Message d'erreur clair si tentative non autorisée
- ✅ Redirection vers la liste des contrats
- ✅ Impossible de contourner via URL directe

---

## 2️⃣ TICKET DE MAINTENANCE

### 🎫 Règles d'Accès

**Peuvent créer un ticket** :
- ✅ L'Administrateur
- ✅ Le Responsable du projet

**Ne peuvent PAS créer de ticket** :
- ❌ Les autres rôles (Développeur, QA, etc.)

### 📌 Implémentation Backend

**Fichier** : `core/views_maintenance.py`

#### Vue `gestion_tickets_view`
```python
# RÈGLE DE GOUVERNANCE : Seuls Admin et Responsable du projet peuvent créer un ticket
responsable_projet = projet.get_responsable_principal()
peut_creer_ticket = user.est_super_admin() or (responsable_projet and responsable_projet == user)

context = {
    'peut_creer': peut_creer_ticket,  # Contrôle l'affichage du bouton
}
```

#### Vue `creer_ticket_view`
```python
# RÈGLE DE GOUVERNANCE 1 : Seuls Admin et Responsable du projet peuvent créer un ticket
responsable_projet = projet.get_responsable_principal()
peut_creer = user.est_super_admin() or (responsable_projet and responsable_projet == user)

if not peut_creer:
    messages.error(request, 'Permissions insuffisantes. Seuls l\'Administrateur et le Responsable du projet peuvent créer un ticket de maintenance.')
    return redirect('gestion_tickets', projet_id=projet.id)
```

### ✅ Sécurité

- ✅ Vérification côté backend
- ✅ Utilisation de `get_responsable_principal()` pour identifier le responsable
- ✅ Message d'erreur explicite
- ✅ Protection contre les accès directs par URL

---

## 3️⃣ CONDITION OBLIGATOIRE : CONTRAT ACTIF

### 📋 Règle Métier

**Un ticket de maintenance ne peut être créé que si** :
- Le projet possède un contrat de maintenance actif

**Si aucun contrat actif** :
- ❌ Afficher un message d'erreur
- ❌ Bloquer la création du ticket

### 📌 Implémentation Backend

**Fichier** : `core/views_maintenance.py`

#### Vue `creer_ticket_view`
```python
# RÈGLE DE GOUVERNANCE 2 : Vérifier qu'il existe un contrat actif
contrats_actifs = [c for c in projet.contrats_garantie.all() if c.est_actif]

if not contrats_actifs:
    messages.error(request, 'Impossible de créer un ticket : aucun contrat de maintenance actif pour ce projet.')
    return redirect('gestion_tickets', projet_id=projet.id)
```

#### Vérification supplémentaire lors de la création
```python
# Vérifier que le contrat est actif
if contrat and not contrat.est_actif:
    messages.error(request, 'Le contrat sélectionné n\'est plus actif.')
    return redirect('creer_ticket', projet_id=projet.id)
```

### ✅ Sécurité

- ✅ Vérification avant affichage du formulaire
- ✅ Vérification lors de la soumission
- ✅ Message d'erreur clair et explicite
- ✅ Impossible de créer un ticket sans contrat actif

---

## 4️⃣ INTERFACE UTILISATEUR

### Boutons Conditionnels

#### Bouton "Créer contrat"
- ✅ Visible uniquement pour l'Administrateur
- ❌ Masqué pour tous les autres utilisateurs

**Template** : `templates/core/gestion_contrats.html`
```django
{% if peut_creer %}
    <a href="{% url 'creer_contrat' projet.id %}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Créer un contrat
    </a>
{% endif %}
```

#### Bouton "Créer ticket de maintenance"
- ✅ Visible pour l'Administrateur
- ✅ Visible pour le Responsable du projet
- ❌ Masqué pour les autres rôles

**Template** : `templates/core/gestion_tickets.html`
```django
{% if peut_creer and a_contrat_actif %}
    <a href="{% url 'creer_ticket' projet.id %}" class="btn btn-primary">
        <i class="fas fa-plus"></i> Créer un ticket
    </a>
{% elif peut_creer and not a_contrat_actif %}
    <button class="btn btn-secondary" disabled title="Aucun contrat actif">
        <i class="fas fa-ban"></i> Créer un ticket (Aucun contrat actif)
    </button>
{% endif %}
```

### Messages d'Erreur

#### Permissions insuffisantes - Contrat
```
Permissions insuffisantes. Seul l'Administrateur peut créer un contrat de maintenance.
```

#### Permissions insuffisantes - Ticket
```
Permissions insuffisantes. Seuls l'Administrateur et le Responsable du projet peuvent créer un ticket de maintenance.
```

#### Aucun contrat actif
```
Impossible de créer un ticket : aucun contrat de maintenance actif pour ce projet.
```

---

## 5️⃣ SÉCURITÉ

### Principes Appliqués

1. **Défense en profondeur**
   - ✅ Contrôle en interface (masquage des boutons)
   - ✅ Contrôle backend (vérification des permissions)
   - ✅ Double vérification (GET et POST)

2. **Principe du moindre privilège**
   - ✅ Seuls les rôles nécessaires ont accès
   - ✅ Pas de permissions par défaut

3. **Validation stricte**
   - ✅ Vérification de l'utilisateur
   - ✅ Vérification du rôle
   - ✅ Vérification des conditions métier

4. **Messages clairs**
   - ✅ L'utilisateur sait pourquoi l'action est refusée
   - ✅ Pas de détails techniques exposés

### Points de Contrôle

| Action | Point de contrôle | Vérification |
|--------|-------------------|--------------|
| Créer contrat | Interface | `peut_creer` = Admin uniquement |
| Créer contrat | Backend GET | `user.est_super_admin()` |
| Créer contrat | Backend POST | `user.est_super_admin()` |
| Créer ticket | Interface | `peut_creer` = Admin OU Responsable |
| Créer ticket | Backend GET | Admin OU Responsable + Contrat actif |
| Créer ticket | Backend POST | Admin OU Responsable + Contrat actif |

---

## 📊 Matrice des Permissions

| Rôle | Créer Contrat | Modifier Contrat | Créer Ticket | Voir Contrats | Voir Tickets |
|------|---------------|------------------|--------------|---------------|--------------|
| **Administrateur** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Responsable Projet** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Chef de Projet** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Développeur** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **QA** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Autre** | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🧪 Tests de Validation

### Test 1 : Création de Contrat par Admin
1. Se connecter en tant qu'Administrateur
2. Accéder à "Gestion des Contrats"
3. ✅ Le bouton "Créer un contrat" est visible
4. Cliquer sur "Créer un contrat"
5. ✅ Le formulaire s'affiche
6. Remplir et soumettre
7. ✅ Le contrat est créé

### Test 2 : Tentative de Création de Contrat par Responsable
1. Se connecter en tant que Responsable du projet
2. Accéder à "Gestion des Contrats"
3. ✅ Le bouton "Créer un contrat" est masqué
4. Tenter d'accéder directement à l'URL `/creer-contrat/`
5. ✅ Message d'erreur : "Permissions insuffisantes..."
6. ✅ Redirection vers la liste des contrats

### Test 3 : Création de Ticket avec Contrat Actif
1. Se connecter en tant qu'Admin ou Responsable
2. S'assurer qu'un contrat actif existe
3. Accéder à "Gestion des Tickets"
4. ✅ Le bouton "Créer un ticket" est visible
5. Cliquer sur "Créer un ticket"
6. ✅ Le formulaire s'affiche
7. Remplir et soumettre
8. ✅ Le ticket est créé

### Test 4 : Tentative de Création de Ticket sans Contrat Actif
1. Se connecter en tant qu'Admin ou Responsable
2. S'assurer qu'aucun contrat actif n'existe
3. Accéder à "Gestion des Tickets"
4. ✅ Le bouton "Créer un ticket" est désactivé ou masqué
5. Tenter d'accéder directement à l'URL `/creer-ticket/`
6. ✅ Message d'erreur : "Impossible de créer un ticket : aucun contrat..."
7. ✅ Redirection vers la liste des tickets

### Test 5 : Tentative de Création de Ticket par Développeur
1. Se connecter en tant que Développeur
2. Accéder à "Gestion des Tickets"
3. ✅ Le bouton "Créer un ticket" est masqué
4. Tenter d'accéder directement à l'URL `/creer-ticket/`
5. ✅ Message d'erreur : "Permissions insuffisantes..."
6. ✅ Redirection vers la liste des tickets

---

## 📁 Fichiers Modifiés

1. **`core/views_maintenance.py`**
   - `gestion_contrats_view` : Contrôle d'affichage du bouton
   - `creer_contrat_view` : Vérification Admin uniquement
   - `gestion_tickets_view` : Contrôle d'affichage du bouton
   - `creer_ticket_view` : Vérification Admin/Responsable + Contrat actif

---

## 📅 Date d'Implémentation

12 février 2026

---

## ✅ Statut

**IMPLÉMENTÉ** - Toutes les règles de gouvernance sont en place et sécurisées côté backend.
