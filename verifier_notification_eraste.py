#!/usr/bin/env python
"""
Script pour vérifier pourquoi Eraste Butela n'a pas reçu de notification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, Affectation, NotificationProjet

print("=" * 80)
print("DIAGNOSTIC: Notification Eraste Butela")
print("=" * 80)

# Trouver Eraste Butela
try:
    eraste = Utilisateur.objects.get(username='eraste.butela')
    print(f"\n✓ Utilisateur trouvé: {eraste.get_full_name()}")
except Utilisateur.DoesNotExist:
    print("\n✗ Utilisateur 'eraste.butela' introuvable")
    exit()

# Trouver le projet
try:
    projet = Projet.objects.get(nom='Systeme de gestion des pharmacie')
    print(f"✓ Projet trouvé: {projet.nom}")
except Projet.DoesNotExist:
    print("\n✗ Projet 'Systeme de gestion des pharmacie' introuvable")
    exit()

# Vérifier l'affectation
print("\n" + "-" * 80)
print("AFFECTATIONS")
print("-" * 80)

affectations = Affectation.objects.filter(
    utilisateur=eraste,
    projet=projet
).order_by('-date_debut')

if not affectations.exists():
    print("✗ Aucune affectation trouvée")
else:
    for aff in affectations:
        print(f"\nAffectation ID: {aff.id}")
        print(f"  - Rôle: {aff.role_projet.nom if aff.role_projet else 'Aucun'}")
        print(f"  - est_responsable_principal: {aff.est_responsable_principal}")
        print(f"  - Date début: {aff.date_debut}")
        print(f"  - Date fin: {aff.date_fin or 'Active'}")

# Vérifier les notifications
print("\n" + "-" * 80)
print("NOTIFICATIONS")
print("-" * 80)

notifications = NotificationProjet.objects.filter(
    destinataire=eraste,
    projet=projet,
    type_notification='AFFECTATION_RESPONSABLE'
).order_by('-date_creation')

if not notifications.exists():
    print("✗ Aucune notification AFFECTATION_RESPONSABLE trouvée")
    print("\nCAUSE PROBABLE:")
    print("  Le signal ne s'est pas déclenché lors de la désignation")
else:
    print(f"✓ {notifications.count()} notification(s) trouvée(s):")
    for notif in notifications:
        print(f"\n  - ID: {notif.id}")
        print(f"  - Titre: {notif.titre}")
        print(f"  - Date: {notif.date_creation}")
        print(f"  - Lue: {notif.lue}")

# Vérifier le signal
print("\n" + "-" * 80)
print("VÉRIFICATION DU SIGNAL")
print("-" * 80)

affectation_active = affectations.filter(
    est_responsable_principal=True,
    date_fin__isnull=True
).first()

if affectation_active:
    print(f"✓ Affectation responsable active trouvée")
    print(f"  - ID: {affectation_active.id}")
    print(f"  - Date création: {affectation_active.date_debut}")
    
    # Le signal se déclenche sur post_save
    # Si l'affectation existe mais pas la notification, le signal n'a pas fonctionné
    if not notifications.exists():
        print("\n⚠ PROBLÈME: Affectation existe mais notification manquante")
        print("  Le signal n'a pas créé la notification")
else:
    print("✗ Aucune affectation responsable active")

print("\n" + "=" * 80)
