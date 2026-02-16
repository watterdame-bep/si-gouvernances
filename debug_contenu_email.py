"""
Script pour débugger le contenu exact de l'email envoyé
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from core.models import Utilisateur, Projet

print("=" * 70)
print("DEBUG CONTENU EMAIL")
print("=" * 70)

# Récupérer les données
user = Utilisateur.objects.filter(email__isnull=False).exclude(email='').first()
projet = Projet.objects.first()

# Préparer le contexte
base_url = "http://localhost:8000"
logo_url = f"{base_url}/media/logos/jconsult_logo.png"

context = {
    'destinataire_nom': user.get_full_name(),
    'projet_nom': projet.nom,
    'projet_client': projet.client,
    'projet_statut': projet.statut.get_nom_display(),
    'projet_budget': f"{projet.budget_previsionnel:,.2f}",
    'projet_devise': projet.devise,
    'affecte_par': 'Administrateur Système',
    'date_notification': '16/02/2026 à 14:30',
    'projet_url': f"{base_url}/projets/{projet.id}/",
    'base_url': base_url,
    'logo_url': logo_url,
}

print(f"\n📋 Contexte:")
for key, value in context.items():
    print(f"   {key}: {value}")

# Tenter de rendre le template
print(f"\n🎨 Rendu du template...")
try:
    message_html = render_to_string('emails/notification_responsable_projet.html', context)
    print(f"   ✅ Template rendu avec succès!")
    print(f"   Longueur HTML: {len(message_html)} caractères")
    
    # Afficher un extrait
    print(f"\n📄 Extrait du HTML (premiers 500 caractères):")
    print("-" * 70)
    print(message_html[:500])
    print("-" * 70)
    
    # Vérifier les éléments clés
    print(f"\n🔍 Vérification des éléments:")
    checks = {
        'Logo': 'logo_url' in message_html or 'jconsult_logo' in message_html,
        'Header coloré': 'gradient' in message_html or '#667eea' in message_html,
        'Bouton action': 'action-button' in message_html,
        'Footer': 'copyright' in message_html.lower() or '2026' in message_html,
        'Nom destinataire': user.get_full_name() in message_html,
        'Nom projet': projet.nom in message_html,
    }
    
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
    
    # Créer et envoyer l'email
    print(f"\n📧 Envoi de l'email...")
    
    message_text = f"""
Bonjour {user.get_full_name()},

Vous avez été désigné responsable principal du projet "{projet.nom}".

Détails du projet:
- Projet: {projet.nom}
- Client: {projet.client}

Cordialement,
L'équipe SI-Gouvernance
"""
    
    email = EmailMultiAlternatives(
        subject='[TEST DEBUG] Responsable de Projet',
        body=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    
    email.attach_alternative(message_html, "text/html")
    email.send(fail_silently=False)
    
    print(f"   ✅ Email envoyé à {user.email}")
    print(f"\n📬 Vérifiez votre boîte mail!")
    print(f"   Si l'email est en texte brut, le problème vient du client email")
    print(f"   Si l'email est en HTML, le problème était le cache/rechargement")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DEBUG TERMINÉ")
print("=" * 70)
