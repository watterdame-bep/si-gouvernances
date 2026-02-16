"""
Script pour débugger le format des emails envoyés
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, NotificationProjet
from core.utils_notifications_email import envoyer_email_notification_projet
from django.utils import timezone

print("=" * 70)
print("DEBUG FORMAT EMAIL")
print("=" * 70)

# Récupérer un utilisateur
user = Utilisateur.objects.filter(email__isnull=False).exclude(email='').first()
if not user:
    print("\n❌ Aucun utilisateur trouvé")
    exit(1)

# Récupérer un projet
projet = Projet.objects.first()
if not projet:
    print("\n❌ Aucun projet trouvé")
    exit(1)

print(f"\n📧 Test avec:")
print(f"   Utilisateur: {user.get_full_name()} ({user.email})")
print(f"   Projet: {projet.nom}")

# Créer une notification de test
notification = NotificationProjet.objects.create(
    destinataire=user,
    projet=projet,
    type_notification='RESPONSABLE_PRINCIPAL',
    titre='Test Email Format',
    message='Ceci est un test pour vérifier le format HTML',
    emetteur=user,
    lue=False
)

print(f"\n✅ Notification créée: {notification.id}")
print(f"   Type: {notification.type_notification}")
print(f"   Titre: {notification.titre}")

# Tester l'envoi
print("\n🔄 Envoi de l'email...")
try:
    resultat = envoyer_email_notification_projet(notification)
    if resultat:
        print("✅ Email envoyé avec succès!")
        print(f"\n📬 Vérifiez votre boîte mail: {user.email}")
        print("   L'email devrait être en format HTML professionnel")
    else:
        print("❌ Échec de l'envoi")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

# Supprimer la notification de test
notification.delete()
print("\n🗑️  Notification de test supprimée")

print("\n" + "=" * 70)
print("DEBUG TERMINÉ")
print("=" * 70)
