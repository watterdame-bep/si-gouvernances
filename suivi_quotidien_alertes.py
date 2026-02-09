"""
Script de suivi quotidien du système d'alertes
À exécuter chaque matin pour vérifier que tout fonctionne
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import NotificationTache, TacheEtape, Utilisateur
from django.utils import timezone

print("=" * 80)
print("📊 SUIVI QUOTIDIEN DU SYSTÈME D'ALERTES")
print("=" * 80)
print(f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()

# 1. Vérifier les alertes créées aujourd'hui
print("🔔 1. ALERTES CRÉÉES AUJOURD'HUI")
print("-" * 80)

aujourd_hui = timezone.now().date()
alertes_aujourd_hui = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD'],
    date_creation__date=aujourd_hui
)

if alertes_aujourd_hui.exists():
    print(f"✅ {alertes_aujourd_hui.count()} alerte(s) créée(s) aujourd'hui")
    
    # Par type
    par_type = {}
    for alerte in alertes_aujourd_hui:
        type_nom = alerte.get_type_notification_display()
        par_type[type_nom] = par_type.get(type_nom, 0) + 1
    
    print("\nRépartition par type :")
    for type_nom, count in par_type.items():
        print(f"  - {type_nom}: {count}")
    
    # Par utilisateur
    print("\nRépartition par utilisateur :")
    utilisateurs = {}
    for alerte in alertes_aujourd_hui:
        user = alerte.destinataire.get_full_name()
        utilisateurs[user] = utilisateurs.get(user, 0) + 1
    
    for user, count in utilisateurs.items():
        print(f"  - {user}: {count} alerte(s)")
else:
    print("⚠️ Aucune alerte créée aujourd'hui")
    print("   Raisons possibles :")
    print("   - Aucune tâche proche de son échéance")
    print("   - La vérification n'a pas encore été exécutée (8h00)")
    print("   - Problème avec le Planificateur de tâches")

# 2. Vérifier les alertes de la semaine
print("\n📅 2. ALERTES DE LA SEMAINE")
print("-" * 80)

il_y_a_7_jours = aujourd_hui - timedelta(days=7)
alertes_semaine = NotificationTache.objects.filter(
    type_notification__in=['ALERTE_ECHEANCE', 'ALERTE_CRITIQUE', 'ALERTE_RETARD'],
    date_creation__date__gte=il_y_a_7_jours
)

print(f"Total alertes cette semaine : {alertes_semaine.count()}")

# Par jour
print("\nRépartition par jour :")
for i in range(7):
    jour = aujourd_hui - timedelta(days=i)
    alertes_jour = alertes_semaine.filter(date_creation__date=jour)
    if alertes_jour.exists():
        print(f"  - {jour.strftime('%d/%m/%Y')}: {alertes_jour.count()} alerte(s)")

# 3. Vérifier les tâches à surveiller
print("\n⏰ 3. TÂCHES À SURVEILLER")
print("-" * 80)

taches_actives = TacheEtape.objects.filter(
    statut__in=['A_FAIRE', 'EN_COURS', 'BLOQUEE']
).exclude(date_fin__isnull=True).select_related('responsable', 'etape__projet')

print(f"Total tâches actives : {taches_actives.count()}")

# Tâches par échéance
taches_retard = []
taches_aujourd_hui = []
taches_demain = []
taches_2_jours = []
taches_prochaines = []

for tache in taches_actives:
    jours_restants = (tache.date_fin - aujourd_hui).days
    
    if jours_restants < 0:
        taches_retard.append(tache)
    elif jours_restants == 0:
        taches_aujourd_hui.append(tache)
    elif jours_restants == 1:
        taches_demain.append(tache)
    elif jours_restants == 2:
        taches_2_jours.append(tache)
    elif jours_restants <= 7:
        taches_prochaines.append(tache)

print(f"\n🔴 En retard : {len(taches_retard)}")
if taches_retard:
    for tache in taches_retard[:3]:
        jours = abs((tache.date_fin - aujourd_hui).days)
        print(f"   - {tache.nom} ({jours}j de retard)")

print(f"🔴 Aujourd'hui : {len(taches_aujourd_hui)}")
if taches_aujourd_hui:
    for tache in taches_aujourd_hui[:3]:
        print(f"   - {tache.nom}")

print(f"🟠 Demain : {len(taches_demain)}")
if taches_demain:
    for tache in taches_demain[:3]:
        print(f"   - {tache.nom}")

print(f"🟡 Dans 2 jours : {len(taches_2_jours)}")
if taches_2_jours:
    for tache in taches_2_jours[:3]:
        print(f"   - {tache.nom}")

print(f"⚪ Prochains 7 jours : {len(taches_prochaines)}")

# 4. Vérifier le fichier de log
print("\n📄 4. DERNIÈRE EXÉCUTION (LOG)")
print("-" * 80)

log_file = "logs/planificateur.log"
if os.path.exists(log_file):
    # Lire les dernières lignes
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lignes = f.readlines()
    
    # Trouver la dernière exécution
    derniere_execution = None
    for ligne in reversed(lignes):
        if "Demarrage verification echeances" in ligne:
            # Extraire la date
            try:
                date_str = ligne.split('[')[1].split(']')[0]
                derniere_execution = date_str
                break
            except:
                pass
    
    if derniere_execution:
        print(f"✅ Dernière exécution : {derniere_execution}")
    else:
        print("⚠️ Aucune exécution trouvée dans le log")
    
    # Vérifier les erreurs récentes
    erreurs = [l for l in lignes[-50:] if "ERREUR" in l or "Error" in l]
    if erreurs:
        print(f"\n⚠️ {len(erreurs)} erreur(s) détectée(s) dans les 50 dernières lignes")
        for erreur in erreurs[:3]:
            print(f"   {erreur.strip()}")
    else:
        print("✅ Aucune erreur détectée dans les logs récents")
else:
    print("❌ Fichier de log non trouvé")
    print(f"   Chemin attendu : {log_file}")

# 5. Vérifier les permissions
print("\n🔒 5. VÉRIFICATION DES PERMISSIONS")
print("-" * 80)

alertes_sans_acces = 0
for alerte in alertes_aujourd_hui:
    if not alerte.destinataire.a_acces_projet(alerte.tache.etape.projet):
        alertes_sans_acces += 1

if alertes_sans_acces > 0:
    print(f"❌ {alertes_sans_acces} alerte(s) sans permission d'accès détectée(s)")
    print("   Action requise : Exécuter nettoyer_alertes_incorrectes.py")
else:
    print("✅ Toutes les alertes respectent les permissions d'accès")

# 6. Résumé et recommandations
print("\n" + "=" * 80)
print("📋 RÉSUMÉ ET RECOMMANDATIONS")
print("=" * 80)

print("\n✅ Points positifs :")
points_positifs = []

if alertes_aujourd_hui.exists():
    points_positifs.append(f"{alertes_aujourd_hui.count()} alerte(s) créée(s) aujourd'hui")

if alertes_sans_acces == 0:
    points_positifs.append("Toutes les permissions sont respectées")

if os.path.exists(log_file):
    points_positifs.append("Fichier de log accessible")

if taches_actives.exists():
    points_positifs.append(f"{taches_actives.count()} tâche(s) active(s) surveillée(s)")

if points_positifs:
    for point in points_positifs:
        print(f"  - {point}")
else:
    print("  - Aucun point positif détecté")

print("\n⚠️ Points d'attention :")
points_attention = []

if not alertes_aujourd_hui.exists() and datetime.now().hour >= 9:
    points_attention.append("Aucune alerte créée aujourd'hui (vérifier le Planificateur)")

if alertes_sans_acces > 0:
    points_attention.append(f"{alertes_sans_acces} alerte(s) sans permission")

if len(taches_retard) > 0:
    points_attention.append(f"{len(taches_retard)} tâche(s) en retard")

if not os.path.exists(log_file):
    points_attention.append("Fichier de log manquant")

if points_attention:
    for point in points_attention:
        print(f"  - {point}")
else:
    print("  - Aucun point d'attention")

print("\n💡 Actions recommandées :")
if not alertes_aujourd_hui.exists() and datetime.now().hour >= 9:
    print("  1. Vérifier le Planificateur de tâches Windows")
    print("  2. Vérifier l'historique d'exécution")
    print("  3. Tester manuellement : run_check_deadlines.bat")

if alertes_sans_acces > 0:
    print("  1. Exécuter : python nettoyer_alertes_incorrectes.py")
    print("  2. Relancer : python manage.py check_task_deadlines")

if len(taches_retard) > 5:
    print("  1. Informer les chefs de projet des tâches en retard")
    print("  2. Analyser les causes des retards")

if not points_attention:
    print("  - Aucune action requise, tout fonctionne correctement ✅")

print("\n" + "=" * 80)
print("✅ SUIVI TERMINÉ")
print("=" * 80)
print(f"\nProchaine vérification : {(aujourd_hui + timedelta(days=1)).strftime('%d/%m/%Y')} à 8h05")
