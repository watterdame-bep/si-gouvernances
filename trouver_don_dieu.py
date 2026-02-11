"""
Script pour trouver l'utilisateur DON DIEU
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

print("=" * 80)
print("RECHERCHE DE L'UTILISATEUR DON DIEU")
print("=" * 80)

# Chercher par nom
utilisateurs = Utilisateur.objects.filter(
    first_name__icontains='don'
) | Utilisateur.objects.filter(
    last_name__icontains='dieu'
) | Utilisateur.objects.filter(
    username__icontains='don'
)

print(f"\nUtilisateurs trouvés: {utilisateurs.count()}")

for user in utilisateurs:
    print(f"\n--- Utilisateur ---")
    print(f"Username: {user.username}")
    print(f"Nom complet: {user.get_full_name()}")
    print(f"Email: {user.email}")
    print(f"ID: {user.id}")
    print(f"Super admin: {user.is_superuser}")
    print(f"Actif: {user.is_active}")

# Lister tous les utilisateurs si aucun trouvé
if utilisateurs.count() == 0:
    print("\n" + "=" * 80)
    print("TOUS LES UTILISATEURS")
    print("=" * 80)
    
    tous = Utilisateur.objects.all()
    for user in tous:
        print(f"{user.username} - {user.get_full_name()} - {user.email}")
