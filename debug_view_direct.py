#!/usr/bin/env python
"""
Debug direct de la vue de modification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.http import HttpRequest
from django.contrib.auth import get_user_model
from core.models import Utilisateur
from core.views import modifier_profil_view

def test_view_direct():
    # Créer une requête simulée
    request = HttpRequest()
    request.method = 'POST'
    request.POST = {
        'first_name': 'DirectTest',
        'last_name': 'ViewTest',
        'telephone': '+243 555 444 333'
    }
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    
    # Obtenir l'admin
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    request.user = admin
    
    print(f"Avant: User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")
    
    # Appeler la vue directement
    response = modifier_profil_view(request)
    
    print(f"Status: {response.status_code}")
    print(f"Content: {response.content.decode()}")
    
    # Vérifier l'état après
    admin.refresh_from_db()
    print(f"Après: User={admin.first_name} {admin.last_name}, Membre={admin.membre.prenom} {admin.membre.nom}")
    
    # Restaurer
    admin.first_name = "AdminTest"
    admin.last_name = "ProfileTest"
    admin.save(sync_from_membre=True)
    admin.membre.prenom = "AdminTest"
    admin.membre.nom = "ProfileTest"
    admin.membre.save()

if __name__ == '__main__':
    test_view_direct()