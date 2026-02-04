#!/usr/bin/env python
"""
Script pour corriger le problème des deux responsables dans le module d'authentification
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, ModuleProjet, AffectationModule, Utilisateur
from django.core.exceptions import ValidationError

def fix_double_responsable():
    """Corriger le problème des deux responsables dans le module d'authentification"""
    print("🔧 Correction du problème des deux responsables")
    print("=" * 50)
    
    try:
        # Chercher le projet "GESTION STOCK"
        projet = Projet.objects.filter(nom__icontains="GESTION STOCK").first()
        if not projet:
            print("❌ Projet 'GESTION STOCK' non trouvé")
            return
        
        print(f"✅ Projet trouvé: {projet.nom}")
        
        # Chercher le module "authentification"
        module = projet.modules.filter(nom__icontains="authentification").first()
        if not module:
            print("❌ Module 'authentification' non trouvé")
            return
        
        print(f"✅ Module trouvé: {module.nom}")
        
        # Récupérer tous les responsables du module
        responsables = AffectationModule.objects.filter(
            module=module,
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        )
        
        print(f"📊 Responsables trouvés: {responsables.count()}")
        
        if responsables.count() <= 1:
            print("✅ Pas de problème détecté - Un seul responsable ou moins")
            return
        
        # Afficher les responsables
        print("\n👥 Responsables actuels:")
        for i, resp in enumerate(responsables, 1):
            print(f"  {i}. {resp.utilisateur.get_full_name()} (affecté le {resp.date_affectation.strftime('%d/%m/%Y')})")
        
        # Demander à l'utilisateur de choisir qui garder
        print(f"\n⚠️  ATTENTION: {responsables.count()} responsables détectés!")
        print("Nous devons en garder un seul.")
        print("\nOptions:")
        print("1. Garder le plus ancien (premier affecté)")
        print("2. Garder le plus récent (dernier affecté)")
        print("3. Choisir manuellement")
        print("4. Annuler")
        
        choix = input("\nVotre choix (1-4): ").strip()
        
        if choix == "1":
            # Garder le plus ancien
            a_garder = responsables.order_by('date_affectation').first()
            a_retirer = responsables.exclude(id=a_garder.id)
            
        elif choix == "2":
            # Garder le plus récent
            a_garder = responsables.order_by('-date_affectation').first()
            a_retirer = responsables.exclude(id=a_garder.id)
            
        elif choix == "3":
            # Choix manuel
            print("\nQuel responsable voulez-vous garder ?")
            for i, resp in enumerate(responsables, 1):
                print(f"  {i}. {resp.utilisateur.get_full_name()}")
            
            try:
                index = int(input("Numéro du responsable à garder: ")) - 1
                if 0 <= index < responsables.count():
                    a_garder = responsables[index]
                    a_retirer = responsables.exclude(id=a_garder.id)
                else:
                    print("❌ Numéro invalide")
                    return
            except ValueError:
                print("❌ Veuillez entrer un numéro valide")
                return
                
        elif choix == "4":
            print("❌ Opération annulée")
            return
            
        else:
            print("❌ Choix invalide")
            return
        
        # Confirmation
        print(f"\n📋 Résumé de l'opération:")
        print(f"✅ Responsable à garder: {a_garder.utilisateur.get_full_name()}")
        print(f"❌ Responsables à retirer:")
        for resp in a_retirer:
            print(f"   - {resp.utilisateur.get_full_name()}")
        
        confirmation = input("\nConfirmer cette opération ? (oui/non): ").strip().lower()
        
        if confirmation not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
        
        # Effectuer les modifications
        print("\n🔄 Application des modifications...")
        
        for resp in a_retirer:
            # Changer le rôle en CONTRIBUTEUR au lieu de supprimer
            ancien_role = resp.role_module
            resp.role_module = 'CONTRIBUTEUR'
            resp.peut_creer_taches = False
            resp.peut_voir_toutes_taches = False
            resp.save()
            
            print(f"✅ {resp.utilisateur.get_full_name()}: {ancien_role} → CONTRIBUTEUR")
        
        print(f"\n✅ Correction terminée!")
        print(f"📊 Responsable unique: {a_garder.utilisateur.get_full_name()}")
        print(f"📊 Contributeurs: {a_retirer.count()}")
        
        # Vérification finale
        responsables_finaux = AffectationModule.objects.filter(
            module=module,
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        )
        
        if responsables_finaux.count() == 1:
            print("✅ Vérification: Un seul responsable confirmé")
        else:
            print(f"❌ Erreur: {responsables_finaux.count()} responsables restants")
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_double_responsable()