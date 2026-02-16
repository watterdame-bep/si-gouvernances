#!/usr/bin/env python
"""
Script de vérification complète du système d'emails HTML
Vérifie que le code utilise bien EmailMultiAlternatives et les templates HTML
"""

import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from core.models import Utilisateur, Projet, NotificationProjet
from core.utils_notifications_email import envoyer_email_notification_projet


def verifier_configuration():
    """Vérifie la configuration email"""
    print("=" * 80)
    print("VÉRIFICATION DE LA CONFIGURATION EMAIL")
    print("=" * 80)
    
    print(f"\n✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"✓ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"✓ BASE_URL: {settings.BASE_URL}")
    
    return True


def verifier_templates():
    """Vérifie que les templates HTML existent"""
    print("\n" + "=" * 80)
    print("VÉRIFICATION DES TEMPLATES HTML")
    print("=" * 80)
    
    templates = [
        'emails/base_email.html',
        'emails/notification_responsable_projet.html',
        'emails/notification_activation_compte.html',
        'emails/notification_assignation_tache.html',
        'emails/notification_alerte_projet.html',
    ]
    
    for template in templates:
        try:
            # Tester le rendu avec un contexte minimal
            context = {
                'destinataire_nom': 'Test User',
                'base_url': 'http://localhost:8000',
                'logo_url': 'http://localhost:8000/media/logos/jconsult_logo.png',
            }
            
            if 'responsable_projet' in template:
                context.update({
                    'projet_nom': 'Test Projet',
                    'projet_client': 'Test Client',
                    'projet_statut': 'En cours',
                    'projet_budget': '100000.00',
                    'projet_devise': 'USD',
                    'affecte_par': 'Admin',
                    'date_notification': '16/02/2026 12:00',
                    'projet_url': 'http://localhost:8000/projets/1/',
                })
            
            html = render_to_string(template, context)
            print(f"\n✓ Template trouvé: {template}")
            print(f"  Taille HTML: {len(html)} caractères")
            
            # Vérifier que c'est bien du HTML
            if '<html' in html and '</html>' in html:
                print(f"  ✓ Contient des balises HTML")
            if 'J-Consult MY' in html or 'J-CONSULT MY' in html:
                print(f"  ✓ Contient le copyright J-Consult MY")
            if 'linear-gradient' in html or 'gradient' in html:
                print(f"  ✓ Contient des styles CSS (gradient)")
                
        except Exception as e:
            print(f"\n✗ Erreur avec template {template}: {e}")
            return False
    
    return True


def verifier_fonction_envoi():
    """Vérifie que la fonction d'envoi utilise EmailMultiAlternatives"""
    print("\n" + "=" * 80)
    print("VÉRIFICATION DU CODE D'ENVOI")
    print("=" * 80)
    
    # Lire le fichier source
    with open('core/utils_notifications_email.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = [
        ('EmailMultiAlternatives', 'Import de EmailMultiAlternatives'),
        ('render_to_string', 'Import de render_to_string'),
        ('email.attach_alternative', 'Attachement du HTML'),
        ('"text/html"', 'Type MIME text/html'),
        ('emails/', 'Utilisation des templates emails/'),
    ]
    
    for check_str, description in checks:
        if check_str in code:
            print(f"✓ {description}: TROUVÉ")
        else:
            print(f"✗ {description}: NON TROUVÉ")
            return False
    
    return True


def verifier_signals():
    """Vérifie que les signaux sont bien configurés"""
    print("\n" + "=" * 80)
    print("VÉRIFICATION DES SIGNAUX")
    print("=" * 80)
    
    # Lire le fichier signals
    with open('core/signals_notifications.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    checks = [
        ('@receiver(post_save, sender=NotificationProjet)', 'Signal NotificationProjet'),
        ('envoyer_email_notification_projet', 'Appel fonction email projet'),
        ('if created:', 'Vérification création'),
    ]
    
    for check_str, description in checks:
        if check_str in code:
            print(f"✓ {description}: TROUVÉ")
        else:
            print(f"✗ {description}: NON TROUVÉ")
    
    return True


def test_envoi_reel():
    """Test d'envoi réel d'un email HTML"""
    print("\n" + "=" * 80)
    print("TEST D'ENVOI RÉEL")
    print("=" * 80)
    
    try:
        # Trouver un utilisateur avec email
        user = Utilisateur.objects.filter(email__isnull=False).exclude(email='').first()
        if not user:
            print("✗ Aucun utilisateur avec email trouvé")
            return False
        
        print(f"\n✓ Utilisateur trouvé: {user.get_full_name()} ({user.email})")
        
        # Trouver un projet
        projet = Projet.objects.first()
        if not projet:
            print("✗ Aucun projet trouvé")
            return False
        
        print(f"✓ Projet trouvé: {projet.nom}")
        
        # Créer une notification de test
        notification = NotificationProjet.objects.create(
            destinataire=user,
            projet=projet,
            type_notification='RESPONSABLE_PRINCIPAL',
            titre=f'Test Email HTML - {user.get_full_name()}',
            message=f'Ceci est un test pour vérifier que les emails HTML fonctionnent correctement.',
            emetteur=user
        )
        
        print(f"✓ Notification créée: ID {notification.id}")
        print(f"\n⏳ Envoi de l'email en cours...")
        
        # Le signal devrait envoyer l'email automatiquement
        # Mais on peut aussi l'envoyer manuellement pour vérifier
        result = envoyer_email_notification_projet(notification)
        
        if result:
            print(f"✓ Email envoyé avec succès!")
            print(f"\n📧 VÉRIFIEZ VOTRE BOÎTE EMAIL: {user.email}")
            print(f"   Sujet: [SI-Gouvernance] Nouveau Responsable: {projet.nom}")
            print(f"   L'email devrait être en HTML avec:")
            print(f"   - Logo J-Consult MY")
            print(f"   - Design moderne avec gradient violet/bleu")
            print(f"   - Bouton 'Accéder au Projet'")
            print(f"   - Footer avec copyright © 2026 J-Consult MY")
            return True
        else:
            print(f"✗ Erreur lors de l'envoi")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale"""
    print("\n" + "=" * 80)
    print("DIAGNOSTIC COMPLET DU SYSTÈME D'EMAILS HTML")
    print("=" * 80)
    
    resultats = []
    
    # 1. Configuration
    resultats.append(("Configuration", verifier_configuration()))
    
    # 2. Templates
    resultats.append(("Templates HTML", verifier_templates()))
    
    # 3. Code d'envoi
    resultats.append(("Code d'envoi", verifier_fonction_envoi()))
    
    # 4. Signaux
    resultats.append(("Signaux", verifier_signals()))
    
    # 5. Test réel
    resultats.append(("Test d'envoi réel", test_envoi_reel()))
    
    # Résumé
    print("\n" + "=" * 80)
    print("RÉSUMÉ DES VÉRIFICATIONS")
    print("=" * 80)
    
    for nom, resultat in resultats:
        statut = "✓ OK" if resultat else "✗ ÉCHEC"
        print(f"{statut:10} {nom}")
    
    tous_ok = all(r for _, r in resultats)
    
    if tous_ok:
        print("\n" + "=" * 80)
        print("✓ TOUT EST CONFIGURÉ CORRECTEMENT!")
        print("=" * 80)
        print("\nSi vous recevez toujours des emails en texte brut:")
        print("1. Vérifiez que vous testez avec une NOUVELLE action (pas un ancien email)")
        print("2. Vérifiez les paramètres de votre client email:")
        print("   - Gmail: Paramètres > Affichage > Afficher les images")
        print("   - Outlook: Fichier > Options > Centre de gestion de la confidentialité")
        print("3. Consultez le code source de l'email (Gmail: ⋮ > Afficher l'original)")
        print("   Cherchez 'Content-Type: text/html' dans les en-têtes")
    else:
        print("\n" + "=" * 80)
        print("✗ CERTAINES VÉRIFICATIONS ONT ÉCHOUÉ")
        print("=" * 80)
        print("\nVeuillez corriger les erreurs ci-dessus.")
    
    return 0 if tous_ok else 1


if __name__ == '__main__':
    sys.exit(main())
