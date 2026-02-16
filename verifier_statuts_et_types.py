"""
Script pour vérifier les statuts de projet et types d'étapes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import StatutProjet, TypeEtape

print("=" * 70)
print("VÉRIFICATION DES DONNÉES DE BASE")
print("=" * 70)

# Vérifier les statuts
print("\n📊 STATUTS DE PROJET:")
print("-" * 70)
statuts = StatutProjet.objects.all().order_by('ordre_affichage')
for statut in statuts:
    print(f"   ✅ {statut.get_nom_display()} ({statut.nom})")
    print(f"      Couleur: {statut.couleur_affichage}")
    print(f"      Ordre: {statut.ordre_affichage}")
    print()

print(f"Total: {statuts.count()} statut(s)")

# Vérifier les types d'étapes
print("\n🔄 TYPES D'ÉTAPES (CYCLE DE VIE):")
print("-" * 70)
types = TypeEtape.objects.all().order_by('ordre_standard')
for type_etape in types:
    print(f"   ✅ {type_etape.get_nom_display()} ({type_etape.nom})")
    print(f"      Couleur: {type_etape.couleur}")
    print(f"      Ordre: {type_etape.ordre_standard}")
    print(f"      Icône: {type_etape.icone_emoji}")
    print()

print(f"Total: {types.count()} type(s) d'étape")

# Vérifier que le statut EN_COURS existe
print("\n🔍 VÉRIFICATION STATUT EN_COURS:")
print("-" * 70)
try:
    statut_en_cours = StatutProjet.objects.get(nom='EN_COURS')
    print(f"   ✅ Statut EN_COURS trouvé: {statut_en_cours.get_nom_display()}")
except StatutProjet.DoesNotExist:
    print("   ❌ ERREUR: Statut EN_COURS non trouvé!")

print("\n" + "=" * 70)
print("✅ VÉRIFICATION TERMINÉE")
print("=" * 70)
