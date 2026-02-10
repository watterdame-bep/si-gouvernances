"""
Script pour changer le mot de passe de l'administrateur
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

def changer_mot_de_passe_admin():
    """Changer le mot de passe de l'administrateur"""
    
    print("=" * 80)
    print("CHANGEMENT DU MOT DE PASSE ADMINISTRATEUR")
    print("=" * 80)
    
    # Trouver l'administrateur
    try:
        admin = Utilisateur.objects.get(is_superuser=True)
        print(f"\n✅ Administrateur trouvé: {admin.get_full_name()}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        
        # Changer le mot de passe
        nouveau_mdp = "admin123"
        admin.set_password(nouveau_mdp)
        admin.save()
        
        print(f"\n✅ Mot de passe changé avec succès!")
        print(f"   Nouveau mot de passe: {nouveau_mdp}")
        print(f"\n📋 Informations de connexion:")
        print(f"   Email: {admin.email}")
        print(f"   Mot de passe: {nouveau_mdp}")
        
    except Utilisateur.DoesNotExist:
        print("\n❌ Aucun administrateur trouvé")
        print("   Recherche d'utilisateurs avec droits admin...")
        
        admins = Utilisateur.objects.filter(is_superuser=True)
        if admins.exists():
            print(f"\n   {admins.count()} administrateur(s) trouvé(s):")
            for admin in admins:
                print(f"   - {admin.get_full_name()} ({admin.email})")
        else:
            print("   Aucun utilisateur avec droits admin trouvé")
    
    except Utilisateur.MultipleObjectsReturned:
        print("\n⚠️  Plusieurs administrateurs trouvés")
        admins = Utilisateur.objects.filter(is_superuser=True)
        print(f"   Total: {admins.count()}")
        
        for i, admin in enumerate(admins, 1):
            print(f"\n   {i}. {admin.get_full_name()}")
            print(f"      Username: {admin.username}")
            print(f"      Email: {admin.email}")
            
            # Changer le mot de passe pour tous
            nouveau_mdp = "admin123"
            admin.set_password(nouveau_mdp)
            admin.save()
            print(f"      ✅ Mot de passe changé: {nouveau_mdp}")

if __name__ == '__main__':
    changer_mot_de_passe_admin()
