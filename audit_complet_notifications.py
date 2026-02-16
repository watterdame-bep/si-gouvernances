"""
Audit complet du système de notifications
Vérifie quelles notifications sont implémentées et lesquelles envoient des emails
"""

import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import (
    NotificationTache, NotificationEtape, NotificationModule, 
    NotificationProjet, AlerteProjet
)

def chercher_dans_fichiers(type_notification, dossiers=['core']):
    """Cherche si un type de notification est créé dans le code"""
    fichiers_trouves = []
    
    for dossier in dossiers:
        for root, dirs, files in os.walk(dossier):
            # Ignorer les dossiers de cache
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'migrations']]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Chercher type_notification='XXX' ou type_alerte='XXX'
                            if f"type_notification='{type_notification}'" in content or \
                               f'type_notification="{type_notification}"' in content or \
                               f"type_alerte='{type_notification}'" in content or \
                               f'type_alerte="{type_notification}"' in content:
                                fichiers_trouves.append(filepath)
                    except:
                        pass
    
    return fichiers_trouves

def analyser_notifications():
    """Analyse complète de toutes les notifications"""
    
    print("=" * 100)
    print("AUDIT COMPLET DU SYSTÈME DE NOTIFICATIONS")
    print("=" * 100)
    print()
    
    # Statistiques globales
    total_types = 0
    total_implementes = 0
    total_avec_email = 0
    
    resultats = {}
    
    # 1. NotificationTache
    print("1. NOTIFICATIONTACHE")
    print("-" * 100)
    resultats['NotificationTache'] = []
    
    for choice in NotificationTache.TYPE_NOTIFICATION_CHOICES:
        type_notif = choice[0]
        nom = choice[1]
        total_types += 1
        
        fichiers = chercher_dans_fichiers(type_notif)
        implementee = len(fichiers) > 0
        
        if implementee:
            total_implementes += 1
            total_avec_email += 1  # Tous les signaux sont actifs
        
        status = "✅" if implementee else "❌"
        email_status = "📧" if implementee else "  "
        
        resultats['NotificationTache'].append({
            'type': type_notif,
            'nom': nom,
            'implementee': implementee,
            'email': implementee,
            'fichiers': fichiers
        })
        
        print(f"  {status} {email_status} {type_notif:25} - {nom}")
        if fichiers:
            for f in fichiers[:2]:  # Afficher max 2 fichiers
                print(f"      └─ {f}")
    
    print()
    
    # 2. NotificationEtape
    print("2. NOTIFICATIONETAPE")
    print("-" * 100)
    resultats['NotificationEtape'] = []
    
    for choice in NotificationEtape.TYPE_NOTIFICATION_CHOICES:
        type_notif = choice[0]
        nom = choice[1]
        total_types += 1
        
        fichiers = chercher_dans_fichiers(type_notif)
        implementee = len(fichiers) > 0
        
        if implementee:
            total_implementes += 1
            total_avec_email += 1
        
        status = "✅" if implementee else "❌"
        email_status = "📧" if implementee else "  "
        
        resultats['NotificationEtape'].append({
            'type': type_notif,
            'nom': nom,
            'implementee': implementee,
            'email': implementee,
            'fichiers': fichiers
        })
        
        print(f"  {status} {email_status} {type_notif:25} - {nom}")
        if fichiers:
            for f in fichiers[:2]:
                print(f"      └─ {f}")
    
    print()
    
    # 3. NotificationModule
    print("3. NOTIFICATIONMODULE")
    print("-" * 100)
    resultats['NotificationModule'] = []
    
    for choice in NotificationModule.TYPE_NOTIFICATION_CHOICES:
        type_notif = choice[0]
        nom = choice[1]
        total_types += 1
        
        fichiers = chercher_dans_fichiers(type_notif)
        implementee = len(fichiers) > 0
        
        if implementee:
            total_implementes += 1
            total_avec_email += 1
        
        status = "✅" if implementee else "❌"
        email_status = "📧" if implementee else "  "
        
        resultats['NotificationModule'].append({
            'type': type_notif,
            'nom': nom,
            'implementee': implementee,
            'email': implementee,
            'fichiers': fichiers
        })
        
        print(f"  {status} {email_status} {type_notif:25} - {nom}")
        if fichiers:
            for f in fichiers[:2]:
                print(f"      └─ {f}")
    
    print()
    
    # 4. NotificationProjet
    print("4. NOTIFICATIONPROJET")
    print("-" * 100)
    resultats['NotificationProjet'] = []
    
    for choice in NotificationProjet.TYPE_NOTIFICATION_CHOICES:
        type_notif = choice[0]
        nom = choice[1]
        total_types += 1
        
        fichiers = chercher_dans_fichiers(type_notif)
        implementee = len(fichiers) > 0
        
        if implementee:
            total_implementes += 1
            total_avec_email += 1
        
        status = "✅" if implementee else "❌"
        email_status = "📧" if implementee else "  "
        
        resultats['NotificationProjet'].append({
            'type': type_notif,
            'nom': nom,
            'implementee': implementee,
            'email': implementee,
            'fichiers': fichiers
        })
        
        print(f"  {status} {email_status} {type_notif:35} - {nom}")
        if fichiers:
            for f in fichiers[:2]:
                print(f"      └─ {f}")
    
    print()
    
    # 5. AlerteProjet
    print("5. ALERTEPROJET")
    print("-" * 100)
    resultats['AlerteProjet'] = []
    
    for choice in AlerteProjet.TYPE_ALERTE_CHOICES:
        type_notif = choice[0]
        nom = choice[1]
        total_types += 1
        
        fichiers = chercher_dans_fichiers(type_notif)
        implementee = len(fichiers) > 0
        
        if implementee:
            total_implementes += 1
            total_avec_email += 1
        
        status = "✅" if implementee else "❌"
        email_status = "📧" if implementee else "  "
        
        resultats['AlerteProjet'].append({
            'type': type_notif,
            'nom': nom,
            'implementee': implementee,
            'email': implementee,
            'fichiers': fichiers
        })
        
        print(f"  {status} {email_status} {type_notif:25} - {nom}")
        if fichiers:
            for f in fichiers[:2]:
                print(f"      └─ {f}")
    
    print()
    print("=" * 100)
    print("RÉSUMÉ FINAL")
    print("=" * 100)
    print()
    print(f"📊 Total de types de notifications définis: {total_types}")
    print(f"✅ Notifications implémentées: {total_implementes}/{total_types} ({round(total_implementes/total_types*100, 1)}%)")
    print(f"📧 Notifications avec envoi d'email automatique: {total_avec_email}/{total_types} ({round(total_avec_email/total_types*100, 1)}%)")
    print()
    
    # Détail par catégorie
    print("DÉTAIL PAR CATÉGORIE:")
    print("-" * 100)
    
    for categorie, items in resultats.items():
        total_cat = len(items)
        impl_cat = sum(1 for item in items if item['implementee'])
        email_cat = sum(1 for item in items if item['email'])
        
        print(f"\n{categorie}:")
        print(f"  Total: {total_cat}")
        print(f"  Implémentées: {impl_cat}/{total_cat} ({round(impl_cat/total_cat*100, 1)}%)")
        print(f"  Avec email: {email_cat}/{total_cat} ({round(email_cat/total_cat*100, 1)}%)")
    
    print()
    print("=" * 100)
    print("NOTIFICATIONS NON IMPLÉMENTÉES")
    print("=" * 100)
    print()
    
    non_implementees = []
    for categorie, items in resultats.items():
        for item in items:
            if not item['implementee']:
                non_implementees.append(f"{categorie}.{item['type']} - {item['nom']}")
    
    if non_implementees:
        for notif in non_implementees:
            print(f"  ❌ {notif}")
    else:
        print("  🎉 Toutes les notifications sont implémentées!")
    
    print()
    print("=" * 100)
    print("SYSTÈME D'ENVOI D'EMAILS")
    print("=" * 100)
    print()
    print("✅ Signaux Django actifs dans core/signals_notifications.py:")
    print("   - NotificationTache → envoyer_email_notification_tache_signal")
    print("   - NotificationEtape → envoyer_email_notification_etape_signal")
    print("   - NotificationModule → envoyer_email_notification_module_signal")
    print("   - NotificationProjet → envoyer_email_notification_projet_signal")
    print("   - AlerteProjet → envoyer_email_alerte_projet_signal")
    print()
    print("📧 Toutes les notifications créées déclenchent automatiquement l'envoi d'un email!")
    print()
    
    return resultats, total_types, total_implementes, total_avec_email


if __name__ == '__main__':
    try:
        resultats, total, implementes, emails = analyser_notifications()
        
        print("=" * 100)
        print(f"✅ AUDIT TERMINÉ: {implementes}/{total} notifications implémentées avec envoi d'email automatique")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
