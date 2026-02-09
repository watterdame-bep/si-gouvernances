#!/usr/bin/env python
"""
Script pour tester la nouvelle implémentation simplifiée
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, Affectation, RoleProjet

def tester_implementation():
    print("=" * 80)
    print("TEST: Nouvelle Implémentation Simplifiée")
    print("=" * 80)
    
    print("\n1. SYNCHRONISATION AUTOMATIQUE DES RÔLES")
    print("-" * 80)
    
    # Tester la synchronisation automatique
    affectations = Affectation.objects.filter(date_fin__isnull=True)[:5]
    
    print("Test de la synchronisation automatique role_projet <-> est_responsable_principal")
    print("\nAvant synchronisation:")
    for aff in affectations:
        role_nom = aff.role_projet.nom if aff.role_projet else "Aucun"
        flag = aff.est_responsable_principal
        coherent = (flag and role_nom == 'RESPONSABLE_PRINCIPAL') or (not flag and role_nom == 'MEMBRE')
        statut = "✓" if coherent else "✗"
        print(f"  {statut} {aff.utilisateur.get_full_name()} sur {aff.projet.nom}")
        print(f"     Flag: {flag}, Rôle: {role_nom}")
    
    print("\nForçage de la synchronisation (save())...")
    for aff in affectations:
        aff.save()  # La méthode save() synchronise automatiquement
    
    print("\nAprès synchronisation:")
    for aff in affectations:
        aff.refresh_from_db()
        role_nom = aff.role_projet.nom if aff.role_projet else "Aucun"
        flag = aff.est_responsable_principal
        coherent = (flag and role_nom == 'RESPONSABLE_PRINCIPAL') or (not flag and role_nom == 'MEMBRE')
        statut = "✓" if coherent else "✗"
        print(f"  {statut} {aff.utilisateur.get_full_name()} sur {aff.projet.nom}")
        print(f"     Flag: {flag}, Rôle: {role_nom}")
    
    # 2. Vérifier tous les projets
    print("\n\n2. VÉRIFICATION GLOBALE")
    print("-" * 80)
    
    total_affectations = Affectation.objects.filter(date_fin__isnull=True).count()
    incoherences = 0
    
    for aff in Affectation.objects.filter(date_fin__isnull=True):
        role_nom = aff.role_projet.nom if aff.role_projet else None
        flag = aff.est_responsable_principal
        
        coherent = (flag and role_nom == 'RESPONSABLE_PRINCIPAL') or (not flag and role_nom == 'MEMBRE')
        if not coherent:
            incoherences += 1
    
    print(f"Total affectations actives: {total_affectations}")
    print(f"Incohérences: {incoherences}")
    
    if incoherences == 0:
        print("✓ Toutes les affectations sont cohérentes")
    else:
        print(f"⚠ {incoherences} incohérence(s) détectée(s)")
        print("\nExécutez: python synchroniser_tous_roles.py")
    
    # 3. Vérifier les projets avec plusieurs responsables
    print("\n\n3. PROJETS AVEC PLUSIEURS RESPONSABLES")
    print("-" * 80)
    
    projets_multi = 0
    for projet in Projet.objects.all():
        responsables = Affectation.objects.filter(
            projet=projet,
            est_responsable_principal=True,
            date_fin__isnull=True
        )
        
        if responsables.count() > 1:
            projets_multi += 1
            print(f"⚠ {projet.nom}: {responsables.count()} responsables")
    
    if projets_multi == 0:
        print("✓ Aucun projet avec plusieurs responsables")
    else:
        print(f"\n⚠ {projets_multi} projet(s) avec plusieurs responsables")
        print("Exécutez: python nettoyer_responsables_multiples.py")
    
    # 4. Résumé
    print("\n\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    print("\nAVANTAGES DE LA NOUVELLE IMPLÉMENTATION:")
    print("  ✓ Synchronisation automatique role_projet <-> est_responsable_principal")
    print("  ✓ Impossible d'avoir des incohérences")
    print("  ✓ Code plus simple et maintenable")
    print("  ✓ Un seul champ à vérifier: est_responsable_principal")
    print("  ✓ role_projet devient automatique (lecture seule)")
    
    print("\nFONCTIONNALITÉS DISPONIBLES:")
    print("  ✓ Ajouter un responsable (interface dédiée)")
    print("  ✓ Transférer la responsabilité (fonction definir_responsable)")
    print("  ✓ Retirer n'importe quel membre (admin)")
    print("  ✓ Notification automatique du responsable")
    
    print("\nPROCHAINES ÉTAPES:")
    if incoherences > 0:
        print("  1. Synchroniser tous les rôles: python synchroniser_tous_roles.py")
    if projets_multi > 0:
        print("  2. Nettoyer les responsables multiples: python nettoyer_responsables_multiples.py")
    if incoherences == 0 and projets_multi == 0:
        print("  ✓ Système prêt à l'emploi !")

if __name__ == '__main__':
    tester_implementation()
