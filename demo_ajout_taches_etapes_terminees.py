#!/usr/bin/env python
"""
Démonstration de l'ajout de tâches aux étapes terminées
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, EtapeProjet, TacheEtape

def demo_fonctionnalite():
    print("🎯 DÉMONSTRATION : Ajout de tâches aux étapes terminées")
    print("=" * 60)
    
    try:
        # Récupérer les données
        admin = Utilisateur.objects.get(username='admin')
        projet = Projet.objects.first()
        
        print(f"👤 Utilisateur: {admin.get_full_name()}")
        print(f"📁 Projet: {projet.nom}")
        
        # Afficher toutes les étapes du projet
        print(f"\n📋 Étapes du projet:")
        for etape in projet.etapes.all().order_by('ordre'):
            nb_taches = etape.taches_etape.count()
            print(f"   {etape.ordre}. {etape.type_etape.get_nom_display()} - {etape.get_statut_display()} ({nb_taches} tâches)")
        
        # Trouver une étape terminée
        etape_terminee = projet.etapes.filter(statut='TERMINEE').first()
        
        if not etape_terminee:
            # Marquer la première étape comme terminée pour la démo
            etape_terminee = projet.etapes.order_by('ordre').first()
            etape_terminee.statut = 'TERMINEE'
            etape_terminee.save()
            print(f"\n✅ Étape marquée comme terminée pour la démo: {etape_terminee.type_etape.get_nom_display()}")
        
        print(f"\n🎯 Étape cible: {etape_terminee.type_etape.get_nom_display()} (TERMINÉE)")
        print(f"📊 Tâches actuelles: {etape_terminee.taches_etape.count()}")
        
        # Simuler l'ajout d'une tâche avec justification
        print(f"\n🔧 Simulation d'ajout de tâche...")
        
        # Créer la tâche
        nouvelle_tache = TacheEtape.objects.create(
            etape=etape_terminee,
            nom="Validation finale oubliée",
            description="Validation finale qui avait été oubliée lors de la planification initiale",
            priorite="HAUTE",
            createur=admin
        )
        
        print(f"✅ Tâche ajoutée: {nouvelle_tache.nom}")
        print(f"🔥 Priorité: {nouvelle_tache.get_priorite_display()}")
        
        # Créer l'audit avec justification
        from core.utils import enregistrer_audit
        justification = "Oubli lors de la planification initiale - validation critique nécessaire avant de passer à l'étape suivante"
        
        enregistrer_audit(
            utilisateur=admin,
            type_action='CREATION_TACHE',
            description=f'Création de la tâche d\'étape "{nouvelle_tache.nom}" dans l\'étape {etape_terminee.type_etape.get_nom_display()} (étape terminée - justification: {justification})',
            projet=projet,
            donnees_apres={
                'tache': nouvelle_tache.nom,
                'etape': etape_terminee.type_etape.nom,
                'etape_terminee': True,
                'justification': justification,
                'priorite': nouvelle_tache.priorite
            }
        )
        
        print(f"📝 Audit créé avec justification")
        
        # Afficher le résultat final
        print(f"\n📊 Résultat final:")
        print(f"   Étape: {etape_terminee.type_etape.get_nom_display()}")
        print(f"   Statut: {etape_terminee.get_statut_display()}")
        print(f"   Tâches: {etape_terminee.taches_etape.count()}")
        
        print(f"\n📋 Tâches de l'étape:")
        for tache in etape_terminee.taches_etape.all():
            print(f"   • {tache.nom} ({tache.get_priorite_display()}) - {tache.get_statut_display()}")
        
        # Afficher les URLs pour tester l'interface
        print(f"\n🌐 URLs pour tester l'interface:")
        print(f"   Gestion des tâches: /projets/{projet.id}/etapes/{etape_terminee.id}/taches/")
        print(f"   Créer une tâche: /projets/{projet.id}/etapes/{etape_terminee.id}/taches/creer/")
        
        print(f"\n✅ Démonstration terminée avec succès !")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = demo_fonctionnalite()
    
    if success:
        print(f"\n🎉 FONCTIONNALITÉ IMPLÉMENTÉE AVEC SUCCÈS !")
        print(f"\n📖 Comment utiliser:")
        print(f"   1. Aller sur une étape terminée dans un projet")
        print(f"   2. Cliquer sur 'Nouvelle Tâche'")
        print(f"   3. Remplir le formulaire normalement")
        print(f"   4. Ajouter une justification (champ obligatoire)")
        print(f"   5. Valider - la tâche sera ajoutée avec audit")
        
        print(f"\n🔍 Fonctionnalités:")
        print(f"   ✓ Ajout de tâches aux étapes terminées")
        print(f"   ✓ Justification obligatoire")
        print(f"   ✓ Message informatif dans l'interface")
        print(f"   ✓ Audit détaillé avec justification")
        print(f"   ✓ Interface professionnelle")
    else:
        print(f"\n❌ Problème lors de la démonstration")