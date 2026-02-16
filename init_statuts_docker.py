"""
Script pour initialiser les statuts de projet dans Docker
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import StatutProjet

print("=" * 70)
print("INITIALISATION DES STATUTS DE PROJET")
print("=" * 70)

# Vérifier si des statuts existent déjà
statuts_existants = StatutProjet.objects.count()
print(f"\n📊 Statuts existants: {statuts_existants}")

if statuts_existants > 0:
    print("\n✅ Les statuts existent déjà:")
    for statut in StatutProjet.objects.all():
        print(f"   - {statut.nom} (ordre: {statut.ordre})")
else:
    print("\n🔄 Création des statuts par défaut...")
    
    statuts = [
        {
            'nom': StatutProjet.IDEE,
            'description': 'Projet à l\'état d\'idée',
            'couleur_affichage': '#9CA3AF',
            'ordre_affichage': 1
        },
        {
            'nom': StatutProjet.AFFECTE,
            'description': 'Projet affecté à une équipe',
            'couleur_affichage': '#3B82F6',
            'ordre_affichage': 2
        },
        {
            'nom': StatutProjet.PLANIFIE,
            'description': 'Projet planifié',
            'couleur_affichage': '#8B5CF6',
            'ordre_affichage': 3
        },
        {
            'nom': StatutProjet.EN_COURS,
            'description': 'Projet en cours de réalisation',
            'couleur_affichage': '#F59E0B',
            'ordre_affichage': 4
        },
        {
            'nom': StatutProjet.SUSPENDU,
            'description': 'Projet suspendu temporairement',
            'couleur_affichage': '#EF4444',
            'ordre_affichage': 5
        },
        {
            'nom': StatutProjet.TERMINE,
            'description': 'Projet terminé avec succès',
            'couleur_affichage': '#10B981',
            'ordre_affichage': 6
        },
        {
            'nom': StatutProjet.ARCHIVE,
            'description': 'Projet archivé',
            'couleur_affichage': '#6B7280',
            'ordre_affichage': 7
        },
    ]
    
    for statut_data in statuts:
        statut, created = StatutProjet.objects.get_or_create(
            nom=statut_data['nom'],
            defaults={
                'description': statut_data['description'],
                'couleur_affichage': statut_data['couleur_affichage'],
                'ordre_affichage': statut_data['ordre_affichage']
            }
        )
        if created:
            print(f"   ✅ Créé: {statut.get_nom_display()}")
        else:
            print(f"   ℹ️  Existe déjà: {statut.get_nom_display()}")
    
    print("\n" + "=" * 70)
    print("✅ INITIALISATION TERMINÉE")
    print("=" * 70)
    print("\nVous pouvez maintenant créer des projets!")
