#!/usr/bin/env python
"""
Script pour lister tous les projets et leurs modules
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, ModuleProjet, AffectationModule

def list_projects_and_modules():
    """Lister tous les projets et leurs modules"""
    print("📋 Liste des projets et modules")
    print("=" * 50)
    
    projets = Projet.objects.all()
    
    if not projets:
        print("❌ Aucun projet trouvé")
        return
    
    for projet in projets:
        print(f"\n🏗️  PROJET: {projet.nom}")
        print(f"   Client: {projet.client}")
        print(f"   Statut: {projet.statut}")
        
        modules = projet.modules.all()
        if modules:
            print(f"   📦 Modules ({modules.count()}):")
            for module in modules:
                print(f"      - {module.nom}")
                
                # Vérifier les responsables
                responsables = AffectationModule.objects.filter(
                    module=module,
                    role_module='RESPONSABLE',
                    date_fin_affectation__isnull=True
                )
                
                if responsables.count() > 1:
                    print(f"        ⚠️  PROBLÈME: {responsables.count()} responsables!")
                    for resp in responsables:
                        print(f"           - {resp.utilisateur.get_full_name()}")
                elif responsables.count() == 1:
                    print(f"        ✅ Responsable: {responsables.first().utilisateur.get_full_name()}")
                else:
                    print(f"        ❌ Aucun responsable")
        else:
            print("   📦 Aucun module")

if __name__ == "__main__":
    list_projects_and_modules()