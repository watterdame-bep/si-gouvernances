import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Utilisateur, Projet, TacheEtape, TacheModule, NotificationTache, NotificationModule
from django.utils import timezone

# Trouver les utilisateurs
don_dieu = Utilisateur.objects.get(email='jovi80@gmail.com')
eraste = Utilisateur.objects.filter(first_name__icontains='Eraste').first()

print("="*60)
print("UTILISATEURS")
print("="*60)
print(f"Don Dieu: {don_dieu.get_full_name()} (ID: {don_dieu.id})")
print(f"Eraste: {eraste.get_full_name()} (ID: {eraste.id})")

# Trouver le projet
projet = Projet.objects.get(nom__icontains='pharmacie')
print(f"\nProjet: {projet.nom}")

# Vérifier le responsable
responsable = projet.get_responsable_principal()
print(f"Responsable: {responsable.get_full_name() if responsable else 'Aucun'}")

print("\n" + "="*60)
print("TÂCHES DE DON DIEU DANS CE PROJET")
print("="*60)

# Tâches d'étapes
taches_etape = TacheEtape.objects.filter(
    responsable=don_dieu,
    etape__projet=projet
)
print(f"\n📋 Tâches d'étapes ({taches_etape.count()}):")
for tache in taches_etape:
    print(f"   - {tache.nom}")
    print(f"     Statut: {tache.statut}")
    print(f"     Étape: {tache.etape.type_etape.get_nom_display()}")
    if tache.date_fin_reelle:
        print(f"     Terminée le: {tache.date_fin_reelle}")
    print()

# Tâches de modules
taches_module = TacheModule.objects.filter(
    responsable=don_dieu,
    module__projet=projet
)
print(f"\n📋 Tâches de modules ({taches_module.count()}):")
for tache in taches_module:
    print(f"   - {tache.nom}")
    print(f"     Statut: {tache.statut}")
    print(f"     Module: {tache.module.nom}")
    if tache.date_fin_reelle:
        print(f"     Terminée le: {tache.date_fin_reelle}")
    print()

print("\n" + "="*60)
print("NOTIFICATIONS POUR ERASTE")
print("="*60)

# Notifications de tâches pour Eraste
notifs_tache = NotificationTache.objects.filter(
    destinataire=eraste
).order_by('-date_creation')

print(f"\n📬 NotificationTache ({notifs_tache.count()}):")
for notif in notifs_tache:
    lue_str = "✅ Lue" if notif.lue else "🔔 Non lue"
    print(f"   {lue_str} | {notif.type_notification}")
    print(f"      Titre: {notif.titre}")
    print(f"      Message: {notif.message}")
    if notif.emetteur:
        print(f"      Émetteur: {notif.emetteur.get_full_name()}")
    print(f"      Date: {notif.date_creation}")
    if notif.donnees_contexte:
        print(f"      Contexte: {notif.donnees_contexte}")
    print()

# Notifications de modules pour Eraste
notifs_module = NotificationModule.objects.filter(
    destinataire=eraste
).order_by('-date_creation')

print(f"\n📬 NotificationModule ({notifs_module.count()}):")
for notif in notifs_module:
    lue_str = "✅ Lue" if notif.lue else "🔔 Non lue"
    print(f"   {lue_str} | {notif.type_notification}")
    print(f"      Titre: {notif.titre}")
    print(f"      Message: {notif.message}")
    if notif.emetteur:
        print(f"      Émetteur: {notif.emetteur.get_full_name()}")
    print(f"      Date: {notif.date_creation}")
    if notif.donnees_contexte:
        print(f"      Contexte: {notif.donnees_contexte}")
    print()

print("\n" + "="*60)
print("TEST MANUEL DE CRÉATION DE NOTIFICATION")
print("="*60)

# Trouver une tâche terminée par Don Dieu
tache_terminee = TacheEtape.objects.filter(
    responsable=don_dieu,
    etape__projet=projet,
    statut='TERMINEE'
).first()

if tache_terminee:
    print(f"\n✅ Tâche terminée trouvée: {tache_terminee.nom}")
    print(f"   Statut: {tache_terminee.statut}")
    print(f"   Date fin: {tache_terminee.date_fin_reelle}")
    
    # Vérifier si une notification existe déjà pour cette tâche
    notif_existante = NotificationTache.objects.filter(
        destinataire=eraste,
        tache=tache_terminee,
        type_notification='CHANGEMENT_STATUT'
    ).first()
    
    if notif_existante:
        print(f"\n✅ Notification existante trouvée:")
        print(f"   Titre: {notif_existante.titre}")
        print(f"   Date: {notif_existante.date_creation}")
    else:
        print(f"\n❌ Aucune notification trouvée pour cette tâche")
        print(f"\n🔧 Création manuelle de la notification...")
        
        # Créer la notification manuellement
        notif = NotificationTache.objects.create(
            destinataire=eraste,
            tache=tache_terminee,
            type_notification='CHANGEMENT_STATUT',
            titre=f"✅ Tâche terminée: {tache_terminee.nom}",
            message=f"{don_dieu.get_full_name()} a terminé la tâche '{tache_terminee.nom}' de l'étape '{tache_terminee.etape.type_etape.get_nom_display()}'",
            emetteur=don_dieu,
            donnees_contexte={
                'tache_id': str(tache_terminee.id),
                'type_tache': 'etape',
                'projet_id': str(projet.id),
                'etape_id': str(tache_terminee.etape.id),
                'ancien_statut': 'EN_COURS',
                'nouveau_statut': 'TERMINEE',
                'date_completion': tache_terminee.date_fin_reelle.isoformat() if tache_terminee.date_fin_reelle else timezone.now().isoformat()
            }
        )
        print(f"✅ Notification créée avec succès!")
        print(f"   ID: {notif.id}")
        print(f"   Titre: {notif.titre}")
else:
    print(f"\n⚠️  Aucune tâche terminée par Don Dieu trouvée")
    print(f"   Veuillez terminer une tâche avec Don Dieu d'abord")

print("\n" + "="*60)
print("VÉRIFICATION FINALE")
print("="*60)

# Compter les notifications non lues pour Eraste
notifs_non_lues_tache = NotificationTache.objects.filter(
    destinataire=eraste,
    lue=False
).count()

notifs_non_lues_module = NotificationModule.objects.filter(
    destinataire=eraste,
    lue=False
).count()

total_non_lues = notifs_non_lues_tache + notifs_non_lues_module

print(f"\n📊 Notifications non lues pour Eraste:")
print(f"   - Tâches: {notifs_non_lues_tache}")
print(f"   - Modules: {notifs_non_lues_module}")
print(f"   - Total: {total_non_lues}")

if total_non_lues > 0:
    print(f"\n✅ Eraste devrait voir {total_non_lues} notification(s) dans l'interface")
else:
    print(f"\n⚠️  Eraste n'a aucune notification non lue")
