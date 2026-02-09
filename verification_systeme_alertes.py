"""
Script de vérification complète du système d'alertes
À exécuter après la configuration pour s'assurer que tout fonctionne
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationTache, TacheEtape, Utilisateur, Projet
from django.utils import timezone
from datetime import timedelta

print("=" * 80)
print("VÉRIFICATION COMPLÈTE DU SYSTÈME D'ALERTES")
print("=" * 80)

# 1. Vérifier les tâches actives
print("\n📊 1. TÂCHES ACTIVES")
print("-" * 80)

taches_actives = TacheEtape.objects.filter(
    statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']
).exclude(date_fin__isnull=True)

print(f"Total tâches actives avec date de fin : {taches_actives.count()}")

if taches_actives.exists():
    print("\nDétail des tâches :")
    for tache in taches_actives[:5]:
        jours_restants = (tache.date_fin - timezone.now().date()).days
        statut_echeance = ""
        if jours_restants < 0:
            statut_echeance = f"🔴 RETARD de {abs(jours_restants)} jour(s)"
        elif jours_restants == 0:
            statut_echeance = "🔴 AUJOURD'HUI"
        elif jours_restants == 1:
            statut_echeance = "🟠 DEMAIN"
        elif jours_restants == 2:
            statut_echeance = "🟡 DANS 2 JOURS"
        else:
            statut_echeance = f"⚪ Dans {jours_restants} jours"
        
        print(f"  - {tache.nom}")
        print(f"    Projet: {tache.etape.projet.nom}")
        print(f"    Responsable: {tache.responsable.get_full_name() if tache.responsable else 'Non assigné'}")
        print(f"    Échéance: {tache.date_fin.strftime('%d/%m/%Y')} - {statut_echeance}")
        print()

# 2. Vérifier les alertes existantes
print("\n📧 2. ALERTES EXISTANTES")
print("-" * 80)

alertes = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
)

print(f"Total alertes dans la base : {alertes.count()}")

# Alertes par type
alertes_echeance = alertes.filter(type_notification='ALERTE_ECHEANCE').count()
alertes_critique = alertes.filter(type_notification='ALERTE_CRITIQUE').count()
alertes_retard = alertes.filter(type_notification='ALERTE_RETARD').count()

print(f"  - Alertes échéance (2j, 1j) : {alertes_echeance}")
print(f"  - Alertes critiques (jour J) : {alertes_critique}")
print(f"  - Alertes retard : {alertes_retard}")

# Alertes d'aujourd'hui
aujourd_hui = timezone.now().date()
alertes_aujourd_hui = alertes.filter(date_creation__date=aujourd_hui)
print(f"\nAlertes créées aujourd'hui : {alertes_aujourd_hui.count()}")

# 3. Vérifier les utilisateurs avec alertes
print("\n👥 3. UTILISATEURS AVEC ALERTES")
print("-" * 80)

utilisateurs_avec_alertes = Utilisateur.objects.filter(
    notifications_taches__type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
).distinct()

print(f"Utilisateurs ayant des alertes : {utilisateurs_avec_alertes.count()}")

for user in utilisateurs_avec_alertes:
    nb_alertes = NotificationTache.objects.filter(
        destinataire=user,
        type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD']
    ).count()
    
    nb_non_lues = NotificationTache.objects.filter(
        destinataire=user,
        type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD'],
        lue=False
    ).count()
    
    print(f"  - {user.get_full_name()} ({user.username})")
    print(f"    Total alertes : {nb_alertes} | Non lues : {nb_non_lues}")

# 4. Vérifier les permissions d'accès
print("\n🔒 4. VÉRIFICATION DES PERMISSIONS")
print("-" * 80)

alertes_avec_acces = 0
alertes_sans_acces = 0

for alerte in alertes:
    if alerte.destinataire.a_acces_projet(alerte.tache.etape.projet):
        alertes_avec_acces += 1
    else:
        alertes_sans_acces += 1
        print(f"  ⚠️ PROBLÈME : {alerte.destinataire.get_full_name()} a une alerte pour '{alerte.tache.etape.projet.nom}' sans accès")

print(f"\nAlertes avec accès projet : {alertes_avec_acces}")
print(f"Alertes SANS accès projet : {alertes_sans_acces}")

if alertes_sans_acces > 0:
    print("\n❌ ATTENTION : Des alertes incorrectes ont été détectées !")
    print("   Exécuter : python nettoyer_alertes_incorrectes.py")
else:
    print("\n✅ Toutes les alertes respectent les permissions d'accès")

# 5. Vérifier le fichier batch
print("\n📄 5. VÉRIFICATION DU FICHIER BATCH")
print("-" * 80)

batch_file = "run_check_deadlines.bat"
if os.path.exists(batch_file):
    print(f"✅ Fichier {batch_file} trouvé")
    with open(batch_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'check_task_deadlines' in content:
            print("✅ Le fichier contient la commande check_task_deadlines")
        else:
            print("❌ Le fichier ne contient pas la commande check_task_deadlines")
else:
    print(f"❌ Fichier {batch_file} non trouvé")

# 6. Résumé et recommandations
print("\n" + "=" * 80)
print("📋 RÉSUMÉ ET RECOMMANDATIONS")
print("=" * 80)

print("\n✅ Points positifs :")
if taches_actives.exists():
    print(f"  - {taches_actives.count()} tâche(s) active(s) à surveiller")
if alertes.exists():
    print(f"  - {alertes.count()} alerte(s) dans le système")
if alertes_sans_acces == 0:
    print("  - Toutes les alertes respectent les permissions")
if os.path.exists(batch_file):
    print("  - Fichier batch prêt pour le planificateur")

print("\n⚠️ Points d'attention :")
if not taches_actives.exists():
    print("  - Aucune tâche active avec date de fin")
    print("    → Créer des tâches de test pour vérifier le système")
if not alertes.exists():
    print("  - Aucune alerte dans le système")
    print("    → Exécuter : python manage.py check_task_deadlines")
if alertes_sans_acces > 0:
    print(f"  - {alertes_sans_acces} alerte(s) sans permission d'accès")
    print("    → Exécuter : python nettoyer_alertes_incorrectes.py")

print("\n📅 Prochaines étapes :")
print("  1. Configurer le Planificateur de tâches Windows")
print("     → Voir : GUIDE_PLANIFICATEUR_WINDOWS.md")
print("  2. Tester l'exécution manuelle de la tâche")
print("  3. Vérifier l'historique après la première exécution automatique")
print("  4. Supprimer les tâches de test si nécessaire")

print("\n" + "=" * 80)
print("✅ VÉRIFICATION TERMINÉE")
print("=" * 80)
