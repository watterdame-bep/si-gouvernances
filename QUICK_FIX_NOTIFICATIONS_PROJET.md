# Quick Fix: Notifications de projet maintenant visibles

## Problème résolu
Les notifications d'affectation de responsable étaient créées mais invisibles dans l'interface.

## Solution
Ajout de `NotificationProjet` dans l'API notifications (`core/views.py`)

## Action requise
```bash
# Redémarrer le serveur Django
python manage.py runserver
```

## Test rapide
1. Se connecter avec Eraste Butela
2. Vérifier le badge de notification (devrait afficher "1")
3. Cliquer sur l'icône de notification
4. La notification "🎯 Vous êtes responsable du projet..." devrait s'afficher

## Scripts de vérification
```bash
# Vérifier que la notification existe en base
python verifier_notification_eraste.py

# Tester l'API
python test_notification_projet_api.py

# Marquer comme non lue pour tester
python marquer_notification_non_lue.py
```

## Résultat attendu
- Badge: Affiche "1" ✅
- Dropdown: Affiche la notification ✅
- Clic: Redirige vers le projet ✅
- Marquage: Notification marquée comme lue ✅

## Documentation complète
Voir `CORRECTION_AFFICHAGE_NOTIFICATIONS_PROJET.md`
