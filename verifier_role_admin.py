"""
Script pour vérifier le rôle de l'utilisateur admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, RoleSysteme

print("=" * 70)
print("VÉRIFICATION DES RÔLES SYSTÈME")
print("=" * 70)

# 1. Lister tous les rôles système
print("\n1. RÔLES SYSTÈME DISPONIBLES")
print("-" * 70)
roles = RoleSysteme.objects.all()
for role in roles:
    print(f"  - {role.nom} : {role.description}")
    nb_users = Utilisateur.objects.filter(role_systeme=role).count()
    print(f"    Utilisateurs avec ce rôle : {nb_users}")

# 2. Vérifier l'utilisateur "admin"
print("\n2. UTILISATEUR 'admin'")
print("-" * 70)
try:
    admin_user = Utilisateur.objects.get(username='admin')
    print(f"Nom complet : {admin_user.get_full_name()}")
    print(f"Email : {admin_user.email}")
    print(f"Rôle système : {admin_user.role_systeme.nom if admin_user.role_systeme else 'AUCUN'}")
    print(f"Est super admin : {admin_user.est_super_admin()}")
    print(f"Est staff : {admin_user.is_staff}")
    print(f"Est superuser : {admin_user.is_superuser}")
except Utilisateur.DoesNotExist:
    print("❌ Utilisateur 'admin' introuvable")

# 3. Lister tous les utilisateurs avec leur rôle
print("\n3. TOUS LES UTILISATEURS")
print("-" * 70)
users = Utilisateur.objects.all()
for user in users:
    role_nom = user.role_systeme.nom if user.role_systeme else "AUCUN"
    print(f"  - {user.username} ({user.get_full_name()}) : {role_nom}")

print("\n" + "=" * 70)
