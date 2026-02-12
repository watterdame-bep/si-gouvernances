# Guide de Test : Redirection Cas de Test depuis Mes Tests

## Objectif
Vérifier que les utilisateurs peuvent accéder aux cas de test depuis "Mes Tests" et que le bouton "Retour" les ramène correctement à "Mes Tests".

## Prérequis

1. Un projet avec une étape TESTS active
2. Au moins une tâche dans l'étape TESTS
3. Un utilisateur assigné comme responsable de cette tâche
4. Quelques cas de test créés pour cette tâche (optionnel mais recommandé)

## Test 1 : Accès depuis "Mes Tests"

### Étapes
1. **Connexion**
   - Se connecter avec l'utilisateur assigné à la tâche TESTS
   
2. **Navigation vers Mes Tests**
   - Aller dans le menu ou cliquer sur "Mes Tests"
   - URL : `/projets/{projet_id}/mes-taches/`
   
3. **Vérification de l'interface**
   - ✅ Vérifier que la section "Tâches d'Étapes" affiche les tâches
   - ✅ Vérifier que les tâches de l'étape TESTS ont un bouton "Cas de Test" (violet avec icône fiole)
   - ✅ Vérifier que les tâches d'autres étapes n'ont PAS ce bouton
   
4. **Accès aux Cas de Test**
   - Cliquer sur le bouton "Cas de Test" d'une tâche TESTS
   - ✅ Vérifier la redirection vers l'interface des cas de test
   - ✅ Vérifier que l'URL contient `?from=mes_tests`
   
5. **Vérification du Bouton Retour**
   - ✅ Vérifier que le bouton affiche "Retour à Mes Tests" (et non juste "Retour")
   - ✅ Vérifier que le bouton est gris avec icône flèche gauche
   
6. **Test de la Redirection**
   - Cliquer sur "Retour à Mes Tests"
   - ✅ Vérifier le retour à l'interface "Mes Tests"
   - ✅ Vérifier que l'URL est `/projets/{projet_id}/mes-taches/`

### Résultat Attendu
- Navigation fluide entre "Mes Tests" et "Cas de Test"
- Le bouton "Retour" ramène toujours à "Mes Tests"
- L'utilisateur ne se perd pas dans la navigation

## Test 2 : Accès depuis "Gestion des Tâches" (Admin)

### Étapes
1. **Connexion Admin**
   - Se connecter en tant qu'administrateur ou responsable de projet
   
2. **Navigation vers Gestion des Tâches**
   - Aller dans le projet → Étapes → Étape TESTS
   - Cliquer sur "Gestion des Tâches"
   - URL : `/projets/{projet_id}/etapes/{etape_id}/taches/`
   
3. **Accès aux Cas de Test**
   - Cliquer sur le lien vers les cas de test d'une tâche
   - ✅ Vérifier que l'URL ne contient PAS `?from=mes_tests`
   
4. **Vérification du Bouton Retour**
   - ✅ Vérifier que le bouton affiche simplement "Retour" (sans "à Mes Tests")
   
5. **Test de la Redirection**
   - Cliquer sur "Retour"
   - ✅ Vérifier le retour à "Gestion des Tâches"
   - ✅ Vérifier que l'URL est `/projets/{projet_id}/etapes/{etape_id}/taches/`

### Résultat Attendu
- Le comportement par défaut est préservé pour les admins
- Le bouton "Retour" ramène à "Gestion des Tâches"

## Test 3 : Cas Limites

### Test 3.1 : Tâche sans Cas de Test
1. Accéder aux cas de test d'une tâche vide depuis "Mes Tests"
2. ✅ Vérifier l'affichage de l'état vide avec message approprié
3. ✅ Vérifier que le bouton "Retour à Mes Tests" fonctionne toujours

### Test 3.2 : Tâches d'Autres Étapes
1. Dans "Mes Tests", vérifier les tâches d'autres étapes (Planification, Développement, etc.)
2. ✅ Vérifier qu'elles n'ont PAS de bouton "Cas de Test"
3. ✅ Vérifier que seules les tâches TESTS ont ce bouton

### Test 3.3 : Navigation Multiple
1. Depuis "Mes Tests" → Cas de Test → Retour à Mes Tests
2. Répéter plusieurs fois
3. ✅ Vérifier que la navigation reste cohérente
4. ✅ Vérifier qu'il n'y a pas d'erreurs dans la console

## Checklist Finale

- [ ] Le bouton "Cas de Test" apparaît uniquement pour les tâches TESTS
- [ ] Le bouton "Cas de Test" a le bon style (violet, icône fiole)
- [ ] L'URL contient `?from=mes_tests` lors de l'accès depuis "Mes Tests"
- [ ] Le bouton "Retour" affiche "Retour à Mes Tests" quand `from=mes_tests`
- [ ] Le bouton "Retour" affiche simplement "Retour" dans les autres cas
- [ ] La redirection vers "Mes Tests" fonctionne correctement
- [ ] La redirection vers "Gestion des Tâches" fonctionne correctement (cas par défaut)
- [ ] Pas d'erreurs dans la console du navigateur
- [ ] Pas d'erreurs dans les logs Django

## Problèmes Potentiels et Solutions

### Problème : Le bouton "Cas de Test" n'apparaît pas
**Solution** : Vérifier que `tache.etape.type_etape.nom == 'TESTS'`

### Problème : Le paramètre `from` n'est pas dans l'URL
**Solution** : Vérifier que le lien inclut bien `?from=mes_tests`

### Problème : Le bouton "Retour" ne change pas de texte
**Solution** : Vérifier que `request.GET.from` est accessible dans le template

### Problème : Erreur 404 lors de la redirection
**Solution** : Vérifier que l'URL `mes_taches` existe et accepte `projet_id`

## Commandes Utiles

### Vérifier les logs Django
```bash
# Voir les logs en temps réel
python manage.py runserver
```

### Vérifier les URLs
```bash
python manage.py show_urls | grep mes_taches
python manage.py show_urls | grep cas_tests
```

## Statut du Test
- [ ] Test 1 : Accès depuis "Mes Tests" - ⏳ En attente
- [ ] Test 2 : Accès depuis "Gestion des Tâches" - ⏳ En attente
- [ ] Test 3 : Cas Limites - ⏳ En attente

## Notes
- Cette fonctionnalité utilise le même pattern que "Mes Modules" avec `?from=mes_modules`
- Aucune modification backend n'est nécessaire
- Tout est géré dans les templates Django
