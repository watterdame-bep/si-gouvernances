# Fonctionnalité d'Impression des Rapports de Tests

## Statut: ✅ IMPLÉMENTÉ ET FONCTIONNEL

## Description
Fonctionnalité complète permettant d'imprimer un rapport détaillé des tests effectués pour une tâche terminée dans une étape de type TEST, incluant la liste complète des cas de test et leurs résultats.

## Emplacement du Bouton
Le bouton d'impression s'affiche dans l'interface de gestion des tâches d'étape (`gestion_taches_etape.html`), et **uniquement** pour les tâches qui remplissent ces conditions:
- ✅ La tâche a le statut `TERMINEE`
- ✅ L'étape est de type `TESTS`

## Architecture Technique

### 1. API Backend
**Nouvelle vue**: `api_cas_tests_tache_view` dans `core/views_tests.py`
- **URL**: `/projets/<projet_id>/etapes/<etape_id>/taches/<tache_id>/cas-tests/api/`
- **Méthode**: GET
- **Authentification**: Requise (`@login_required`)
- **Permissions**: Vérifie que l'utilisateur peut voir les tests

**Données retournées (JSON)**:
```json
{
  "success": true,
  "stats": {
    "total": 10,
    "passes": 7,
    "echecs": 2,
    "en_cours": 1,
    "en_attente": 0,
    "bloques": 0,
    "pourcentage_reussite": 70
  },
  "cas_tests": [
    {
      "numero_cas": "CT-001",
      "nom": "Test de connexion",
      "description": "Vérifier la connexion utilisateur",
      "priorite": "Haute",
      "statut": "PASSE",
      "statut_display": "Passé",
      "etapes_execution": "1. Ouvrir la page\n2. Saisir identifiants",
      "resultats_attendus": "Connexion réussie",
      "resultats_obtenus": "OK - Connexion fonctionnelle",
      "executeur": "Jean Dupont",
      "date_execution": "06/02/2026 à 14:30"
    }
  ],
  "tache": {
    "nom": "Tests de connexion",
    "description": "..."
  },
  "etape": {
    "nom": "Tests"
  },
  "projet": {
    "nom": "Mon Projet"
  }
}
```

### 2. Frontend JavaScript
**Fonction**: `imprimerRapportTache(tacheId, tacheNom)`

**Processus**:
1. Ouvre une nouvelle fenêtre avec un document HTML
2. Affiche un message de chargement
3. Appelle l'API pour récupérer les données
4. Génère un rapport HTML complet avec:
   - En-tête professionnel
   - Statistiques en cartes colorées
   - Tableau détaillé de tous les cas de test
   - Footer avec informations
5. Déclenche automatiquement l'impression
6. Gère les erreurs avec messages clairs

## Contenu du Rapport Imprimé

### En-tête
- 📋 Titre: "Rapport de Tests"
- Nom du projet
- Type d'étape et nom de la tâche
- Date et heure de génération (format français)

### Statistiques Globales (6 cartes)
1. **Total des cas** (gris)
2. **Cas passés** (vert) - avec fond coloré
3. **Cas échoués** (rouge) - avec fond coloré
4. **En cours** (bleu) - avec fond coloré
5. **Bloqués** (orange) - avec fond coloré
6. **Taux de réussite** (violet) - pourcentage

### Tableau Détaillé des Cas de Test
Colonnes:
- **#**: Numéro séquentiel
- **Numéro**: Identifiant du cas (CT-XXX)
- **Cas de Test**: Nom + description
- **Statut**: Badge coloré avec icône
  - ✓ Passé (vert)
  - ✗ Échec (rouge)
  - ▶ En cours (bleu)
  - ⊘ Bloqué (orange)
  - ○ En attente (gris)
- **Priorité**: Critique, Haute, Moyenne, Basse
- **Exécuteur**: Nom complet
- **Date**: Date et heure d'exécution
- **Résultats**: Résultats obtenus

### Footer
- Nom du projet
- Date et heure de génération
- Mention "SI-Gouvernance JCM"

## Style du Rapport

### Mise en page
- Police: Arial, sans-serif
- Largeur max: 1200px, centré
- Padding: 20px
- Couleur du texte: #333

### Cartes de statistiques
- Grille 3 colonnes responsive
- Bordures colorées selon le type
- Fonds colorés légers
- Valeurs en gros (32px)
- Labels en petit (14px)

### Tableau
- Largeur 100%
- Bordures: 1px solid #ddd
- En-têtes: fond gris (#f3f4f6)
- Lignes alternées: fond gris clair
- Padding cellules: 10-12px
- Police: 13px

### Badges de statut
- Border-radius: 12px
- Padding: 4px 10px
- Police: 11px, bold
- Couleurs thématiques

### Optimisation impression
- `@media print` pour ajustements
- Évite les coupures de page dans les cartes
- Évite les coupures de lignes du tableau

## Fichiers Modifiés

### 1. `core/views_tests.py`
- **Ajout**: Fonction `api_cas_tests_tache_view()` (ligne ~740)
- Récupère tous les cas de test d'une tâche
- Calcule les statistiques
- Retourne les données en JSON

### 2. `core/urls.py`
- **Ajout**: URL pattern pour l'API
```python
path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/api/', 
     views_tests.api_cas_tests_tache_view, name='api_cas_tests_tache'),
```

### 3. `templates/core/gestion_taches_etape.html`
- **Ligne ~330**: Bouton d'impression conditionnel
- **Ligne ~1402**: Fonction JavaScript complète `imprimerRapportTache()`
- Utilise l'API pour charger les données
- Génère un rapport HTML professionnel
- Gestion d'erreurs robuste

## Avantages de cette Implémentation

1. **API dédiée**: Données structurées en JSON, pas de parsing HTML
2. **Performance**: Chargement rapide des données
3. **Fiabilité**: Pas de dépendance sur la structure HTML
4. **Maintenabilité**: Code séparé et réutilisable
5. **Rapport complet**: Toutes les informations des cas de test
6. **Design professionnel**: Mise en page claire et structurée
7. **Statistiques visuelles**: Cartes colorées pour lecture rapide
8. **Tableau détaillé**: Tous les cas avec leurs résultats
9. **Gestion d'erreurs**: Messages clairs en cas de problème
10. **Optimisé impression**: Styles adaptés pour l'impression

## Utilisation

1. Accéder à une étape de type TEST
2. Aller dans "Gestion des tâches"
3. Trouver une tâche avec le statut "Terminée"
4. Cliquer sur l'icône d'imprimante (🖨️) à côté du badge "Terminée"
5. Le rapport se génère dans une nouvelle fenêtre
6. La boîte de dialogue d'impression s'affiche automatiquement
7. Choisir l'imprimante ou "Enregistrer en PDF"
8. Confirmer l'impression

## Exemple de Rapport

```
┌─────────────────────────────────────────────────────┐
│           📋 Rapport de Tests                       │
│              Mon Projet SI                          │
│        Tests - Tests de connexion                   │
│      Généré le 06/02/2026 à 14:30                  │
└─────────────────────────────────────────────────────┘

📊 Statistiques Globales
┌──────────┬──────────┬──────────┐
│ Total: 10│ Passés: 7│ Échecs: 2│
├──────────┼──────────┼──────────┤
│En cours:1│Bloqués: 0│Réussite:70%│
└──────────┴──────────┴──────────┘

📝 Détails des Cas de Test
┌───┬────────┬─────────────┬────────┬─────────┬──────────┬──────────┬────────────┐
│ # │ Numéro │ Cas de Test │ Statut │Priorité │Exécuteur │   Date   │ Résultats  │
├───┼────────┼─────────────┼────────┼─────────┼──────────┼──────────┼────────────┤
│ 1 │CT-001  │Test connexion│✓ Passé │  Haute  │Jean D.   │06/02 14:30│OK - Fonct. │
│ 2 │CT-002  │Test déconnex│✓ Passé │ Moyenne │Marie L.  │06/02 14:35│OK - Correct│
└───┴────────┴─────────────┴────────┴─────────┴──────────┴──────────┴────────────┘

────────────────────────────────────────────────────────
Mon Projet SI - Rapport généré le 06/02/2026 à 14:30
SI-Gouvernance JCM
```

## Gestion des Erreurs

### Erreur de chargement API
- Message: "❌ Erreur lors du chargement des données"
- Affiche le message d'erreur technique
- Permet quand même d'imprimer le rapport d'erreur

### Erreur de communication
- Message: "❌ Erreur de communication"
- Affiche le message d'erreur réseau
- Rapport d'erreur imprimable

### Aucun cas de test
- Message: "Aucun cas de test disponible"
- Affiche quand même les statistiques (à 0)

## Conformité avec les Exigences

✅ Le bouton s'affiche dans l'interface de gestion des tâches  
✅ Le bouton apparaît uniquement pour les tâches terminées  
✅ Le bouton apparaît uniquement pour les étapes de type TEST  
✅ L'utilisateur peut imprimer la liste complète des tests effectués  
✅ Le rapport inclut tous les résultats des tests  
✅ Le rapport inclut les détails de chaque cas de test  
✅ Les statistiques sont calculées et affichées  
✅ Le bouton a été retiré de l'interface de détails des cas de test  
✅ Utilisation d'icônes FontAwesome sans background  
✅ Design moderne et professionnel  
✅ API dédiée pour les données  
✅ Gestion d'erreurs robuste  
✅ Optimisé pour l'impression

## Notes Techniques

- L'API utilise `@login_required` pour la sécurité
- Les permissions sont vérifiées via `ServiceTests._peut_voir_tests()`
- Les données sont sérialisées en JSON pour faciliter le traitement
- La fonction JavaScript utilise `fetch()` pour l'appel AJAX
- Un délai de 500ms est appliqué avant l'impression pour assurer le rendu
- Les styles sont inline pour garantir l'impression correcte
- Le rapport est responsive et s'adapte à différentes tailles de page
