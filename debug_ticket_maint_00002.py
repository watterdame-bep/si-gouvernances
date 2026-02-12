"""
Script de debug pour vérifier le statut du ticket MAINT-00002
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import TicketMaintenance

# Récupérer le ticket
try:
    ticket = TicketMaintenance.objects.get(numero_ticket='MAINT-00002')
    
    print("=" * 60)
    print(f"TICKET: {ticket.numero_ticket}")
    print("=" * 60)
    print(f"Titre: {ticket.titre}")
    print(f"Statut: {ticket.statut}")
    print(f"Priorité: {ticket.priorite}")
    print(f"Date création: {ticket.date_creation}")
    print(f"Date résolution: {ticket.date_resolution}")
    print(f"Solution: {ticket.solution[:100] if ticket.solution else 'Aucune'}")
    print(f"Assignés à: {[u.get_full_name() for u in ticket.assignes_a.all()]}")
    print("=" * 60)
    
    # Vérifier la condition du template
    print("\nVÉRIFICATION DE LA CONDITION:")
    print(f"ticket.statut == 'EN_COURS': {ticket.statut == 'EN_COURS'}")
    print(f"ticket.statut == 'RESOLU': {ticket.statut == 'RESOLU'}")
    print(f"ticket.statut == 'FERME': {ticket.statut == 'FERME'}")
    
    if ticket.statut == 'EN_COURS':
        print("\n⚠️ Le formulaire DEVRAIT s'afficher (statut EN_COURS)")
    elif ticket.statut == 'RESOLU':
        print("\n✅ Le formulaire NE DEVRAIT PAS s'afficher (statut RESOLU)")
        print("   La section verte 'Ticket résolu' devrait s'afficher")
    else:
        print(f"\n❓ Statut inattendu: {ticket.statut}")
    
except TicketMaintenance.DoesNotExist:
    print("❌ Ticket MAINT-00002 introuvable")
except Exception as e:
    print(f"❌ Erreur: {e}")
