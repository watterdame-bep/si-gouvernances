import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

print("="*70)
print("TOUS LES UTILISATEURS AVEC 'DON' OU 'DIEU' DANS LE NOM")
print("="*70)

utilisateurs = Utilisateur.objects.filter(
    first_name__icontains='don'
) | Utilisateur.objects.filter(
    last_name__icontains='dieu'
) | Utilisateur.objects.filter(
    first_name__icontains='dieu'
) | Utilisateur.objects.filter(
    last_name__icontains='don'
)

for user in utilisateurs.distinct():
    print(f"\n👤 Utilisateur:")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Prénom: {user.first_name}")
    print(f"   Nom: {user.last_name}")
    print(f"   Nom complet: {user.get_full_name()}")
    print(f"   Actif: {'Oui' if user.statut_actif else 'Non'}")
    print(f"   Super admin: {'Oui' if user.est_super_admin() else 'Non'}")

print("\n" + "="*70)
print("UTILISATEUR AVEC EMAIL jovi80@gmail.com")
print("="*70)

try:
    user = Utilisateur.objects.get(email='jovi80@gmail.com')
    print(f"\n✅ Trouvé:")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Prénom: {user.first_name}")
    print(f"   Nom: {user.last_name}")
    print(f"   Nom complet: {user.get_full_name()}")
except:
    print("\n❌ Non trouvé")
