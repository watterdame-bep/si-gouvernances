# Guide de Test - Optimisation Liste des Projets

**Date**: 13 février 2026  
**Durée estimée**: 10 minutes

## Prérequis

- Serveur Django démarré: `python manage.py runserver`
- Compte administrateur actif
- Au moins 2-3 projets dans la base de données

## Test 1: Vérification de l'Interface (2 min)

### Étapes
1. Se connecter en tant qu'administrateur
2. Accéder à la liste des projets: `/projets/`
3. Observer le tableau

### Points à vérifier
- ✅ L'icône circulaire avec l'initiale du projet a disparu
- ✅ La colonne "Budget" n'apparaît plus
- ✅ L'ordre des colonnes est: Projet, Date création, Statut, Client, Responsable, Actions
- ✅ La date de création est bien en 2ème position
- ✅ Le tableau est propre et lisible

### Résultat attendu
```
┌─────────────┬──────────────┬─────────┬─────────┬──────────────┬─────────┐
│ Projet      │ Date création│ Statut  │ Client  │ Responsable  │ Actions │
├─────────────┼──────────────┼─────────┼─────────┼──────────────┼─────────┤
│ Mon Projet  │ 13/02/2026   │ En cours│ Client A│ John Doe     │ 👁️ ✏️ 🗑️ │
└─────────────┴──────────────┴─────────┴─────────┴──────────────┴─────────┘
```

## Test 2: Bouton de Suppression (2 min)

### Étapes
1. Dans la liste des projets
2. Localiser la colonne "Actions"
3. Observer les boutons pour chaque projet

### Points à vérifier
- ✅ 3 boutons visibles: Voir (bleu), Modifier (gris), Supprimer (rouge)
- ✅ Le bouton de suppression a une icône de corbeille
- ✅ Le bouton est rouge (bg-red-100 hover:bg-red-200)
- ✅ Survol du bouton affiche "Supprimer le projet"

### Résultat attendu
Trois boutons alignés horizontalement:
- 👁️ (bleu) - Voir
- ✏️ (gris) - Modifier
- 🗑️ (rouge) - Supprimer

## Test 3: Modale de Confirmation (3 min)

### Étapes
1. Cliquer sur le bouton rouge de suppression d'un projet
2. Observer la modale qui s'affiche

### Points à vérifier
- ✅ Modale s'affiche au centre de l'écran
- ✅ Fond semi-transparent (overlay gris)
- ✅ Icône d'avertissement rouge visible
- ✅ Titre: "Confirmer la suppression"
- ✅ Message affiche le nom du projet en gras
- ✅ Message d'avertissement en rouge: "Cette action est irréversible..."
- ✅ Deux boutons: "Annuler" (gris) et "Supprimer" (rouge)

### Test de fermeture
1. ✅ Cliquer sur "Annuler" → modale se ferme
2. ✅ Cliquer en dehors de la modale → modale se ferme
3. ✅ Rouvrir la modale pour le test suivant

## Test 4: Suppression Effective (3 min)

### Étapes
1. Créer un projet de test nommé "PROJET_TEST_SUPPRESSION"
2. Retourner à la liste des projets
3. Cliquer sur le bouton de suppression du projet test
4. Dans la modale, vérifier que le nom "PROJET_TEST_SUPPRESSION" s'affiche
5. Cliquer sur "Supprimer"

### Points à vérifier
- ✅ Message de succès s'affiche: "Projet "PROJET_TEST_SUPPRESSION" supprimé avec succès."
- ✅ Redirection vers la liste des projets
- ✅ Le projet n'apparaît plus dans la liste
- ✅ Le compteur de projets a diminué de 1

### Vérification de l'audit
```python
# Dans le shell Django
python manage.py shell

from core.models import ActionAudit
from django.utils import timezone

# Dernière suppression
derniere_suppression = ActionAudit.objects.filter(
    type_action='SUPPRESSION_PROJET'
).order_by('-timestamp').first()

print(f"Action: {derniere_suppression.type_action}")
print(f"Description: {derniere_suppression.description}")
print(f"Utilisateur: {derniere_suppression.utilisateur.get_full_name()}")
print(f"Date: {derniere_suppression.timestamp}")
print(f"Données: {derniere_suppression.donnees_avant}")
```

### Résultat attendu
```
Action: SUPPRESSION_PROJET
Description: Suppression du projet PROJET_TEST_SUPPRESSION
Utilisateur: Admin User
Date: 2026-02-13 14:30:00
Données: {'nom': 'PROJET_TEST_SUPPRESSION', 'client': '...', ...}
```

## Test 5: Permissions (2 min)

### Test avec utilisateur normal

#### Étapes
1. Se déconnecter
2. Se connecter avec un compte utilisateur normal (non admin)
3. Accéder à la liste des projets

#### Points à vérifier
- ✅ Le bouton de suppression (rouge) n'apparaît PAS
- ✅ Seuls les boutons "Voir" et éventuellement "Modifier" sont visibles
- ✅ Pas d'erreur JavaScript dans la console

### Test d'accès direct à l'URL

#### Étapes
1. Toujours connecté en tant qu'utilisateur normal
2. Tenter d'accéder directement à: `/projets/<uuid>/supprimer/`
3. Utiliser la méthode POST (via curl ou Postman)

#### Résultat attendu
- ✅ Erreur 403 Forbidden ou redirection
- ✅ Message: "Accès non autorisé"
- ✅ Audit enregistre la tentative d'accès non autorisé

## Test 6: Responsivité (2 min)

### Test sur PC
1. Ouvrir la liste des projets sur un écran large
2. Vérifier que toutes les colonnes sont visibles
3. Vérifier l'espacement entre les colonnes

### Test sur Tablette
1. Réduire la fenêtre du navigateur (ou utiliser les outils de développement)
2. Vérifier que le tableau reste lisible
3. Vérifier le défilement horizontal si nécessaire

### Test sur Smartphone
1. Ouvrir sur un smartphone ou simuler (F12 → mode responsive)
2. Vérifier que le tableau a un défilement horizontal
3. Vérifier que la modale s'affiche correctement
4. Vérifier que les boutons sont cliquables

### Points à vérifier
- ✅ Tableau responsive avec défilement horizontal
- ✅ Modale centrée sur tous les écrans
- ✅ Boutons d'action accessibles
- ✅ Texte lisible sur petit écran

## Checklist Finale

### Interface
- [ ] Icône du projet supprimée
- [ ] Colonne Budget supprimée
- [ ] Date création en 2ème position
- [ ] Ordre des colonnes correct
- [ ] Bouton de suppression visible (admin)

### Fonctionnalité
- [ ] Modale s'affiche correctement
- [ ] Nom du projet affiché dans la modale
- [ ] Bouton "Annuler" fonctionne
- [ ] Fermeture en cliquant dehors fonctionne
- [ ] Suppression effective du projet
- [ ] Message de confirmation affiché

### Sécurité
- [ ] Bouton invisible pour utilisateurs normaux
- [ ] Accès direct à l'URL bloqué
- [ ] Audit enregistré
- [ ] Protection CSRF active

### Responsivité
- [ ] Lisible sur PC
- [ ] Lisible sur tablette
- [ ] Lisible sur smartphone
- [ ] Modale responsive

## Problèmes Courants et Solutions

### Problème 1: Bouton de suppression ne s'affiche pas
**Cause**: Utilisateur non administrateur  
**Solution**: Se connecter avec un compte Super Admin

### Problème 2: Modale ne s'affiche pas
**Cause**: Erreur JavaScript  
**Solution**: Vérifier la console (F12) pour les erreurs

### Problème 3: Erreur 403 lors de la suppression
**Cause**: Permissions insuffisantes  
**Solution**: Vérifier que l'utilisateur est bien Super Admin

### Problème 4: Projet non supprimé
**Cause**: Erreur dans la vue ou cascade  
**Solution**: Vérifier les logs Django et la console

## Commandes Utiles

### Créer un projet de test
```python
python manage.py shell

from core.models import Projet, StatutProjet, Utilisateur
from decimal import Decimal

admin = Utilisateur.objects.filter(is_superuser=True).first()
statut = StatutProjet.objects.get(nom='IDEE')

projet_test = Projet.objects.create(
    nom='PROJET_TEST_SUPPRESSION',
    description='Projet pour tester la suppression',
    client='Client Test',
    budget_previsionnel=Decimal('10000'),
    statut=statut,
    createur=admin,
    duree_projet=30
)

print(f"Projet créé: {projet_test.id}")
```

### Vérifier les audits
```python
from core.models import ActionAudit

# Toutes les suppressions
suppressions = ActionAudit.objects.filter(
    type_action='SUPPRESSION_PROJET'
).order_by('-timestamp')

for audit in suppressions[:5]:
    print(f"{audit.timestamp} - {audit.description}")
```

### Nettoyer les projets de test
```python
from core.models import Projet

# Supprimer tous les projets de test
Projet.objects.filter(nom__icontains='TEST').delete()
```

## Résultat Final Attendu

✅ Interface épurée et professionnelle  
✅ Suppression sécurisée avec confirmation  
✅ Audit complet des actions  
✅ Permissions respectées  
✅ Responsive sur tous les écrans  

**Temps total**: ~10 minutes  
**Statut**: Prêt pour la production
