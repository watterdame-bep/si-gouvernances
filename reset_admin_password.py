"""
Script pour réinitialiser le mot de passe de l'admin
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
    
    # Définir un nouveau mot de passe
    nouveau_mot_de_passe = "Admin123!"
    user.set_password(nouveau_mot_de_passe)
    user.save()
    
    print(f"✅ Mot de passe réinitialisé avec succès pour {email}")
    print(f"📧 Email: {email}")
    print(f"🔑 Nouveau mot de passe: {nouveau_mot_de_passe}")
    print(f"\n⚠️  Changez ce mot de passe après connexion!")
    
except User.DoesNotExist:
    print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
except Exception as e:
    print(f"❌ Erreur: {e}")
