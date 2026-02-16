# Guide de Test des Optimisations dans Docker

## 🎯 Objectif
Tester toutes les optimisations d'interface déployées dans Docker

---

## ✅ Statut du Déploiement

**Date** : 2026-02-16  
**Container** : `si_gouvernance_web`  
**Statut** : ✅ Redémarré avec succès  
**URL** : http://localhost:8000

---

## 🧪 Tests à Effectuer

### 1. Test de Suppression Dynamique des Lignes Budgétaires

**Étapes** :
1. Connectez-vous en tant qu'administrateur ou chef de projet
2. Accédez à un projet → Onglet "Paramètres"
3. Cliquez sur "Voir les dépenses" dans la section Budget
4. Cliquez sur le bouton "Supprimer" (🗑️) d'une ligne budgétaire
5. Confirmez la suppression

**Résultat attendu** :
- ✅ La ligne disparaît immédiatement du tableau
- ✅ Le résumé budgétaire se met à jour automatiquement
- ✅ Les cartes budgétaires (Matériel, Services, Disponible) se mettent à jour
- ✅ Message de succès affiché en haut à droite
- ✅ AUCUN rechargement de page

**Temps d'exécution** : < 0.5 seconde

---

### 2. Test d'Ajout Instantané de Lignes Budgétaires

**Étapes** :
1. Dans la section Budget, cliquez sur "Ajouter une dépense"
2. Remplissez le formulaire :
   - Description : "Test matériel"
   - Montant : 1000
   - Type : Matériel
3. Cliquez sur "Ajouter une ligne" (➕)
4. Ajoutez une deuxième ligne si vous voulez
5. Cliquez sur "Enregistrer"

**Résultat attendu** :
- ✅ La modale se ferme immédiatement
- ✅ Message de succès affiché
- ✅ Les cartes budgétaires se mettent à jour automatiquement
- ✅ Le total "Matériel" augmente de 1000€
- ✅ Le "Budget Disponible" diminue de 1000€
- ✅ AUCUN rechargement de page

**Temps d'exécution** : < 0.5 seconde

---

### 3. Test de Modification Instantanée du Budget Total

**Étapes** :
1. Dans la section Budget, cliquez sur "Définir le budget"
2. Entrez un nouveau montant (ex: 50000)
3. Cliquez sur "Enregistrer"

**Résultat attendu** :
- ✅ La modale se ferme immédiatement
- ✅ Message de succès affiché
- ✅ La carte "Budget Total" se met à jour avec le nouveau montant
- ✅ Le "Budget Disponible" est recalculé automatiquement
- ✅ Si le budget est dépassé, le "Budget Disponible" devient rouge
- ✅ AUCUN rechargement de page

**Temps d'exécution** : < 0.5 seconde

---

### 4. Test de Gestion Optimisée des Membres

#### 4.1 Ajouter un Membre

**Étapes** :
1. Dans l'onglet "Paramètres" du projet
2. Section "Équipe du projet"
3. Cliquez sur "Ajouter un membre"
4. Sélectionnez un membre
5. Cliquez sur "Ajouter"

**Résultat attendu** :
- ✅ Bouton affiche un spinner : "🔄 Ajout..."
- ✅ Message de succès vert avec icône ✓ apparaît en haut à droite
- ✅ Message : "Membre ajouté avec succès !"
- ✅ Rechargement de la page après 1.5 secondes
- ✅ Le nouveau membre apparaît dans la liste

**Temps d'exécution** : 1.5 secondes (avec rechargement différé)

#### 4.2 Ajouter un Responsable

**Étapes** :
1. Cliquez sur "Ajouter un responsable"
2. Sélectionnez un membre
3. Cliquez sur "Ajouter"

**Résultat attendu** :
- ✅ Bouton affiche un spinner : "🔄 Ajout..."
- ✅ Message de succès jaune avec icône 👑 : "Responsable ajouté avec succès !"
- ✅ Rechargement après 1.5 secondes

#### 4.3 Retirer un Membre

**Étapes** :
1. Cliquez sur le bouton "Retirer" (🗑️) à côté d'un membre
2. Confirmez la suppression

**Résultat attendu** :
- ✅ Bouton affiche un spinner : "🔄 Suppression..."
- ✅ Message de succès rouge avec icône 🗑️ : "Membre retiré avec succès !"
- ✅ Rechargement après 1.5 secondes

#### 4.4 Transférer la Responsabilité

**Étapes** :
1. Cliquez sur "Transférer la responsabilité"
2. Sélectionnez le nouveau responsable
3. Cliquez sur "Transférer"

**Résultat attendu** :
- ✅ Bouton affiche un spinner : "🔄 Transfert..."
- ✅ Message de succès orange avec icône ↔️ : "Responsabilité transférée avec succès !"
- ✅ Rechargement après 1.5 secondes

---

## 🎨 Vérifications Visuelles

### Messages de Succès
- Position : En haut à droite de l'écran
- Animation : Glisse depuis la droite
- Durée : 3-4 secondes avant disparition
- Couleurs :
  - Vert : Ajout de membre
  - Jaune : Ajout de responsable
  - Rouge : Suppression
  - Orange : Transfert

### Spinners
- Icône : 🔄 (rotation animée)
- Texte : "Ajout...", "Suppression...", "Transfert..."
- Bouton désactivé pendant le traitement

### Mise à Jour Dynamique
- Cartes budgétaires : Mise à jour en temps réel
- Couleur rouge : Si budget dépassé
- Suppression de lignes : Animation fluide

---

## 🐛 Problèmes Potentiels

### Si les changements ne sont pas visibles :

1. **Vider le cache du navigateur** :
   - Chrome : Ctrl + Shift + Delete
   - Firefox : Ctrl + Shift + Delete
   - Ou utilisez le mode navigation privée

2. **Vérifier que le container est bien redémarré** :
   ```bash
   docker ps --filter "name=si_gouvernance_web"
   ```

3. **Vérifier les logs** :
   ```bash
   docker logs --tail 50 si_gouvernance_web
   ```

4. **Redémarrer manuellement** :
   ```bash
   docker restart si_gouvernance_web
   ```

5. **Vérifier que vous êtes sur le bon port** :
   - URL : http://localhost:8000
   - Pas http://127.0.0.1:8000 (même si ça devrait fonctionner)

---

## 📊 Comparaison Avant/Après

| Action | Avant | Après | Gain |
|--------|-------|-------|------|
| Suppression budget | 2-3s (rechargement) | < 0.5s (dynamique) | 80-90% |
| Ajout budget | 2-3s (rechargement) | < 0.5s (dynamique) | 80-90% |
| Modification budget | 2-3s (rechargement) | < 0.5s (dynamique) | 80-90% |
| Gestion membres | 2-3s (rechargement immédiat) | 1.5s (message + rechargement) | 50% |

---

## ✅ Checklist de Test

- [ ] Suppression dynamique de ligne budgétaire
- [ ] Ajout instantané de ligne budgétaire
- [ ] Modification instantanée du budget total
- [ ] Ajout de membre avec spinner et message
- [ ] Ajout de responsable avec spinner et message
- [ ] Retrait de membre avec spinner et message
- [ ] Transfert de responsabilité avec spinner et message
- [ ] Vérification des couleurs des messages
- [ ] Vérification des animations
- [ ] Test sur mobile/tablette (responsive)

---

## 🚀 Prochaine Étape

Une fois tous les tests validés, nous pourrons implémenter la dernière fonctionnalité :
- **Synchronisation de l'email du profil membre avec le compte utilisateur** (Admin uniquement)

---

**Date** : 2026-02-16  
**Statut** : ✅ Prêt pour les tests  
**Container** : si_gouvernance_web (redémarré)
