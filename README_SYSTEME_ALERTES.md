# 🔔 Système d'Alertes d'Échéances - Guide Complet

## 📋 Vue d'ensemble

Le système d'alertes surveille automatiquement les échéances des tâches et notifie les utilisateurs concernés.

## ✅ État Actuel

- ✅ **Logique métier** : Complète et testée
- ✅ **Architecture** : Portable (Windows, Linux, Celery)
- ✅ **Tests** : Tous validés
- ✅ **Documentation** : Complète
- ⏳ **Configuration** : À faire (Planificateur Windows)

## 🚀 Démarrage Rapide

### 1. Configuration (5 minutes)

Suivez ce guide :
```
📄 CONFIGURATION_PLANIFICATEUR_ETAPE_PAR_ETAPE.md
```

### 2. Test Immédiat

```bash
# Tester manuellement
run_check_deadlines.bat

# Vérifier les résultats
python verification_systeme_alertes.py
```

### 3. Suivi Quotidien

```bash
# Chaque matin
python suivi_quotidien_alertes.py
```

## 📚 Documentation

### Guides de Configuration
| Document | Description | Durée |
|----------|-------------|-------|
| `CONFIGURATION_PLANIFICATEUR_ETAPE_PAR_ETAPE.md` | Guide rapide | 5 min |
| `CHECKLIST_CONFIGURATION_PLANIFICATEUR.md` | Checklist détaillée | 10 min |
| `GUIDE_PLANIFICATEUR_WINDOWS.md` | Guide complet | 15 min |

### Documentation Technique
| Document | Description |
|----------|-------------|
| `ETAT_SYSTEME_ALERTES_FINAL.md` | État complet du système |
| `ARCHITECTURE_ALERTES_PORTABLE.md` | Architecture et portabilité |
| `SYSTEME_ALERTES_ECHEANCES.md` | Documentation complète |

### Migration Future
| Document | Description |
|----------|-------------|
| `MIGRATION_CELERY_READY.md` | Fichiers prêts pour Celery |
| `PROCHAINE_ETAPE_CONFIGURATION.md` | Prochaines étapes |

### Résolution de Problèmes
| Document | Description |
|----------|-------------|
| `RESOLUTION_FINALE_ALERTES_ACCES_PROJET.md` | Correction bug d'accès |
| `RESOLUTION_PROBLEME_NOTIFICATIONS.md` | Diagnostic et solutions |

## 🛠️ Scripts Disponibles

### Scripts de Test
```bash
# Vérification complète du système
python verification_systeme_alertes.py

# Test du système d'alertes
python test_alertes_echeances.py

# Test d'un utilisateur spécifique
python test_don_dieu_alertes.py

# Test du filtrage
python test_filtrage_notifications.py
```

### Scripts Utilitaires
```bash
# Suivi quotidien
python suivi_quotidien_alertes.py

# Nettoyage des alertes incorrectes
python nettoyer_alertes_incorrectes.py
```

### Scripts d'Exécution
```bash
# Exécution manuelle
python manage.py check_task_deadlines

# Via script batch (avec logs)
run_check_deadlines.bat
```

## 📊 Types d'Alertes

| Type | Quand | Destinataire |
|------|-------|--------------|
| 🟡 Échéance 2 jours | 2 jours avant | Responsable tâche |
| 🟠 Échéance 1 jour | 1 jour avant | Responsable tâche |
| 🔴 Jour J | Le jour même | Responsable tâche + Responsable projet |
| 🔴 Retard | Après échéance | Responsable tâche + Responsable projet |

## 🔒 Sécurité

- ✅ Vérification systématique de `a_acces_projet()`
- ✅ Filtrage par destinataire dans l'API
- ✅ Aucune alerte pour des projets sans accès
- ✅ Prévention des doublons

## 📅 Planning

### Phase 1 : Configuration (Aujourd'hui)
- [ ] Configurer le Planificateur de tâches Windows
- [ ] Tester l'exécution manuelle
- [ ] Vérifier les logs et les alertes

### Phase 2 : Test (7 jours)
- [ ] Vérifier l'exécution quotidienne
- [ ] Surveiller les logs
- [ ] Noter les éventuels problèmes

### Phase 3 : Production (Après validation)
- [ ] Supprimer les tâches de test
- [ ] Nettoyer les alertes de test
- [ ] Documenter la configuration finale

### Phase 4 : Évolution (Futur)
- [ ] Migrer vers Celery (optionnel)
- [ ] Ajouter des alertes supplémentaires
- [ ] Implémenter l'envoi d'emails

## 🎯 Commandes Essentielles

### Exécution
```bash
# Exécution manuelle
python manage.py check_task_deadlines

# Via script batch
run_check_deadlines.bat
```

### Vérification
```bash
# Vérification complète
python verification_systeme_alertes.py

# Suivi quotidien
python suivi_quotidien_alertes.py

# Voir les logs
type logs\planificateur.log
```

### Maintenance
```bash
# Nettoyer les alertes incorrectes
python nettoyer_alertes_incorrectes.py

# Supprimer toutes les alertes
python manage.py shell
>>> from core.models import NotificationTache
>>> NotificationTache.objects.filter(type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']).delete()
```

## 🔧 Dépannage

### Problème : Aucune alerte créée

**Vérifications** :
1. Vérifier qu'il y a des tâches actives avec date de fin
2. Vérifier que les tâches sont proches de leur échéance
3. Vérifier les permissions d'accès projet
4. Vérifier les logs : `type logs\planificateur.log`

**Solution** :
```bash
# Tester manuellement
python manage.py check_task_deadlines

# Vérifier les tâches
python verification_systeme_alertes.py
```

### Problème : Alertes incorrectes

**Symptôme** : Utilisateurs voient des alertes pour des projets sans accès

**Solution** :
```bash
# Nettoyer les alertes incorrectes
python nettoyer_alertes_incorrectes.py

# Relancer la vérification
python manage.py check_task_deadlines
```

### Problème : Le Planificateur ne s'exécute pas

**Vérifications** :
1. Ouvrir le Planificateur de tâches
2. Trouver la tâche "Alertes SI-Gouvernance"
3. Clic droit → Propriétés → Onglet Historique
4. Vérifier le code de sortie (0 = succès)

**Solution** :
1. Vérifier les permissions (Exécuter avec autorisations maximales)
2. Vérifier le chemin du fichier .bat
3. Tester manuellement : `run_check_deadlines.bat`

## 📈 Monitoring

### Quotidien
```bash
# Chaque matin à 8h05
python suivi_quotidien_alertes.py
```

### Hebdomadaire
```bash
# Vérifier les statistiques de la semaine
python verification_systeme_alertes.py
```

### Mensuel
```bash
# Analyser les logs
type logs\planificateur.log | findstr "Total alertes"

# Nettoyer les anciennes alertes (optionnel)
python nettoyer_alertes_incorrectes.py
```

## 🚀 Migration Future vers Celery

Quand vous serez prêt :

1. **Lire la documentation** : `MIGRATION_CELERY_READY.md`
2. **Installer Redis et Celery** : `pip install celery redis`
3. **Créer les fichiers** : Copier-coller depuis MIGRATION_CELERY_READY.md
4. **Tester** : Démarrer les services
5. **Migrer** : Désactiver le Planificateur Windows

**Avantages** :
- ✅ Asynchrone et distribué
- ✅ Retry automatique
- ✅ Monitoring avancé (Flower)
- ✅ Scalable

## 📞 Support

### En cas de problème

1. **Consulter les logs** : `logs\planificateur.log`
2. **Exécuter le suivi** : `python suivi_quotidien_alertes.py`
3. **Vérifier le système** : `python verification_systeme_alertes.py`
4. **Consulter la documentation** : Voir section "Documentation" ci-dessus

### Codes de sortie

- `0` : Succès ✅
- `1` : Erreur générale ❌
- Autre : Erreur spécifique ❌

## 🎉 Félicitations !

Vous avez maintenant un système d'alertes complet et fonctionnel.

**Prochaine étape** : Configurer le Planificateur de tâches Windows

**Durée** : 5 minutes

**Difficulté** : Facile ⭐

**Résultat** : Système 100% automatisé ✅

---

**Date** : 09/02/2026  
**Version** : 1.0  
**Statut** : Prêt pour configuration  
**Auteur** : Système SI-Gouvernance
