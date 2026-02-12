# Accès Rapide - Système d'Alertes ⚡

## ✅ Statut : TERMINÉ ET TESTÉ

---

## 🚀 Tester en 2 commandes

### Test alertes J-7 (échéances)
```bash
python test_alerte_j7.py
```

### Test alertes projets en retard
```bash
python test_alerte_retard.py
```

### Test alertes tâches en retard
```bash
python test_alerte_tache_retard.py
```

Puis ouvrir : `http://127.0.0.1:8000/`

---

## 📊 Types d'Alertes

| Type | Niveau | Destinataires |
|------|--------|---------------|
| J-7 | Avertissement | Resp projet + Admin |
| J-3 | Attention | Resp projet + Admin |
| J-1 | Urgent | Resp projet + Admin |
| Projet en retard | Critique | Resp projet + Admin |
| Tâche en retard | Critique | Resp tâche + Resp projet |

---

## 🔧 Commandes

### Vérifier les échéances projets
```bash
python manage.py check_project_deadlines
```

### Vérifier les échéances tâches
```bash
python manage.py check_task_deadlines
```

---

## 📚 Documentation

### Démarrage rapide
- `ALERTES_QUICK_START.md` - 5 minutes

### Guides de test
- `COMMENT_TESTER_ALERTE_RETARD.md` - Projets en retard
- `COMMENT_TESTER_ALERTE_TACHE_RETARD.md` - Tâches en retard

### Documentation complète
- `INDEX_DOCUMENTATION_ALERTES_COMPLETE.md` - Index complet
- `SESSION_2026_02_12_ALERTES_COMPLETE_FINAL.md` - Récap session

### Configuration
- `GUIDE_PLANIFICATEUR_WINDOWS.md` - Automatisation

---

## 🐛 Problème résolu

**ProtectedError** lors de la suppression des projets de test :
- ✅ Correction appliquée dans `test_alerte_tache_retard.py`
- ✅ Suppression des `ActionAudit` avant les projets

---

## 📁 Fichiers Clés

### Code source
- `core/management/commands/check_project_deadlines.py`
- `core/management/commands/check_task_deadlines.py`
- `core/views_alertes.py`
- `templates/core/alertes.html`
- `templates/base.html`

### Scripts de test
- `test_alerte_j7.py`
- `test_alerte_retard.py`
- `test_alerte_tache_retard.py`

---

## ✅ Checklist

- [x] Alertes J-7, J-3, J-1 implémentées
- [x] Alertes projets en retard implémentées
- [x] Alertes tâches en retard implémentées
- [x] JavaScript mise à jour badge automatique
- [x] Scripts de test fonctionnels
- [x] Documentation complète
- [x] Correction ProtectedError
- [ ] Configuration Planificateur Windows (à faire)

---

**Prochaine étape** : Configurer le Planificateur Windows pour automatiser les vérifications quotidiennes.

Voir : `GUIDE_PLANIFICATEUR_WINDOWS.md`

