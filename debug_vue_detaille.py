#!/usr/bin/env python3
"""
Debug détaillé de la vue gestion_modules_view
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, ModuleProjet, AffectationModule
from django.db.models import Case, When, Value, IntegerField

def debug_vue_detaille():
    """Debug détaillé de la logique de la vue"""
    
    print("🔍 DEBUG DÉTAILLÉ - Logique de la vue")
    print("=" * 60)
    
    try:
        projet = Projet.objects.get(nom="GESTION STOCK")
        print(f"✅ Projet trouvé: {projet.nom}")
        
        # Étape 1: Récupérer les modules
        modules = projet.modules.all().prefetch_related(
            'affectations__utilisateur', 
            'taches',
            'affectations'
        ).select_related('createur')
        
        print(f"📊 Nombre de modules: {modules.count()}")
        
        # Étape 2: Traiter chaque module
        modules_data = []
        for i, module in enumerate(modules):
            print(f"\n🧩 Module {i+1}: {module.nom}")
            
            # Vérifier les affectations
            print(f"   🔍 Vérification des affectations...")
            
            try:
                # Test 1: Compter toutes les affectations
                toutes_affectations = module.affectations.all()
                print(f"   📋 Toutes les affectations: {toutes_affectations.count()}")
                
                for aff in toutes_affectations:
                    print(f"      - {aff.utilisateur.get_full_name()} ({aff.role_module}) - Fin: {aff.date_fin_affectation}")
                
                # Test 2: Affectations actives
                affectations_actives = module.affectations.filter(date_fin_affectation__isnull=True)
                print(f"   ✅ Affectations actives: {affectations_actives.count()}")
                
                for aff in affectations_actives:
                    print(f"      - {aff.utilisateur.get_full_name()} ({aff.role_module})")
                
                # Test 3: Tri des affectations
                affectations_triees = list(affectations_actives.order_by(
                    Case(
                        When(role_module='RESPONSABLE', then=Value(0)),
                        default=Value(1),
                        output_field=IntegerField()
                    ),
                    'date_affectation'
                ))
                
                print(f"   🔄 Affectations triées: {len(affectations_triees)}")
                
                # Créer les données du module
                module_data = {
                    'module': module,
                    'affectations_triees': affectations_triees,
                    'total_affectations': len(affectations_triees),
                    'has_affectations': len(affectations_triees) > 0,
                    'responsable': affectations_triees[0] if affectations_triees else None,
                    'autres_membres_count': len(affectations_triees) - 1 if len(affectations_triees) > 1 else 0
                }
                
                print(f"   📊 Données du module:")
                print(f"      - has_affectations: {module_data['has_affectations']}")
                print(f"      - total_affectations: {module_data['total_affectations']}")
                print(f"      - autres_membres_count: {module_data['autres_membres_count']}")
                
                if module_data['responsable']:
                    print(f"      - responsable: {module_data['responsable'].utilisateur.get_full_name()}")
                else:
                    print(f"      - responsable: None")
                
                modules_data.append(module_data)
                
            except Exception as e:
                print(f"   ❌ Erreur lors du traitement: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📈 RÉSUMÉ:")
        print(f"   • Modules trouvés: {len(modules)}")
        print(f"   • Modules traités: {len(modules_data)}")
        print(f"   • Modules avec affectations: {sum(1 for m in modules_data if m['has_affectations'])}")
        
        if len(modules_data) == 0:
            print(f"   ❌ PROBLÈME: Aucun module dans modules_data")
        else:
            print(f"   ✅ modules_data contient des données")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vue_detaille()