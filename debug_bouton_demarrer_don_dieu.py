"""
Script de diagnostic pour vérifier pourquoi DON DIEU ne voit pas le bouton démarrer
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, ModuleProjet, TacheModule

print("=" * 80)
print("DIAGNOSTIC: Bouton Démarrer Tâche - DON DIEU")
print("=" * 80)

# Trouver DON DIEU
try:
    don_dieu = Utilisateur.objects.get(username='don.dieu')
    print(f"\n✅ Utilisateur trouvé: {don_dieu.get_full_name()} (ID: {don_dieu.id})")
except Utilisateur.DoesNotExist:
    print("\n❌ Utilisateur 'don.dieu' non trouvé")
    exit()

# Trouver le projet
try:
    projet = Projet.objects.get(nom__icontains='pharmacie')
    print(f"✅ Projet trouvé: {projet.nom} (ID: {projet.id})")
except Projet.DoesNotExist:
    print("\n❌ Projet 'pharmacie' non trouvé")
    exit()

# Trouver le module Dashboard
try:
    module = ModuleProjet.objects.get(projet=projet, nom__icontains='dashboard')
    print(f"✅ Module trouvé: {module.nom} (ID: {module.id})")
except ModuleProjet.DoesNotExist:
    print("\n❌ Module 'dashboard' non trouvé")
    exit()

# Trouver la tâche
print("\n" + "=" * 80)
print("TÂCHES DU MODULE")
print("=" * 80)

taches = TacheModule.objects.filter(module=module).order_by('-date_creation')
print(f"\nNombre total de tâches: {taches.count()}")

for i, tache in enumerate(taches, 1):
    print(f"\n--- Tâche {i} ---")
    print(f"Nom: {tache.nom}")
    print(f"ID: {tache.id}")
    print(f"Statut: {tache.statut}")
    print(f"Responsable: {tache.responsable.get_full_name() if tache.responsable else 'Non assignée'}")
    print(f"Responsable ID: {tache.responsable.id if tache.responsable else 'N/A'}")
    print(f"Créateur: {tache.createur.get_full_name() if tache.createur else 'N/A'}")
    print(f"Date création: {tache.date_creation}")
    
    # Vérifier si DON DIEU est le responsable
    if tache.responsable and tache.responsable.id == don_dieu.id:
        print(f"✅ DON DIEU est le responsable de cette tâche")
        
        # Vérifier les conditions d'affichage du bouton
        print("\n🔍 ANALYSE DES CONDITIONS D'AFFICHAGE DU BOUTON:")
        print(f"   1. Tâche a un responsable: {'✅ OUI' if tache.responsable else '❌ NON'}")
        print(f"   2. Responsable = DON DIEU: {'✅ OUI' if tache.responsable.id == don_dieu.id else '❌ NON'}")
        print(f"   3. Statut de la tâche: {tache.statut}")
        
        if tache.statut == 'A_FAIRE':
            print(f"   4. Bouton à afficher: ✅ DÉMARRER (play-circle)")
        elif tache.statut == 'EN_COURS':
            print(f"   4. Boutons à afficher: ✅ PAUSE + TERMINER")
        elif tache.statut == 'EN_PAUSE':
            print(f"   4. Bouton à afficher: ✅ REPRENDRE (play-circle)")
        elif tache.statut == 'TERMINEE':
            print(f"   4. Bouton à afficher: ✅ CHECK (grisé)")
        else:
            print(f"   4. ⚠️ STATUT INCONNU: {tache.statut}")
    else:
        print(f"❌ DON DIEU n'est PAS le responsable de cette tâche")

# Vérifier l'affectation de DON DIEU au module
print("\n" + "=" * 80)
print("AFFECTATION DE DON DIEU AU MODULE")
print("=" * 80)

affectation = module.affectations.filter(utilisateur=don_dieu, date_fin_affectation__isnull=True).first()
if affectation:
    print(f"✅ DON DIEU est affecté au module")
    print(f"   Rôle: {affectation.get_role_module_display()}")
    print(f"   Peut créer des tâches: {affectation.peut_creer_taches}")
    print(f"   Peut voir toutes les tâches: {affectation.peut_voir_toutes_taches}")
else:
    print(f"❌ DON DIEU n'est PAS affecté au module")

# Vérifier l'accès au projet
print("\n" + "=" * 80)
print("ACCÈS AU PROJET")
print("=" * 80)

if don_dieu.est_super_admin():
    print("✅ DON DIEU est super admin")
elif projet.createur == don_dieu:
    print("✅ DON DIEU est le créateur du projet")
elif don_dieu.a_acces_projet(projet):
    print("✅ DON DIEU a accès au projet")
    affectation_projet = projet.affectations.filter(utilisateur=don_dieu, date_fin__isnull=True).first()
    if affectation_projet:
        print(f"   Rôle sur le projet: {affectation_projet.role_projet.get_nom_display() if affectation_projet.role_projet else 'N/A'}")
        print(f"   Responsable principal: {affectation_projet.est_responsable_principal}")
else:
    print("❌ DON DIEU n'a PAS accès au projet")

# Résumé et recommandations
print("\n" + "=" * 80)
print("RÉSUMÉ ET RECOMMANDATIONS")
print("=" * 80)

tache_test = taches.filter(nom__icontains='tester').first()
if tache_test:
    print(f"\n📋 Tâche de test trouvée: {tache_test.nom}")
    print(f"   Statut actuel: {tache_test.statut}")
    print(f"   Responsable: {tache_test.responsable.get_full_name() if tache_test.responsable else 'Non assignée'}")
    
    if tache_test.responsable and tache_test.responsable.id == don_dieu.id:
        print("\n✅ DON DIEU est bien le responsable")
        
        if tache_test.statut == 'A_FAIRE':
            print("✅ Le statut est A_FAIRE - Le bouton DÉMARRER devrait être visible")
            print("\n🔧 CONDITION TEMPLATE À VÉRIFIER:")
            print("   {% if tache.responsable and tache.responsable.id == user.id %}")
            print("       {% if tache.statut == 'A_FAIRE' %}")
            print("           <button onclick=\"mettreEnCours('{{ tache.id }}')\"...>")
        elif tache_test.statut == 'EN_ATTENTE':
            print("⚠️ PROBLÈME DÉTECTÉ: Le statut est EN_ATTENTE (statut invalide)")
            print("   Le modèle TacheModule n'a pas de statut EN_ATTENTE")
            print("   Statuts valides: A_FAIRE, EN_COURS, EN_PAUSE, TERMINEE")
            print("\n🔧 SOLUTION: Corriger le statut de la tâche")
            print(f"   Exécuter: python corriger_statuts_taches_module.py")
        else:
            print(f"⚠️ Le statut est {tache_test.statut} - Vérifier si c'est normal")
    else:
        print("❌ DON DIEU n'est PAS le responsable de cette tâche")
        if tache_test.responsable:
            print(f"   Responsable actuel: {tache_test.responsable.get_full_name()}")
        else:
            print("   La tâche n'a pas de responsable assigné")
else:
    print("\n❌ Aucune tâche de test trouvée")

print("\n" + "=" * 80)
