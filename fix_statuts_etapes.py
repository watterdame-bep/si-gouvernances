#!/usr/bin/env python
"""
Correction des statuts d'étapes incohérents
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import EtapeProjet

def fix_statuts_etapes():
    print("🔧 CORRECTION : Statuts d'étapes incohérents")
    print("=" * 50)
    
    try:
        # Trouver toutes les étapes avec statut incorrect
        etapes_incorrectes = EtapeProjet.objects.filter(statut='TERMINE')
        
        print(f"📊 Étapes avec statut incorrect 'TERMINE': {etapes_incorrectes.count()}")
        
        if etapes_incorrectes.exists():
            for etape in etapes_incorrectes:
                print(f"  - {etape.projet.nom} > {etape.type_etape.get_nom_display()}: TERMINE → TERMINEE")
                etape.statut = 'TERMINEE'
                etape.save()
            
            print(f"✅ {etapes_incorrectes.count()} étapes corrigées")
        else:
            print("✅ Aucune étape à corriger")
        
        # Vérification finale
        print(f"\n📈 Statistiques finales:")
        stats = {
            'A_VENIR': EtapeProjet.objects.filter(statut='A_VENIR').count(),
            'EN_COURS': EtapeProjet.objects.filter(statut='EN_COURS').count(),
            'TERMINEE': EtapeProjet.objects.filter(statut='TERMINEE').count(),
            'TERMINE': EtapeProjet.objects.filter(statut='TERMINE').count(),
        }
        
        for statut, count in stats.items():
            if count > 0:
                status_icon = "✅" if statut != 'TERMINE' else "❌"
                print(f"  {status_icon} {statut}: {count}")
        
        print(f"\n🎉 Correction terminée!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_statuts_etapes()