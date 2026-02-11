"""
Script pour lister toutes les affectations de modules et leurs permissions
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import AffectationModule

print("=" * 80)
print("LISTE DES AFFECTATIONS DE MODULES ACTIVES")
print("=" * 80)

affectations = AffectationModule.objects.filter(
    date_fin_affectation__isnull=True
).select_related('utilisateur', 'module', 'module__projet')

if not affectations.exists():
    print("\n❌ Aucune affectation active trouvée")
else:
    print(f"\n✅ {affectations.count()} affectation(s) active(s) trouvée(s)\n")
    
    for aff in affectations:
        print(f"📦 Module: {aff.module.nom} (ID: {aff.module.id})")
        print(f"   Projet: {aff.module.projet.nom}")
        print(f"   👤 Utilisateur: {aff.utilisateur.get_full_name()}")
        print(f"   🎭 Rôle: {aff.get_role_module_display()}")
        print(f"   🔐 Permissions:")
        print(f"      - peut_creer_taches: {'✅ OUI' if aff.peut_creer_taches else '❌ NON'}")
        print(f"      - peut_voir_toutes_taches: {'✅ OUI' if aff.peut_voir_toutes_taches else '❌ NON'}")
        
        if aff.role_module == 'CONTRIBUTEUR' and not aff.peut_creer_taches:
            print(f"   ⚠️  ATTENTION: Contributeur sans permission de créer des tâches!")
        
        print("-" * 80)

print("\n" + "=" * 80)
