# Comment Tester l'Alerte de Retard ? 🔴

## En 2 commandes

### 1. Exécuter le script de test
```bash
python test_alerte_retard.py
```

### 2. Ouvrir le navigateur
```
http://127.0.0.1:8000/
```

Regarder la sidebar → Le menu "Alertes" devrait avoir un badge rouge

Cliquer sur "Alertes" → Voir l'alerte de RETARD avec badge "Critique" (rouge)

---

## C'est tout ! ✅

Le script fait automatiquement :
- ✅ Crée un projet en retard de 3 jours
- ✅ Exécute la commande de vérification
- ✅ Crée l'alerte de niveau CRITIQUE
- ✅ Affiche les instructions

---

## Résultat attendu

### Dans la console
```
✅ TEST RÉUSSI!

Le système d'alertes de retard fonctionne correctement:
  ✓ Projet en retard créé
  ✓ Commande exécutée sans erreur
  ✓ Alerte RETARD créée avec niveau CRITIQUE
```

### Dans l'interface
- Badge rouge sur "Alertes"
- Alerte avec badge "Critique" (rouge)
- Icône ❌ (fa-times-circle)
- Message : "Le projet X est en retard de 3 jours..."

---

## Guide complet

Pour plus de détails : `ALERTE_PROJET_EN_RETARD.md`
