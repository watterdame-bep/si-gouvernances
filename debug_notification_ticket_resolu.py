"""
Script de debug pour vérifier les notifications de tickets résolus
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import TicketMaintenance, NotificationProjet, Utilisateur

print("=" * 70)
print("DEBUG : Notifications Tickets Résolus")
print("=" * 70)

# 1. Vérifier l'administrateur
print("\n1. VÉRIFICATION DE L'ADMINISTRATEUR")
print("-" * 70)
admins = Utilisateur.objects.filter(role_systeme__nom='ADMINISTRATEUR')
print(f"Nombre d'administrateurs trouvés : {admins.count()}")
for admin in admins:
    print(f"  - {admin.get_full_name()} (ID: {admin.id}, Email: {admin.email})")

if not admins.exists():
    print("❌ PROBLÈME : Aucun administrateur trouvé !")
    print("   La notification ne peut pas être créée sans administrateur.")
else:
    admin = admins.first()
    print(f"✅ Administrateur principal : {admin.get_full_name()}")

# 2. Vérifier les tickets résolus
print("\n2. TICKETS RÉSOLUS")
print("-" * 70)
tickets_resolus = TicketMaintenance.objects.filter(statut='RESOLU').order_by('-date_resolution')
print(f"Nombre de tickets résolus : {tickets_resolus.count()}")

for ticket in tickets_resolus[:5]:  # Afficher les 5 derniers
    print(f"\n  Ticket: {ticket.numero_ticket}")
    print(f"  Titre: {ticket.titre}")
    print(f"  Projet: {ticket.projet.nom}")
    print(f"  Résolu le: {ticket.date_resolution}")
    print(f"  Résolu par: {ticket.modifie_par.get_full_name() if ticket.modifie_par else 'Inconnu'}")

# 3. Vérifier les notifications de type TICKET_RESOLU
print("\n3. NOTIFICATIONS TICKET_RESOLU")
print("-" * 70)
notifs_ticket_resolu = NotificationProjet.objects.filter(
    type_notification='TICKET_RESOLU'
).order_by('-date_creation')

print(f"Nombre de notifications TICKET_RESOLU : {notifs_ticket_resolu.count()}")

if notifs_ticket_resolu.exists():
    print("\nDernières notifications :")
    for notif in notifs_ticket_resolu[:5]:
        print(f"\n  Notification ID: {notif.id}")
        print(f"  Destinataire: {notif.destinataire.get_full_name()}")
        print(f"  Titre: {notif.titre}")
        print(f"  Message: {notif.message[:100]}...")
        print(f"  Date: {notif.date_creation}")
        print(f"  Lue: {notif.lue}")
else:
    print("❌ Aucune notification TICKET_RESOLU trouvée !")

# 4. Vérifier le dernier ticket résolu du projet "Système de gestion de pharmacie"
print("\n4. PROJET 'SYSTÈME DE GESTION DE PHARMACIE'")
print("-" * 70)

try:
    from django.db.models import Q
    projet_pharma = None
    
    # Chercher le projet (plusieurs variantes possibles)
    projets = TicketMaintenance.objects.filter(
        Q(projet__nom__icontains='pharmacie') | 
        Q(projet__nom__icontains='pharma')
    ).values_list('projet__nom', 'projet__id').distinct()
    
    if projets:
        print(f"Projets trouvés contenant 'pharmacie' :")
        for nom, id in projets:
            print(f"  - {nom} (ID: {id})")
            
        # Prendre le premier
        projet_id = projets[0][1]
        tickets_pharma = TicketMaintenance.objects.filter(
            projet__id=projet_id,
            statut='RESOLU'
        ).order_by('-date_resolution')
        
        print(f"\nTickets résolus dans ce projet : {tickets_pharma.count()}")
        
        if tickets_pharma.exists():
            dernier_ticket = tickets_pharma.first()
            print(f"\nDernier ticket résolu :")
            print(f"  Numéro: {dernier_ticket.numero_ticket}")
            print(f"  Titre: {dernier_ticket.titre}")
            print(f"  Résolu le: {dernier_ticket.date_resolution}")
            print(f"  Résolu par: {dernier_ticket.modifie_par.get_full_name() if dernier_ticket.modifie_par else 'Inconnu'}")
            
            # Vérifier si une notification existe pour ce ticket
            notif_existe = NotificationProjet.objects.filter(
                type_notification='TICKET_RESOLU',
                donnees_contexte__ticket_numero=dernier_ticket.numero_ticket
            ).exists()
            
            if notif_existe:
                print(f"  ✅ Notification créée pour ce ticket")
                notif = NotificationProjet.objects.filter(
                    type_notification='TICKET_RESOLU',
                    donnees_contexte__ticket_numero=dernier_ticket.numero_ticket
                ).first()
                print(f"     Destinataire: {notif.destinataire.get_full_name()}")
                print(f"     Lue: {notif.lue}")
            else:
                print(f"  ❌ AUCUNE notification trouvée pour ce ticket !")
                print(f"     Cela signifie que la notification n'a pas été créée lors de la résolution.")
    else:
        print("❌ Aucun projet contenant 'pharmacie' trouvé")
        
except Exception as e:
    print(f"❌ Erreur : {e}")

# 5. Diagnostic
print("\n5. DIAGNOSTIC")
print("=" * 70)

if not admins.exists():
    print("❌ PROBLÈME IDENTIFIÉ : Aucun administrateur dans le système")
    print("   SOLUTION : Créer un utilisateur avec le rôle ADMINISTRATEUR")
elif notifs_ticket_resolu.count() == 0:
    print("❌ PROBLÈME IDENTIFIÉ : Aucune notification TICKET_RESOLU créée")
    print("   CAUSES POSSIBLES :")
    print("   1. Le code de notification n'est pas exécuté")
    print("   2. Une erreur silencieuse empêche la création")
    print("   3. Le type TICKET_RESOLU n'existe pas dans les choix")
elif notifs_ticket_resolu.count() < tickets_resolus.count():
    print("⚠️  PROBLÈME PARTIEL : Certaines notifications manquent")
    print(f"   Tickets résolus: {tickets_resolus.count()}")
    print(f"   Notifications créées: {notifs_ticket_resolu.count()}")
    print(f"   Manquantes: {tickets_resolus.count() - notifs_ticket_resolu.count()}")
else:
    print("✅ Tout semble fonctionner correctement")
    print(f"   Tickets résolus: {tickets_resolus.count()}")
    print(f"   Notifications créées: {notifs_ticket_resolu.count()}")

print("\n" + "=" * 70)
