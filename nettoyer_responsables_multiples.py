#!/usr/bin/env python
"""
Script pour nettoyer les projets avec plusieurs responsables
et implémenter la gestion de transfert de responsabilité
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, Affectation, RoleProjet
from django.utils import timezone

def nettoyer_responsables_multiples():
    print("=" * 80)
    print("NETTOYAGE: Projets avec Plusieurs Responsables")
    print("=" * 80)
    
    # 1. Identifier les projets avec plusieurs responsables
    projets_multi_resp = []
    
    for projet in Projet.objects.all():
        responsables = Affectation.objects.filter(
            projet=projet,
            est_responsable_principal=True,
            date_fin__isnull=True
        ).order_by('date_debut')
        
        if responsables.count() > 1:
            projets_multi_resp.append({
                'projet': projet,
                'responsables': list(responsables)
            })
    
    if not projets_multi_resp:
        print("\n✓ Aucun projet avec plusieurs responsables")
        return
    
    print(f"\n⚠ {len(projets_multi_resp)} projet(s) avec plusieurs responsables")
    print("\nSTRATÉGIE DE NETTOYAGE:")
    print("  - Garder le PREMIER responsable désigné (date_debut la plus ancienne)")
    print("  - Convertir les autres en membres normaux")
    print("  - Vous pourrez ensuite choisir le bon responsable manuellement")
    
    # 2. Nettoyer chaque projet
    print("\n" + "-" * 80)
    
    for item in projets_multi_resp:
        projet = item['projet']
        responsables = item['responsables']
        
        print(f"\nProjet: {projet.nom}")
        print(f"  Responsables actuels: {len(responsables)}")
        
        # Garder le premier (le plus ancien)
        premier = responsables[0]
        autres = responsables[1:]
        
        print(f"\n  ✓ GARDER comme responsable:")
        print(f"    - {premier.utilisateur.get_full_name()}")
        print(f"      Date désignation: {premier.date_debut}")
        
        print(f"\n  → CONVERTIR en membres:")
        for aff in autres:
            print(f"    - {aff.utilisateur.get_full_name()}")
            print(f"      Date désignation: {aff.date_debut}")
            
            # Convertir en membre
            aff.est_responsable_principal = False
            
            # Mettre à jour le rôle si nécessaire
            try:
                role_membre = RoleProjet.objects.get(nom='MEMBRE')
                aff.role_projet = role_membre
            except RoleProjet.DoesNotExist:
                pass
            
            aff.save()
            print(f"      ✓ Converti en membre")
    
    # 3. Vérification finale
    print("\n" + "=" * 80)
    print("VÉRIFICATION FINALE")
    print("=" * 80)
    
    projets_encore_multi = 0
    for projet in Projet.objects.all():
        responsables = Affectation.objects.filter(
            projet=projet,
            est_responsable_principal=True,
            date_fin__isnull=True
        )
        
        if responsables.count() > 1:
            projets_encore_multi += 1
            print(f"⚠ {projet.nom}: {responsables.count()} responsables")
    
    if projets_encore_multi == 0:
        print("✓ Tous les projets ont maintenant UN SEUL responsable maximum")
    
    # 4. Statistiques finales
    print("\n" + "=" * 80)
    print("STATISTIQUES FINALES")
    print("=" * 80)
    
    total_projets = Projet.objects.count()
    projets_avec_resp = Projet.objects.filter(
        affectations__est_responsable_principal=True,
        affectations__date_fin__isnull=True
    ).distinct().count()
    
    print(f"  Total projets: {total_projets}")
    print(f"  Projets avec responsable: {projets_avec_resp}")
    print(f"  Projets sans responsable: {total_projets - projets_avec_resp}")
    print(f"  Projets nettoyés: {len(projets_multi_resp)}")
    
    print("\n" + "=" * 80)
    print("PROCHAINES ÉTAPES")
    print("=" * 80)
    print("""
  1. Vérifiez les responsables gardés pour chaque projet
  2. Si nécessaire, transférez la responsabilité:
     - Retirez le responsable actuel (devient membre)
     - Désignez le nouveau responsable
  3. L'administrateur peut maintenant:
     - Supprimer n'importe quel membre (responsable ou pas)
     - Transférer la responsabilité facilement
    """)

if __name__ == '__main__':
    nettoyer_responsables_multiples()
