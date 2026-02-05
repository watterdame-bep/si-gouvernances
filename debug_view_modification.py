#!/usr/bin/env python
"""
Debug de la vue de modification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.test import Client
from core.models import Utilisateur

def debug_modification():
    client = Client()
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    client.force_login(admin)
    
    print(f"=== AVANT MODIFICATION ===")
    print(f"User: {admin.first_name} {admin.last_name} {admin.telephone}")
    if hasattr(admin, 'membre') and admin.membre:
        print(f"Membre: {admin.membre.prenom} {admin.membre.nom} {admin.membre.telephone}")
    
    # Simuler la modification
    print(f"\n=== MODIFICATION EN COURS ===")
    
    # Données de test
    new_data = {
        'first_name': 'DebugTest',
        'last_name': 'ModifTest',
        'telephone': '+243 555 666 777'
    }
    
    # Appliquer la logique de la vue manuellement
    user = admin
    first_name = new_data['first_name']
    last_name = new_data['last_name']
    telephone = new_data['telephone']
    
    if hasattr(user, 'membre') and user.membre:
        print("Cas 1: Utilisateur avec profil membre")
        membre = user.membre
        
        print(f"Membre avant update: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Mettre à jour le membre
        membre.prenom = first_name
        membre.nom = last_name
        if telephone:
            membre.telephone = telephone
        membre.save()
        
        print(f"Membre après save: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Mettre à jour l'utilisateur
        user.first_name = first_name
        user.last_name = last_name
        user.telephone = telephone
        user.save(sync_from_membre=True)
        
        print(f"User après save: {user.first_name} {user.last_name} {user.telephone}")
        
        # Forcer la synchronisation du membre après la sauvegarde de l'utilisateur
        membre.refresh_from_db()
        print(f"Membre après refresh: {membre.prenom} {membre.nom} {membre.telephone}")
        
        if membre.prenom != first_name or membre.nom != last_name:
            print("Resynchronisation nécessaire")
            membre.prenom = first_name
            membre.nom = last_name
            membre.save()
            print(f"Membre après resync: {membre.prenom} {membre.nom} {membre.telephone}")
    
    print(f"\n=== APRÈS MODIFICATION ===")
    user.refresh_from_db()
    print(f"User final: {user.first_name} {user.last_name} {user.telephone}")
    if hasattr(user, 'membre') and user.membre:
        user.membre.refresh_from_db()
        print(f"Membre final: {user.membre.prenom} {user.membre.nom} {user.membre.telephone}")
    
    # Restaurer
    print(f"\n=== RESTAURATION ===")
    user.first_name = "AdminTest"
    user.last_name = "ProfileTest"
    user.telephone = "+243 999 888 777"
    user.save(sync_from_membre=True)
    
    if hasattr(user, 'membre') and user.membre:
        membre = user.membre
        membre.prenom = "AdminTest"
        membre.nom = "ProfileTest"
        membre.telephone = "+243 123 456 789"
        membre.save()

if __name__ == '__main__':
    debug_modification()