#!/usr/bin/env python
"""
Script pour créer les notifications manquantes pour les responsables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Affectation, NotificationProjet
from django.utils import timezone

def creer_notifications_manquantes():
    print("=" * 80)
    print("CRÉATION DES NOTIFICATIONS MANQUANTES")
    print("=" * 80)
    
    # Récupérer toutes les affectations responsables actives
    affectations_responsables = Affectation.objects.filter(
        est_responsable_principal=True,
        date_fin__isnull=True
    ).select_related('utilisateur', 'projet')
    
    print(f"\n✓ {affectations_responsables.count()} affectation(s) responsable(s) active(s)")
    
    # Vérifier lesquelles n'ont pas de notification
    notifications_creees = 0
    
    for aff in affectations_responsables:
        # Vérifier si une notification existe
        notif_existe = NotificationProjet.objects.filter(
            destinataire=aff.utilisateur,
            projet=aff.projet,
            type_notification='AFFECTATION_RESPONSABLE'
        ).exists()
        
        if not notif_existe:
            print(f"\n📝 Création notification pour:")
            print(f"   Utilisateur: {aff.utilisateur.get_full_name()}")
            print(f"   Projet: {aff.projet.nom}")
            
            # Déterminer le message selon l'état du projet
            if aff.projet.peut_etre_demarre():
                message_action = "Vous pouvez maintenant démarrer le projet en cliquant sur le bouton 'Commencer le projet'."
            elif aff.projet.date_debut:
                message_action = f"Le projet a déjà été démarré le {aff.projet.date_debut.strftime('%d/%m/%Y')}."
            else:
                message_action = "Définissez une durée pour le projet avant de pouvoir le démarrer."
            
            # Créer la notification
            notification = NotificationProjet.objects.create(
                destinataire=aff.utilisateur,
                projet=aff.projet,
                type_notification='AFFECTATION_RESPONSABLE',
                titre=f"🎯 Vous êtes responsable du projet {aff.projet.nom}",
                message=f"Vous avez été désigné(e) comme responsable principal du projet '{aff.projet.nom}'. "
                        f"{message_action} "
                        f"Budget: {aff.projet.budget_previsionnel} {aff.projet.devise}. "
                        f"Client: {aff.projet.client}.",
                emetteur=None,
                lue=False,
                donnees_contexte={
                    'role': 'RESPONSABLE_PRINCIPAL',
                    'date_affectation': aff.date_debut.isoformat() if aff.date_debut else timezone.now().isoformat(),
                    'projet_id': str(aff.projet.id),
                    'peut_demarrer': aff.projet.peut_etre_demarre(),
                    'projet_demarre': aff.projet.date_debut is not None,
                    'creation_retroactive': True
                }
            )
            
            print(f"   ✓ Notification créée (ID: {notification.id})")
            notifications_creees += 1
    
    # Résumé
    print("\n" + "=" * 80)
    if notifications_creees > 0:
        print(f"✓ {notifications_creees} notification(s) créée(s)")
    else:
        print("✓ Aucune notification manquante")
    print("=" * 80)
    
    # Vérification finale
    print("\nVÉRIFICATION FINALE")
    print("-" * 80)
    
    responsables_sans_notif = 0
    for aff in affectations_responsables:
        notif_existe = NotificationProjet.objects.filter(
            destinataire=aff.utilisateur,
            projet=aff.projet,
            type_notification='AFFECTATION_RESPONSABLE'
        ).exists()
        
        if not notif_existe:
            responsables_sans_notif += 1
    
    if responsables_sans_notif == 0:
        print("✅ Tous les responsables ont maintenant une notification")
    else:
        print(f"⚠️  {responsables_sans_notif} responsable(s) sans notification")

if __name__ == '__main__':
    creer_notifications_manquantes()
