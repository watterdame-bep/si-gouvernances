#!/usr/bin/env python
"""
Script pour corriger l'ordre des étapes dans les projets existants
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import TypeEtape, EtapeProjet

def fix_etapes_order():
    print("🔧 Correction de l'ordre des étapes")
    
    # Nouvel ordre logique
    nouvel_ordre = {
        'PLANIFICATION': 1,
        'CONCEPTION': 2,
        'DEVELOPPEMENT': 3,
        'TESTS': 4,
        'DEPLOIEMENT': 5,
        'MAINTENANCE': 6
    }
    
    # Mettre à jour les TypeEtape
    print("\n📋 Mise à jour des types d'étapes...")
    for nom_type, ordre in nouvel_ordre.items():
        try:
            type_etape = TypeEtape.objects.get(nom=nom_type)
            ancien_ordre = type_etape.ordre_standard
            type_etape.ordre_standard = ordre
            type_etape.save()
            print(f"  ✅ {type_etape.get_nom_display()}: {ancien_ordre} → {ordre}")
        except TypeEtape.DoesNotExist:
            print(f"  ⚠️  Type d'étape '{nom_type}' non trouvé")
    
    # Réorganiser les étapes des projets existants
    print("\n🔄 Réorganisation des étapes des projets existants...")
    
    # Récupérer tous les projets qui ont des étapes
    projets_avec_etapes = EtapeProjet.objects.values('projet').distinct()
    
    for projet_data in projets_avec_etapes:
        projet_id = projet_data['projet']
        etapes = EtapeProjet.objects.filter(projet_id=projet_id).select_related('type_etape')
        
        if etapes.exists():
            projet_nom = etapes.first().projet.nom
            print(f"\n  📁 Projet: {projet_nom}")
            
            # Trier les étapes selon le nouvel ordre
            etapes_triees = sorted(etapes, key=lambda e: nouvel_ordre.get(e.type_etape.nom, 999))
            
            # Première passe: assigner des ordres temporaires pour éviter les conflits
            for index, etape in enumerate(etapes_triees):
                etape.ordre = 1000 + index  # Ordre temporaire
                etape.save()
            
            # Deuxième passe: assigner les vrais ordres
            for index, etape in enumerate(etapes_triees, 1):
                ancien_ordre = etape.ordre - 1000  # Récupérer l'ancien ordre (approximatif)
                etape.ordre = index
                etape.save()
                print(f"    ✅ {etape.type_etape.get_nom_display()}: réorganisé à l'ordre {index}")
    
    print("\n🎉 Correction terminée avec succès !")
    print("\n📊 Nouvel ordre des étapes:")
    for nom_type, ordre in nouvel_ordre.items():
        try:
            type_etape = TypeEtape.objects.get(nom=nom_type)
            print(f"  {ordre}. {type_etape.get_nom_display()}")
        except TypeEtape.DoesNotExist:
            pass

if __name__ == '__main__':
    fix_etapes_order()