import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, ModuleProjet, TacheModule, AffectationModule, NotificationModule, Utilisateur

print("=" * 80)
print("DIAGNOSTIC NOTIFICATION TÂCHE MODULE")
print("=" * 80)

# 1. Trouver le projet "Gestion de Stock"
try:
    projet = Projet.objects.get(nom__iexact="GESTION STOCK")
    print(f"\n✅ Projet trouvé: {projet.nom} (ID: {projet.id})")
    print(f"   Responsable principal: {projet.get_responsable_principal()}")
except Projet.DoesNotExist:
    print("\n❌ Projet 'GESTION STOCK' non trouvé")
    print("\nProjets disponibles:")
    for p in Projet.objects.all():
        print(f"   - {p.nom}")
    exit()

# 2. Trouver le module "Authentification"
modules = ModuleProjet.objects.filter(projet=projet, nom__icontains="authentification")
if not modules.exists():
    print("\n❌ Module 'Authentification' non trouvé")
    print("\nModules disponibles pour ce projet:")
    for m in ModuleProjet.objects.filter(projet=projet):
        print(f"   - {m.nom} (ID: {m.id})")
    exit()
elif modules.count() > 1:
    print(f"\n⚠️  Plusieurs modules 'Authentification' trouvés:")
    for m in modules:
        print(f"   - {m.nom} (ID: {m.id})")
    module = modules.first()
    print(f"\n   Utilisation du premier: {module.nom}")
else:
    module = modules.first()
    print(f"\n✅ Module trouvé: {module.nom} (ID: {module.id})")

# 3. Vérifier les affectations du module
print(f"\n📋 Affectations du module '{module.nom}':")
affectations = AffectationModule.objects.filter(
    module=module,
    date_fin_affectation__isnull=True
)

if not affectations.exists():
    print("   ❌ Aucune affectation active trouvée")
else:
    for aff in affectations:
        print(f"   - {aff.utilisateur.get_full_name()} : {aff.role_module}")

# 4. Chercher le responsable du module
responsable_module = AffectationModule.objects.filter(
    module=module,
    role_module='RESPONSABLE',
    date_fin_affectation__isnull=True
).first()

if responsable_module:
    print(f"\n✅ Responsable du module: {responsable_module.utilisateur.get_full_name()}")
else:
    print(f"\n❌ Aucun responsable assigné au module")
    print("\n   Rôles disponibles dans AffectationModule:")
    for choice in AffectationModule._meta.get_field('role_module').choices:
        print(f"      - {choice[0]}: {choice[1]}")

# 5. Vérifier les tâches du module
print(f"\n📝 Tâches du module '{module.nom}':")
taches = TacheModule.objects.filter(module=module)

if not taches.exists():
    print("   ❌ Aucune tâche trouvée")
else:
    for tache in taches:
        print(f"   - {tache.nom} : {tache.statut}")
        if tache.statut == 'TERMINEE':
            print(f"     → Terminée le: {tache.date_modification}")

# 6. Vérifier les notifications existantes
print(f"\n🔔 Notifications pour le module '{module.nom}':")
notifications = NotificationModule.objects.filter(module=module).order_by('-date_creation')

if not notifications.exists():
    print("   ❌ Aucune notification trouvée")
else:
    for notif in notifications[:5]:  # Dernières 5
        print(f"   - {notif.date_creation.strftime('%d/%m/%Y %H:%M')} : {notif.titre}")
        print(f"     Destinataire: {notif.destinataire.get_full_name()}")
        print(f"     Type: {notif.type_notification}")
        print(f"     Lue: {'Oui' if notif.lue else 'Non'}")

# 7. Vérifier le responsable du projet
responsable_projet = projet.get_responsable_principal()
print(f"\n👤 Responsable du projet: {responsable_projet.get_full_name() if responsable_projet else 'Aucun'}")

# 8. Résumé du diagnostic
print("\n" + "=" * 80)
print("RÉSUMÉ DU DIAGNOSTIC")
print("=" * 80)

problemes = []

if not responsable_module:
    problemes.append("❌ Aucun responsable assigné au module avec role_module='RESPONSABLE'")

if not responsable_projet:
    problemes.append("❌ Aucun responsable principal pour le projet")

if not taches.filter(statut='TERMINEE').exists():
    problemes.append("⚠️  Aucune tâche terminée trouvée")

if not notifications.exists():
    problemes.append("❌ Aucune notification créée pour ce module")

if problemes:
    print("\n🔴 PROBLÈMES DÉTECTÉS:")
    for p in problemes:
        print(f"   {p}")
else:
    print("\n✅ Tout semble correct")

# 9. Suggestion de correction
if not responsable_module:
    print("\n💡 SOLUTION:")
    print("   Le module n'a pas de responsable avec role_module='RESPONSABLE'")
    print("   Vérifiez que le champ role_module utilise bien la valeur 'RESPONSABLE'")
    print("\n   Pour corriger, exécutez:")
    print(f"   python manage.py shell")
    print(f"   >>> from core.models import AffectationModule")
    print(f"   >>> aff = AffectationModule.objects.filter(module_id='{module.id}').first()")
    print(f"   >>> aff.role_module = 'RESPONSABLE'")
    print(f"   >>> aff.save()")

print("\n" + "=" * 80)
