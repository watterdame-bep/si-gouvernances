"""
Script pour marquer la notification de projet comme non lue pour tester l'affichage
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationProjet

def marquer_non_lue():
    """Marquer la notification ID 38 comme non lue"""
    
    try:
        notif = NotificationProjet.objects.get(id=38)
        print(f"Notification trouvée: {notif.titre}")
        print(f"Statut actuel: {'Lue' if notif.lue else 'Non lue'}")
        
        if notif.lue:
            notif.lue = False
            notif.date_lecture = None
            notif.save()
            print("\n✅ Notification marquée comme NON LUE")
            print("   Elle devrait maintenant apparaître dans l'interface")
        else:
            print("\n⚠️  La notification est déjà non lue")
            
    except NotificationProjet.DoesNotExist:
        print("❌ Notification ID 38 non trouvée")

if __name__ == '__main__':
    marquer_non_lue()
