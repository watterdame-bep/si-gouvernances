#!/usr/bin/env python
"""
Script pour corriger l'affectation de DON DIEU et créer la notification manquante
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, Affectation, NotificationProjet
from django.utils import timezone

def corriger_affectation():
    print("=" * 80)
    print("CORRECTION: Affectation DON DIEU - Test UI Transfer")
    print("=" * 80)
    
    # Récupérer l'utilisateur et le projet
    user = Utilisateur.objects.get(username='don.dieu')
    projet = Projet.objects.get(nom='Test UI Transfer')
    
    print(f"\n✓ Utilisateur: {user.get_full_name()}")
    print(f"✓ Projet: {projet.nom}")
    
    # Trouver l'affectation problématique
    affectation = Affectation.objects.get(id='f88eb89d-9fb5-4383-8559-3e534771881a')
    
    print(f"\n1. ÉTAT ACTUEL DE L'AFFECTATION")
    print("-" * 80)
    print(f"  - ID: {affectation.id}")
    print(f"  - Rôle: {affectation.role_projet.nom}")
    print(f"  - est_responsable_principal: {affectation.est_responsable_principal}")
    print(f"  - Date début: {affectation.date_debut}")
    print(f"  - Date fin: {affectation.date_fin or 'Active'}")
    
    # Corriger le flag
    print(f"\n2. CORRECTION DU FLAG")
    print("-" * 80)
    affectation.est_responsable_principal = True
    affectation.save()
    print(f"✓ Flag 'est_responsable_principal' mis à True")
    
    # Vérifier si une notification existe déjà
    notification_existante = NotificationProjet.objects.filter(
        destinataire=user,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE'
    ).first()
    
    if notification_existante:
        print(f"\n3. NOTIFICATION EXISTANTE")
        print("-" * 80)
        print(f"✓ Une notification existe déjà (ID: {notification_existante.id})")
        print(f"  - Lue: {notification_existante.lue}")
        print(f"  - Date création: {notification_existante.date_creation}")
    else:
        print(f"\n3. CRÉATION DE LA NOTIFICATION")
        print("-" * 80)
        
        # Déterminer le message selon l'état du projet
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
                'correction_manuelle': True
            }
        )
        
        print(f"✓ Notification créée avec succès")
        print(f"  - ID: {notification.id}")
        print(f"  - Titre: {notification.titre}")
        print(f"  - Type: {notification.type_notification}")
        print(f"  - Date: {notification.date_creation}")
    
    print(f"\n4. VÉRIFICATION FINALE")
    print("-" * 80)
    
    # Recharger l'affectation
    affectation.refresh_from_db()
    print(f"✓ Affectation corrigée:")
    print(f"  - est_responsable_principal: {affectation.est_responsable_principal}")
    
    # Compter les notifications
    nb_notifications = NotificationProjet.objects.filter(
        destinataire=user,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE'
    ).count()
    print(f"✓ Notifications AFFECTATION_RESPONSABLE: {nb_notifications}")
    
    print("\n" + "=" * 80)
    print("✓ CORRECTION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print(f"\nDON DIEU devrait maintenant voir la notification dans son interface.")

if __name__ == '__main__':
    corriger_affectation()
