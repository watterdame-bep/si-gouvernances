"""
Script pour vérifier si Eraste Butela a un email et ses notifications récentes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, NotificationTache, NotificationModule, NotificationProjet
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*80)
print("VÉRIFICATION EMAIL ET NOTIFICATIONS - ERASTE BUTELA")
print("="*80)

# Rechercher Eraste
print("\n1. RECHERCHE DE L'UTILISATEUR")
print("-"*80)

eraste = Utilisateur.objects.filter(first_name__icontains='Eraste').first()

if not eraste:
    print("❌ Utilisateur 'Eraste' non trouvé")
    print("\nUtilisateurs disponibles:")
    for user in Utilisateur.objects.all()[:10]:
        print(f"  - {user.get_full_name()} ({user.username})")
else:
    print(f"✓ Utilisateur trouvé: {eraste.get_full_name()}")
    print(f"  - Username: {eraste.username}")
    print(f"  - Email: {eraste.email if eraste.email else '❌ PAS D\'EMAIL CONFIGURÉ'}")
    print(f"  - Actif: {'✓' if eraste.statut_actif else '❌'}")
    
    # Vérifier les notifications récentes
    print("\n2. NOTIFICATIONS RÉCENTES (dernières 24 heures)")
    print("-"*80)
    
    hier = timezone.now() - timedelta(hours=24)
    
    # NotificationTache
    notifs_tache = NotificationTache.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"\n📋 NotificationTache: {notifs_tache.count()} notification(s)")
    if notifs_tache.exists():
        for notif in notifs_tache:
            print(f"  [{notif.date_creation.strftime('%d/%m %H:%M')}] {notif.type_notification}")
            print(f"    Titre: {notif.titre}")
            print(f"    Tâche: {notif.tache.nom}")
            print()
    
    # NotificationModule
    notifs_module = NotificationModule.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"📦 NotificationModule: {notifs_module.count()} notification(s)")
    if notifs_module.exists():
        for notif in notifs_module:
            print(f"  [{notif.date_creation.strftime('%d/%m %H:%M')}] {notif.type_notification}")
            print(f"    Titre: {notif.titre}")
            print(f"    Module: {notif.module.nom}")
            print()
    
    # NotificationProjet
    notifs_projet = NotificationProjet.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"🎯 NotificationProjet: {notifs_projet.count()} notification(s)")
    if notifs_projet.exists():
        for notif in notifs_projet:
            print(f"  [{notif.date_creation.strftime('%d/%m %H:%M')}] {notif.type_notification}")
            print(f"    Titre: {notif.titre}")
            print(f"    Projet: {notif.projet.nom}")
            print()
    
    # Résumé
    total = notifs_tache.count() + notifs_module.count() + notifs_projet.count()
    
    print("\n" + "="*80)
    print("DIAGNOSTIC")
    print("="*80)
    
    if not eraste.email:
        print("\n❌ PROBLÈME IDENTIFIÉ: Pas d'adresse email!")
        print("\n📝 SOLUTION:")
        print("   1. Allez dans 'Gestion des Utilisateurs'")
        print("   2. Trouvez 'Eraste Butela'")
        print("   3. Cliquez sur 'Modifier'")
        print("   4. Ajoutez son adresse email")
        print("   5. Sauvegardez")
        print("\n   → Après cela, il recevra les emails automatiquement")
    elif total == 0:
        print("\n⚠️  Aucune notification créée dans les dernières 24h")
        print("\n💡 EXPLICATIONS POSSIBLES:")
        print("   1. L'action effectuée ne crée pas de notification")
        print("   2. La notification a été créée il y a plus de 24h")
        print("   3. L'action n'est pas encore implémentée")
        print("\n📖 Consultez: STATUT_NOTIFICATIONS_EMAIL_ACTUELLES.md")
        print("   pour voir les actions qui envoient des emails")
    else:
        print(f"\n✓ {total} notification(s) créée(s)")
        print("✓ Email configuré")
        print("\n💡 Si l'email n'a pas été reçu:")
        print("   1. Vérifiez les spams/courrier indésirable")
        print("   2. Attendez quelques minutes")
        print("   3. Vérifiez que le serveur Django est démarré")
        print("   4. Consultez les logs Django pour les erreurs")

print("\n" + "="*80)
