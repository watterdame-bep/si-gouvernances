#!/usr/bin/env python3
"""
Vérifier la phase du projet GESTION STOCK
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet

def check_project_phase():
    """Vérifier la phase du projet"""
    
    print("🔍 VÉRIFICATION - Phase du projet GESTION STOCK")
    print("=" * 60)
    
    try:
        projet = Projet.objects.get(nom="GESTION STOCK")
        print(f"✅ Projet trouvé: {projet.nom}")
        
        # Vérifier l'étape courante
        etape_courante = projet.etapes.filter(statut='EN_COURS').first()
        if etape_courante:
            print(f"✅ Étape courante: {etape_courante.type_etape.nom}")
            print(f"   Nom d'affichage: {etape_courante.type_etape.get_nom_display()}")
            print(f"   Statut: {etape_courante.statut}")
        else:
            print("❌ Aucune étape en cours trouvée")
            
            # Lister toutes les étapes
            print("\n📋 Toutes les étapes du projet:")
            for etape in projet.etapes.all():
                print(f"   - {etape.type_etape.nom} ({etape.statut})")
        
        # Vérifier la méthode get_etape_courante()
        try:
            etape_courante_method = projet.get_etape_courante()
            if etape_courante_method:
                print(f"\n✅ get_etape_courante(): {etape_courante_method.type_etape.nom}")
            else:
                print(f"\n❌ get_etape_courante() retourne None")
        except Exception as e:
            print(f"\n❌ Erreur avec get_etape_courante(): {e}")
        
    except Projet.DoesNotExist:
        print("❌ Projet 'GESTION STOCK' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_project_phase()