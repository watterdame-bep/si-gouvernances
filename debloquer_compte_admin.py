"""
Script pour débloquer le compte admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Trouver l'utilisateur
email = "jovi80@gmail.com"
try:
    user = User.objects.get(email=email)
    
    # Débloquer le compte
    user.tentatives_connexion = 0
    user.compte_bloque_jusqu_a = None
    user.is_active = True
    
    # Réinitialiser le mot de passe
    nouveau_mot_de_passe = "Admin123!"
    user.set_password(nouveau_mot_de_passe)
    
    user.save()
    
    print(f"✅ Compte débloqué avec succès pour {email}")
    print(f"📧 Email: {email}")
    print(f"🔑 Mot de passe: {nouveau_mot_de_passe}")
    print(f"🔓 Tentatives réinitialisées: {user.tentatives_connexion}")
    print(f"✅ Compte actif: {user.is_active}")
    print(f"\n🎉 Vous pouvez maintenant vous connecter!")
    
except User.DoesNotExist:
    print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
