#!/usr/bin/env python
"""
Debug étape par étape de la vue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

def debug_step_by_step():
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    
    print(f"=== DEBUG ÉTAPE PAR ÉTAPE ===")
    print(f"User: {admin}")
    print(f"User.first_name: {admin.first_name}")
    print(f"User.last_name: {admin.last_name}")
    print(f"User.telephone: {admin.telephone}")
    
    print(f"\nhasattr(admin, 'membre'): {hasattr(admin, 'membre')}")
    if hasattr(admin, 'membre'):
        print(f"admin.membre: {admin.membre}")
        print(f"admin.membre is not None: {admin.membre is not None}")
        if admin.membre:
            print(f"Membre.prenom: {admin.membre.prenom}")
            print(f"Membre.nom: {admin.membre.nom}")
            print(f"Membre.telephone: {admin.membre.telephone}")
    
    # Test de la condition de la vue
    condition = hasattr(admin, 'membre') and admin.membre
    print(f"\nCondition (hasattr(user, 'membre') and user.membre): {condition}")
    
    # Simuler la logique de modification
    first_name = 'TestDebug'
    last_name = 'StepByStep'
    telephone = '+243 111 222 333'
    
    print(f"\n=== SIMULATION DE LA MODIFICATION ===")
    print(f"Nouvelles valeurs: {first_name} {last_name} {telephone}")
    
    if condition:
        print("Entrée dans le cas 1: utilisateur avec profil membre")
        membre = admin.membre
        
        print(f"Membre avant: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Mettre à jour le membre
        membre.prenom = first_name
        membre.nom = last_name
        if telephone:
            membre.telephone = telephone
        membre.save()
        
        print(f"Membre après save: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Mettre à jour l'utilisateur
        admin.first_name = first_name
        admin.last_name = last_name
        admin.telephone = telephone
        admin.save(sync_from_membre=True)
        
        print(f"User après save: {admin.first_name} {admin.last_name} {admin.telephone}")
        
    else:
        print("Entrée dans le cas 2: utilisateur sans profil membre")
        admin.first_name = first_name
        admin.last_name = last_name
        admin.telephone = telephone
        admin.save()
        
        print(f"User après save: {admin.first_name} {admin.last_name} {admin.telephone}")
    
    # Vérifier le résultat final
    admin.refresh_from_db()
    print(f"\n=== RÉSULTAT FINAL ===")
    print(f"User final: {admin.first_name} {admin.last_name} {admin.telephone}")
    if hasattr(admin, 'membre') and admin.membre:
        admin.membre.refresh_from_db()
        print(f"Membre final: {admin.membre.prenom} {admin.membre.nom} {admin.membre.telephone}")
    
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
    debug_step_by_step()