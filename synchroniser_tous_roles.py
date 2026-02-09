#!/usr/bin/env python
"""
Script pour synchroniser tous les rôles avec le flag est_responsable_principal
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Affectation

def synchroniser_roles():
    print("=" * 80)
    print("SYNCHRONISATION: Rôles et Flags")
    print("=" * 80)
    
    affectations = Affectation.objects.filter(date_fin__isnull=True)
    total = affectations.count()
    
    print(f"\n✓ {total} affectation(s) active(s) à synchroniser")
    
    print("\nSynchronisation en cours...")
    print("-" * 80)
    
    synchronisees = 0
    
    for aff in affectations:
        role_avant = aff.role_projet.nom if aff.role_projet else "Aucun"
        
        # La méthode save() synchronise automatiquement
        aff.save()
        
        aff.refresh_from_db()
        role_apres = aff.role_projet.nom if aff.role_projet else "Aucun"
        
        if role_avant != role_apres:
            print(f"✓ {aff.utilisateur.get_full_name()} sur {aff.projet.nom}")
            print(f"  Rôle: {role_avant} → {role_apres}")
            synchronisees += 1
    
    print("\n" + "=" * 80)
    print("RÉSULTAT")
    print("=" * 80)
    
    if synchronisees == 0:
        print("✓ Tous les rôles étaient déjà synchronisés")
    else:
        print(f"✓ {synchronisees} affectation(s) synchronisée(s)")
    
    # Vérification finale
    print("\nVérification finale...")
    incoherences = 0
    
    for aff in Affectation.objects.filter(date_fin__isnull=True):
        role_nom = aff.role_projet.nom if aff.role_projet else None
        flag = aff.est_responsable_principal
        
        coherent = (flag and role_nom == 'RESPONSABLE_PRINCIPAL') or (not flag and role_nom == 'MEMBRE')
        if not coherent:
            incoherences += 1
            print(f"⚠ Incohérence: {aff.utilisateur.get_full_name()} sur {aff.projet.nom}")
            print(f"  Flag: {flag}, Rôle: {role_nom}")
    
    if incoherences == 0:
        print("✓ Toutes les affectations sont maintenant cohérentes")
    else:
        print(f"✗ {incoherences} incohérence(s) restante(s)")

if __name__ == '__main__':
    synchroniser_roles()
