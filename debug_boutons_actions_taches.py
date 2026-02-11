"""
Script de diagnostic pour vérifier pourquoi les boutons d'action ne s'affichent pas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, ModuleProjet, TacheModule

# Rechercher l'utilisateur
username = "Eraste Butela"
print(f"\n{'='*60}")
print(f"DIAGNOSTIC - Boutons d'action tâches module")
print(f"{'='*60}\n")

# Chercher l'utilisateur par nom complet ou username
user = None
try:
    # Essayer par nom complet
    parts = username.split()
    if len(parts) >= 2:
        user = Utilisateur.objects.filter(
            first_name__icontains=parts[0],
            last_name__icontains=parts[1]
        ).first()
    
    if not user:
        # Essayer par username
        user = Utilisateur.objects.filter(username__icontains=username).first()
    
    if not user:
        print(f"❌ Utilisateur '{username}' non trouvé")
        print("\nUtilisateurs disponibles:")
        for u in Utilisateur.objects.all()[:10]:
            print(f"  - {u.username} ({u.get_full_name()})")
        exit()
    
    print(f"✅ Utilisateur trouvé: {user.username} ({user.get_full_name()})")
    print(f"   ID: {user.id}")
    print(f"   Super admin: {user.est_super_admin()}")
    
except Exception as e:
    print(f"❌ Erreur lors de la recherche de l'utilisateur: {e}")
    exit()

# Chercher le projet "Gestion de pharmacie"
print(f"\n{'='*60}")
print("PROJET")
print(f"{'='*60}\n")

projet = Projet.objects.filter(nom__icontains="pharmacie").first()
if not projet:
    print("❌ Projet 'Gestion de pharmacie' non trouvé")
    print("\nProjets disponibles:")
    for p in Projet.objects.all()[:10]:
        print(f"  - {p.nom}")
    exit()

print(f"✅ Projet trouvé: {projet.nom}")
print(f"   ID: {projet.id}")
print(f"   Créateur: {projet.createur.get_full_name() if projet.createur else 'Aucun'}")

# Vérifier l'accès au projet
print(f"\n{'='*60}")
print("ACCÈS AU PROJET")
print(f"{'='*60}\n")

print(f"Créateur du projet: {projet.createur == user}")
print(f"A accès au projet: {user.a_acces_projet(projet)}")

# Affectations au projet
affectations_projet = projet.affectations.filter(
    utilisateur=user,
    date_fin__isnull=True
)
print(f"\nAffectations actives au projet: {affectations_projet.count()}")
for aff in affectations_projet:
    print(f"  - Responsable principal: {aff.est_responsable_principal}")

# Modules du projet
print(f"\n{'='*60}")
print("MODULES DU PROJET")
print(f"{'='*60}\n")

modules = ModuleProjet.objects.filter(projet=projet)
print(f"Nombre de modules: {modules.count()}")

for module in modules:
    print(f"\n📦 Module: {module.nom}")
    print(f"   ID: {module.id}")
    
    # Affectations au module
    affectations_module = module.affectations.filter(
        utilisateur=user,
        date_fin_affectation__isnull=True
    )
    
    if affectations_module.exists():
        for aff in affectations_module:
            print(f"   ✅ Affecté au module")
            print(f"      Role: {aff.role_module} ({aff.get_role_module_display()})")
            print(f"      Peut créer tâches: {aff.peut_creer_taches}")
            print(f"      Peut voir toutes tâches: {aff.peut_voir_toutes_taches}")
    else:
        print(f"   ❌ Non affecté au module")
        continue
    
    # Tâches du module
    taches = TacheModule.objects.filter(module=module)
    print(f"\n   Tâches du module: {taches.count()}")
    
    for tache in taches:
        print(f"\n   📋 Tâche: {tache.nom}")
        print(f"      ID: {tache.id}")
        print(f"      Statut: {tache.statut} ({tache.get_statut_display()})")
        print(f"      Progression: {tache.pourcentage_completion}%")
        print(f"      Créateur: {tache.createur.get_full_name() if tache.createur else 'Aucun'}")
        print(f"      Responsable: {tache.responsable.get_full_name() if tache.responsable else 'Aucun'}")
        
        # Vérifier les permissions
        print(f"\n      PERMISSIONS:")
        print(f"      - Est créateur: {tache.createur == user if tache.createur else False}")
        print(f"      - Est responsable: {tache.responsable == user if tache.responsable else False}")
        
        # Calculer peut_modifier_taches (logique de la vue)
        peut_modifier_taches = False
        if user.est_super_admin():
            peut_modifier_taches = True
        elif projet.createur == user:
            peut_modifier_taches = True
        else:
            aff_projet = projet.affectations.filter(
                utilisateur=user,
                est_responsable_principal=True,
                date_fin__isnull=True
            ).first()
            if aff_projet:
                peut_modifier_taches = True
            else:
                aff_module = module.affectations.filter(
                    utilisateur=user,
                    role_module='RESPONSABLE',
                    date_fin_affectation__isnull=True
                ).first()
                if aff_module:
                    peut_modifier_taches = True
        
        print(f"      - peut_modifier_taches: {peut_modifier_taches}")
        
        # Condition d'affichage des boutons
        condition = (
            peut_modifier_taches or 
            (tache.createur and tache.createur.id == user.id) or 
            (tache.responsable and tache.responsable.id == user.id)
        )
        
        print(f"\n      CONDITION D'AFFICHAGE: {condition}")
        if condition:
            print(f"      ✅ Les boutons d'action DEVRAIENT s'afficher")
            if tache.statut == 'A_FAIRE':
                print(f"         → Bouton 'Démarrer' devrait être visible")
            elif tache.statut == 'EN_COURS':
                print(f"         → Boutons 'Progression', 'Pause', 'Terminer' devraient être visibles")
            elif tache.statut == 'EN_PAUSE':
                print(f"         → Bouton 'Reprendre' devrait être visible")
            elif tache.statut == 'TERMINEE':
                print(f"         → Icône check grise devrait être visible")
        else:
            print(f"      ❌ Les boutons d'action NE DEVRAIENT PAS s'afficher")
            print(f"         Raisons:")
            print(f"         - peut_modifier_taches = {peut_modifier_taches}")
            print(f"         - Est créateur = {tache.createur == user if tache.createur else False}")
            print(f"         - Est responsable = {tache.responsable == user if tache.responsable else False}")

print(f"\n{'='*60}")
print("FIN DU DIAGNOSTIC")
print(f"{'='*60}\n")
