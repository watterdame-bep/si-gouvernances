#!/usr/bin/env python
"""
Script pour supprimer tous les projets en gérant les audits
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, ActionAudit

# Compter
nb_projets = Projet.objects.count()
nb_audits_projet = ActionAudit.objects.filter(projet__isnull=False).count()

print(f"Projets à supprimer: {nb_projets}")
print(f"Audits liés aux projets: {nb_audits_projet}")

if nb_projets > 0:
    # 1. Supprimer les audits liés aux projets
    if nb_audits_projet > 0:
        ActionAudit.objects.filter(projet__isnull=False).delete()
        print(f"✓ {nb_audits_projet} audit(s) supprimé(s)")
    
    # 2. Supprimer les projets
    Projet.objects.all().delete()
    print(f"✓ {nb_projets} projet(s) supprimé(s)")
    print("✓ Toutes les données liées ont été supprimées automatiquement")
else:
    print("✓ Aucun projet à supprimer")

# Vérifier
nb_restants = Projet.objects.count()
print(f"\nProjets restants: {nb_restants}")

if nb_restants == 0:
    print("\n✅ Base de données nettoyée !")
    print("Vous pouvez maintenant créer vos propres projets pour tester.")
