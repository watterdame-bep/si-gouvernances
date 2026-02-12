# Guide de Test : Masquage du Formulaire de Résolution

**Date**: 12 février 2026  
**Ticket de test**: MAINT-00002 "Attaque du titan"

---

## 📋 ÉTAT ACTUEL DU TICKET

```
Numéro: MAINT-00002
Titre: Attaque du titan
Statut: EN_COURS
Priorité: BASSE
Assignés: DON DIEU, Eraste Butela
Date résolution: Aucune
Solution: Aucune
```

---

## ✅ COMPORTEMENT ATTENDU

### AVANT Résolution (Statut = EN_COURS)
- ✅ Le formulaire "Résoudre le ticket" DOIT être visible
- ✅ Les champs suivants doivent être présents :
  - Solution apportée (obligatoire)
  - Fichiers modifiés (optionnel)
  - Temps passé (heures)
  - Bouton "Marquer comme résolu"
- ❌ La section verte "Ticket résolu" NE DOIT PAS être visible

### APRÈS Résolution (Statut = RESOLU)
- ❌ Le formulaire "Résoudre le ticket" NE DOIT PLUS être visible
- ✅ La section verte "Ticket résolu" DOIT apparaître avec :
  - Titre "Ticket résolu"
  - Solution apportée
  - Fichiers modifiés (si fournis)
  - Date de résolution

---

## 🧪 PROCÉDURE DE TEST

### Étape 1 : Vérifier l'état initial (EN_COURS)
1. Se connecter en tant que **DON DIEU**
2. Aller sur le ticket **MAINT-00002**
3. **VÉRIFIER** :
   - ✅ Le formulaire "Résoudre le ticket" est visible
   - ✅ Les 3 champs sont présents
   - ❌ Pas de section verte "Ticket résolu"

### Étape 2 : Résoudre le ticket
1. Remplir le formulaire :
   - **Solution apportée** : "Test de résolution du ticket. Le problème a été corrigé en modifiant le fichier X."
   - **Fichiers modifiés** : "src/components/Ticket.js\nsrc/utils/helpers.js"
   - **Temps passé** : 2.5
2. Cliquer sur **"Marquer comme résolu"**
3. **ATTENDRE** le message de succès vert : "Ticket marqué comme résolu avec succès !"

### Étape 3 : Vérifier l'état après résolution (RESOLU)
1. La page devrait se recharger automatiquement
2. **VÉRIFIER** :
   - ❌ Le formulaire "Résoudre le ticket" a disparu
   - ✅ La section verte "Ticket résolu" est visible
   - ✅ La solution s'affiche correctement
   - ✅ Les fichiers modifiés s'affichent
   - ✅ La date de résolution s'affiche

### Étape 4 : Vérifier le statut dans la base
Exécuter le script de debug :
```bash
python debug_ticket_maint_00002.py
```

**Résultat attendu** :
```
Statut: RESOLU
Date résolution: 2026-02-12 XX:XX:XX
Solution: Test de résolution du ticket...
ticket.statut == 'RESOLU': True
✅ Le formulaire NE DEVRAIT PAS s'afficher (statut RESOLU)
```

---

## 🐛 SI LE FORMULAIRE S'AFFICHE ENCORE APRÈS RÉSOLUTION

### Diagnostic
1. Vérifier le statut réel du ticket :
   ```bash
   python debug_ticket_maint_00002.py
   ```

2. Si le statut est toujours `EN_COURS` :
   - ❌ La résolution a échoué
   - Vérifier les erreurs dans la console du navigateur (F12)
   - Vérifier les logs Django

3. Si le statut est `RESOLU` mais le formulaire s'affiche :
   - ❌ Problème dans le template
   - Vérifier la condition : `{% if peut_resoudre and ticket.statut == 'EN_COURS' %}`

### Solutions
- Rafraîchir la page (Ctrl+F5)
- Vider le cache du navigateur
- Vérifier que le fichier `templates/core/detail_ticket.html` a bien été modifié

---

## 📊 RÉSULTATS ATTENDUS

| État | Statut | Formulaire visible ? | Section verte visible ? |
|------|--------|---------------------|------------------------|
| Initial | EN_COURS | ✅ OUI | ❌ NON |
| Après résolution | RESOLU | ❌ NON | ✅ OUI |
| Après fermeture | FERME | ❌ NON | ✅ OUI |

---

## 🎯 CONCLUSION

Le ticket MAINT-00002 est actuellement en statut **EN_COURS**, donc le formulaire s'affiche normalement.

Pour tester le masquage du formulaire, il faut :
1. Remplir le formulaire de résolution
2. Cliquer sur "Marquer comme résolu"
3. Vérifier que le formulaire disparaît et que la section verte apparaît

**C'est le comportement attendu et correct !**
