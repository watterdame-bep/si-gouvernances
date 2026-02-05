#!/usr/bin/env python
"""
Debug des tâches spéciales - Vérification complète
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, EtapeProjet, TacheEtape

def debug_taches_speciales():
    print("🔍 DEBUG : Tâches spéciales")
    print("=" * 50)
    
    try:
        # Récupérer les données
        admin = Utilisateur.objects.get(username='admin')
        projet = Projet.objects.first()
        
        print(f"👤 Utilisateur: {admin.get_full_name()}")
        print(f"📁 Projet: {projet.nom}")
        
        # Vérifier les étapes
        print(f"\n📊 Étapes du projet:")
        for etape in projet.etapes.all():
            taches_count = etape.taches_etape.count()
            taches_speciales = etape.taches_etape.filter(ajoutee_apres_cloture=True).count()
            print(f"  - {etape.type_etape.get_nom_display()}: {etape.statut} ({taches_count} tâches, {taches_speciales} spéciales)")
            
            # Vérifier la méthode a_taches_speciales
            if hasattr(etape, 'a_taches_speciales'):
                print(f"    → a_taches_speciales(): {etape.a_taches_speciales()}")
            else:
                print(f"    → ERREUR: Méthode a_taches_speciales() manquante!")
        
        # Trouver ou créer une étape terminée
        etape_terminee = projet.etapes.filter(statut='TERMINEE').first()
        if not etape_terminee:
            etape_terminee = projet.etapes.first()
            etape_terminee.statut = 'TERMINEE'
            etape_terminee.save()
            print(f"\n✅ Étape marquée comme terminée: {etape_terminee.type_etape.get_nom_display()}")
        else:
            print(f"\n🎯 Étape terminée trouvée: {etape_terminee.type_etape.get_nom_display()}")
        
        # Créer une tâche spéciale
        print(f"\n⭐ Création d'une tâche spéciale...")
        tache_speciale = TacheEtape.objects.create(
            etape=etape_terminee,
            nom="Test Tâche Spéciale",
            description="Tâche de test pour vérifier les fonctionnalités spéciales",
            priorite="HAUTE",
            createur=admin,
            ajoutee_apres_cloture=True,
            justification_ajout_tardif="Test de fonctionnalité - vérification du système"
        )
        
        print(f"✅ Tâche spéciale créée:")
        print(f"  - ID: {tache_speciale.id}")
        print(f"  - Nom: {tache_speciale.nom}")
        print(f"  - Ajoutée après clôture: {tache_speciale.ajoutee_apres_cloture}")
        print(f"  - Justification: {tache_speciale.justification_ajout_tardif}")
        
        # Vérifier l'ordre des tâches
        print(f"\n📋 Ordre des tâches dans l'étape:")
        taches = etape_terminee.taches_etape.all()
        for i, tache in enumerate(taches, 1):
            special = "⭐ SPÉCIALE" if tache.ajoutee_apres_cloture else "📋 Normale"
            print(f"  {i}. {tache.nom} - {special} - {tache.date_creation.strftime('%d/%m/%Y %H:%M')}")
        
        # Vérifier les méthodes de l'étape
        print(f"\n🔍 Méthodes de l'étape:")
        print(f"  - a_taches_speciales(): {etape_terminee.a_taches_speciales()}")
        print(f"  - get_nombre_taches_speciales(): {etape_terminee.get_nombre_taches_speciales()}")
        
        # Test de l'URL de création
        print(f"\n🌐 URLs pour tester:")
        print(f"  - Détail projet: http://127.0.0.1:8000/projets/{projet.id}/")
        print(f"  - Détail étape: http://127.0.0.1:8000/projets/{projet.id}/etapes/{etape_terminee.id}/")
        print(f"  - Créer tâche: http://127.0.0.1:8000/projets/{projet.id}/etapes/{etape_terminee.id}/taches/creer/")
        
        # Vérifier le template
        print(f"\n📄 Vérification du template:")
        from django.template.loader import get_template
        try:
            template = get_template('core/creer_tache_etape.html')
            print(f"  ✅ Template trouvé: core/creer_tache_etape.html")
        except Exception as e:
            print(f"  ❌ Erreur template: {e}")
        
        print(f"\n🎉 Debug terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_taches_speciales()