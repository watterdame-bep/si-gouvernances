#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

admin = Utilisateur.objects.filter(is_superuser=True).first()
print(f"Initial: User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")

# Test 1: Modifier le membre seulement
print("\n=== Test 1: Modifier membre seulement ===")
admin.membre.prenom = "TestMembre"
admin.membre.nom = "ModifMembre"
admin.membre.save()
print(f"Après membre.save(): User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")

# Test 2: Modifier l'utilisateur avec sync_from_membre=True
print("\n=== Test 2: Modifier user avec sync_from_membre=True ===")
admin.first_name = "TestUser"
admin.last_name = "ModifUser"
admin.save(sync_from_membre=True)
print(f"Après user.save(sync_from_membre=True): User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")

# Test 3: Modifier l'utilisateur sans paramètre
print("\n=== Test 3: Modifier user sans paramètre ===")
admin.first_name = "TestUser2"
admin.last_name = "ModifUser2"
admin.save()
admin.refresh_from_db()
print(f"Après user.save(): User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")

# Restaurer
admin.first_name = "AdminTest"
admin.last_name = "ProfileTest"
admin.save(sync_from_membre=True)
admin.membre.prenom = "AdminTest"
admin.membre.nom = "ProfileTest"
admin.membre.save()