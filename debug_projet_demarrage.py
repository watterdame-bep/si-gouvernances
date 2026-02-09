"""
Script pour déboguer pourquoi un projet ne peut pas être démarré
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, StatutProjet

# Trouver le projet
projet = Projet.objects.filter(nom__icontains="gestion d'ecole").first()

if projet:
    print(f"Projet: {projet.nom}")
    print(f"Durée définie: {projet.duree_projet}")
    print(f"Date début: {projet.date_debut}")
    print(f"Statut actuel: {projet.statut.nom} ({projet.statut.get_nom_display()})")
    print()
    
    # Vérifier les conditions pour démarrer
    print("Conditions pour démarrer:")
    print(f"  • date_debut is None: {projet.date_debut is None}")
    print(f"  • duree_projet is not None: {projet.duree_projet is not None}")
    print(f"  • duree_projet > 0: {projet.duree_projet > 0 if projet.duree_projet else False}")
    print(f"  • statut.nom == 'CREE': {projet.statut.nom == 'CREE'}")
    print()
    
    print(f"Peut être démarré: {projet.peut_etre_demarre()}")
    print()
    
    # Vérifier si le statut CREE existe
    try:
        statut_cree = StatutProjet.objects.get(nom='CREE')
        print(f"✅ Statut CREE existe: {statut_cree.get_nom_display()}")
    except StatutProjet.DoesNotExist:
        print("❌ Statut CREE n'existe pas dans la base de données")
        print()
        print("Statuts disponibles:")
        for statut in StatutProjet.objects.all():
            print(f"  • {statut.nom} - {statut.get_nom_display()}")
