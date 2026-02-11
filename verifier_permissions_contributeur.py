"""
Script pour vérifier les permissions d'un contributeur sur un module
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, ModuleProjet, AffectationModule

# Demander les informations
print("=" * 60)
print("VÉRIFICATION DES PERMISSIONS CONTRIBUTEUR")
print("=" * 60)

# Lister les utilisateurs
print("\n📋 Utilisateurs disponibles:")
for user in Utilisateur.objects.all():
    print(f"  - ID: {user.id} | {user.get_full_name()} ({user.email})")

user_id = input("\n👤 Entrez l'ID de l'utilisateur: ")
try:
    user = Utilisateur.objects.get(id=user_id)
    print(f"✅ Utilisateur sélectionné: {user.get_full_name()}")
except Utilisateur.DoesNotExist:
    print("❌ Utilisateur non trouvé")
    exit()

# Lister les modules
print("\n📦 Modules disponibles:")
for module in ModuleProjet.objects.all():
    print(f"  - ID: {module.id} | {module.nom} (Projet: {module.projet.nom})")

module_id = input("\n📦 Entrez l'ID du module: ")
try:
    module = ModuleProjet.objects.get(id=module_id)
    print(f"✅ Module sélectionné: {module.nom}")
except ModuleProjet.DoesNotExist:
    print("❌ Module non trouvé")
    exit()

# Vérifier l'affectation
print("\n" + "=" * 60)
print("RÉSULTATS DE LA VÉRIFICATION")
print("=" * 60)

affectation = AffectationModule.objects.filter(
    utilisateur=user,
    module=module,
    date_fin_affectation__isnull=True
).first()

if not affectation:
    print(f"\n❌ AUCUNE AFFECTATION ACTIVE")
    print(f"   {user.get_full_name()} n'est pas affecté au module {module.nom}")
    
    # Vérifier s'il y a des affectations terminées
    affectations_terminees = AffectationModule.objects.filter(
        utilisateur=user,
        module=module,
        date_fin_affectation__isnull=False
    )
    if affectations_terminees.exists():
        print(f"\n⚠️  Il existe {affectations_terminees.count()} affectation(s) terminée(s)")
else:
    print(f"\n✅ AFFECTATION ACTIVE TROUVÉE")
    print(f"\n📊 Détails de l'affectation:")
    print(f"   - Rôle: {affectation.get_role_module_display()}")
    print(f"   - Date affectation: {affectation.date_affectation}")
    print(f"   - Affecté par: {affectation.affecte_par.get_full_name()}")
    
    print(f"\n🔐 Permissions:")
    print(f"   - peut_creer_taches: {'✅ OUI' if affectation.peut_creer_taches else '❌ NON'}")
    print(f"   - peut_voir_toutes_taches: {'✅ OUI' if affectation.peut_voir_toutes_taches else '❌ NON'}")
    
    if not affectation.peut_creer_taches:
        print(f"\n⚠️  PROBLÈME IDENTIFIÉ:")
        print(f"   Le champ 'peut_creer_taches' est à False")
        print(f"   C'est pourquoi le bouton 'Nouvelle Tâche' ne s'affiche pas")
        
        reponse = input("\n🔧 Voulez-vous activer 'peut_creer_taches' ? (oui/non): ")
        if reponse.lower() in ['oui', 'o', 'yes', 'y']:
            affectation.peut_creer_taches = True
            affectation.save()
            print(f"✅ Permission 'peut_creer_taches' activée avec succès!")
            print(f"   Le bouton 'Nouvelle Tâche' devrait maintenant s'afficher")
        else:
            print("❌ Aucune modification effectuée")
    else:
        print(f"\n✅ TOUT EST CORRECT")
        print(f"   Le bouton 'Nouvelle Tâche' devrait s'afficher")
        print(f"   Si ce n'est pas le cas, vérifiez:")
        print(f"   1. Que vous êtes bien connecté avec cet utilisateur")
        print(f"   2. Que vous êtes sur la bonne page du module")
        print(f"   3. Rechargez la page (Ctrl+F5)")

print("\n" + "=" * 60)
