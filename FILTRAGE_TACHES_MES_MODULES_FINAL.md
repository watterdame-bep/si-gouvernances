# Filtrage des Tâches - "Mes Modules" vs "Gestion des Modules"

**Date**: 11 février 2026  
**Statut**: ✅ Implémenté

## Règle Métier Implémentée

### Via "Mes Modules" (Vue Personnelle)

**Principe** : Chacun voit uniquement SES tâches, sauf le responsable du module qui voit tout.

| Utilisateur | Tâches Visibles |
|-------------|-----------------|
| Responsable du module | ✅ TOUTES les tâches du module |
| Contributeur | ✅ Uniquement ses tâches assignées |
| Responsable du projet (non responsable du module) | ✅ Uniquement ses tâches assignées |
| Créateur du projet (non responsable du module) | ✅ Uniquement ses tâches assignées |

### Via "Gestion des Modules" (Vue de Gestion)

**Principe** : Vue complète pour la gestion et la supervision.

| Utilisateur | Tâches Visibles |
|-------------|-----------------|
| Responsable du module | ✅ TOUTES les tâches du module |
| Responsable du projet | ✅ TOUTES les tâches du module |
| Créateur du projet | ✅ TOUTES les tâches du module |
| Contributeur | ✅ TOUTES les tâches du module |

## Implémentation

### Fichier Modifié

**Fichier** : `core/views_taches_module.py`

### Changements Clés

#### 1. Ajout du Flag `est_responsable_module`

```python
est_responsable_module = False  # Flag pour identifier le responsable du module

# Vérifier si l'utilisateur est responsable du module
affectation_module = module.affectations.filter(
    utilisateur=user,
    role_module='RESPONSABLE',
    date_fin_affectation__isnull=True
).first()

if affectation_module:
    peut_gerer_taches = True
    peut_creer_taches = True
    peut_modifier_taches = True
    est_responsable_module = True
```

#### 2. Nouvelle Logique de Filtrage

**Avant** :
```python
if from_mes_modules and est_membre_simple:
    taches = module.taches.filter(responsable=user)
else:
    taches = module.taches.all()
```

**Après** :
```python
# RÈGLE: Si on vient de "Mes Modules" ET qu'on n'est PAS responsable du module,
# on ne voit que ses propres tâches (même si on est responsable du projet)
if from_mes_modules and not est_responsable_module:
    taches = module.taches.filter(responsable=user)
else:
    # Sinon, on voit toutes les tâches du module
    taches = module.taches.all()
```

### Message Informatif

**Fichier** : `templates/core/gestion_taches_module.html`

```django
{% if from_mes_modules and not peut_creer_taches %}
<div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
    <div class="flex items-start space-x-2">
        <i class="fas fa-info-circle text-blue-600 mt-0.5"></i>
        <div class="text-sm text-blue-800">
            <p class="font-medium">Mes Tâches</p>
            <p class="text-blue-700">Vous voyez uniquement les tâches qui vous sont assignées dans ce module. Seul le responsable d'une tâche peut la démarrer et la gérer.</p>
        </div>
    </div>
</div>
{% endif %}
```

## Scénarios Concrets

### Scénario 1 : Responsable du Projet (Non Responsable du Module)

**Contexte** :
- Projet : "Système de gestion des pharmacies"
- Responsable du projet : Eraste Butela
- Module : "Authentification"
- Responsable du module : DON DIEU

**Tâches du module** :
1. "Front-end login" → Responsable: Eraste Butela
2. "Backend API" → Responsable: DON DIEU
3. "Tests unitaires" → Responsable: Autre développeur

**Via "Mes Modules"** :
- Eraste Butela voit : ✅ Tâche #1 uniquement
- Message affiché : "Vous voyez uniquement les tâches qui vous sont assignées"

**Via "Gestion des Modules"** :
- Eraste Butela voit : ✅ Toutes les tâches (#1, #2, #3)
- Peut superviser tout le module

### Scénario 2 : Responsable du Module

**Contexte** :
- Module : "Authentification"
- Responsable du module : DON DIEU

**Via "Mes Modules"** :
- DON DIEU voit : ✅ Toutes les tâches (#1, #2, #3)
- Peut créer de nouvelles tâches
- Peut assigner des tâches

**Via "Gestion des Modules"** :
- DON DIEU voit : ✅ Toutes les tâches (#1, #2, #3)
- Même vue que "Mes Modules"

### Scénario 3 : Contributeur Simple

**Contexte** :
- Module : "Authentification"
- Contributeur : Jean Dupont
- Tâches assignées : Tâche #3 uniquement

**Via "Mes Modules"** :
- Jean Dupont voit : ✅ Tâche #3 uniquement
- Ne peut pas créer de tâches
- Message affiché : "Vous voyez uniquement les tâches qui vous sont assignées"

**Via "Gestion des Modules"** :
- Jean Dupont voit : ✅ Toutes les tâches (#1, #2, #3)
- Peut voir le contexte complet du module

## Avantages de Cette Logique

### 1. Séparation Claire des Contextes

- **"Mes Modules"** = Vue personnelle, focus sur MES tâches
- **"Gestion des Modules"** = Vue de gestion, vision complète

### 2. Respect de la Hiérarchie

- Le responsable du module garde le contrôle total
- Les autres voient uniquement leurs tâches dans leur vue personnelle

### 3. Flexibilité

- Le responsable du projet peut voir ses tâches dans "Mes Modules"
- Il peut aller dans "Gestion" s'il veut superviser tout le module

### 4. Cohérence avec le Nom

- "Mes Modules" implique vraiment "mes tâches dans ces modules"
- Pas de confusion sur ce qu'on voit

### 5. Pas de Surcharge

- Chacun se concentre sur son travail dans sa vue personnelle
- La vue de gestion reste disponible pour la supervision

## Tableau Récapitulatif Complet

| Utilisateur | Accès | Tâches Visibles | Peut Créer | Peut Modifier |
|-------------|-------|-----------------|------------|---------------|
| **Responsable du module** | Mes Modules | Toutes | ✅ Oui | ✅ Toutes |
| **Responsable du module** | Gestion | Toutes | ✅ Oui | ✅ Toutes |
| **Responsable du projet** | Mes Modules | Ses tâches | ❌ Non | ❌ Non |
| **Responsable du projet** | Gestion | Toutes | ❌ Non | ❌ Non |
| **Contributeur** | Mes Modules | Ses tâches | ❌ Non | ❌ Non |
| **Contributeur** | Gestion | Toutes | ❌ Non | ❌ Non |

## Tests Recommandés

### Test 1 : Responsable du Projet (Non Responsable du Module)

1. ✅ Se connecter en tant que responsable du projet
2. ✅ Aller dans "Mes Modules"
3. ✅ Cliquer sur un module où on n'est pas responsable
4. ✅ Vérifier qu'on ne voit QUE ses tâches assignées
5. ✅ Vérifier le message informatif
6. ✅ Retourner et aller dans "Gestion des Modules"
7. ✅ Vérifier qu'on voit TOUTES les tâches

### Test 2 : Responsable du Module

1. ✅ Se connecter en tant que responsable du module
2. ✅ Aller dans "Mes Modules"
3. ✅ Cliquer sur son module
4. ✅ Vérifier qu'on voit TOUTES les tâches
5. ✅ Vérifier qu'on peut créer des tâches
6. ✅ Pas de message informatif restrictif

### Test 3 : Contributeur

1. ✅ Se connecter en tant que contributeur
2. ✅ Aller dans "Mes Modules"
3. ✅ Cliquer sur un module
4. ✅ Vérifier qu'on ne voit QUE ses tâches
5. ✅ Vérifier le message informatif
6. ✅ Vérifier qu'on ne peut pas créer de tâches

## Fichiers Modifiés

1. **core/views_taches_module.py**
   - Ajout du flag `est_responsable_module`
   - Modification de la logique de filtrage des tâches
   - Nouvelle condition : `if from_mes_modules and not est_responsable_module`

2. **templates/core/gestion_taches_module.html**
   - Mise à jour du message informatif
   - Condition : `{% if from_mes_modules and not peut_creer_taches %}`

## Action Requise

⚠️ **Redémarrer le serveur Django** pour que les changements prennent effet :

```bash
# Arrêter avec Ctrl+C puis relancer
python manage.py runserver
```

## Résultat Final

✅ "Mes Modules" = Vue personnelle (mes tâches uniquement)  
✅ Responsable du module voit tout dans "Mes Modules"  
✅ Responsable du projet voit uniquement ses tâches dans "Mes Modules"  
✅ "Gestion des Modules" = Vue complète pour tous  
✅ Séparation claire des contextes  
✅ Cohérence avec le nom de l'interface

---

**Note** : Cette logique renforce la distinction entre la vue personnelle ("Mes Modules") et la vue de gestion ("Gestion des Modules"), offrant ainsi une meilleure expérience utilisateur et une meilleure organisation du travail.
