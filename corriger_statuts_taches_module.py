"""
Script pour corriger les statuts invalides des tâches de module
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import TacheModule

print("\n" + "="*60)
print("CORRECTION DES STATUTS INVALIDES - TACHES MODULE")
print("="*60 + "\n")

# Statuts valides
STATUTS_VALIDES = ['A_FAIRE', 'EN_COURS', 'EN_PAUSE', 'TERMINEE']

# Trouver toutes les tâches
taches = TacheModule.objects.all()
print(f"Nombre total de tâches de module: {taches.count()}\n")

# Vérifier les statuts
taches_invalides = []
for tache in taches:
    if tache.statut not in STATUTS_VALIDES:
        taches_invalides.append(tache)
        print(f"❌ Tâche #{tache.id}: {tache.nom}")
        print(f"   Statut actuel: '{tache.statut}' (INVALIDE)")
        print(f"   Module: {tache.module.nom}")
        print(f"   Responsable: {tache.responsable.get_full_name() if tache.responsable else 'Aucun'}")
        print()

if not taches_invalides:
    print("✅ Tous les statuts sont valides !")
else:
    print(f"\n{len(taches_invalides)} tâche(s) avec statut invalide trouvée(s).\n")
    
    reponse = input("Voulez-vous corriger ces statuts en les changeant en 'A_FAIRE' ? (oui/non): ")
    
    if reponse.lower() in ['oui', 'o', 'yes', 'y']:
        print("\nCorrection en cours...")
        for tache in taches_invalides:
            ancien_statut = tache.statut
            tache.statut = 'A_FAIRE'
            tache.save()
            print(f"✅ Tâche #{tache.id}: '{ancien_statut}' → 'A_FAIRE'")
        
        print(f"\n✅ {len(taches_invalides)} tâche(s) corrigée(s) avec succès !")
    else:
        print("\nAucune modification effectuée.")

print("\n" + "="*60)
print("FIN")
print("="*60 + "\n")
