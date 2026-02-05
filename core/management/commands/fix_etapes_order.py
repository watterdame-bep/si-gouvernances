from django.core.management.base import BaseCommand
from core.models import TypeEtape, EtapeProjet, Projet


class Command(BaseCommand):
    help = 'Corrige l\'ordre des étapes pour que Planification vienne en premier'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Correction de l\'ordre des étapes'))
        
        # 1. Corriger l'ordre des types d'étapes
        self.fix_types_etapes_order()
        
        # 2. Réorganiser les étapes des projets existants
        self.reorganize_project_stages()
        
        self.stdout.write(self.style.SUCCESS('🎉 Correction terminée avec succès !'))
        self.stdout.write('📊 Nouvel ordre des étapes:')
        self.stdout.write('1. Planification')
        self.stdout.write('2. Conception')
        self.stdout.write('3. Développement')
        self.stdout.write('4. Tests')
        self.stdout.write('5. Déploiement')
        self.stdout.write('6. Maintenance')

    def fix_types_etapes_order(self):
        """Corrige l'ordre standard des types d'étapes"""
        self.stdout.write('📋 Mise à jour des types d\'étapes...')
        
        ordre_correct = {
            'PLANIFICATION': 1,
            'CONCEPTION': 2,
            'DEVELOPPEMENT': 3,
            'TESTS': 4,
            'DEPLOIEMENT': 5,
            'MAINTENANCE': 6
        }
        
        for nom_type, nouvel_ordre in ordre_correct.items():
            try:
                type_etape = TypeEtape.objects.get(nom=nom_type)
                ancien_ordre = type_etape.ordre_standard
                
                if ancien_ordre != nouvel_ordre:
                    type_etape.ordre_standard = nouvel_ordre
                    type_etape.save()
                    self.stdout.write(f'✅ {type_etape.get_nom_display()}: {ancien_ordre} → {nouvel_ordre}')
                else:
                    self.stdout.write(f'✅ {type_etape.get_nom_display()}: {ancien_ordre} → {nouvel_ordre}')
                    
            except TypeEtape.DoesNotExist:
                self.stdout.write(f'⚠ Type d\'étape {nom_type} non trouvé')

    def reorganize_project_stages(self):
        """Réorganise les étapes des projets existants selon le nouvel ordre"""
        self.stdout.write('🔄 Réorganisation des étapes des projets existants...')
        
        # Mapping des types d'étapes vers leur nouvel ordre
        ordre_etapes = {
            'PLANIFICATION': 1,
            'CONCEPTION': 2,
            'DEVELOPPEMENT': 3,
            'TESTS': 4,
            'DEPLOIEMENT': 5,
            'MAINTENANCE': 6
        }
        
        projets = Projet.objects.all()
        
        for projet in projets:
            self.stdout.write(f'📁 Projet: {projet.nom}')
            
            # Récupérer toutes les étapes du projet
            etapes = list(projet.etapes.all().order_by('ordre'))
            
            if not etapes:
                continue
            
            # Réorganiser temporairement avec des ordres négatifs pour éviter les conflits
            for i, etape in enumerate(etapes):
                etape.ordre = -(i + 1000)  # Ordre temporaire négatif
                etape.save()
            
            # Maintenant, assigner les bons ordres selon le type d'étape
            for etape in etapes:
                nouveau_ordre = ordre_etapes.get(etape.type_etape.nom, 999)
                etape.ordre = nouveau_ordre
                etape.save()
                self.stdout.write(f'✅ {etape.type_etape.get_nom_display()}: réorganisé à l\'ordre {nouveau_ordre}')