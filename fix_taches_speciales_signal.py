#!/usr/bin/env python
"""
Solution de contournement : Signal pour marquer les tâches comme spéciales
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import TacheEtape

def setup_taches_speciales_signal():
    """Configure le signal pour marquer automatiquement les tâches comme spéciales"""
    
    @receiver(post_save, sender=TacheEtape)
    def marquer_tache_speciale(sender, instance, created, **kwargs):
        """Signal qui marque une tâche comme spéciale si elle est créée sur une étape terminée"""
        if created and instance.etape.statut == 'TERMINEE':
            # Marquer comme spéciale seulement si ce n'est pas déjà fait
            if not instance.ajoutee_apres_cloture:
                instance.ajoutee_apres_cloture = True
                if not instance.justification_ajout_tardif:
                    instance.justification_ajout_tardif = "Tâche ajoutée automatiquement à une étape terminée"
                instance.save(update_fields=['ajoutee_apres_cloture', 'justification_ajout_tardif'])
                print(f"✅ Tâche '{instance.nom}' marquée comme spéciale automatiquement")
    
    print("🔧 Signal configuré pour marquer automatiquement les tâches spéciales")
    return marquer_tache_speciale

if __name__ == "__main__":
    print("🛠️ CONFIGURATION : Signal pour tâches spéciales")
    print("=" * 50)
    
    # Configurer le signal
    signal_handler = setup_taches_speciales_signal()
    
    print("✅ Signal configuré avec succès")
    print("\nCe signal marquera automatiquement comme spéciales toutes les tâches")
    print("créées sur des étapes terminées.")
    
    # Test du signal
    print("\n🧪 Test du signal...")
    from core.models import Utilisateur, Projet
    
    admin = Utilisateur.objects.get(username='admin')
    projet_stock = Projet.objects.filter(nom__icontains='GESTION STOCK').first()
    etape_terminee = projet_stock.etapes.filter(statut='TERMINEE').first()
    
    print(f"📁 Projet: {projet_stock.nom}")
    print(f"🎯 Étape: {etape_terminee.type_etape.get_nom_display()}")
    print(f"📊 Statut: {etape_terminee.statut}")
    
    # Créer une tâche de test
    tache_test = TacheEtape.objects.create(
        etape=etape_terminee,
        nom="Test Signal Automatique",
        description="Test du signal automatique",
        priorite="MOYENNE",
        createur=admin
    )
    
    # Recharger la tâche pour voir les modifications
    tache_test.refresh_from_db()
    
    print(f"\n🎯 Résultat du test:")
    print(f"   - Tâche créée: {tache_test.nom}")
    print(f"   - Marquée comme spéciale: {tache_test.ajoutee_apres_cloture}")
    print(f"   - Justification: '{tache_test.justification_ajout_tardif}'")
    
    if tache_test.ajoutee_apres_cloture:
        print("\n🎉 Le signal fonctionne parfaitement !")
    else:
        print("\n❌ Le signal ne fonctionne pas")
    
    print("\n📋 Pour activer ce signal de façon permanente,")
    print("ajoutez ce code dans core/apps.py ou core/models.py")