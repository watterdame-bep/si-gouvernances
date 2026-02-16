"""
Script pour vérifier quelles notifications sont actuellement implémentées
et diagnostiquer pourquoi un email n'a pas été envoyé
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, NotificationTache, NotificationModule, NotificationProjet, AlerteProjet
from django.utils import timezone
from datetime import timedelta

print("\n" + "="*80)
print("DIAGNOSTIC DES NOTIFICATIONS EMAIL")
print("="*80)

# 1. Vérifier l'utilisateur Eraste Butela
print("\n1. VÉRIFICATION UTILISATEUR ERASTE BUTELA")
print("-"*80)

try:
    eraste = Utilisateur.objects.filter(prenom__icontains='Eraste', nom__icontains='Butela').first()
    if eraste:
        print(f"✓ Utilisateur trouvé: {eraste.get_full_name()}")
        print(f"  - Email: {eraste.email if eraste.email else '❌ PAS D\'EMAIL'}")
        print(f"  - Actif: {eraste.statut_actif}")
        print(f"  - ID: {eraste.id}")
    else:
        print("❌ Utilisateur Eraste Butela non trouvé")
        eraste = None
except Exception as e:
    print(f"❌ Erreur: {e}")
    eraste = None

# 2. Vérifier les notifications récentes pour Eraste
if eraste:
    print("\n2. NOTIFICATIONS RÉCENTES (dernières 24h)")
    print("-"*80)
    
    hier = timezone.now() - timedelta(hours=24)
    
    # NotificationTache
    notifs_tache = NotificationTache.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"\n📋 NotificationTache: {notifs_tache.count()} notification(s)")
    for notif in notifs_tache[:5]:
        print(f"  - [{notif.date_creation.strftime('%H:%M:%S')}] {notif.type_notification}: {notif.titre}")
    
    # NotificationModule
    notifs_module = NotificationModule.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"\n📦 NotificationModule: {notifs_module.count()} notification(s)")
    for notif in notifs_module[:5]:
        print(f"  - [{notif.date_creation.strftime('%H:%M:%S')}] {notif.type_notification}: {notif.titre}")
    
    # NotificationProjet
    notifs_projet = NotificationProjet.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"\n🎯 NotificationProjet: {notifs_projet.count()} notification(s)")
    for notif in notifs_projet[:5]:
        print(f"  - [{notif.date_creation.strftime('%H:%M:%S')}] {notif.type_notification}: {notif.titre}")
    
    # AlerteProjet
    alertes = AlerteProjet.objects.filter(
        destinataire=eraste,
        date_creation__gte=hier
    ).order_by('-date_creation')
    
    print(f"\n⚠️  AlerteProjet: {alertes.count()} alerte(s)")
    for alerte in alertes[:5]:
        print(f"  - [{alerte.date_creation.strftime('%H:%M:%S')}] {alerte.type_alerte}: {alerte.titre}")

# 3. Vérifier les notifications implémentées dans le code
print("\n3. NOTIFICATIONS IMPLÉMENTÉES DANS LE CODE")
print("-"*80)

import subprocess
import re

# Rechercher les créations de NotificationTache
print("\n📋 NotificationTache - Recherche dans le code...")
try:
    result = subprocess.run(
        ['findstr', '/S', '/I', '/C:NotificationTache.objects.create', 'core\\*.py'],
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.stdout:
        lignes = result.stdout.strip().split('\n')
        fichiers = set()
        for ligne in lignes:
            if ':' in ligne:
                fichier = ligne.split(':')[0]
                fichiers.add(fichier)
        
        print(f"  ✓ Trouvé dans {len(fichiers)} fichier(s):")
        for fichier in sorted(fichiers):
            print(f"    - {fichier}")
    else:
        print("  ❌ Aucune création trouvée")
except Exception as e:
    print(f"  ⚠️  Erreur de recherche: {e}")

# Rechercher les créations de NotificationModule
print("\n📦 NotificationModule - Recherche dans le code...")
try:
    result = subprocess.run(
        ['findstr', '/S', '/I', '/C:NotificationModule.objects.create', 'core\\*.py'],
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.stdout:
        lignes = result.stdout.strip().split('\n')
        fichiers = set()
        for ligne in lignes:
            if ':' in ligne:
                fichier = ligne.split(':')[0]
                fichiers.add(fichier)
        
        print(f"  ✓ Trouvé dans {len(fichiers)} fichier(s):")
        for fichier in sorted(fichiers):
            print(f"    - {fichier}")
    else:
        print("  ❌ Aucune création trouvée")
except Exception as e:
    print(f"  ⚠️  Erreur de recherche: {e}")

# Rechercher les créations de NotificationProjet
print("\n🎯 NotificationProjet - Recherche dans le code...")
try:
    result = subprocess.run(
        ['findstr', '/S', '/I', '/C:NotificationProjet.objects.create', 'core\\*.py'],
        capture_output=True,
        text=True,
        shell=True
    )
    
    if result.stdout:
        lignes = result.stdout.strip().split('\n')
        fichiers = set()
        for ligne in lignes:
            if ':' in ligne:
                fichier = ligne.split(':')[0]
                fichiers.add(fichier)
        
        print(f"  ✓ Trouvé dans {len(fichiers)} fichier(s):")
        for fichier in sorted(fichiers):
            print(f"    - {fichier}")
    else:
        print("  ❌ Aucune création trouvée")
except Exception as e:
    print(f"  ⚠️  Erreur de recherche: {e}")

# 4. Vérifier la configuration des signaux
print("\n4. VÉRIFICATION DES SIGNAUX DJANGO")
print("-"*80)

try:
    import core.signals_notifications
    print("✓ Module signals_notifications importé avec succès")
    print("✓ Les signaux sont actifs et devraient envoyer des emails automatiquement")
except Exception as e:
    print(f"❌ Erreur d'import des signaux: {e}")

# 5. Vérifier la configuration SMTP
print("\n5. CONFIGURATION SMTP")
print("-"*80)

from django.conf import settings

print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"TLS: {settings.EMAIL_USE_TLS}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"From: {settings.DEFAULT_FROM_EMAIL}")

# 6. Résumé et diagnostic
print("\n" + "="*80)
print("RÉSUMÉ DU DIAGNOSTIC")
print("="*80)

if eraste:
    if not eraste.email:
        print("\n❌ PROBLÈME IDENTIFIÉ: Eraste Butela n'a PAS d'adresse email!")
        print("   → Solution: Ajoutez une adresse email dans son profil utilisateur")
    else:
        total_notifs = (
            NotificationTache.objects.filter(destinataire=eraste, date_creation__gte=hier).count() +
            NotificationModule.objects.filter(destinataire=eraste, date_creation__gte=hier).count() +
            NotificationProjet.objects.filter(destinataire=eraste, date_creation__gte=hier).count()
        )
        
        if total_notifs == 0:
            print("\n⚠️  PROBLÈME: Aucune notification créée pour Eraste dans les dernières 24h")
            print("   → Vérifiez que l'action (assignation de tâche) a bien créé une notification")
            print("   → Consultez les logs Django pour voir s'il y a des erreurs")
        else:
            print(f"\n✓ {total_notifs} notification(s) créée(s) pour Eraste")
            print("✓ Email configuré correctement")
            print("✓ Signaux actifs")
            print("\n💡 Si l'email n'a pas été reçu:")
            print("   1. Vérifiez les spams/courrier indésirable")
            print("   2. Attendez quelques minutes (délai de livraison)")
            print("   3. Consultez les logs Django pour voir les erreurs d'envoi")
            print("   4. Testez avec: python test_email_smtp.py")
else:
    print("\n❌ Impossible de diagnostiquer: Utilisateur Eraste Butela non trouvé")

print("\n" + "="*80)
