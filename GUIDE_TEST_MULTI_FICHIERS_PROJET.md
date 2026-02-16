# Guide de Test - Multi-Fichiers Projet

## Accès
- URL: http://localhost:8000
- Compte admin requis pour tester toutes les fonctionnalités

## Test 1: Création de projet avec fichiers
1. Aller sur "Projets" → "Nouveau Projet"
2. Remplir le formulaire
3. Dans "Fichiers joints", cliquer et sélectionner plusieurs fichiers
4. Vérifier que la liste des fichiers sélectionnés s'affiche
5. Soumettre le formulaire
6. Vérifier le message de succès

## Test 2: Affichage des fichiers
1. Ouvrir le projet créé
2. Dans la sidebar droite, chercher la section "Fichiers"
3. Vérifier que tous les fichiers sont affichés avec:
   - Icône selon le type
   - Nom du fichier
   - Taille formatée
   - Date d'ajout
   - Boutons télécharger et supprimer

## Test 3: Téléchargement
1. Cliquer sur l'icône de téléchargement (flèche vers le bas)
2. Vérifier que le fichier se télécharge correctement
3. Vérifier que le nom du fichier est correct

## Test 4: Ajout de fichiers supplémentaires
1. Dans la section "Fichiers", cliquer sur le bouton "+" (admins uniquement)
2. Sélectionner un ou plusieurs nouveaux fichiers
3. Vérifier l'affichage de la liste des fichiers sélectionnés
4. Cliquer sur "Ajouter"
5. Vérifier que les nouveaux fichiers apparaissent dans la liste

## Test 5: Suppression de fichier
1. Cliquer sur l'icône de suppression (poubelle) d'un fichier
2. Confirmer la suppression dans la modale
3. Vérifier que le fichier disparaît de la liste
4. Vérifier le message de succès

## Test 6: Permissions
1. Se connecter avec un compte non-admin membre du projet
2. Vérifier que le bouton "+" n'est pas visible
3. Vérifier que les icônes de suppression ne sont pas visibles
4. Vérifier que le téléchargement fonctionne

## Test 7: Validation
1. Essayer d'ajouter un fichier > 10MB
2. Vérifier le message d'erreur
3. Essayer d'ajouter un fichier avec un format non supporté
4. Vérifier le comportement

## Test 8: Responsive
1. Réduire la fenêtre du navigateur (mobile)
2. Vérifier que la section fichiers reste lisible
3. Vérifier que les boutons sont accessibles
4. Tester sur tablette (largeur moyenne)

## Test 9: Scroll
1. Ajouter plus de 5 fichiers à un projet
2. Vérifier que la section a un scroll vertical
3. Vérifier que la hauteur reste raisonnable (max-h-64)

## Test 10: Types de fichiers
Tester avec différents types:
- PDF → Icône rouge
- Word (.doc, .docx) → Icône bleue
- Excel (.xls, .xlsx) → Icône verte
- PowerPoint (.ppt, .pptx) → Icône orange
- Images (.jpg, .png) → Icône violette
- Archives (.zip, .rar) → Icône jaune
- Texte (.txt) → Icône grise

## Résultats attendus
✅ Tous les fichiers s'affichent correctement
✅ Les icônes correspondent aux types
✅ Le téléchargement fonctionne
✅ La suppression fonctionne (admins)
✅ Les permissions sont respectées
✅ L'interface est responsive
✅ La validation fonctionne
✅ Le scroll apparaît si nécessaire

## En cas de problème
1. Vérifier les logs Docker: `docker-compose logs web`
2. Vérifier la console du navigateur (F12)
3. Vérifier que la migration est appliquée
4. Redémarrer le conteneur: `docker-compose restart web`
