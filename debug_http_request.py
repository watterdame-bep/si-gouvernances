#!/usr/bin/env python
"""
Debug de la requête HTTP exacte
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.models import Utilisateur
from core.views import modifier_profil_view
import json

def debug_http_request():
    factory = RequestFactory()
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    
    print(f"=== AVANT REQUÊTE ===")
    print(f"User: {admin.first_name} {admin.last_name} {admin.telephone}")
    if hasattr(admin, 'membre') and admin.membre:
        print(f"Membre: {admin.membre.prenom} {admin.membre.nom} {admin.membre.telephone}")
    
    # Créer une requête POST exacte
    request = factory.post('/profil/modifier/', {
        'first_name': 'HTTPTest',
        'last_name': 'RequestTest',
        'telephone': '+243 999 111 222'
    })
    request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'
    request.user = admin
    
    print(f"\n=== DONNÉES DE LA REQUÊTE ===")
    print(f"POST data: {dict(request.POST)}")
    print(f"first_name: '{request.POST.get('first_name', '').strip()}'")
    print(f"last_name: '{request.POST.get('last_name', '').strip()}'")
    print(f"telephone: '{request.POST.get('telephone', '').strip()}'")
    
    # Appeler la vue
    print(f"\n=== APPEL DE LA VUE ===")
    response = modifier_profil_view(request)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            content = json.loads(response.content.decode())
            print(f"Response: {content}")
        except:
            print(f"Raw content: {response.content.decode()}")
    
    # Vérifier l'état après
    print(f"\n=== APRÈS REQUÊTE ===")
    admin.refresh_from_db()
    print(f"User: {admin.first_name} {admin.last_name} {admin.telephone}")
    if hasattr(admin, 'membre') and admin.membre:
        admin.membre.refresh_from_db()
        print(f"Membre: {admin.membre.prenom} {admin.membre.nom} {admin.membre.telephone}")
    
    # Restaurer
    admin.first_name = "AdminTest"
    admin.last_name = "ProfileTest"
    admin.telephone = "+243 999 888 777"
    admin.save(sync_from_membre=True)
    if hasattr(admin, 'membre') and admin.membre:
        admin.membre.prenom = "AdminTest"
        admin.membre.nom = "ProfileTest"
        admin.membre.telephone = "+243 123 456 789"
        admin.membre.save()

if __name__ == '__main__':
    debug_http_request()