"""
Script pour supprimer les statuts inutiles et ne garder que Idée et Planifié
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import StatutProjet

print("=" * 70)
print("NETTOYAGE DES STATUTS DE PROJET")
print("=" * 70)

# Statuts à garder
statuts_a_garder = [StatutProjet.IDEE, StatutProjet.PLANIFIE]

# Statuts à supprimer
statuts_a_supprimer = [
    StatutProjet.AFFECTE,
    StatutProjet.EN_COURS,
    StatutProjet.SUSPENDU,
    StatutProjet.TERMINE,
    StatutProjet.ARCHIVE,
]

print(f"\n📊 Statuts actuels: {StatutProjet.objects.count()}")

print("\n🗑️  Suppression des statuts inutiles...")
for statut_nom in statuts_a_supprimer:
    try:
        statut = StatutProjet.objects.get(nom=statut_nom)
        statut_display = statut.get_nom_display()
        statut.delete()
        print(f"   ✅ Supprimé: {statut_display}")
    except StatutProjet.DoesNotExist:
        print(f"   ℹ️  N'existe pas: {statut_nom}")

print(f"\n📊 Statuts restants: {StatutProjet.objects.count()}")
print("\n✅ Statuts conservés:")
for statut in StatutProjet.objects.all():
    print(f"   - {statut.get_nom_display()}")

print("\n" + "=" * 70)
print("✅ NETTOYAGE TERMINÉ")
print("=" * 70)
