"""
Script pour supprimer les alertes incorrectes (créées avant la correction)
et relancer la vérification avec le code corrigé
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationTache, Utilisateur

print("=" * 70)
print("NETTOYAGE DES ALERTES INCORRECTES")
print("=" * 70)

# Compter les alertes avant suppression
total_avant = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
).count()

print(f"\n📊 Total alertes avant nettoyage: {total_avant}")

# Supprimer TOUTES les alertes (pour repartir sur une base saine)
alertes_supprimees = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
).delete()

print(f"🗑️  Alertes supprimées: {alertes_supprimees[0]}")

# Vérifier qu'il n'y a plus d'alertes
total_apres = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
).count()

print(f"✅ Total alertes après nettoyage: {total_apres}")

print("\n" + "=" * 70)
print("✅ NETTOYAGE TERMINÉ")
print("=" * 70)
print("\n💡 PROCHAINE ÉTAPE:")
print("Exécuter: python manage.py check_task_deadlines")
print("\nCette commande va recréer les alertes UNIQUEMENT pour les utilisateurs")
print("qui ont accès aux projets concernés.")
