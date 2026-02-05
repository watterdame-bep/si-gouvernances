#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

admin = Utilisateur.objects.filter(is_superuser=True).first()
print(f'Admin: {admin.get_full_name()}')
print(f'Has membre: {hasattr(admin, "membre") and admin.membre is not None}')
if hasattr(admin, 'membre') and admin.membre:
    print(f'Membre: {admin.membre.prenom} {admin.membre.nom}')
    print(f'Membre telephone: {admin.membre.telephone}')
else:
    print('No membre profile')