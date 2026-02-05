#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

admin = Utilisateur.objects.filter(is_superuser=True).first()
print(f"Admin: {admin.first_name} {admin.last_name}")

if hasattr(admin, 'membre') and admin.membre:
    membre = admin.membre
    print(f"Membre avant: {membre.prenom} {membre.nom}")
    
    # Test direct de modification du membre
    membre.prenom = "TestDirect"
    membre.nom = "ModifDirect"
    membre.save()
    
    print(f"Membre après save: {membre.prenom} {membre.nom}")
    
    # Recharger depuis la base
    membre.refresh_from_db()
    print(f"Membre après refresh: {membre.prenom} {membre.nom}")
    
    # Restaurer
    membre.prenom = "AdminTest"
    membre.nom = "ProfileTest"
    membre.save()
    print(f"Membre restauré: {membre.prenom} {membre.nom}")