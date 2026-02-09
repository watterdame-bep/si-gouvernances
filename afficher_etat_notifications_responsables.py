#!/usr/bin/env python
"""
Script pour afficher l'état actuel des notifications de responsables
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Affectation, NotificationProjet, Projet
from django.db.models import Count, Q

def afficher_etat():
    print("=" * 80)
    print("ÉTAT DES NOTIFICATIONS RESPONSABLES")
    print("=" * 80)
    
    # 1. Statistiques globales
    print("\n1. STATISTIQUES GLOBALES")
    print("-" * 80)
    
    total_projets = Projet.objects.count()
    projets_avec_responsable = Projet.objects.filter(
        affectations__est_responsable_principal=True,
        affectations__date_fin__isnull=True
    ).distinct().count()
    projets_sans_responsable = total_projets - projets_avec_responsable
    
    print(f"  Total projets: {total_projets}")
    print(f"  Projets avec responsable: {projets_avec_responsable}")
    print(f"  Projets sans responsable: {projets_sans_responsable}")
    
    # 2. Affectations responsables
    print("\n2. AFFECTATIONS RESPONSABLES ACTIVES")
    print("-" * 80)
    
    affectations_responsables = Affectation.objects.filter(
        est_responsable_principal=True,
        date_fin__isnull=True
    ).select_related('utilisateur', 'projet', 'role_projet')
    
    print(f"  Total: {affectations_responsables.count()}")
    
    # 3. Notifications créées
    print("\n3. NOTIFICATIONS AFFECTATION_RESPONSABLE")
    print("-" * 80)
    
    notifications = NotificationProjet.objects.filter(
        type_notification='AFFECTATION_RESPONSABLE'
    )
    
    total_notifs = notifications.count()
    notifs_lues = notifications.filter(lue=True).count()
    notifs_non_lues = notifications.filter(lue=False).count()
    
    print(f"  Total notifications: {total_notifs}")
    print(f"  Lues: {notifs_lues}")
    print(f"  Non lues: {notifs_non_lues}")
    
    # 4. Cohérence
    print("\n4. VÉRIFICATION DE COHÉRENCE")
    print("-" * 80)
    
    # Vérifier que chaque responsable a au moins une notification
    responsables_sans_notif = []
    
    for aff in affectations_responsables:
        notif_existe = NotificationProjet.objects.filter(
            destinataire=aff.utilisateur,
            projet=aff.projet,
            type_notification='AFFECTATION_RESPONSABLE'
        ).exists()
        
        if not notif_existe:
            responsables_sans_notif.append(aff)
    
    if not responsables_sans_notif:
        print("  ✓ Tous les responsables ont une notification")
    else:
        print(f"  ⚠ {len(responsables_sans_notif)} responsable(s) sans notification:")
        for aff in responsables_sans_notif:
            print(f"    - {aff.utilisateur.get_full_name()} sur {aff.projet.nom}")
    
    # 5. Détail par projet
    print("\n5. DÉTAIL PAR PROJET (avec responsable)")
    print("-" * 80)
    
    projets_avec_resp = Projet.objects.filter(
        affectations__est_responsable_principal=True,
        affectations__date_fin__isnull=True
    ).distinct().order_by('nom')
    
    for projet in projets_avec_resp:
        responsable_aff = projet.affectations.filter(
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        
        if responsable_aff:
            nb_notifs = NotificationProjet.objects.filter(
                destinataire=responsable_aff.utilisateur,
                projet=projet,
                type_notification='AFFECTATION_RESPONSABLE'
            ).count()
            
            notif_non_lue = NotificationProjet.objects.filter(
                destinataire=responsable_aff.utilisateur,
                projet=projet,
                type_notification='AFFECTATION_RESPONSABLE',
                lue=False
            ).exists()
            
            statut = "📬 Non lue" if notif_non_lue else "✓ Lue"
            
            print(f"\n  Projet: {projet.nom}")
            print(f"    Responsable: {responsable_aff.utilisateur.get_full_name()}")
            print(f"    Notifications: {nb_notifs} {statut}")
    
    # 6. Résumé final
    print("\n" + "=" * 80)
    print("RÉSUMÉ")
    print("=" * 80)
    
    coherence = len(responsables_sans_notif) == 0
    
    if coherence:
        print("✅ SYSTÈME COHÉRENT")
        print("   Tous les responsables ont leurs notifications")
    else:
        print("⚠️  INCOHÉRENCES DÉTECTÉES")
        print(f"   {len(responsables_sans_notif)} responsable(s) sans notification")
        print("\n   Exécutez: python verifier_coherence_affectations.py")
    
    print(f"\n   Projets: {total_projets}")
    print(f"   Responsables actifs: {affectations_responsables.count()}")
    print(f"   Notifications: {total_notifs} ({notifs_non_lues} non lues)")

if __name__ == '__main__':
    afficher_etat()
