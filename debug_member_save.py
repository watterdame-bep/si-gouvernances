#!/usr/bin/env python
"""
Debug du save du membre
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur

def debug_member_save():
    admin = Utilisateur.objects.filter(is_superuser=True).first()
    membre = admin.membre
    
    print(f"=== AVANT MODIFICATION ===")
    print(f"Membre: {membre.prenom} {membre.nom} {membre.telephone}")
    print(f"Membre ID: {membre.id}")
    print(f"Membre type: {type(membre)}")
    
    try:
        # Test de modification du membre
        print(f"\n=== MODIFICATION DU MEMBRE ===")
        membre.prenom = "TestSave"
        membre.nom = "DebugSave"
        membre.telephone = "+243 777 888 999"
        
        print(f"Avant save: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Sauvegarder
        membre.save()
        
        print(f"Après save: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Recharger depuis la base
        membre.refresh_from_db()
        print(f"Après refresh: {membre.prenom} {membre.nom} {membre.telephone}")
        
        # Vérifier depuis l'utilisateur
        admin.refresh_from_db()
        print(f"Via admin.membre: {admin.membre.prenom} {admin.membre.nom} {admin.membre.telephone}")
        
    except Exception as e:
        print(f"ERREUR lors du save du membre: {e}")
        import traceback
        traceback.print_exc()
    
    # Restaurer
    try:
        membre.prenom = "AdminTest"
        membre.nom = "ProfileTest"
        membre.telephone = "+243 123 456 789"
        membre.save()
        print(f"\n=== RESTAURÉ ===")
        print(f"Membre: {membre.prenom} {membre.nom} {membre.telephone}")
    except Exception as e:
        print(f"ERREUR lors de la restauration: {e}")

if __name__ == '__main__':
    debug_member_save()