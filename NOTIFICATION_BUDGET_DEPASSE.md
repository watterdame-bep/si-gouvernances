# Notification Automatique - Budget Dépassé
## Date: 16 février 2026

## ✅ FONCTIONNALITÉ IMPLÉMENTÉE

### Objectif
Notifier automatiquement l'administrateur lorsque les dépenses d'un projet dépassent le budget total (budget disponible devient négatif).

## 📋 DÉTAILS DE L'IMPLÉMENTATION

### 1. Déclencheur
La notification est envoyée automatiquement lors de l'ajout d'une ligne budgétaire qui fait passer le budget disponible en négatif.

### 2. Logique
```python
# Dans core/views_budget.py - fonction ajouter_lignes_budget()

# Après l'ajout des lignes budgétaires
resume = ResumeBudget(projet)

# Si le budget disponible est négatif
if resume.budget_disponible < 0:
    # Créer une alerte pour chaque administrateur
    admins = Utilisateur.objects.filter(is_superuser=True, is_active=True)
    
    for admin in admins:
        # Éviter les doublons (vérifier si alerte non lue existe)
        if not AlerteProjet.objects.filter(
            utilisateur=admin,
            projet=projet,
            type_alerte='BUDGET_DEPASSE',
            lue=False
        ).exists():
            # Créer l'alerte
            AlerteProjet.objects.create(...)
```

### 3. Type d'alerte
- **Type**: `BUDGET_DEPASSE`
- **Modèle**: `AlerteProjet`
- **Icône**: `fa-dollar-sign` (💲)

### 4. Contenu de la notification

#### Titre
```
⚠️ Budget dépassé - [Nom du projet]
```

#### Message
```
Le budget du projet "[Nom du projet]" a été dépassé.
Budget total: $X,XXX.XX | Dépenses: $X,XXX.XX | Dépassement: $X,XXX.XX
```

#### Lien
```
/projets/{projet_id}/parametres/
```
→ Redirige vers la page des paramètres du projet (onglet Budget)

### 5. Destinataires
- Tous les administrateurs actifs (is_superuser=True, is_active=True)
- Une seule alerte par admin (évite les doublons si alerte non lue existe)

## 🔧 FICHIERS MODIFIÉS

### core/views_budget.py
- Fonction `ajouter_lignes_budget()` modifiée
- Ajout de la logique de vérification et création d'alerte

## 📊 CALCUL DU BUDGET

### Formule
```python
budget_disponible = budget_total - total_depenses

# Si budget_disponible < 0 → DÉPASSEMENT
```

### Exemple
```
Budget total:     $10,000.00
Dépenses:         $12,500.00
─────────────────────────────
Budget disponible: -$2,500.00  ← DÉPASSEMENT!
```

## 🎯 COMPORTEMENT

### Scénario 1: Premier dépassement
1. Admin ajoute une dépense
2. Budget devient négatif
3. ✅ Alerte créée et envoyée à tous les admins

### Scénario 2: Dépassement déjà notifié
1. Admin ajoute une autre dépense
2. Budget reste négatif
3. ⚠️ Alerte NON créée (une alerte non lue existe déjà)

### Scénario 3: Budget revient positif puis redépasse
1. Admin supprime des dépenses
2. Budget redevient positif
3. Admin ajoute une grosse dépense
4. Budget redevient négatif
5. ✅ Nouvelle alerte créée

## 🔔 AFFICHAGE DES ALERTES

### Dans l'interface
- Icône cloche dans la navbar
- Badge avec nombre d'alertes non lues
- Liste déroulante des alertes
- Clic sur l'alerte → Redirection vers paramètres du projet

### Couleur et style
- Fond rouge/orange pour indiquer la criticité
- Icône dollar ($) pour identifier le type
- Message clair avec montants formatés

## 🧪 TESTS

### Test manuel
1. Créer un projet avec budget de $10,000
2. Ajouter des dépenses pour $8,000
3. Ajouter une dépense de $3,000
4. ✅ Vérifier qu'une alerte est créée
5. Vérifier l'affichage dans l'interface

### Script de test
```bash
python test_notification_budget_depasse.py
```

Le script:
- Trouve un projet avec budget
- Ajoute une dépense qui dépasse le budget
- Crée l'alerte manuellement (simulation)
- Affiche toutes les alertes
- Propose de nettoyer

## 📝 NOTES IMPORTANTES

### Prévention des doublons
- Une seule alerte non lue par admin et par projet
- Si l'admin lit l'alerte, une nouvelle peut être créée au prochain dépassement

### Calcul en temps réel
- Le calcul est fait à chaque ajout de ligne budgétaire
- Utilise la classe `ResumeBudget` pour les calculs

### Permissions
- Seuls les admins et responsables de projet peuvent ajouter des dépenses
- Seuls les admins reçoivent les alertes de dépassement

## 🚀 UTILISATION

### Pour l'administrateur
1. Recevoir l'alerte dans la cloche de notification
2. Cliquer sur l'alerte
3. Être redirigé vers les paramètres du projet
4. Consulter le budget détaillé
5. Prendre des mesures (supprimer dépenses, augmenter budget, etc.)

### Actions possibles
- Supprimer des lignes budgétaires inutiles
- Modifier le budget prévisionnel du projet
- Contacter le responsable du projet
- Analyser les dépenses par type (Matériel/Service)

## ✨ AVANTAGES

1. **Réactivité**: Notification immédiate dès le dépassement
2. **Visibilité**: Tous les admins sont informés
3. **Traçabilité**: Historique des alertes conservé
4. **Prévention**: Évite les dépassements non contrôlés
5. **Clarté**: Message avec montants précis

## 🔄 AMÉLIORATIONS FUTURES POSSIBLES

1. **Email**: Envoyer aussi un email aux admins
2. **Seuils**: Alerter avant le dépassement (90%, 95%)
3. **Responsable**: Notifier aussi le responsable du projet
4. **Statistiques**: Dashboard des projets en dépassement
5. **Historique**: Graphique d'évolution du budget

## 📊 STATUTS BUDGET

Le système utilise plusieurs statuts:

- **OK**: < 75% utilisé (vert)
- **ATTENTION**: 75-90% utilisé (jaune)
- **CRITIQUE**: 90-100% utilisé (orange)
- **DEPASSE**: > 100% utilisé (rouge) ← Déclenche l'alerte

## 🎨 INTERFACE

### Badge de statut
```html
<!-- Dans parametres_projet.html -->
<span class="badge badge-danger">DÉPASSÉ</span>
```

### Couleur de la barre
```css
/* Rouge si dépassé */
background-color: #dc3545;
```

### Message d'alerte
```html
<div class="alert alert-danger">
  ⚠️ Budget dépassé de $X,XXX.XX
</div>
```

## ✅ RÉSULTAT

Système de notification automatique fonctionnel qui:
- Détecte les dépassements de budget en temps réel
- Notifie tous les administrateurs
- Évite les doublons
- Fournit des informations précises
- Permet une action rapide
