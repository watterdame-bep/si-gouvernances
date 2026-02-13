"""
Script pour vérifier l'activation de Joe Nkondolo
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_activation import AccountActivationToken, AccountActivationLog
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

Utilisateur = get_user_model()

print("\n" + "="*70)
print("VÉRIFICATION ACTIVATION - JOE NKONDOLO")
print("="*70 + "\n")

# 1. Vérifier la configuration email
print("1️⃣ CONFIGURATION EMAIL")
print("-" * 70)
print(f"Backend: {settings.EMAIL_BACKEND}")

if 'console' in settings.EMAIL_BACKEND.lower():
    print("\n⚠️ MODE DÉVELOPPEMENT DÉTECTÉ")
    print("Les emails sont affichés dans la CONSOLE (terminal) et NON envoyés.")
    print("\n💡 Pour voir l'email:")
    print("   - Regardez dans le terminal où 'python manage.py runserver' tourne")
    print("   - Cherchez le texte de l'email après la création du compte")
else:
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"User: {settings.EMAIL_HOST_USER}")

# 2. Chercher l'utilisateur
print("\n\n2️⃣ RECHERCHE DE L'UTILISATEUR")
print("-" * 70)

try:
    user = Utilisateur.objects.get(email='joelnkondolo@gmail.com')
    print(f"✅ Utilisateur trouvé:")
    print(f"   Nom: {user.get_full_name()}")
    print(f"   Email: {user.email}")
    print(f"   Username: {user.username}")
    print(f"   Compte actif: {'✅ OUI' if user.is_active else '❌ NON (en attente d\'activation)'}")
    
    # 3. Vérifier les tokens
    print("\n\n3️⃣ TOKENS D'ACTIVATION")
    print("-" * 70)
    
    tokens = AccountActivationToken.objects.filter(user=user).order_by('-created_at')
    
    if not tokens.exists():
        print("❌ AUCUN TOKEN TROUVÉ")
        print("\n⚠️ Cela signifie que:")
        print("   1. Le compte a été créé avec l'ancien système (avant l'activation sécurisée)")
        print("   2. OU une erreur s'est produite lors de la création du token")
        print("\n💡 SOLUTION:")
        print("   Utilisez le bouton 'Renvoyer lien' dans l'interface admin")
    else:
        print(f"✅ {tokens.count()} token(s) trouvé(s)\n")
        
        for i, token in enumerate(tokens, 1):
            print(f"Token #{i}:")
            print(f"   Créé le: {token.created_at.strftime('%d/%m/%Y à %H:%M:%S')}")
            print(f"   Expire le: {token.expires_at.strftime('%d/%m/%Y à %H:%M:%S')}")
            
            if token.is_used:
                print(f"   Statut: ✅ UTILISÉ (compte activé)")
            elif token.is_expired():
                print(f"   Statut: ⏰ EXPIRÉ")
            elif token.attempts >= 5:
                print(f"   Statut: 🚫 BLOQUÉ (trop de tentatives)")
            else:
                print(f"   Statut: 🟢 ACTIF")
            
            print(f"   Tentatives: {token.attempts}/5")
            
            # Si le token est valide, générer un nouveau lien
            if token.is_valid():
                print(f"\n   ⚠️ Le token original est hashé en base (sécurité)")
                print(f"   💡 Génération d'un NOUVEAU lien...")
                
                # Créer un nouveau token
                new_token_instance, new_token_plain = AccountActivationToken.create_for_user(user)
                
                # Construire le lien
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                activation_url = f"http://127.0.0.1:8000/activate-account/{uidb64}/{new_token_plain}/"
                
                print(f"\n   ✅ NOUVEAU LIEN GÉNÉRÉ:")
                print(f"\n   {activation_url}")
                print(f"\n   ⏰ Valide jusqu'au: {new_token_instance.expires_at.strftime('%d/%m/%Y à %H:%M:%S')}")
                print(f"\n   📧 Envoyez ce lien à Joe Nkondolo par:")
                print(f"      - Email manuel")
                print(f"      - WhatsApp")
                print(f"      - SMS")
                print(f"      - Ou utilisez le bouton 'Renvoyer lien' dans l'interface")
            
            print()
    
    # 4. Vérifier les logs
    print("\n4️⃣ HISTORIQUE DES ACTIONS")
    print("-" * 70)
    
    logs = AccountActivationLog.objects.filter(user=user).order_by('-created_at')
    
    if not logs.exists():
        print("Aucune action enregistrée")
    else:
        print(f"{logs.count()} action(s) enregistrée(s):\n")
        for log in logs[:5]:
            print(f"   {log.created_at.strftime('%d/%m/%Y %H:%M:%S')} - {log.get_action_display()}")
            if log.details:
                print(f"      Détails: {log.details}")
            if log.ip_address:
                print(f"      IP: {log.ip_address}")
            print()

except Utilisateur.DoesNotExist:
    print("❌ UTILISATEUR NON TROUVÉ")
    print("\nUtilisateurs avec 'joel' ou 'nkondolo' dans l'email:")
    
    users = Utilisateur.objects.filter(
        email__icontains='joel'
    ) | Utilisateur.objects.filter(
        email__icontains='nkondolo'
    )
    
    if users.exists():
        for u in users:
            print(f"   - {u.email} ({u.get_full_name()})")
    else:
        print("   Aucun utilisateur trouvé")
        print("\n   Tous les utilisateurs:")
        for u in Utilisateur.objects.all()[:10]:
            print(f"   - {u.email} ({u.get_full_name()})")

print("\n" + "="*70)
print("FIN DE LA VÉRIFICATION")
print("="*70 + "\n")
