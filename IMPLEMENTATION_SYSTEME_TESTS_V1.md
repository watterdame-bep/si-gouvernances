# IMPLÉMENTATION SYSTÈME DE TESTS V1

## 🎯 OBJECTIF
Implémenter une V1 fonctionnelle de l'étape TEST, simple, robuste et professionnelle.

## 📊 MODÈLES SIMPLIFIÉS

### 1. TacheTest
- Hérite du concept de tâche existant
- Types: FONCTIONNEL uniquement (V1)
- Statuts: EN_ATTENTE, EN_COURS, PASSE, ECHEC
- Assignation QA

### 2. BugTest
- Gravité: CRITIQUE, MAJEUR, MINEUR
- Workflow simple: OUVERT → ASSIGNE → RESOLU → FERME
- Lien avec TacheTest
- Assignation développeur

### 3. ValidationTest
- Validation par Chef de projet uniquement
- Critères: aucun bug critique + tous tests passés
- Traçabilité complète

## 🔄 FLUX MÉTIER V1

### Phase 1: Création des tests
1. Étape DÉVELOPPEMENT terminée
2. Activation automatique étape TEST
3. QA créent les tâches de test
4. Assignation et exécution

### Phase 2: Gestion des bugs
1. Test échoue → création bug
2. Bug assigné au développeur
3. Correction → re-test
4. Fermeture du bug

### Phase 3: Validation
1. Vérification: aucun bug critique
2. Vérification: tous tests passés
3. Chef de projet valide
4. Passage au DÉPLOIEMENT

## 🎨 INTERFACE V1

### Pages principales:
- `/projets/{id}/etapes/{id}/tests/` - Vue d'ensemble
- `/projets/{id}/etapes/{id}/tests/creer/` - Créer test
- `/projets/{id}/etapes/{id}/bugs/` - Liste bugs
- `/projets/{id}/etapes/{id}/bugs/creer/` - Créer bug

### Composants:
- Liste tests avec statuts
- Liste bugs avec gravité
- Bouton validation (Chef projet uniquement)
- Formulaires simples Bootstrap

## 📋 PLAN D'IMPLÉMENTATION

1. ✅ Architecture et modèles
2. 🔄 Modèles Django
3. ⏳ Services métier
4. ⏳ Vues et URLs
5. ⏳ Templates
6. ⏳ Tests et validation

## 🚫 EXCLUSIONS V1

- Métriques avancées
- Tests de performance
- Couverture de code
- Intégration CI/CD
- Rapports complexes