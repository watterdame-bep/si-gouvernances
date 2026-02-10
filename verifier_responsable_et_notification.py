import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, NotificationTache, NotificationModule

# Trouver les utilisateurs
try:
    don_dieu = Utilisateur.objects.get(email='jovi80@gmail.com')
    print(f"✅ Don Dieu trouvé: {don_dieu.get_full_name()} (ID: {don_dieu.id})")
except:
    print("❌ Don Dieu non trouvé")
    don_dieu = None

try:
    eraste = Utilisateur.objects.filter(first_name__icontains='Eraste').first()
    if eraste:
        print(f"✅ Eraste trouvé: {eraste.get_full_name()} (ID: {eraste.id}, Email: {eraste.email})")
    else:
        print("❌ Eraste non trouvé")
except:
    print("❌ Erreur lors de la recherche d'Eraste")
    eraste = None

print("\n" + "="*60)
print("PROJETS ET RESPONSABLES")
print("="*60)

# Lister tous les projets avec leurs responsables
projets = Projet.objects.all()
for projet in projets:
    responsable = projet.get_responsable_principal()
    print(f"\n📁 Projet: {projet.nom}")
    if responsable:
        print(f"   👤 Responsable: {responsable.get_full_name()} (ID: {responsable.id})")
    else:
        print(f"   ⚠️  Pas de responsable principal")
    
    # Afficher les membres
    affectations = projet.affectations.filter(date_fin__isnull=True)
    print(f"   👥 Membres ({affectations.count()}):")
    for aff in affectations:
        role = "Responsable" if aff.est_responsable_principal else "Membre"
        print(f"      - {aff.utilisateur.get_full_name()} ({role})")

print("\n" + "="*60)
print("NOTIFICATIONS RÉCENTES")
print("="*60)

# Notifications de tâches récentes
print("\n📬 NotificationTache (5 dernières):")
notifs_tache = NotificationTache.objects.all().order_by('-date_creation')[:5]
for notif in notifs_tache:
    lue_str = "✅ Lue" if notif.lue else "🔔 Non lue"
    print(f"   {lue_str} | {notif.destinataire.get_full_name()} | {notif.type_notification}")
    print(f"      Titre: {notif.titre}")
    if notif.emetteur:
        print(f"      Émetteur: {notif.emetteur.get_full_name()}")
    print(f"      Date: {notif.date_creation}")
    print()

# Notifications de modules récentes
print("\n📬 NotificationModule (5 dernières):")
notifs_module = NotificationModule.objects.all().order_by('-date_creation')[:5]
for notif in notifs_module:
    lue_str = "✅ Lue" if notif.lue else "🔔 Non lue"
    print(f"   {lue_str} | {notif.destinataire.get_full_name()} | {notif.type_notification}")
    print(f"      Titre: {notif.titre}")
    if notif.emetteur:
        print(f"      Émetteur: {notif.emetteur.get_full_name()}")
    print(f"      Date: {notif.date_creation}")
    print()

print("\n" + "="*60)
print("DIAGNOSTIC")
print("="*60)

if don_dieu and eraste:
    # Vérifier si Eraste est responsable d'un projet
    projets_eraste_responsable = []
    for projet in projets:
        resp = projet.get_responsable_principal()
        if resp and resp.id == eraste.id:
            projets_eraste_responsable.append(projet)
    
    if projets_eraste_responsable:
        print(f"\n✅ Eraste est responsable de {len(projets_eraste_responsable)} projet(s):")
        for p in projets_eraste_responsable:
            print(f"   - {p.nom}")
    else:
        print(f"\n⚠️  Eraste n'est responsable d'aucun projet")
        print(f"   → C'est pourquoi il ne reçoit pas de notifications de tâches terminées")
    
    # Vérifier si Don Dieu est responsable d'un projet
    projets_don_responsable = []
    for projet in projets:
        resp = projet.get_responsable_principal()
        if resp and resp.id == don_dieu.id:
            projets_don_responsable.append(projet)
    
    if projets_don_responsable:
        print(f"\n✅ Don Dieu est responsable de {len(projets_don_responsable)} projet(s):")
        for p in projets_don_responsable:
            print(f"   - {p.nom}")
    else:
        print(f"\n⚠️  Don Dieu n'est responsable d'aucun projet")

print("\n" + "="*60)
print("SOLUTION")
print("="*60)
print("""
Pour qu'Eraste reçoive des notifications de tâches terminées:
1. Eraste doit être le RESPONSABLE PRINCIPAL du projet
2. Un autre membre (pas Eraste) doit terminer une tâche
3. La notification sera créée automatiquement

Pour définir Eraste comme responsable:
1. Aller dans Paramètres du projet
2. Section "Gérer les membres"
3. Cliquer sur "Définir comme responsable" pour Eraste
""")
