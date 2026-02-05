#!/usr/bin/env python3
"""
Script de debug pour analyser le problème des badges de tâches spéciales
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, EtapeProjet, TacheEtape

def debug_badges_taches_speciales():
    """Debug complet du système de badges de tâches spéciales"""
    
    print("=" * 70)
    print("DEBUG COMPLET - BADGES DE TÂCHES SPÉCIALES")
    print("=" * 70)
    
    # Projet GESTION STOCK
    projet_id = "515732ad-5ad2-4176-be84-d42868efce95"
    etape_id = "ac0df394-69ca-4dc9-bb25-aa21a625c901"
    
    try:
        # Récupérer le projet
        projet = Projet.objects.get(id=projet_id)
        print(f"📁 Projet: {projet.nom}")
        print(f"   Statut: {projet.statut}")
        
        # Récupérer l'étape
        etape = EtapeProjet.objects.get(id=etape_id)
        print(f"\n📋 Étape: {etape.type_etape.get_nom_display()}")
        print(f"   Statut: {etape.statut}")
        print(f"   Ordre: {etape.ordre}")
        
        # Vérifier les tâches de cette étape
        taches = etape.taches_etape.all()
        print(f"\n📝 Tâches dans cette étape: {taches.count()}")
        
        for i, tache in enumerate(taches, 1):
            print(f"   Tâche {i}: {tache.nom}")
            print(f"      - Ajoutée après clôture: {tache.ajoutee_apres_cloture}")
            print(f"      - Justification: {tache.justification_ajout_tardif[:50] if tache.justification_ajout_tardif else 'Aucune'}")
            print(f"      - Date création: {tache.date_creation}")
        
        # Tester les méthodes de l'étape
        print(f"\n🔍 Test des méthodes de l'étape:")
        print(f"   a_taches_speciales(): {etape.a_taches_speciales()}")
        print(f"   get_nombre_taches_speciales(): {etape.get_nombre_taches_speciales()}")
        
        # Vérifier toutes les étapes du projet
        print(f"\n📊 Toutes les étapes du projet:")
        timeline = projet.get_timeline_etapes()
        
        print(f"   Étapes passées: {len(timeline['passees'])}")
        for etape_p in timeline['passees']:
            nb_speciales = etape_p.get_nombre_taches_speciales()
            print(f"      - {etape_p.type_etape.get_nom_display()}: {nb_speciales} tâche(s) spéciale(s)")
        
        if timeline['courante']:
            nb_speciales = timeline['courante'].get_nombre_taches_speciales()
            print(f"   Étape courante: {timeline['courante'].type_etape.get_nom_display()}: {nb_speciales} tâche(s) spéciale(s)")
        
        print(f"   Étapes futures: {len(timeline['futures'])}")
        for etape_f in timeline['futures']:
            nb_speciales = etape_f.get_nombre_taches_speciales()
            print(f"      - {etape_f.type_etape.get_nom_display()}: {nb_speciales} tâche(s) spéciale(s)")
        
        # Créer une tâche spéciale manuellement pour test
        print(f"\n🧪 Création d'une tâche spéciale de test...")
        
        # Vérifier si une tâche de test existe déjà
        tache_test = taches.filter(nom__icontains="test").first()
        
        if not tache_test:
            # Créer une nouvelle tâche de test
            tache_test = TacheEtape.objects.create(
                etape=etape,
                nom="Tâche spéciale de test - DEBUG",
                description="Tâche créée pour tester le système de badges",
                priorite="MOYENNE",
                ajoutee_apres_cloture=True,
                justification_ajout_tardif="Test du système de badges de tâches spéciales"
            )
            print(f"   ✅ Tâche de test créée: {tache_test.nom}")
        else:
            # Marquer la tâche existante comme spéciale
            tache_test.ajoutee_apres_cloture = True
            tache_test.justification_ajout_tardif = "Test du système de badges de tâches spéciales"
            tache_test.save()
            print(f"   ✅ Tâche existante marquée comme spéciale: {tache_test.nom}")
        
        # Re-tester les méthodes
        print(f"\n🔍 Re-test des méthodes après création:")
        print(f"   a_taches_speciales(): {etape.a_taches_speciales()}")
        print(f"   get_nombre_taches_speciales(): {etape.get_nombre_taches_speciales()}")
        
        # Vérifier la requête SQL
        print(f"\n🔍 Vérification SQL directe:")
        taches_speciales = etape.taches_etape.filter(ajoutee_apres_cloture=True)
        print(f"   Tâches avec ajoutee_apres_cloture=True: {taches_speciales.count()}")
        
        for tache in taches_speciales:
            print(f"      - {tache.nom} (ID: {tache.id})")
        
        print(f"\n✅ DEBUG TERMINÉ")
        
        if etape.a_taches_speciales():
            print(f"🎉 L'étape a maintenant des tâches spéciales!")
            print(f"   Les badges devraient maintenant s'afficher dans l'interface")
        else:
            print(f"❌ L'étape n'a toujours pas de tâches spéciales")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_badges_taches_speciales()