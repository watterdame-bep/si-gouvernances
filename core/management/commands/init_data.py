"""
Commande Django pour initialiser toutes les données de base
Exécutée automatiquement au démarrage de Docker
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import StatutProjet, TypeEtape


class Command(BaseCommand):
    help = 'Initialise toutes les données de base (statuts, types d\'étapes, etc.)'

    def handle(self, *args, **options):
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("INITIALISATION DES DONNÉES DE BASE"))
        self.stdout.write("=" * 70)
        
        with transaction.atomic():
            # 1. Initialiser les statuts de projet
            self.init_statuts_projet()
            
            # 2. Initialiser les types d'étapes (cycle de vie)
            self.init_types_etapes()
        
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("✅ INITIALISATION TERMINÉE"))
        self.stdout.write("=" * 70)
    
    def init_statuts_projet(self):
        """Initialise les statuts de projet"""
        self.stdout.write("\n📊 Initialisation des statuts de projet...")
        
        statuts = [
            {
                'nom': StatutProjet.IDEE,
                'description': 'Projet à l\'état d\'idée',
                'couleur_affichage': '#9CA3AF',
                'ordre_affichage': 1
            },
            {
                'nom': StatutProjet.PLANIFIE,
                'description': 'Projet planifié et prêt à démarrer',
                'couleur_affichage': '#8B5CF6',
                'ordre_affichage': 2
            },
            {
                'nom': StatutProjet.EN_COURS,
                'description': 'Projet en cours de réalisation',
                'couleur_affichage': '#F59E0B',
                'ordre_affichage': 3
            },
        ]
        
        created_count = 0
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
                self.stdout.write(f"   ✅ Créé: {statut.get_nom_display()}")
                created_count += 1
            else:
                self.stdout.write(f"   ℹ️  Existe déjà: {statut.get_nom_display()}")
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"   {created_count} statut(s) créé(s)"))
    
    def init_types_etapes(self):
        """Initialise les types d'étapes (cycle de vie par défaut)"""
        self.stdout.write("\n🔄 Initialisation des types d'étapes (cycle de vie)...")
        
        types_etapes = [
            {
                'nom': TypeEtape.PLANIFICATION,
                'description': 'Phase de planification et analyse des besoins',
                'ordre_standard': 1,
                'couleur': '#3B82F6',
                'icone_emoji': '📋'
            },
            {
                'nom': TypeEtape.CONCEPTION,
                'description': 'Phase de conception et architecture',
                'ordre_standard': 2,
                'couleur': '#8B5CF6',
                'icone_emoji': '🎨'
            },
            {
                'nom': TypeEtape.DEVELOPPEMENT,
                'description': 'Phase de développement et implémentation',
                'ordre_standard': 3,
                'couleur': '#F59E0B',
                'icone_emoji': '💻'
            },
            {
                'nom': TypeEtape.TESTS,
                'description': 'Phase de tests et validation',
                'ordre_standard': 4,
                'couleur': '#EF4444',
                'icone_emoji': '🧪'
            },
            {
                'nom': TypeEtape.DEPLOIEMENT,
                'description': 'Phase de déploiement en production',
                'ordre_standard': 5,
                'couleur': '#10B981',
                'icone_emoji': '🚀'
            },
            {
                'nom': TypeEtape.MAINTENANCE,
                'description': 'Phase de maintenance et support',
                'ordre_standard': 6,
                'couleur': '#6B7280',
                'icone_emoji': '🔧'
            },
        ]
        
        created_count = 0
        for type_data in types_etapes:
            type_etape, created = TypeEtape.objects.get_or_create(
                nom=type_data['nom'],
                defaults={
                    'description': type_data['description'],
                    'ordre_standard': type_data['ordre_standard'],
                    'couleur': type_data['couleur'],
                    'icone_emoji': type_data['icone_emoji']
                }
            )
            if created:
                self.stdout.write(f"   ✅ Créé: {type_etape.nom}")
                created_count += 1
            else:
                self.stdout.write(f"   ℹ️  Existe déjà: {type_etape.nom}")
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f"   {created_count} type(s) d'étape créé(s)"))
