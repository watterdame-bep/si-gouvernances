#!/usr/bin/env python
"""
Script pour créer manuellement une notification de responsable si elle manque
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, Affectation, NotificationProjet
from django.utils import timezone

def creer_notification_manuelle(username, nom_projet):
    """Crée une notification manuelle pour un responsable"""
    
    # Trouver l'utilisateur
    try:
        user = Utilisateur.objects.get(username=username)
        print(f"✓ Utilisateur trouvé: {user.get_full_name()}")
    except Utilisateur.DoesNotExist:
        print(f"✗ Utilisateur '{username}' introuvable")
        return
    
    # Trouver le projet
    try:
        projet = Projet.objects.get(nom=nom_projet)
        print(f"✓ Projet trouvé: {projet.nom}")
    except Projet.DoesNotExist:
        print(f"✗ Projet '{nom_projet}' introuvable")
        return
    
    # Vérifier l'affectation
    affectation = Affectation.objects.filter(
        utilisateur=user,
        projet=projet,
        est_responsable_principal=True,
        date_fin__isnull=True
    ).first()
    
    if not affectation:
        print(f"✗ {user.get_full_name()} n'est pas responsable de {projet.nom}")
        return
    
    print(f"✓ Affectation responsable trouvée")
    
    # Vérifier si la notification existe déjà
    notif_existe = NotificationProjet.objects.filter(
        destinataire=user,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE'
    ).exists()
    
    if notif_existe:
        print(f"✓ Notification déjà existante")
        return
    
    # Créer la notification
    if projet.peut_etre_demarre():
        message_action = "Vous pouvez maintenant démarrer le projet en cliquant sur le bouton 'Commencer le projet'."
    elif projet.date_debut:
        message_action = f"Le projet a déjà été démarré le {projet.date_debut.strftime('%d/%m/%Y')}."
    else:
        message_action = "Définissez une durée pour le projet avant de pouvoir le démarrer."
    
    notification = NotificationProjet.objects.create(
        destinataire=user,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE',
        titre=f"🎯 Vous êtes responsable du projet {projet.nom}",
        message=f"Vous avez été désigné(e) comme responsable principal du projet '{projet.nom}'. "
                f"{message_action} "
                f"Budget: {projet.budget_previsionnel} {projet.devise}. "
                f"Client: {projet.client}.",
        emetteur=None,
        lue=False,
        donnees_contexte={
            'role': 'RESPONSABLE_PRINCIPAL',
            'date_affectation': affectation.date_debut.isoformat() if affectation.date_debut else timezone.now().isoformat(),
            'projet_id': str(projet.id),
            'peut_demarrer': projet.peut_etre_demarre(),
            'projet_demarre': projet.date_debut is not None,
            'creation_manuelle': True
        }
    )
    
    print(f"✓ Notification créée (ID: {notification.id})")
    print(f"  Titre: {notification.titre}")
    print(f"  Date: {notification.date_creation}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python creer_notification_responsable_manuelle.py <username> <nom_projet>")
        print("Exemple: python creer_notification_responsable_manuelle.py eraste.butela 'Systeme de gestion des pharmacie'")
    else:
        username = sys.argv[1]
        nom_projet = ' '.join(sys.argv[2:])
        creer_notification_manuelle(username, nom_projet)
