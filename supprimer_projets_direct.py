#!/usr/bin/env python
"""
Script pour supprimer directement tous les projets
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet

# Compter
nb_projets = Projet.objects.count()

print(f"Projets à supprimer: {nb_projets}")

if nb_projets > 0:
    # Supprimer
    Projet.objects.all().delete()
    print(f"✓ {nb_projets} projet(s) supprimé(s)")
    print("✓ Toutes les données liées ont été supprimées automatiquement (cascade)")
else:
    print("✓ Aucun projet à supprimer")

# Vérifier
nb_restants = Projet.objects.count()
print(f"\nProjets restants: {nb_restants}")
