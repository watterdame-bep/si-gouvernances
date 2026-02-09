#!/usr/bin/env python
"""
Script pour nettoyer complètement la base de données des projets
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import (
    Projet, ActionAudit, EtapeProjet, ModuleProjet,
    TacheEtape, TacheModule, Affectation,
    NotificationProjet, NotificationEtape, NotificationModule, NotificationTache
)

print("=" * 80)
print("NETTOYAGE COMPLET DE LA BASE DE DONNÉES")
print("=" * 80)

# Compter
nb_projets = Projet.objects.count()
nb_audits = ActionAudit.objects.filter(projet__isnull=False).count()
nb_etapes = EtapeProjet.objects.count()
nb_modules = ModuleProjet.objects.count()
nb_taches_etape = TacheEtape.objects.count()
nb_taches_module = TacheModule.objects.count()
nb_affectations = Affectation.objects.count()
nb_notif_projet = NotificationProjet.objects.count()
nb_notif_etape = NotificationEtape.objects.count()
nb_notif_module = NotificationModule.objects.count()
nb_notif_tache = NotificationTache.objects.count()

total = (nb_projets + nb_audits + nb_etapes + nb_modules + nb_taches_etape + 
         nb_taches_module + nb_affectations + nb_notif_projet + nb_notif_etape +
         nb_notif_module + nb_notif_tache)

print(f"\nÉléments à supprimer:")
print(f"  - Projets: {nb_projets}")
print(f"  - Audits: {nb_audits}")
print(f"  - Étapes: {nb_etapes}")
print(f"  - Modules: {nb_modules}")
print(f"  - Tâches d'étape: {nb_taches_etape}")
print(f"  - Tâches de module: {nb_taches_module}")
print(f"  - Affectations: {nb_affectations}")
print(f"  - Notifications: {nb_notif_projet + nb_notif_etape + nb_notif_module + nb_notif_tache}")
print(f"\n  TOTAL: {total} éléments")

if total == 0:
    print("\n✓ Base de données déjà propre")
else:
    print("\nSuppression en cours...")
    print("-" * 80)
    
    # Supprimer dans l'ordre
    if nb_notif_tache > 0:
        NotificationTache.objects.all().delete()
        print(f"✓ {nb_notif_tache} notification(s) tâche supprimée(s)")
    
    if nb_notif_module > 0:
        NotificationModule.objects.all().delete()
        print(f"✓ {nb_notif_module} notification(s) module supprimée(s)")
    
    if nb_notif_etape > 0:
        NotificationEtape.objects.all().delete()
        print(f"✓ {nb_notif_etape} notification(s) étape supprimée(s)")
    
    if nb_notif_projet > 0:
        NotificationProjet.objects.all().delete()
        print(f"✓ {nb_notif_projet} notification(s) projet supprimée(s)")
    
    if nb_taches_module > 0:
        TacheModule.objects.all().delete()
        print(f"✓ {nb_taches_module} tâche(s) de module supprimée(s)")
    
    if nb_taches_etape > 0:
        TacheEtape.objects.all().delete()
        print(f"✓ {nb_taches_etape} tâche(s) d'étape supprimée(s)")
    
    if nb_modules > 0:
        ModuleProjet.objects.all().delete()
        print(f"✓ {nb_modules} module(s) supprimé(s)")
    
    if nb_etapes > 0:
        EtapeProjet.objects.all().delete()
        print(f"✓ {nb_etapes} étape(s) supprimée(s)")
    
    if nb_affectations > 0:
        Affectation.objects.all().delete()
        print(f"✓ {nb_affectations} affectation(s) supprimée(s)")
    
    if nb_audits > 0:
        ActionAudit.objects.filter(projet__isnull=False).delete()
        print(f"✓ {nb_audits} audit(s) supprimé(s)")
    
    if nb_projets > 0:
        Projet.objects.all().delete()
        print(f"✓ {nb_projets} projet(s) supprimé(s)")
    
    print("\n" + "=" * 80)
    print("✅ NETTOYAGE TERMINÉ")
    print("=" * 80)

# Vérification finale
nb_restants = Projet.objects.count()
print(f"\nProjets restants: {nb_restants}")

if nb_restants == 0:
    print("\n✅ Base de données nettoyée avec succès !")
    print("\nVous pouvez maintenant créer vos propres projets pour tester:")
    print("  1. Connectez-vous à l'interface")
    print("  2. Créez un nouveau projet")
    print("  3. Ajoutez un responsable")
    print("  4. Testez les fonctionnalités")
    print()
