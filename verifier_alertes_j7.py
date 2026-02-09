"""
Script pour vérifier les alertes J-7 créées
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationProjet, Projet

print("=" * 80)
print("VÉRIFICATION DES ALERTES J-7")
print("=" * 80)
print()

# Trouver le projet démarré
projet = Projet.objects.filter(nom__icontains="gestion d'ecole").first()

if projet:
    print(f"Projet: {projet.nom}")
    print(f"Date de fin: {projet.date_fin}")
    print(f"Jours restants: {projet.jours_restants()}")
    print()
    
    # Récupérer toutes les notifications pour ce projet
    notifications = NotificationProjet.objects.filter(projet=projet).order_by('-date_creation')
    
    print(f"Total de notifications: {notifications.count()}")
    print()
    
    # Grouper par type
    for type_notif in ['PROJET_DEMARRE', 'ALERTE_FIN_PROJET']:
        notifs = notifications.filter(type_notification=type_notif)
        if notifs.exists():
            print(f"📧 {type_notif} ({notifs.count()} notification(s)):")
            for notif in notifs:
                statut_lecture = "✅ Lue" if notif.lue else "📬 Non lue"
                print(f"   • {notif.destinataire.get_full_name()} - {statut_lecture}")
                print(f"     Titre: {notif.titre}")
                print(f"     Message: {notif.message[:100]}...")
                print(f"     Créée le: {notif.date_creation.strftime('%d/%m/%Y %H:%M')}")
                print()
    
    print("=" * 80)
    print("✅ VÉRIFICATION TERMINÉE")
    print("=" * 80)
