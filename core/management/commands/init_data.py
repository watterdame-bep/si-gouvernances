from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from core.models import RoleSysteme, RoleProjet, StatutProjet, Utilisateur, Projet, Affectation, Membre
from decimal import Decimal


class Command(BaseCommand):
    help = 'Initialise les données de base du système SI-Gouvernance JCM'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Initialisation des données de base...'))
        
        # 1. Créer les rôles système
        self.create_roles_systeme()
        
        # 2. Créer les rôles projet
        self.create_roles_projet()
        
        # 3. Créer les statuts de projet
        self.create_statuts()
        
        # 4. Créer le super admin uniquement
        self.create_super_admin()
        
        # 5. Créer les types d'étapes standard
        self.create_types_etapes()
        
        # 6. Créer quelques projets de démonstration
        self.create_demo_projects()
        
        # 7. Initialiser les étapes pour les projets existants
        self.initialize_project_stages()
        
        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée avec succès !'))

    def create_types_etapes(self):
        """Crée les types d'étapes standard"""
        from core.models import TypeEtape
        
        self.stdout.write('🔄 Création des types d\'étapes standard...')
        
        types_etapes = [
            {
                'nom': 'CONCEPTION',
                'description': 'Phase de conception et analyse des besoins',
                'ordre_standard': 1,
                'couleur': '#8B5CF6',
                'icone_emoji': '💡'
            },
            {
                'nom': 'PLANIFICATION',
                'description': 'Planification détaillée du projet',
                'ordre_standard': 2,
                'couleur': '#3B82F6',
                'icone_emoji': '📋'
            },
            {
                'nom': 'DEVELOPPEMENT',
                'description': 'Phase de développement',
                'ordre_standard': 3,
                'couleur': '#10B981',
                'icone_emoji': '⚙️'
            },
            {
                'nom': 'TESTS',
                'description': 'Phase de tests et validation',
                'ordre_standard': 4,
                'couleur': '#F59E0B',
                'icone_emoji': '🧪'
            },
            {
                'nom': 'DEPLOIEMENT',
                'description': 'Déploiement et mise en production',
                'ordre_standard': 5,
                'couleur': '#EF4444',
                'icone_emoji': '🚀'
            },
            {
                'nom': 'MAINTENANCE',
                'description': 'Maintenance et support',
                'ordre_standard': 6,
                'couleur': '#6B7280',
                'icone_emoji': '🔧'
            }
        ]
        
        for type_data in types_etapes:
            type_etape, created = TypeEtape.objects.get_or_create(
                nom=type_data['nom'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'  ✓ Type d\'étape créé: {type_etape.get_nom_display()}')

    def initialize_project_stages(self):
        """Initialise les étapes pour les projets existants"""
        self.stdout.write('🔄 Initialisation des étapes pour les projets existants...')
        
        try:
            admin = Utilisateur.objects.get(username='admin')
            projets_sans_etapes = Projet.objects.filter(etapes__isnull=True).distinct()
            
            for projet in projets_sans_etapes:
                try:
                    projet.initialiser_etapes_standard(admin)
                    self.stdout.write(f'  ✓ Étapes initialisées pour: {projet.nom}')
                except Exception as e:
                    self.stdout.write(f'  ❌ Erreur pour {projet.nom}: {str(e)}')
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Erreur lors de l\'initialisation des étapes: {e}'))

    def create_roles_systeme(self):
        """Crée les rôles système pour la connexion à l'interface"""
        roles_data = [
            {
                'nom': RoleSysteme.DEVELOPPEUR,
                'description': 'Développeur - Accès aux projets assignés et fonctionnalités de développement',
                'niveau_hierarchique': 1
            },
            {
                'nom': RoleSysteme.CHEF_PROJET,
                'description': 'Chef de projet - Gestion des projets et équipes',
                'niveau_hierarchique': 2
            },
            {
                'nom': RoleSysteme.QA,
                'description': 'Quality Assurance - Tests, validation et contrôle qualité',
                'niveau_hierarchique': 1
            },
            {
                'nom': RoleSysteme.DIRECTION,
                'description': 'Direction - Accès complet et supervision générale',
                'niveau_hierarchique': 3
            },
        ]
        
        for role_data in roles_data:
            role, created = RoleSysteme.objects.get_or_create(
                nom=role_data['nom'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'  ✓ Rôle système créé: {role.get_nom_display()}')

    def create_roles_projet(self):
        """Crée les rôles spécifiques aux projets"""
        roles_data = [
            {
                'nom': RoleProjet.RESPONSABLE_PRINCIPAL,
                'description': 'Responsable principal du projet - Gestion complète du projet et de son équipe'
            },
            {
                'nom': RoleProjet.MEMBRE,
                'description': 'Membre de l\'équipe projet - Participation aux tâches du projet'
            },
        ]
        
        for role_data in roles_data:
            role, created = RoleProjet.objects.get_or_create(
                nom=role_data['nom'],
                defaults=role_data
            )
            if created:
                self.stdout.write(f'  ✓ Rôle projet créé: {role.get_nom_display()}')

    def create_statuts(self):
        """Crée les statuts de projet"""
        statuts_data = [
            {
                'nom': StatutProjet.IDEE,
                'description': 'Projet en phase d\'idée, pas encore affecté',
                'couleur_affichage': '#6B7280',
                'ordre_affichage': 1
            },
            {
                'nom': StatutProjet.AFFECTE,
                'description': 'Projet affecté à un responsable',
                'couleur_affichage': '#3B82F6',
                'ordre_affichage': 2
            },
            {
                'nom': StatutProjet.PLANIFIE,
                'description': 'Projet planifié avec phases définies',
                'couleur_affichage': '#8B5CF6',
                'ordre_affichage': 3
            },
            {
                'nom': StatutProjet.EN_COURS,
                'description': 'Projet en cours de développement',
                'couleur_affichage': '#F59E0B',
                'ordre_affichage': 4
            },
            {
                'nom': StatutProjet.SUSPENDU,
                'description': 'Projet temporairement suspendu',
                'couleur_affichage': '#EF4444',
                'ordre_affichage': 5
            },
            {
                'nom': StatutProjet.TERMINE,
                'description': 'Projet terminé et livré',
                'couleur_affichage': '#10B981',
                'ordre_affichage': 6
            },
            {
                'nom': StatutProjet.ARCHIVE,
                'description': 'Projet archivé',
                'couleur_affichage': '#374151',
                'ordre_affichage': 7
            },
        ]
        
        for statut_data in statuts_data:
            statut, created = StatutProjet.objects.get_or_create(
                nom=statut_data['nom'],
                defaults=statut_data
            )
            if created:
                self.stdout.write(f'  ✓ Statut créé: {statut.get_nom_display()}')

    def create_super_admin(self):
        """Crée le super administrateur système"""
        super_admin_data = {
            'username': 'admin',
            'email': 'admin@jconsult.my',
            'first_name': 'Super',
            'last_name': 'Admin',
            'is_superuser': True,
            'is_staff': True,
            'taux_horaire': Decimal('200.00'),
            'telephone': '+33 1 23 45 67 89',
            'statut_actif': True,
            'role_systeme': None  # Super admin n'a pas besoin de rôle système
        }
        
        user, created = Utilisateur.objects.get_or_create(
            username='admin',
            defaults={
                **super_admin_data,
                'password': make_password('admin123')
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Super Admin créé: {user.get_full_name()} (admin/admin123)')
        else:
            self.stdout.write(f'  → Super Admin existe déjà: {user.get_full_name()}')

    def create_demo_projects(self):
        """Crée quelques projets de démonstration"""
        # Récupérer le super admin et les statuts
        try:
            admin = Utilisateur.objects.get(username='admin')
            statut_idee = StatutProjet.objects.get(nom=StatutProjet.IDEE)
            statut_affecte = StatutProjet.objects.get(nom=StatutProjet.AFFECTE)
            
            projects_data = [
                {
                    'nom': 'E-commerce BoutiquePlus 2026',
                    'description': 'Développement d\'une plateforme e-commerce complète pour BoutiquePlus SARL',
                    'client': 'BoutiquePlus SARL',
                    'budget_previsionnel': Decimal('35000.00'),
                    'statut': statut_affecte,
                    'priorite': 'HAUTE',
                    'createur': admin,
                    'commentaires': 'Projet prioritaire avec deadline serrée'
                },
                {
                    'nom': 'Application Mobile EcoShop',
                    'description': 'Application mobile pour le suivi écologique des achats',
                    'client': 'EcoShop SARL',
                    'budget_previsionnel': Decimal('25000.00'),
                    'statut': statut_idee,
                    'priorite': 'MOYENNE',
                    'createur': admin,
                    'commentaires': 'En attente de validation client'
                },
                {
                    'nom': 'Système de Gestion Documentaire',
                    'description': 'GED pour la mairie de Villeneuve',
                    'client': 'Mairie de Villeneuve',
                    'budget_previsionnel': Decimal('45000.00'),
                    'statut': statut_idee,
                    'priorite': 'BASSE',
                    'createur': admin,
                    'commentaires': 'Projet public - procédure d\'appel d\'offres'
                }
            ]
            
            for project_data in projects_data:
                projet, created = Projet.objects.get_or_create(
                    nom=project_data['nom'],
                    defaults=project_data
                )
                
                if created:
                    self.stdout.write(f'  ✓ Projet de démo créé: {projet.nom}')
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Erreur lors de la création des projets de démo: {e}'))
    def create_demo_membres(self):
        """Crée quelques membres de démonstration"""
        self.stdout.write('📋 Création des membres de démonstration...')
        
        membres_data = [
            {
                'nom': 'Dupont',
                'prenom': 'Jean',
                'email_personnel': 'jean.dupont@exemple.com',
                'telephone': '+33 1 23 45 67 89',
                'adresse': '123 Rue de la Paix, 75001 Paris',
                'poste': 'Développeur Full Stack Senior',
                'departement': 'IT / Développement',
                'niveau_experience': 'SENIOR',
                'competences_techniques': 'Python, Django, React, PostgreSQL, Docker, AWS, Git',
                'specialites': 'Architecture microservices, API REST, DevOps',
                'statut': 'ACTIF'
            },
            {
                'nom': 'Martin',
                'prenom': 'Sophie',
                'email_personnel': 'sophie.martin@exemple.com',
                'telephone': '+33 1 34 56 78 90',
                'adresse': '456 Avenue des Champs, 69000 Lyon',
                'poste': 'Chef de Projet IT',
                'departement': 'Management',
                'niveau_experience': 'EXPERT',
                'competences_techniques': 'Gestion de projet, Scrum, Kanban, JIRA, Confluence',
                'specialites': 'Transformation digitale, Agilité, Management d\'équipe',
                'statut': 'ACTIF'
            },
            {
                'nom': 'Leroy',
                'prenom': 'Pierre',
                'email_personnel': 'pierre.leroy@exemple.com',
                'telephone': '+33 1 45 67 89 01',
                'adresse': '789 Boulevard Saint-Germain, 75007 Paris',
                'poste': 'Ingénieur QA',
                'departement': 'Qualité',
                'niveau_experience': 'INTERMEDIAIRE',
                'competences_techniques': 'Tests automatisés, Selenium, Jest, Cypress, CI/CD',
                'specialites': 'Tests fonctionnels, Tests de performance, Automatisation',
                'statut': 'ACTIF'
            },
            {
                'nom': 'Dubois',
                'prenom': 'Marie',
                'email_personnel': 'marie.dubois@exemple.com',
                'telephone': '+33 1 56 78 90 12',
                'adresse': '321 Rue de Rivoli, 75004 Paris',
                'poste': 'Développeuse Frontend',
                'departement': 'IT / Développement',
                'niveau_experience': 'JUNIOR',
                'competences_techniques': 'React, Vue.js, TypeScript, HTML5, CSS3, Sass',
                'specialites': 'UI/UX, Responsive design, Accessibilité web',
                'statut': 'ACTIF'
            },
            {
                'nom': 'Moreau',
                'prenom': 'Thomas',
                'email_personnel': 'thomas.moreau@exemple.com',
                'telephone': '+33 1 67 89 01 23',
                'adresse': '654 Avenue Montaigne, 13000 Marseille',
                'poste': 'Architecte Solution',
                'departement': 'Architecture',
                'niveau_experience': 'EXPERT',
                'competences_techniques': 'Architecture cloud, Kubernetes, Microservices, Java, Spring',
                'specialites': 'Architecture distribuée, Scalabilité, Sécurité',
                'statut': 'EN_CONGE'
            }
        ]
        
        try:
            for membre_data in membres_data:
                membre, created = Membre.objects.get_or_create(
                    email_personnel=membre_data['email_personnel'],
                    defaults=membre_data
                )
                
                if created:
                    self.stdout.write(f'  ✓ Membre créé: {membre.get_nom_complet()} ({membre.poste})')
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Erreur lors de la création des membres: {e}'))