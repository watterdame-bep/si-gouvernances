# 🔧 IMPLÉMENTATION SYSTÈME DE MAINTENANCE V1

## 📋 RÉSUMÉ EXÉCUTIF

Implémentation complète d'un système de maintenance conforme aux pratiques d'entreprise réelles, avec traçabilité complète et gouvernance stricte.

**Date:** 06/02/2026  
**Version:** 1.0  
**Statut:** ✅ Modèles créés et migrés

---

## 🎯 OBJECTIFS

### Objectifs Métier
- ✅ Gérer la maintenance post-déploiement
- ✅ Respecter les contrats de garantie
- ✅ Traçabilité complète des interventions
- ✅ Gouvernance stricte (autorisation obligatoire)
- ✅ Rapport technique obligatoire

### Objectifs Techniques
- ✅ Architecture simple et évolutive
- ✅ Audit complet (qui / quand / pourquoi)
- ✅ Validation métier automatique
- ✅ Pas de complexité inutile (V1)

---

## 🏗️ ARCHITECTURE MÉTIER

### Flux Complet

```
Projet
  └── Contrat de Garantie (obligatoire)
        └── Ticket de Maintenance (incident)
              └── Billet d'Intervention (autorisation)
                    └── Intervention Technique (actions)
                          └── Statut Technique (rapport obligatoire)
```

### Exemple Concret

```
Projet: "Application E-Commerce"
  │
  ├── Contrat Garantie Corrective (01/01/2026 → 31/12/2026)
  │     │
  │     ├── Ticket MAINT-00001: "Erreur paiement CB"
  │     │     │
  │     │     ├── Billet BILLET-00001 (Dev: Jean Dupont)
  │     │     │     │
  │     │     │     ├── Intervention (2h passées)
  │     │     │     │     │
  │     │     │     │     └── Statut Technique (Root cause + Solution)
  │     │     │
  │     │     └── Ticket résolu → fermé
  │     │
  │     └── Ticket MAINT-00002: "Lenteur recherche"
  │
  └── Contrat Garantie Évolutive (01/01/2026 → 30/06/2026)
```

---

## 📊 MODÈLES DE DONNÉES

### 1. ContratGarantie

**Rôle:** Définit les conditions de maintenance gratuite

**Champs principaux:**
```python
- projet (FK)
- type_garantie (CORRECTIVE / EVOLUTIVE)
- date_debut, date_fin
- sla_heures (temps de réponse max)
- description_couverture
- exclusions
```

**Propriétés calculées:**
- `est_actif` → Vérifie si le contrat est actif aujourd'hui
- `jours_restants` → Nombre de jours avant expiration

**Règles métier:**
- ✅ Pas de chevauchement pour le même type
- ✅ Date fin > Date début
- ✅ Un seul contrat actif par type

**Exemple:**
```python
contrat = ContratGarantie.objects.create(
    projet=projet,
    type_garantie='CORRECTIVE',
    date_debut='2026-01-01',
    date_fin='2026-12-31',
    sla_heures=24,
    description_couverture="Correction de tous les bugs bloquants"
)
```

---

### 2. TicketMaintenance

**Rôle:** Point d'entrée pour toute demande de maintenance

**Champs principaux:**
```python
- numero_ticket (auto: MAINT-00001)
- projet (FK)
- contrat_garantie (FK, nullable)
- titre, description_probleme
- gravite (MINEUR / MAJEUR / CRITIQUE)
- origine (CLIENT / MONITORING / INTERNE)
- statut (OUVERT / EN_COURS / RESOLU / FERME / REJETE)
- est_payant (calculé automatiquement)
- raison_rejet
```

**Propriétés calculées:**
- `peut_etre_traite` → Vérifie si traitable (garantie active)
- `temps_ecoule` → Heures depuis création
- `sla_depasse` → Vérifie si SLA dépassé

**Règles métier CRITIQUES:**
```python
def _verifier_garantie(self):
    """À la création du ticket"""
    if not self.contrat_garantie:
        self.est_payant = True  # Pas de contrat
    elif not self.contrat_garantie.est_actif:
        self.est_payant = True  # Contrat expiré
        self.raison_rejet = "Contrat de garantie expiré"
    else:
        self.est_payant = False  # OK, gratuit
```

**Méthodes:**
- `resoudre()` → Marque comme résolu
- `fermer()` → Ferme le ticket (après validation client)
- `rejeter(raison)` → Rejette le ticket

**Exemple:**
```python
ticket = TicketMaintenance.objects.create(
    projet=projet,
    contrat_garantie=contrat,
    titre="Erreur lors du paiement par carte bancaire",
    description_probleme="Les utilisateurs ne peuvent pas payer...",
    gravite='CRITIQUE',
    origine='CLIENT',
    cree_par=user
)
# → est_payant = False (contrat actif)
# → numero_ticket = "MAINT-00001"
```

---

### 3. BilletIntervention

**Rôle:** Autorisation d'intervention (OBLIGATOIRE)

**Champs principaux:**
```python
- numero_billet (auto: BILLET-00001)
- ticket (FK)
- developpeur_autorise (FK User)
- type_intervention (ANALYSE / CORRECTION / DEPLOIEMENT_CORRECTIF)
- duree_estimee (heures)
- autorise_par (FK User - Chef projet/Admin)
- instructions
```

**Règles métier CRITIQUES:**
```python
def clean(self):
    # Vérifier que le ticket peut être traité
    if not self.ticket.peut_etre_traite:
        raise ValidationError("Ticket rejeté ou payant")
    
    # Vérifier les permissions du développeur
    if self.developpeur_autorise.role_systeme.nom not in ['DEVELOPPEUR', 'CHEF_PROJET']:
        raise ValidationError("Seuls dev/chef projet peuvent intervenir")
```

**⚠️ RÈGLE FONDAMENTALE:**
> **Aucun développeur ne peut intervenir sans billet validé**

**Exemple:**
```python
billet = BilletIntervention.objects.create(
    ticket=ticket,
    developpeur_autorise=jean_dupont,
    type_intervention='CORRECTION',
    duree_estimee=2.5,
    autorise_par=chef_projet,
    instructions="Vérifier la configuration du gateway de paiement"
)
# → numero_billet = "BILLET-00001"
```

---

### 4. InterventionMaintenance

**Rôle:** Enregistre les actions techniques réelles

**Champs principaux:**
```python
- billet (FK)
- description_actions
- date_debut, date_fin
- temps_passe (heures réelles)
- correctif_applique
- fichiers_modifies
```

**Règles métier:**
- ✅ Date fin > Date début
- ✅ Avertissement si temps_passe > duree_estimee * 2

**Exemple:**
```python
intervention = InterventionMaintenance.objects.create(
    billet=billet,
    description_actions="Correction du paramètre API_KEY dans config.py",
    date_debut=timezone.now(),
    temps_passe=1.5,
    correctif_applique="Mise à jour de la clé API Stripe",
    fichiers_modifies="config/payment.py, tests/test_payment.py"
)
```

---

### 5. StatutTechnique

**Rôle:** Rapport technique final (OBLIGATOIRE pour clôture)

**Champs principaux:**
```python
- intervention (OneToOne)
- probleme_initial
- cause_reelle (Root Cause Analysis)
- solution_apportee
- impact_systeme
- risques_futurs
- recommandations
- valide_par (FK User)
- redige_par (FK User)
```

**Règles métier CRITIQUES:**
```python
def valider(self, validateur):
    """Valider le statut technique"""
    self.valide_par = validateur
    self.date_validation = timezone.now()
    self.save()
    
    # Marquer automatiquement le ticket comme résolu
    self.intervention.billet.ticket.resoudre()
```

**⚠️ RÈGLE FONDAMENTALE:**
> **Un ticket ne peut être clôturé sans statut technique validé**

**Exemple:**
```python
statut = StatutTechnique.objects.create(
    intervention=intervention,
    probleme_initial="Erreur 500 lors du paiement",
    cause_reelle="Clé API Stripe expirée dans l'environnement de production",
    solution_apportee="Mise à jour de la clé API avec la nouvelle clé fournie par Stripe",
    impact_systeme="Module de paiement uniquement",
    risques_futurs="Risque de récurrence si rotation des clés non automatisée",
    recommandations="Mettre en place un système d'alerte pour expiration des clés API",
    redige_par=jean_dupont
)

# Validation par le chef de projet
statut.valider(chef_projet)
# → Ticket automatiquement marqué RESOLU
```

---

## 🔄 WORKFLOW COMPLET

### Étape 1: Création du Contrat de Garantie

```python
# Chef de projet crée le contrat après déploiement
contrat = ContratGarantie.objects.create(
    projet=projet,
    type_garantie='CORRECTIVE',
    date_debut='2026-01-01',
    date_fin='2026-12-31',
    sla_heures=24,
    description_couverture="Correction bugs bloquants et critiques",
    exclusions="Nouvelles fonctionnalités, modifications de design",
    cree_par=chef_projet
)
```

### Étape 2: Création du Ticket

```python
# Client ou monitoring détecte un problème
ticket = TicketMaintenance.objects.create(
    projet=projet,
    contrat_garantie=contrat,  # Lié au contrat
    titre="Erreur paiement CB",
    description_probleme="Les utilisateurs reçoivent une erreur 500...",
    gravite='CRITIQUE',
    origine='CLIENT',
    cree_par=support_user
)

# Vérification automatique
print(ticket.est_payant)  # False (contrat actif)
print(ticket.peut_etre_traite)  # True
print(ticket.numero_ticket)  # "MAINT-00001"
```

### Étape 3: Émission du Billet d'Intervention

```python
# Chef de projet autorise l'intervention
billet = BilletIntervention.objects.create(
    ticket=ticket,
    developpeur_autorise=jean_dupont,
    type_intervention='ANALYSE',
    duree_estimee=2.0,
    autorise_par=chef_projet,
    instructions="Analyser les logs de production"
)

# Mise à jour du ticket
ticket.statut = 'EN_COURS'
ticket.assigne_a = jean_dupont
ticket.save()
```

### Étape 4: Intervention Technique

```python
# Développeur effectue l'intervention
intervention = InterventionMaintenance.objects.create(
    billet=billet,
    description_actions="""
    1. Analyse des logs Stripe
    2. Identification: clé API expirée
    3. Mise à jour de la clé dans config
    4. Tests en staging
    5. Déploiement en production
    """,
    date_debut=timezone.now(),
    temps_passe=1.5,
    correctif_applique="Mise à jour API_KEY dans config/payment.py",
    fichiers_modifies="config/payment.py"
)
```

### Étape 5: Rédaction du Statut Technique

```python
# Développeur rédige le rapport
statut = StatutTechnique.objects.create(
    intervention=intervention,
    probleme_initial="Erreur 500 lors du paiement par CB",
    cause_reelle="Clé API Stripe expirée (rotation automatique non configurée)",
    solution_apportee="Mise à jour manuelle de la clé API + configuration alerte",
    impact_systeme="Module paiement uniquement, pas d'impact sur autres modules",
    risques_futurs="Risque de récurrence si pas d'automatisation",
    recommandations="""
    1. Automatiser la rotation des clés API
    2. Mettre en place des alertes d'expiration
    3. Documenter la procédure de renouvellement
    """,
    redige_par=jean_dupont
)
```

### Étape 6: Validation et Clôture

```python
# Chef de projet valide le statut technique
statut.valider(chef_projet)
# → Ticket automatiquement marqué RESOLU

# Après validation client
ticket.fermer()
# → Ticket marqué FERME
```

---

## 📊 STATISTIQUES ET INDICATEURS

### Indicateurs par Projet

```python
# Tickets par statut
tickets_ouverts = projet.tickets_maintenance.filter(statut='OUVERT').count()
tickets_en_cours = projet.tickets_maintenance.filter(statut='EN_COURS').count()
tickets_resolus = projet.tickets_maintenance.filter(statut='RESOLU').count()

# Tickets par gravité
critiques = projet.tickets_maintenance.filter(gravite='CRITIQUE').count()
majeurs = projet.tickets_maintenance.filter(gravite='MAJEUR').count()

# SLA
tickets_sla_depasse = [t for t in projet.tickets_maintenance.all() if t.sla_depasse]

# Temps moyen de résolution
from django.db.models import Avg, F
temps_moyen = projet.tickets_maintenance.filter(
    statut='RESOLU'
).annotate(
    duree=F('date_resolution') - F('date_creation')
).aggregate(Avg('duree'))
```

### Indicateurs par Contrat

```python
# Tickets traités sous garantie
tickets_gratuits = contrat.tickets.filter(est_payant=False).count()
tickets_payants = contrat.tickets.filter(est_payant=True).count()

# Jours restants
print(f"Jours restants: {contrat.jours_restants}")
print(f"Actif: {contrat.est_actif}")
```

---

## ✅ RÈGLES MÉTIER IMPLÉMENTÉES

### 1. Contrat de Garantie

- ✅ Obligatoire pour maintenance gratuite
- ✅ Vérification automatique de l'activité
- ✅ Pas de chevauchement de contrats
- ✅ SLA défini et vérifié

### 2. Ticket de Maintenance

- ✅ Numérotation automatique (MAINT-XXXXX)
- ✅ Vérification garantie à la création
- ✅ Marquage automatique payant/gratuit
- ✅ Calcul SLA dépassé
- ✅ Workflow statut strict

### 3. Billet d'Intervention

- ✅ Autorisation obligatoire
- ✅ Vérification permissions développeur
- ✅ Vérification ticket traitable
- ✅ Numérotation automatique (BILLET-XXXXX)

### 4. Intervention Technique

- ✅ Lié à un billet validé
- ✅ Traçabilité complète des actions
- ✅ Temps passé vs estimé

### 5. Statut Technique

- ✅ Obligatoire pour clôture
- ✅ Root Cause Analysis
- ✅ Validation par chef de projet
- ✅ Résolution automatique du ticket

---

## 🔐 PERMISSIONS ET SÉCURITÉ

### Qui peut faire quoi?

| Action | Admin | Chef Projet | Développeur | Autres |
|--------|-------|-------------|-------------|--------|
| Créer contrat | ✅ | ✅ | ❌ | ❌ |
| Créer ticket | ✅ | ✅ | ✅ | ✅ |
| Émettre billet | ✅ | ✅ | ❌ | ❌ |
| Intervenir | ✅ | ✅ | ✅ (si billet) | ❌ |
| Rédiger statut | ✅ | ✅ | ✅ | ❌ |
| Valider statut | ✅ | ✅ | ❌ | ❌ |
| Clôturer ticket | ✅ | ✅ | ❌ | ❌ |

---

## 📁 FICHIERS CRÉÉS

### Modèles
- ✅ `core/models.py` - Modèles ajoutés (fin du fichier)
- ✅ `core/models_maintenance.py` - Version standalone (référence)

### Migrations
- ✅ `core/migrations/0024_add_systeme_maintenance.py`

### Documentation
- ✅ `IMPLEMENTATION_SYSTEME_MAINTENANCE_V1.md` (ce fichier)

---

## 🚀 PROCHAINES ÉTAPES

### Phase 2: Vues et URLs (À faire)

```python
# core/views_maintenance.py
- gestion_contrats_view()
- creer_contrat_view()
- gestion_tickets_view()
- creer_ticket_view()
- emettre_billet_view()
- enregistrer_intervention_view()
- rediger_statut_technique_view()
```

### Phase 3: Templates (À faire)

```
templates/core/
  ├── gestion_contrats.html
  ├── creer_contrat.html
  ├── gestion_tickets.html
  ├── creer_ticket.html
  ├── detail_ticket.html
  ├── emettre_billet.html
  ├── enregistrer_intervention.html
  └── rediger_statut_technique.html
```

### Phase 4: Dashboard et Statistiques (À faire)

- Dashboard maintenance par projet
- Indicateurs SLA
- Graphiques tickets par statut
- Alertes contrats expirés

---

## 💡 EXEMPLES D'UTILISATION

### Cas 1: Maintenance Corrective Standard

```python
# 1. Contrat actif
contrat = projet.contrats_garantie.get(type_garantie='CORRECTIVE', est_actif=True)

# 2. Ticket créé par client
ticket = TicketMaintenance.objects.create(
    projet=projet,
    contrat_garantie=contrat,
    titre="Bug affichage panier",
    gravite='MAJEUR',
    origine='CLIENT'
)

# 3. Billet émis
billet = BilletIntervention.objects.create(
    ticket=ticket,
    developpeur_autorise=dev,
    type_intervention='CORRECTION',
    duree_estimee=3.0
)

# 4. Intervention
intervention = InterventionMaintenance.objects.create(
    billet=billet,
    description_actions="Correction CSS",
    temps_passe=2.5
)

# 5. Statut technique
statut = StatutTechnique.objects.create(
    intervention=intervention,
    cause_reelle="Conflit CSS avec nouvelle version Bootstrap",
    solution_apportee="Ajout de règles CSS spécifiques"
)
statut.valider(chef_projet)
```

### Cas 2: Ticket Hors Garantie

```python
# Ticket sans contrat ou contrat expiré
ticket = TicketMaintenance.objects.create(
    projet=projet,
    contrat_garantie=None,  # Pas de contrat
    titre="Nouvelle fonctionnalité demandée",
    gravite='MINEUR',
    origine='CLIENT'
)

print(ticket.est_payant)  # True
print(ticket.peut_etre_traite)  # False

# Ticket rejeté ou nécessite devis
ticket.rejeter("Hors garantie - Devis nécessaire")
```

---

## 🎯 AVANTAGES DE L'ARCHITECTURE

### 1. Conformité Métier
- ✅ Respecte les pratiques d'entreprise
- ✅ Traçabilité complète
- ✅ Gouvernance stricte

### 2. Simplicité
- ✅ Modèles clairs et simples
- ✅ Pas de sur-ingénierie
- ✅ Facile à comprendre

### 3. Évolutivité
- ✅ Peut évoluer vers facturation
- ✅ Peut ajouter notifications
- ✅ Peut ajouter SLA complexes

### 4. Audit
- ✅ Qui a fait quoi et quand
- ✅ Historique complet
- ✅ Rapports techniques

---

## ⚠️ LIMITATIONS V1 (VOLONTAIRES)

### Non implémenté (pour simplicité)
- ❌ Facturation automatique
- ❌ Notifications avancées
- ❌ SLA complexes (escalade)
- ❌ Gestion des pièces jointes
- ❌ Commentaires sur tickets
- ❌ Workflow d'approbation multi-niveaux

### Pourquoi?
> **V1 = Architecture simple et fonctionnelle**  
> Ces fonctionnalités peuvent être ajoutées progressivement selon les besoins

---

## 📝 NOTES TECHNIQUES

### Numérotation Automatique

```python
# Tickets: MAINT-00001, MAINT-00002, ...
count = TicketMaintenance.objects.count() + 1
numero_ticket = f"MAINT-{count:05d}"

# Billets: BILLET-00001, BILLET-00002, ...
count = BilletIntervention.objects.count() + 1
numero_billet = f"BILLET-{count:05d}"
```

### Calculs de Dates

```python
# Temps écoulé
delta = timezone.now() - ticket.date_creation
heures = delta.total_seconds() / 3600

# Jours restants
jours = (contrat.date_fin - timezone.now().date()).days
```

### Validation Métier

```python
# Dans clean()
def clean(self):
    if self.date_debut >= self.date_fin:
        raise ValidationError("Date fin > Date début")
```

---

**Date de création:** 06/02/2026  
**Version:** 1.0  
**Statut:** ✅ Modèles implémentés et migrés  
**Prochaine étape:** Vues et interfaces

**Auteur:** Kiro AI Assistant  
**Projet:** SI-Gouvernance JCONSULT MY
