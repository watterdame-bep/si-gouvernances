"""
Script pour corriger l'ordre d'affichage des statuts
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import StatutProjet

print("=" * 70)
print("CORRECTION DE L'ORDRE DES STATUTS")
print("=" * 70)

# Corriger l'ordre
try:
    statut_planifie = StatutProjet.objects.get(nom='PLANIFIE')
    statut_planifie.ordre_affichage = 2
    statut_planifie.save()
    print(f"✅ Statut PLANIFIE mis à jour: ordre_affichage = 2")
except StatutProjet.DoesNotExist:
    print("❌ Statut PLANIFIE non trouvé")

try:
    statut_en_cours = StatutProjet.objects.get(nom='EN_COURS')
    statut_en_cours.ordre_affichage = 3
    statut_en_cours.save()
    print(f"✅ Statut EN_COURS mis à jour: ordre_affichage = 3")
except StatutProjet.DoesNotExist:
    print("❌ Statut EN_COURS non trouvé")

print("\n📊 STATUTS APRÈS CORRECTION:")
print("-" * 70)
statuts = StatutProjet.objects.all().order_by('ordre_affichage')
for statut in statuts:
    print(f"   {statut.get_nom_display()} - Ordre: {statut.ordre_affichage}")

print("\n" + "=" * 70)
print("✅ CORRECTION TERMINÉE")
print("=" * 70)
