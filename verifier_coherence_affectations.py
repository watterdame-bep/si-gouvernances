#!/usr/bin/env python
"""
Script pour vérifier la cohérence entre role_projet et est_responsable_principal
dans toutes les affectations actives
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Affectation, RoleProjet

def verifier_coherence():
    print("=" * 80)
    print("VÉRIFICATION: Cohérence des affectations")
    print("=" * 80)
    
    # Récupérer toutes les affectations actives
    affectations_actives = Affectation.objects.filter(date_fin__isnull=True)
    total = affectations_actives.count()
    
    print(f"\n✓ {total} affectation(s) active(s) trouvée(s)")
    
    # Vérifier les incohérences
    incoherences = []
    
    for aff in affectations_actives:
        role_nom = aff.role_projet.nom if aff.role_projet else None
        flag = aff.est_responsable_principal
        
        # Incohérence 1: Rôle RESPONSABLE_PRINCIPAL mais flag à False
        if role_nom == 'RESPONSABLE_PRINCIPAL' and not flag:
            incoherences.append({
                'type': 'ROLE_SANS_FLAG',
                'affectation': aff,
                'description': f"Rôle RESPONSABLE_PRINCIPAL mais flag=False"
            })
        
        # Incohérence 2: Flag True mais rôle différent
        if flag and role_nom != 'RESPONSABLE_PRINCIPAL':
            incoherences.append({
                'type': 'FLAG_SANS_ROLE',
                'affectation': aff,
                'description': f"Flag=True mais rôle={role_nom}"
            })
    
    # Afficher les résultats
    print(f"\n{'=' * 80}")
    if not incoherences:
        print("✓ AUCUNE INCOHÉRENCE DÉTECTÉE")
        print("  Toutes les affectations sont cohérentes.")
    else:
        print(f"⚠ {len(incoherences)} INCOHÉRENCE(S) DÉTECTÉE(S)")
        print("=" * 80)
        
        for i, inc in enumerate(incoherences, 1):
            aff = inc['affectation']
            print(f"\nIncohérence #{i}: {inc['type']}")
            print("-" * 80)
            print(f"  Affectation ID: {aff.id}")
            print(f"  Utilisateur: {aff.utilisateur.get_full_name()} ({aff.utilisateur.username})")
            print(f"  Projet: {aff.projet.nom}")
            print(f"  Rôle: {aff.role_projet.nom if aff.role_projet else 'Aucun'}")
            print(f"  Flag est_responsable_principal: {aff.est_responsable_principal}")
            print(f"  Description: {inc['description']}")
            print(f"  Date début: {aff.date_debut}")
        
        # Proposer une correction
        print(f"\n{'=' * 80}")
        print("CORRECTION RECOMMANDÉE")
        print("=" * 80)
        
        reponse = input("\nVoulez-vous corriger automatiquement ces incohérences? (o/n): ")
        if reponse.lower() == 'o':
            corriger_incoherences(incoherences)
    
    # Statistiques finales
    print(f"\n{'=' * 80}")
    print("STATISTIQUES")
    print("=" * 80)
    
    nb_responsables = affectations_actives.filter(est_responsable_principal=True).count()
    nb_membres = affectations_actives.filter(est_responsable_principal=False).count()
    
    print(f"  - Total affectations actives: {total}")
    print(f"  - Responsables principaux: {nb_responsables}")
    print(f"  - Membres normaux: {nb_membres}")
    print(f"  - Incohérences: {len(incoherences)}")

def corriger_incoherences(incoherences):
    """Corrige automatiquement les incohérences détectées"""
    print("\nCORRECTION EN COURS...")
    print("-" * 80)
    
    for i, inc in enumerate(incoherences, 1):
        aff = inc['affectation']
        
        if inc['type'] == 'ROLE_SANS_FLAG':
            # Rôle RESPONSABLE_PRINCIPAL mais flag à False
            print(f"\n{i}. Correction de l'affectation {aff.id}")
            print(f"   Utilisateur: {aff.utilisateur.get_full_name()}")
            print(f"   Projet: {aff.projet.nom}")
            print(f"   Action: Mise à jour du flag est_responsable_principal = True")
            
            aff.est_responsable_principal = True
            aff.save()
            print(f"   ✓ Corrigé")
        
        elif inc['type'] == 'FLAG_SANS_ROLE':
            # Flag True mais rôle différent
            print(f"\n{i}. Correction de l'affectation {aff.id}")
            print(f"   Utilisateur: {aff.utilisateur.get_full_name()}")
            print(f"   Projet: {aff.projet.nom}")
            print(f"   Action: Mise à jour du rôle vers RESPONSABLE_PRINCIPAL")
            
            try:
                role_responsable = RoleProjet.objects.get(nom='RESPONSABLE_PRINCIPAL')
            except RoleProjet.DoesNotExist:
                role_responsable = RoleProjet.objects.create(
                    nom='RESPONSABLE_PRINCIPAL',
                    description='Responsable Principal du Projet'
                )
            
            aff.role_projet = role_responsable
            aff.save()
            print(f"   ✓ Corrigé")
    
    print(f"\n{'=' * 80}")
    print(f"✓ {len(incoherences)} incohérence(s) corrigée(s)")
    print("=" * 80)

if __name__ == '__main__':
    verifier_coherence()
