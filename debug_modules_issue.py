#!/usr/bin/env python3
"""
Debug du problème d'affichage des modules
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet

def debug_modules_issue():
    """Debug du problème d'affichage des modules"""
    
    print("🔍 DEBUG - Problème d'affichage des modules")
    print("=" * 60)
    
    try:
        projet = Projet.objects.get(nom="GESTION STOCK")
        print(f"✅ Projet trouvé: {projet.nom}")
        
        # Vérifier les modules
        modules = projet.modules.all()
        print(f"📊 Nombre de modules: {modules.count()}")
        
        for module in modules:
            print(f"   🧩 {module.nom} - {module.description}")
        
        # Vérifier l'étape courante avec les deux méthodes
        print(f"\n🔍 Vérification des étapes:")
        
        # Méthode 1: projet.etapes.filter(statut='EN_COURS')
        etape_courante_1 = projet.etapes.filter(statut='EN_COURS').first()
        if etape_courante_1:
            print(f"✅ Méthode 1 (etapes.filter): {etape_courante_1.type_etape.nom}")
        else:
            print(f"❌ Méthode 1 (etapes.filter): Aucune étape EN_COURS")
            
            # Lister toutes les étapes
            print(f"   📋 Toutes les étapes:")
            for etape in projet.etapes.all():
                print(f"      - {etape.type_etape.nom} ({etape.statut})")
        
        # Méthode 2: projet.get_etape_courante()
        try:
            etape_courante_2 = projet.get_etape_courante()
            if etape_courante_2:
                print(f"✅ Méthode 2 (get_etape_courante): {etape_courante_2.type_etape.nom}")
            else:
                print(f"❌ Méthode 2 (get_etape_courante): None")
        except Exception as e:
            print(f"❌ Méthode 2 (get_etape_courante): Erreur - {e}")
        
        # Test de la condition de la vue
        print(f"\n🧪 Test de la condition de la vue:")
        etape_courante = projet.etapes.filter(statut='EN_COURS').first()
        
        if not etape_courante:
            print(f"❌ Condition 1 ÉCHOUE: Aucune étape courante")
        elif etape_courante.type_etape.nom != 'DEVELOPPEMENT':
            print(f"❌ Condition 2 ÉCHOUE: Étape = {etape_courante.type_etape.nom} (pas DEVELOPPEMENT)")
        else:
            print(f"✅ Toutes les conditions PASSENT: Étape = {etape_courante.type_etape.nom}")
        
    except Projet.DoesNotExist:
        print("❌ Projet 'GESTION STOCK' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_modules_issue()