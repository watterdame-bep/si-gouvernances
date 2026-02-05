"""
Services métier pour le système de tests V1
Gestion de la logique business pour les tests, bugs et validations
"""

from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.db import transaction
from .models import TacheTest, BugTest, ValidationTest, EtapeProjet, Utilisateur


class ServiceTests:
    """Service pour la gestion des tâches de test"""
    
    @staticmethod
    def creer_tache_test(etape, createur, nom, description, type_test='FONCTIONNEL', 
                        priorite='MOYENNE', scenario_test='', resultats_attendus='',
                        module_concerne=None, assignee_qa=None):
        """
        Crée une nouvelle tâche de test
        
        Args:
            etape: EtapeProjet (doit être de type TESTS)
            createur: Utilisateur qui crée la tâche
            nom: Nom de la tâche
            description: Description détaillée
            type_test: Type de test (FONCTIONNEL, SECURITE, INTEGRATION)
            priorite: Priorité (CRITIQUE, HAUTE, MOYENNE, BASSE)
            scenario_test: Étapes du test
            resultats_attendus: Résultats attendus
            module_concerne: Module concerné (optionnel)
            assignee_qa: QA assigné (optionnel)
        
        Returns:
            TacheTest: La tâche créée
        
        Raises:
            ValidationError: Si l'étape n'est pas de type TESTS
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if etape.type_etape.nom != 'TESTS':
            raise ValidationError("Les tâches de test ne peuvent être créées que sur une étape TESTS")
        
        if not ServiceTests._peut_creer_tests(createur, etape.projet):
            raise PermissionDenied("Vous n'avez pas les permissions pour créer des tests sur ce projet")
        
        # Création
        tache = TacheTest.objects.create(
            etape=etape,
            createur=createur,
            nom=nom,
            description=description,
            type_test=type_test,
            priorite=priorite,
            scenario_test=scenario_test,
            resultats_attendus=resultats_attendus,
            module_concerne=module_concerne,
            assignee_qa=assignee_qa
        )
        
        return tache
    
    @staticmethod
    def executer_test(tache_test, executeur, statut_resultat, resultats_obtenus=''):
        """
        Exécute un test et met à jour son statut
        
        Args:
            tache_test: TacheTest à exécuter
            executeur: Utilisateur qui exécute le test
            statut_resultat: 'PASSE' ou 'ECHEC'
            resultats_obtenus: Résultats obtenus
        
        Returns:
            TacheTest: La tâche mise à jour
        
        Raises:
            ValidationError: Si le test ne peut pas être exécuté
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if not tache_test.peut_etre_executee():
            raise ValidationError(f"Le test {tache_test.numero_test} ne peut pas être exécuté dans son état actuel")
        
        if not ServiceTests._peut_executer_tests(executeur, tache_test.etape.projet):
            raise PermissionDenied("Vous n'avez pas les permissions pour exécuter des tests sur ce projet")
        
        # Exécution
        if statut_resultat == 'PASSE':
            tache_test.marquer_comme_passe(executeur, resultats_obtenus)
        elif statut_resultat == 'ECHEC':
            tache_test.marquer_comme_echec(executeur, resultats_obtenus)
        else:
            raise ValidationError("Le statut doit être 'PASSE' ou 'ECHEC'")
        
        return tache_test
    
    @staticmethod
    def _peut_creer_tests(utilisateur, projet):
        """Vérifie si l'utilisateur peut créer des tests"""
        # QA, Chef de projet ou admin peuvent créer des tests
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom in ['QA', 'CHEF_PROJET'] or
            projet.createur == utilisateur
        )
    
    @staticmethod
    def _peut_executer_tests(utilisateur, projet):
        """Vérifie si l'utilisateur peut exécuter des tests"""
        # QA peuvent exécuter des tests
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom == 'QA' or
            projet.createur == utilisateur
        )


class ServiceBugs:
    """Service pour la gestion des bugs de test"""
    
    @staticmethod
    def creer_bug(tache_test, rapporteur, titre, description, gravite, 
                  etapes_reproduction, type_bug='FONCTIONNEL', 
                  environnement='', module_concerne=None):
        """
        Crée un nouveau bug suite à un échec de test
        
        Args:
            tache_test: TacheTest qui a échoué
            rapporteur: Utilisateur (QA) qui rapporte le bug
            titre: Titre du bug
            description: Description détaillée
            gravite: CRITIQUE, MAJEUR, MINEUR
            etapes_reproduction: Étapes pour reproduire
            type_bug: Type de bug
            environnement: Environnement de test
            module_concerne: Module concerné
        
        Returns:
            BugTest: Le bug créé
        
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if not ServiceBugs._peut_creer_bugs(rapporteur, tache_test.etape.projet):
            raise PermissionDenied("Vous n'avez pas les permissions pour créer des bugs sur ce projet")
        
        # Création
        bug = BugTest.objects.create(
            tache_test=tache_test,
            projet=tache_test.etape.projet,
            rapporteur=rapporteur,
            titre=titre,
            description=description,
            gravite=gravite,
            etapes_reproduction=etapes_reproduction,
            type_bug=type_bug,
            environnement=environnement,
            module_concerne=module_concerne
        )
        
        return bug
    
    @staticmethod
    def assigner_bug(bug, assignee_dev, assigneur):
        """
        Assigne un bug à un développeur
        
        Args:
            bug: BugTest à assigner
            assignee_dev: Développeur à qui assigner
            assigneur: Utilisateur qui fait l'assignation
        
        Returns:
            BugTest: Le bug mis à jour
        
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if not ServiceBugs._peut_assigner_bugs(assigneur, bug.projet):
            raise PermissionDenied("Vous n'avez pas les permissions pour assigner des bugs")
        
        # Assignation
        bug.assigner_a_developpeur(assignee_dev)
        
        return bug
    
    @staticmethod
    def resoudre_bug(bug, resolution, resolveur):
        """
        Marque un bug comme résolu
        
        Args:
            bug: BugTest à résoudre
            resolution: Description de la résolution
            resolveur: Utilisateur qui résout
        
        Returns:
            BugTest: Le bug mis à jour
        
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if not ServiceBugs._peut_resoudre_bugs(resolveur, bug):
            raise PermissionDenied("Vous n'avez pas les permissions pour résoudre ce bug")
        
        # Résolution
        bug.marquer_comme_resolu(resolution)
        
        return bug
    
    @staticmethod
    def fermer_bug(bug, fermeur):
        """
        Ferme définitivement un bug après validation
        
        Args:
            bug: BugTest à fermer
            fermeur: Utilisateur qui ferme (QA)
        
        Returns:
            BugTest: Le bug mis à jour
        
        Raises:
            PermissionDenied: Si l'utilisateur n'a pas les permissions
            ValidationError: Si le bug n'est pas résolu
        """
        # Vérifications
        if bug.statut != 'RESOLU':
            raise ValidationError("Seuls les bugs résolus peuvent être fermés")
        
        if not ServiceBugs._peut_fermer_bugs(fermeur, bug.projet):
            raise PermissionDenied("Vous n'avez pas les permissions pour fermer des bugs")
        
        # Fermeture
        bug.fermer_bug()
        
        return bug
    
    @staticmethod
    def _peut_creer_bugs(utilisateur, projet):
        """Vérifie si l'utilisateur peut créer des bugs"""
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom in ['QA', 'CHEF_PROJET'] or
            projet.createur == utilisateur
        )
    
    @staticmethod
    def _peut_assigner_bugs(utilisateur, projet):
        """Vérifie si l'utilisateur peut assigner des bugs"""
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom in ['QA', 'CHEF_PROJET'] or
            projet.createur == utilisateur
        )
    
    @staticmethod
    def _peut_resoudre_bugs(utilisateur, bug):
        """Vérifie si l'utilisateur peut résoudre des bugs"""
        return (
            utilisateur.est_super_admin() or
            bug.assignee_dev == utilisateur or
            utilisateur.role_systeme.nom == 'CHEF_PROJET' or
            bug.projet.createur == utilisateur
        )
    
    @staticmethod
    def _peut_fermer_bugs(utilisateur, projet):
        """Vérifie si l'utilisateur peut fermer des bugs"""
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom in ['QA', 'CHEF_PROJET'] or
            projet.createur == utilisateur
        )


class ServiceValidation:
    """Service pour la validation des étapes de test"""
    
    @staticmethod
    @transaction.atomic
    def valider_etape_test(etape, validateur, commentaires='', conditions_specifiques=''):
        """
        Valide une étape de test
        
        Args:
            etape: EtapeProjet de type TESTS
            validateur: Utilisateur qui valide (Chef de projet)
            commentaires: Commentaires de validation
            conditions_specifiques: Conditions spéciales
        
        Returns:
            ValidationTest: La validation créée/mise à jour
        
        Raises:
            ValidationError: Si l'étape ne peut pas être validée
            PermissionDenied: Si l'utilisateur n'a pas les permissions
        """
        # Vérifications
        if etape.type_etape.nom != 'TESTS':
            raise ValidationError("Seules les étapes TESTS peuvent être validées")
        
        if not ServiceValidation._peut_valider_tests(validateur, etape.projet):
            raise PermissionDenied("Seuls les Chefs de projet peuvent valider les étapes de test")
        
        # Récupérer ou créer la validation
        validation, created = ValidationTest.objects.get_or_create(etape=etape)
        
        # Vérifier les critères
        if not validation.peut_etre_validee():
            raise ValidationError(
                "L'étape ne peut pas être validée :\n"
                f"- Tests passés : {validation.nb_tests_passes}/{validation.nb_tests_total}\n"
                f"- Bugs critiques ouverts : {validation.nb_bugs_critiques}"
            )
        
        # Validation
        validation.valider_etape(validateur, commentaires)
        validation.conditions_specifiques = conditions_specifiques
        validation.save()
        
        return validation
    
    @staticmethod
    def get_statut_validation(etape):
        """
        Retourne le statut de validation d'une étape
        
        Args:
            etape: EtapeProjet
        
        Returns:
            dict: Informations sur le statut de validation
        """
        try:
            validation = etape.validation_test
            validation.calculer_metriques()
            
            return {
                'peut_etre_validee': validation.peut_etre_validee(),
                'est_validee': validation.est_validee,
                'nb_tests_total': validation.nb_tests_total,
                'nb_tests_passes': validation.nb_tests_passes,
                'nb_bugs_critiques': validation.nb_bugs_critiques,
                'nb_bugs_majeurs': validation.nb_bugs_majeurs,
                'nb_bugs_mineurs': validation.nb_bugs_mineurs,
                'taux_reussite': validation.get_taux_reussite_tests(),
                'validateur': validation.validateur,
                'date_validation': validation.date_validation,
                'commentaires': validation.commentaires_validation
            }
        except ValidationTest.DoesNotExist:
            return {
                'peut_etre_validee': False,
                'est_validee': False,
                'nb_tests_total': 0,
                'nb_tests_passes': 0,
                'nb_bugs_critiques': 0,
                'nb_bugs_majeurs': 0,
                'nb_bugs_mineurs': 0,
                'taux_reussite': 0,
                'validateur': None,
                'date_validation': None,
                'commentaires': ''
            }
    
    @staticmethod
    def _peut_valider_tests(utilisateur, projet):
        """Vérifie si l'utilisateur peut valider les tests"""
        return (
            utilisateur.est_super_admin() or
            utilisateur.role_systeme.nom in ['CHEF_PROJET', 'DIRECTION'] or
            projet.createur == utilisateur
        )


class ServiceEtapeTest:
    """Service pour la gestion globale des étapes de test"""
    
    @staticmethod
    def get_dashboard_test(etape):
        """
        Retourne un dashboard complet pour une étape de test
        
        Args:
            etape: EtapeProjet de type TESTS
        
        Returns:
            dict: Dashboard avec toutes les informations
        """
        # Tests
        tests = etape.taches_test.all()
        tests_par_statut = {
            'EN_ATTENTE': tests.filter(statut='EN_ATTENTE').count(),
            'EN_COURS': tests.filter(statut='EN_COURS').count(),
            'PASSE': tests.filter(statut='PASSE').count(),
            'ECHEC': tests.filter(statut='ECHEC').count(),
            'BLOQUE': tests.filter(statut='BLOQUE').count(),
        }
        
        # Bugs
        bugs = BugTest.objects.filter(projet=etape.projet)
        bugs_ouverts = bugs.filter(statut__in=['OUVERT', 'ASSIGNE', 'EN_COURS'])
        bugs_par_gravite = {
            'CRITIQUE': bugs_ouverts.filter(gravite='CRITIQUE').count(),
            'MAJEUR': bugs_ouverts.filter(gravite='MAJEUR').count(),
            'MINEUR': bugs_ouverts.filter(gravite='MINEUR').count(),
        }
        
        # Validation
        statut_validation = ServiceValidation.get_statut_validation(etape)
        
        return {
            'etape': etape,
            'tests': {
                'total': tests.count(),
                'par_statut': tests_par_statut,
                'derniers': tests.order_by('-date_creation')[:5]
            },
            'bugs': {
                'total_ouverts': bugs_ouverts.count(),
                'par_gravite': bugs_par_gravite,
                'derniers': bugs.order_by('-date_creation')[:5]
            },
            'validation': statut_validation,
            'peut_passer_deploiement': statut_validation['est_validee']
        }