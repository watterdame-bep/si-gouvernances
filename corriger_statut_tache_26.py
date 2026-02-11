"""
Script pour corriger le statut de la tâche 26 (EN_ATTENTE → A_FAIRE)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import TacheModule

print("=" * 80)
print("CORRECTION DU STATUT DE LA TÂCHE 26")
print("=" * 80)

try:
    tache = TacheModule.objects.get(id=26)
    print(f"\n✅ Tâche trouvée: {tache.nom}")
    print(f"   Statut actuel: {tache.statut}")
    print(f"   Responsable: {tache.responsable.get_full_name() if tache.responsable else 'N/A'}")
    
    if tache.statut == 'EN_ATTENTE':
        print("\n🔧 Correction du statut EN_ATTENTE → A_FAIRE")
        tache.statut = 'A_FAIRE'
        tache.save()
        print("✅ Statut corrigé avec succès !")
        print(f"   Nouveau statut: {tache.statut}")
    else:
        print(f"\n✅ Le statut est déjà valide: {tache.statut}")
        
except TacheModule.DoesNotExist:
    print("\n❌ Tâche 26 non trouvée")

print("\n" + "=" * 80)
print("VÉRIFICATION DE TOUTES LES TÂCHES AVEC STATUT INVALIDE")
print("=" * 80)

# Vérifier toutes les tâches avec statut EN_ATTENTE
taches_invalides = TacheModule.objects.filter(statut='EN_ATTENTE')
print(f"\nNombre de tâches avec statut EN_ATTENTE: {taches_invalides.count()}")

if taches_invalides.count() > 0:
    print("\n🔧 Correction de toutes les tâches...")
    for tache in taches_invalides:
        print(f"   - Tâche {tache.id}: {tache.nom} → A_FAIRE")
        tache.statut = 'A_FAIRE'
        tache.save()
    print(f"\n✅ {taches_invalides.count()} tâche(s) corrigée(s)")
else:
    print("\n✅ Aucune tâche avec statut invalide")

print("\n" + "=" * 80)
