"""
Script pour définir une durée de 7 jours (1 semaine) pour tous les projets existants
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet

print("=" * 80)
print("DÉFINITION DE LA DURÉE POUR LES PROJETS EXISTANTS")
print("=" * 80)

# Récupérer tous les projets
tous_projets = Projet.objects.all()
print(f"\n📊 Total de projets dans la base : {tous_projets.count()}")

# Filtrer les projets sans durée
projets_sans_duree = tous_projets.filter(duree_projet__isnull=True)
print(f"📊 Projets sans durée définie : {projets_sans_duree.count()}")

if projets_sans_duree.count() == 0:
    print("\n✅ Tous les projets ont déjà une durée définie !")
else:
    print(f"\n🔧 Définition de la durée à 7 jours (1 semaine) pour {projets_sans_duree.count()} projet(s)...\n")
    
    projets_modifies = 0
    
    for projet in projets_sans_duree:
        print(f"  - {projet.nom}")
        print(f"    Client: {projet.client}")
        print(f"    Statut: {projet.statut.get_nom_display()}")
        
        # Définir la durée à 7 jours
        projet.duree_projet = 7
        projet.save()
        
        projets_modifies += 1
        print(f"    ✅ Durée définie : 7 jours\n")
    
    print("=" * 80)
    print(f"✅ {projets_modifies} projet(s) modifié(s) avec succès !")
    print("=" * 80)

# Vérification finale
print("\n📊 VÉRIFICATION FINALE")
print("-" * 80)

tous_projets_refresh = Projet.objects.all()
projets_avec_duree = tous_projets_refresh.exclude(duree_projet__isnull=True)
projets_sans_duree_final = tous_projets_refresh.filter(duree_projet__isnull=True)

print(f"Total projets : {tous_projets_refresh.count()}")
print(f"Projets avec durée : {projets_avec_duree.count()}")
print(f"Projets sans durée : {projets_sans_duree_final.count()}")

if projets_sans_duree_final.count() == 0:
    print("\n✅ Tous les projets ont maintenant une durée définie !")
else:
    print(f"\n⚠️ Il reste {projets_sans_duree_final.count()} projet(s) sans durée")

# Afficher un résumé des durées
print("\n📊 RÉSUMÉ DES DURÉES")
print("-" * 80)

for projet in tous_projets_refresh:
    duree_text = f"{projet.duree_projet} jours" if projet.duree_projet else "Non définie"
    print(f"  - {projet.nom}: {duree_text}")

print("\n" + "=" * 80)
print("✅ OPÉRATION TERMINÉE")
print("=" * 80)
print("\n💡 Les projets peuvent maintenant être démarrés par leurs responsables !")
print("   Le responsable verra le bouton 'Commencer le projet' dans l'interface.")
