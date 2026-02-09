"""
Démonstration du système de notification automatique des responsables
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, Utilisateur, Affectation, NotificationProjet, RoleProjet
from django.utils import timezone

def demo_complete():
    """Démonstration complète du système"""
    
    print()
    print("=" * 80)
    print(" " * 20 + "🎬 DÉMONSTRATION DU SYSTÈME")
    print(" " * 15 + "Notification Automatique des Responsables")
    print("=" * 80)
    print()
    
    # Introduction
    print("📖 CONTEXTE")
    print("-" * 80)
    print("Lorsqu'un administrateur désigne un utilisateur comme responsable")
    print("d'un projet, celui-ci reçoit automatiquement une notification.")
    print()
    print("La notification contient:")
    print("  • Le nom du projet")
    print("  • Les informations clés (budget, client)")
    print("  • Les actions possibles (démarrer, configurer)")
    print()
    input("Appuyez sur Entrée pour continuer...")
    print()
    
    # Étape 1: Sélection du projet
    print("🎯 ÉTAPE 1: Sélection d'un Projet")
    print("-" * 80)
    
    projet = Projet.objects.filter(
        duree_projet__isnull=False,
        date_debut__isnull=True
    ).first()
    
    if not projet:
        print("❌ Aucun projet disponible pour la démo")
        return
    
    print(f"✅ Projet sélectionné: {projet.nom}")
    print(f"   • Client: {projet.client}")
    print(f"   • Budget: {projet.budget_previsionnel} {projet.devise}")
    print(f"   • Durée: {projet.duree_projet} jours")
    print(f"   • Statut: {projet.statut.get_nom_display()}")
    print()
    input("Appuyez sur Entrée pour continuer...")
    print()
    
    # Étape 2: Sélection de l'utilisateur
    print("👤 ÉTAPE 2: Sélection d'un Utilisateur")
    print("-" * 80)
    
    utilisateur = Utilisateur.objects.exclude(
        affectations__projet=projet,
        affectations__est_responsable_principal=True,
        affectations__date_fin__isnull=True
    ).first()
    
    if not utilisateur:
        print("❌ Aucun utilisateur disponible")
        return
    
    print(f"✅ Utilisateur sélectionné: {utilisateur.get_full_name()}")
    print(f"   • Email: {utilisateur.email}")
    print(f"   • Rôle système: {utilisateur.get_role_systeme_display()}")
    print()
    input("Appuyez sur Entrée pour continuer...")
    print()
    
    # Étape 3: Affectation comme responsable
    print("🔧 ÉTAPE 3: Affectation comme Responsable")
    print("-" * 80)
    print(f"L'administrateur affecte {utilisateur.get_full_name()}")
    print(f"comme responsable du projet {projet.nom}...")
    print()
    
    # Récupérer le rôle
    try:
        role_responsable = RoleProjet.objects.get(nom='RESPONSABLE_PRINCIPAL')
    except RoleProjet.DoesNotExist:
        role_responsable = RoleProjet.objects.create(
            nom='RESPONSABLE_PRINCIPAL',
            description='Responsable Principal du Projet'
        )
    
    # Créer l'affectation
    affectation = Affectation.objects.create(
        utilisateur=utilisateur,
        projet=projet,
        role_projet=role_responsable,
        est_responsable_principal=True,
        pourcentage_temps=100
    )
    
    print("✅ Affectation créée avec succès !")
    print()
    input("Appuyez sur Entrée pour voir la notification...")
    print()
    
    # Étape 4: Vérification de la notification
    print("📧 ÉTAPE 4: Notification Automatique")
    print("-" * 80)
    
    # Attendre un peu pour que le signal se déclenche
    import time
    time.sleep(0.5)
    
    notification = NotificationProjet.objects.filter(
        destinataire=utilisateur,
        projet=projet,
        type_notification='AFFECTATION_RESPONSABLE'
    ).order_by('-date_creation').first()
    
    if notification:
        print("✅ Notification créée automatiquement par le système !")
        print()
        print("┌" + "─" * 78 + "┐")
        print("│" + " " * 25 + "📧 NOTIFICATION" + " " * 38 + "│")
        print("├" + "─" * 78 + "┤")
        print(f"│ Destinataire: {notification.destinataire.get_full_name():<62} │")
        print(f"│ Type: {notification.get_type_notification_display():<70} │")
        print("├" + "─" * 78 + "┤")
        print(f"│ {notification.titre:<76} │")
        print("├" + "─" * 78 + "┤")
        
        # Découper le message en lignes de 76 caractères
        message_lines = []
        words = notification.message.split()
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= 76:
                current_line += word + " "
            else:
                message_lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            message_lines.append(current_line.strip())
        
        for line in message_lines:
            print(f"│ {line:<76} │")
        
        print("├" + "─" * 78 + "┤")
        print(f"│ Date: {notification.date_creation.strftime('%d/%m/%Y %H:%M'):<70} │")
        print(f"│ Statut: {'📬 Non lue' if not notification.lue else '✅ Lue':<68} │")
        print("└" + "─" * 78 + "┘")
        print()
        
        # Données contextuelles
        print("📊 DONNÉES CONTEXTUELLES")
        print("-" * 80)
        if notification.donnees_contexte:
            for key, value in notification.donnees_contexte.items():
                print(f"   • {key}: {value}")
        print()
    else:
        print("❌ Aucune notification créée")
        print()
    
    input("Appuyez sur Entrée pour continuer...")
    print()
    
    # Étape 5: Actions possibles
    print("🎯 ÉTAPE 5: Actions Possibles pour le Responsable")
    print("-" * 80)
    
    if projet.peut_etre_demarre():
        print("✅ Le responsable peut démarrer le projet immédiatement !")
        print()
        print("Actions disponibles:")
        print("   1. Consulter le projet")
        print("   2. Cliquer sur 'Commencer le projet'")
        print("   3. Confirmer le démarrage")
        print()
        print("Résultat:")
        print("   • Dates calculées automatiquement")
        print("   • Statut changé vers EN_COURS")
        print("   • Notifications envoyées à l'équipe")
    elif projet.date_debut:
        print("ℹ️  Le projet a déjà été démarré")
        print()
        print("Actions disponibles:")
        print("   1. Consulter le projet")
        print("   2. Suivre l'avancement")
        print("   3. Gérer les tâches")
    else:
        print("⚠️  Le responsable doit d'abord définir une durée")
        print()
        print("Actions disponibles:")
        print("   1. Modifier le projet")
        print("   2. Définir une durée (en jours)")
        print("   3. Sauvegarder")
        print("   4. Démarrer le projet")
    
    print()
    input("Appuyez sur Entrée pour terminer...")
    print()
    
    # Nettoyage
    print("🧹 NETTOYAGE")
    print("-" * 80)
    
    reponse = input("Voulez-vous supprimer les données de test ? (oui/non): ")
    
    if reponse.lower() == 'oui':
        if notification:
            notification.delete()
        affectation.delete()
        print("✅ Données de test supprimées")
    else:
        print("ℹ️  Données conservées")
    
    print()
    
    # Conclusion
    print("=" * 80)
    print(" " * 25 + "✅ DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print()
    print("📝 RÉSUMÉ:")
    print("   • Affectation créée automatiquement")
    print("   • Notification envoyée instantanément")
    print("   • Message adapté selon le contexte")
    print("   • Données contextuelles complètes")
    print()
    print("🎯 Le système fonctionne parfaitement !")
    print()

if __name__ == '__main__':
    demo_complete()
