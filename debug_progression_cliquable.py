"""
Script de diagnostic pour vérifier pourquoi la progression est cliquable pour tous
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, ModuleProjet, TacheModule

print(f"\n{'='*60}")
print(f"DIAGNOSTIC - Progression Cliquable")
print(f"{'='*60}\n")

# Chercher le projet "Gestion de pharmacie"
projet = Projet.objects.filter(nom__icontains="pharmacie").first()
if not projet:
    print("❌ Projet 'Gestion de pharmacie' non trouvé")
    exit()

print(f"✅ Projet trouvé: {projet.nom}")
print(f"   ID: {projet.id}")

# Modules du projet
modules = ModuleProjet.objects.filter(projet=projet)
print(f"\n{'='*60}")
print(f"MODULES ET TÂCHES")
print(f"{'='*60}\n")

for module in modules:
    print(f"\n📦 Module: {module.nom}")
    print(f"   ID: {module.id}")
    
    # Tâches du module
    taches = TacheModule.objects.filter(module=module)
    
    if not taches.exists():
        print("   Aucune tâche")
        continue
    
    for tache in taches:
        print(f"\n   📋 Tâche: {tache.nom}")
        print(f"      ID: {tache.id}")
        print(f"      Statut: {tache.statut}")
        print(f"      Progression: {tache.pourcentage_completion}%")
        print(f"      Créateur: {tache.createur.get_full_name() if tache.createur else 'Aucun'}")
        print(f"      Créateur ID: {tache.createur.id if tache.createur else 'N/A'}")
        print(f"      Responsable: {tache.responsable.get_full_name() if tache.responsable else 'Aucun'}")
        print(f"      Responsable ID: {tache.responsable.id if tache.responsable else 'N/A'}")
        
        # Tester avec différents utilisateurs
        print(f"\n      TEST DE LA CONDITION:")
        
        utilisateurs = Utilisateur.objects.all()[:5]
        for user in utilisateurs:
            # Condition du template
            est_responsable = tache.responsable and tache.responsable.id == user.id
            
            print(f"      - {user.get_full_name()} (ID: {user.id})")
            print(f"        tache.responsable: {tache.responsable}")
            print(f"        tache.responsable.id: {tache.responsable.id if tache.responsable else 'N/A'}")
            print(f"        user.id: {user.id}")
            print(f"        tache.responsable.id == user.id: {tache.responsable.id == user.id if tache.responsable else False}")
            print(f"        Condition complète: {est_responsable}")
            print(f"        → Progression cliquable: {'✅ OUI' if est_responsable else '❌ NON'}")
            print()

print(f"\n{'='*60}")
print("FIN DU DIAGNOSTIC")
print(f"{'='*60}\n")
