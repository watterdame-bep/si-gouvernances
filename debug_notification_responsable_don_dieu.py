#!/usr/bin/env python
"""
Script de diagnostic pour vérifier pourquoi DON DIEU n'a pas reçu
la notification de responsable du projet "Test UI Transfer"
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, Affectation, NotificationProjet
from django.utils import timezone

def diagnostic_complet():
    print("=" * 80)
    print("DIAGNOSTIC: Notification Responsable - DON DIEU")
    print("=" * 80)
    
    # 1. Vérifier l'utilisateur
    print("\n1. RECHERCHE DE L'UTILISATEUR DON DIEU")
    print("-" * 80)
    try:
        user = Utilisateur.objects.get(username='don.dieu')
        print(f"✓ Utilisateur trouvé:")
        print(f"  - ID: {user.id}")
        print(f"  - Username: {user.username}")
        print(f"  - Nom complet: {user.get_full_name()}")
        print(f"  - Email: {user.email}")
        print(f"  - Actif: {user.statut_actif}")
    except Utilisateur.DoesNotExist:
        print("✗ ERREUR: Utilisateur 'don.dieu' introuvable")
        return
    
    # 2. Vérifier le projet
    print("\n2. RECHERCHE DU PROJET 'Test UI Transfer'")
    print("-" * 80)
    try:
        projet = Projet.objects.get(nom='Test UI Transfer')
        print(f"✓ Projet trouvé:")
        print(f"  - ID: {projet.id}")
        print(f"  - Nom: {projet.nom}")
        print(f"  - Client: {projet.client}")
        print(f"  - Date début: {projet.date_debut}")
        print(f"  - Durée prévue: {projet.duree_projet} jours" if projet.duree_projet else "  - Durée: Non définie")
        print(f"  - Peut être démarré: {projet.peut_etre_demarre()}")
    except Projet.DoesNotExist:
        print("✗ ERREUR: Projet 'Test UI Transfer' introuvable")
        print("\nProjets disponibles contenant 'Test':")
        projets_test = Projet.objects.filter(nom__icontains='test')
        for p in projets_test:
            print(f"  - {p.nom}")
        return
    
    # 3. Vérifier l'affectation
    print("\n3. VÉRIFICATION DE L'AFFECTATION")
    print("-" * 80)
    affectations = Affectation.objects.filter(
        utilisateur=user,
        projet=projet
    ).order_by('-date_debut')
    
    if not affectations.exists():
        print("✗ AUCUNE affectation trouvée pour DON DIEU sur ce projet")
        return
    
    print(f"✓ {affectations.count()} affectation(s) trouvée(s):")
    for i, aff in enumerate(affectations, 1):
        print(f"\n  Affectation #{i}:")
        print(f"    - ID: {aff.id}")
        print(f"    - Rôle: {aff.role_projet.nom if aff.role_projet else 'Aucun'}")
        print(f"    - Est responsable principal: {aff.est_responsable_principal}")
        print(f"    - Date début: {aff.date_debut}")
        print(f"    - Date fin: {aff.date_fin or 'Active'}")
        print(f"    - Date création: {aff.date_creation if hasattr(aff, 'date_creation') else 'N/A'}")
    
    # Trouver l'affectation active de responsable
    affectation_responsable = affectations.filter(
        est_responsable_principal=True,
        date_fin__isnull=True
    ).first()
    
    if not affectation_responsable:
        print("\n  ⚠ ATTENTION: Aucune affectation active comme responsable principal")
        return
    
    print(f"\n  ✓ Affectation responsable active trouvée (ID: {affectation_responsable.id})")
    
    # 4. Vérifier les notifications
    print("\n4. VÉRIFICATION DES NOTIFICATIONS")
    print("-" * 80)
    notifications = NotificationProjet.objects.filter(
        destinataire=user,
        projet=projet
    ).order_by('-date_creation')
    
    if not notifications.exists():
        print("✗ AUCUNE notification trouvée pour DON DIEU sur ce projet")
        print("\n  CAUSE PROBABLE:")
        print("  L'affectation a été créée AVANT l'implémentation du signal.")
        print("  Le signal ne se déclenche que lors de la CRÉATION d'une nouvelle affectation.")
        
        # Proposer une solution
        print("\n5. SOLUTION PROPOSÉE")
        print("-" * 80)
        print("Option 1: Créer manuellement la notification")
        print("Option 2: Retirer et réaffecter DON DIEU comme responsable")
        
        reponse = input("\nVoulez-vous créer manuellement la notification maintenant? (o/n): ")
        if reponse.lower() == 'o':
            creer_notification_manuelle(user, projet, affectation_responsable)
        return
    
    print(f"✓ {notifications.count()} notification(s) trouvée(s):")
    for i, notif in enumerate(notifications, 1):
        print(f"\n  Notification #{i}:")
        print(f"    - ID: {notif.id}")
        print(f"    - Type: {notif.type_notification}")
        print(f"    - Titre: {notif.titre}")
        print(f"    - Message: {notif.message[:100]}...")
        print(f"    - Date création: {notif.date_creation}")
        print(f"    - Lue: {notif.lue}")
        print(f"    - Date lecture: {notif.date_lecture or 'Non lue'}")
    
    # Vérifier spécifiquement la notification d'affectation responsable
    notif_responsable = notifications.filter(
        type_notification='AFFECTATION_RESPONSABLE'
    ).first()
    
    if notif_responsable:
        print("\n  ✓ Notification AFFECTATION_RESPONSABLE trouvée")
        print(f"    - Statut: {'Lue' if notif_responsable.lue else 'NON LUE'}")
    else:
        print("\n  ✗ Aucune notification de type AFFECTATION_RESPONSABLE")

def creer_notification_manuelle(user, projet, affectation):
    """Crée manuellement la notification pour le responsable"""
    print("\nCréation de la notification...")
    
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
            'creation_manuelle': True
        }
    )
    
    print(f"✓ Notification créée avec succès (ID: {notification.id})")
    print(f"  - Titre: {notification.titre}")
    print(f"  - Type: {notification.type_notification}")
    print(f"  - Date: {notification.date_creation}")

if __name__ == '__main__':
    diagnostic_complet()
