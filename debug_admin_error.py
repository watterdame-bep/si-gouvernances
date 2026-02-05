#!/usr/bin/env python
"""
Debug de l'erreur admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.test import Client
from core.models import Utilisateur
import json

def test_admin_functions():
    print("🧪 Test des fonctions admin")
    
    client = Client()
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    print(f"Admin: {admin.get_full_name()} (is_superuser: {admin.is_superuser})")
    print(f"est_super_admin(): {admin.est_super_admin()}")
    
    # Test 1: Modification du profil
    print("\n=== Test 1: Modification du profil ===")
    response = client.post('/profil/modifier/', {
        'first_name': 'TestDebug',
        'last_name': 'ErrorDebug',
        'telephone': '+243 111 222 333'
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode())
            print(f"Response: {data}")
        except:
            print(f"Raw response: {response.content.decode()}")
    else:
        print(f"Error response: {response.content.decode()}")
    
    # Test 2: Changement de mot de passe
    print("\n=== Test 2: Changement de mot de passe ===")
    response = client.post('/profil/changer-mot-de-passe/', {
        'ancien_mot_de_passe': 'admin123',  # Remplace par le vrai mot de passe
        'nouveau_mot_de_passe': 'nouveaumdp123',
        'confirmer_mot_de_passe': 'nouveaumdp123'
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = json.loads(response.content.decode())
            print(f"Response: {data}")
        except:
            print(f"Raw response: {response.content.decode()}")
    else:
        print(f"Error response: {response.content.decode()}")

if __name__ == '__main__':
    test_admin_functions()