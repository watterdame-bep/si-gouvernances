"""
Vues pour le système de tests V1
Interface utilisateur pour la gestion des tests, bugs et validations
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction

from .models import Projet, EtapeProjet, TacheTest, BugTest, ValidationTest, ModuleProjet, Utilisateur
from .services_tests import ServiceTests, ServiceBugs, ServiceValidation, ServiceEtapeTest


@login_required
@require_http_methods(["POST"])
def creer_cas_test_view(request, projet_id, etape_id, test_id):
    """Vue de création d'un cas de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache_test = get_object_or_404(TacheTest, id=test_id, etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_creer_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        priorite = request.POST.get('priorite', 'MOYENNE')
        donnees_entree = request.POST.get('donnees_entree', '').strip()
        preconditions = request.POST.get('preconditions', '').strip()
        etapes_execution = request.POST.get('etapes_execution', '').strip()
        resultats_attendus = request.POST.get('resultats_attendus', '').strip()
        
        # Validation
        if not nom:
            return JsonResponse({'success': False, 'error': 'Le nom du cas de test est obligatoire'})
        if not description:
            return JsonResponse({'success': False, 'error': 'La description est obligatoire'})
        if not etapes_execution:
            return JsonResponse({'success': False, 'error': 'Les étapes d\'exécution sont obligatoires'})
        if not resultats_attendus:
            return JsonResponse({'success': False, 'error': 'Les résultats attendus sont obligatoires'})
        
        # Créer le cas de test
        from .models import CasTest
        cas_test = CasTest.objects.create(
            tache_test=tache_test,
            nom=nom,
            description=description,
            priorite=priorite,
            donnees_entree=donnees_entree,
            preconditions=preconditions,
            etapes_execution=etapes_execution,
            resultats_attendus=resultats_attendus,
            createur=user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Cas de test "{cas_test.numero_cas}" créé avec succès',
            'cas_test': {
                'id': str(cas_test.id),
                'numero_cas': cas_test.numero_cas,
                'nom': cas_test.nom
            }
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors de la création : {str(e)}'})


@login_required
@require_http_methods(["POST"])
def executer_cas_test_view(request, projet_id, etape_id, cas_test_id):
    """Vue d'exécution d'un cas de test (marquer comme passé/échoué)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    from .models import CasTest
    cas_test = get_object_or_404(CasTest, id=cas_test_id, tache_test__etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_executer_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        statut = request.POST.get('statut')
        resultats_obtenus = request.POST.get('resultats_obtenus', '')
        
        if statut not in ['PASSE', 'ECHEC']:
            return JsonResponse({'success': False, 'error': 'Statut invalide'})
        
        # Marquer le cas de test
        if statut == 'PASSE':
            cas_test.marquer_comme_passe(user, resultats_obtenus)
            message = f'Cas de test "{cas_test.numero_cas}" marqué comme réussi'
        else:
            cas_test.marquer_comme_echec(user, resultats_obtenus)
            message = f'Cas de test "{cas_test.numero_cas}" marqué comme échoué'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'nouveau_statut': cas_test.statut,
            'statut_tache_test': cas_test.tache_test.statut
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors de l\'exécution : {str(e)}'})


@login_required
def details_cas_test_view(request, projet_id, etape_id, cas_test_id):
    """Vue des détails d'un cas de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    from .models import CasTest
    cas_test = get_object_or_404(CasTest, id=cas_test_id, tache_test__etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_voir_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        return JsonResponse({
            'success': True,
            'cas': {
                'id': str(cas_test.id),
                'numero_cas': cas_test.numero_cas,
                'nom': cas_test.nom,
                'description': cas_test.description,
                'priorite': cas_test.priorite,
                'priorite_display': cas_test.get_priorite_display(),
                'statut': cas_test.statut,
                'statut_display': cas_test.get_statut_display(),
                'donnees_entree': cas_test.donnees_entree,
                'preconditions': cas_test.preconditions,
                'etapes_execution': cas_test.etapes_execution,
                'resultats_attendus': cas_test.resultats_attendus,
                'resultats_obtenus': cas_test.resultats_obtenus,
                'date_creation': cas_test.date_creation.strftime('%d/%m/%Y à %H:%M'),
                'date_execution': cas_test.date_execution.strftime('%d/%m/%Y à %H:%M') if cas_test.date_execution else None,
                'executeur': cas_test.executeur.get_full_name() if cas_test.executeur else None,
                'createur': cas_test.createur.get_full_name() if cas_test.createur else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors du chargement : {str(e)}'})


# ============================================================================
# VUES EXISTANTES (conservées)
# ============================================================================

@login_required
def gestion_tests_view(request, projet_id, etape_id):
    """Vue principale de gestion des tests pour une étape"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Vérifier que c'est bien une étape de tests
    if etape.type_etape.nom != 'TESTS':
        messages.error(request, 'Cette étape n\'est pas une étape de tests.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Récupérer le dashboard complet
    dashboard = ServiceEtapeTest.get_dashboard_test(etape)
    
    # Permissions utilisateur
    peut_creer_tests = ServiceTests._peut_creer_tests(user, projet)
    peut_executer_tests = ServiceTests._peut_executer_tests(user, projet)
    peut_valider = ServiceValidation._peut_valider_tests(user, projet)
    
    context = {
        'projet': projet,
        'etape': etape,
        'dashboard': dashboard,
        'peut_creer_tests': peut_creer_tests,
        'peut_executer_tests': peut_executer_tests,
        'peut_valider': peut_valider,
    }
    
    return render(request, 'core/gestion_tests.html', context)


@login_required
def creer_test_view(request, projet_id, etape_id):
    """Vue de création d'un test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not ServiceTests._peut_creer_tests(user, projet):
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des tests.')
        return redirect('gestion_tests', projet_id=projet.id, etape_id=etape.id)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.POST.get('nom')
            description = request.POST.get('description')
            type_test = request.POST.get('type_test', 'FONCTIONNEL')
            priorite = request.POST.get('priorite', 'MOYENNE')
            scenario_test = request.POST.get('scenario_test', '')
            resultats_attendus = request.POST.get('resultats_attendus', '')
            
            # Module concerné (optionnel)
            module_id = request.POST.get('module_concerne')
            module_concerne = None
            if module_id:
                module_concerne = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
            
            # QA assigné (optionnel)
            assignee_qa_id = request.POST.get('assignee_qa')
            assignee_qa = None
            if assignee_qa_id:
                assignee_qa = get_object_or_404(Utilisateur, id=assignee_qa_id)
            
            # Créer le test
            test = ServiceTests.creer_tache_test(
                etape=etape,
                createur=user,
                nom=nom,
                description=description,
                type_test=type_test,
                priorite=priorite,
                scenario_test=scenario_test,
                resultats_attendus=resultats_attendus,
                module_concerne=module_concerne,
                assignee_qa=assignee_qa
            )
            
            messages.success(request, f'Test "{test.nom}" créé avec succès.')
            return redirect('gestion_tests', projet_id=projet.id, etape_id=etape.id)
            
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Récupérer les données pour le formulaire
    modules = projet.modules.all()
    qas = Utilisateur.objects.filter(role_systeme__nom='QA')
    
    context = {
        'projet': projet,
        'etape': etape,
        'modules': modules,
        'qas': qas,
        'TYPE_TEST_CHOICES': TacheTest.TYPE_TEST_CHOICES,
        'PRIORITE_CHOICES': TacheTest.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/creer_test.html', context)


@login_required
@require_http_methods(["POST"])
def executer_test_view(request, projet_id, etape_id, test_id):
    """Vue d'exécution d'un test (AJAX)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    test = get_object_or_404(TacheTest, id=test_id, etape=etape)
    
    try:
        # Récupérer les données
        statut_resultat = request.POST.get('statut_resultat')  # 'PASSE' ou 'ECHEC'
        resultats_obtenus = request.POST.get('resultats_obtenus', '')
        
        # Exécuter le test
        test_mis_a_jour = ServiceTests.executer_test(
            test, user, statut_resultat, resultats_obtenus
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Test {test.numero_test} exécuté avec succès',
            'nouveau_statut': test_mis_a_jour.statut,
            'date_execution': test_mis_a_jour.date_execution.strftime('%d/%m/%Y %H:%M') if test_mis_a_jour.date_execution else None
        })
        
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur inattendue : {str(e)}'})


# ============================================================================
# VUES GESTION DES BUGS
# ============================================================================

@login_required
def gestion_bugs_view(request, projet_id, etape_id):
    """Vue de gestion des bugs pour une étape de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer tous les bugs du projet
    bugs = BugTest.objects.filter(projet=projet).order_by('-date_creation')
    
    # Filtrer par statut si demandé
    statut_filtre = request.GET.get('statut')
    if statut_filtre:
        bugs = bugs.filter(statut=statut_filtre)
    
    # Filtrer par gravité si demandé
    gravite_filtre = request.GET.get('gravite')
    if gravite_filtre:
        bugs = bugs.filter(gravite=gravite_filtre)
    
    # Statistiques
    bugs_ouverts = bugs.filter(statut__in=['OUVERT', 'ASSIGNE', 'EN_COURS'])
    stats = {
        'total': bugs.count(),
        'ouverts': bugs_ouverts.count(),
        'critiques': bugs_ouverts.filter(gravite='CRITIQUE').count(),
        'majeurs': bugs_ouverts.filter(gravite='MAJEUR').count(),
        'mineurs': bugs_ouverts.filter(gravite='MINEUR').count(),
    }
    
    # Permissions
    peut_creer_bugs = ServiceBugs._peut_creer_bugs(user, projet)
    peut_assigner_bugs = ServiceBugs._peut_assigner_bugs(user, projet)
    
    context = {
        'projet': projet,
        'etape': etape,
        'bugs': bugs,
        'stats': stats,
        'peut_creer_bugs': peut_creer_bugs,
        'peut_assigner_bugs': peut_assigner_bugs,
        'STATUT_CHOICES': BugTest.STATUT_CHOICES,
        'GRAVITE_CHOICES': BugTest.GRAVITE_CHOICES,
        'statut_filtre': statut_filtre,
        'gravite_filtre': gravite_filtre,
    }
    
    return render(request, 'core/gestion_bugs.html', context)


@login_required
def creer_bug_view(request, projet_id, etape_id):
    """Vue de création d'un bug"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not ServiceBugs._peut_creer_bugs(user, projet):
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des bugs.')
        return redirect('gestion_bugs', projet_id=projet.id, etape_id=etape.id)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            tache_test_id = request.POST.get('tache_test')
            tache_test = get_object_or_404(TacheTest, id=tache_test_id, etape=etape)
            
            titre = request.POST.get('titre')
            description = request.POST.get('description')
            gravite = request.POST.get('gravite')
            etapes_reproduction = request.POST.get('etapes_reproduction')
            type_bug = request.POST.get('type_bug', 'FONCTIONNEL')
            environnement = request.POST.get('environnement', '')
            
            # Module concerné (optionnel)
            module_id = request.POST.get('module_concerne')
            module_concerne = None
            if module_id:
                module_concerne = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
            
            # Créer le bug
            bug = ServiceBugs.creer_bug(
                tache_test=tache_test,
                rapporteur=user,
                titre=titre,
                description=description,
                gravite=gravite,
                etapes_reproduction=etapes_reproduction,
                type_bug=type_bug,
                environnement=environnement,
                module_concerne=module_concerne
            )
            
            messages.success(request, f'Bug "{bug.titre}" créé avec succès.')
            return redirect('gestion_bugs', projet_id=projet.id, etape_id=etape.id)
            
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Récupérer les données pour le formulaire
    tests_echec = etape.taches_test.filter(statut='ECHEC')
    modules = projet.modules.all()
    
    context = {
        'projet': projet,
        'etape': etape,
        'tests_echec': tests_echec,
        'modules': modules,
        'GRAVITE_CHOICES': BugTest.GRAVITE_CHOICES,
        'TYPE_BUG_CHOICES': BugTest.TYPE_BUG_CHOICES,
    }
    
    return render(request, 'core/creer_bug.html', context)


# ============================================================================
# VUES VALIDATION
# ============================================================================

@login_required
def validation_test_view(request, projet_id, etape_id):
    """Vue de validation d'une étape de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer le statut de validation
    statut_validation = ServiceValidation.get_statut_validation(etape)
    
    # Dashboard complet
    dashboard = ServiceEtapeTest.get_dashboard_test(etape)
    
    # Permissions
    peut_valider = ServiceValidation._peut_valider_tests(user, projet)
    
    context = {
        'projet': projet,
        'etape': etape,
        'statut_validation': statut_validation,
        'dashboard': dashboard,
        'peut_valider': peut_valider,
    }
    
    return render(request, 'core/validation_test.html', context)


@login_required
@require_http_methods(["POST"])
def valider_etape_test_view(request, projet_id, etape_id):
    """Vue de validation effective d'une étape de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    try:
        # Récupérer les commentaires
        commentaires = request.POST.get('commentaires', '')
        conditions_specifiques = request.POST.get('conditions_specifiques', '')
        
        # Valider l'étape
        validation = ServiceValidation.valider_etape_test(
            etape, user, commentaires, conditions_specifiques
        )
        
        messages.success(request, 'Étape de test validée avec succès ! Le projet peut maintenant passer au déploiement.')
        return redirect('gestion_etapes_view', projet_id=projet.id)
        
    except (ValidationError, PermissionDenied) as e:
        messages.error(request, str(e))
        return redirect('validation_test', projet_id=projet.id, etape_id=etape.id)
    except Exception as e:
        messages.error(request, f'Erreur lors de la validation : {str(e)}')
        return redirect('validation_test', projet_id=projet.id, etape_id=etape.id)


# ============================================================================
# VUES AJAX - ACTIONS RAPIDES
# ============================================================================

@login_required
@require_http_methods(["POST"])
def assigner_bug_view(request, projet_id, bug_id):
    """Assigne un bug à un développeur (AJAX)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    bug = get_object_or_404(BugTest, id=bug_id, projet=projet)
    
    try:
        assignee_id = request.POST.get('assignee_id')
        assignee = get_object_or_404(Utilisateur, id=assignee_id)
        
        bug_mis_a_jour = ServiceBugs.assigner_bug(bug, assignee, user)
        
        return JsonResponse({
            'success': True,
            'message': f'Bug assigné à {assignee.get_full_name()}',
            'nouveau_statut': bug_mis_a_jour.statut
        })
        
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})


@login_required
@require_http_methods(["POST"])
def resoudre_bug_view(request, projet_id, bug_id):
    """Marque un bug comme résolu (AJAX)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    bug = get_object_or_404(BugTest, id=bug_id, projet=projet)
    
    try:
        resolution = request.POST.get('resolution', '')
        
        bug_mis_a_jour = ServiceBugs.resoudre_bug(bug, resolution, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Bug marqué comme résolu',
            'nouveau_statut': bug_mis_a_jour.statut
        })
        
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})


@login_required
@require_http_methods(["POST"])
def fermer_bug_view(request, projet_id, bug_id):
    """Ferme définitivement un bug (AJAX)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    bug = get_object_or_404(BugTest, id=bug_id, projet=projet)
    
    try:
        bug_mis_a_jour = ServiceBugs.fermer_bug(bug, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Bug fermé définitivement',
            'nouveau_statut': bug_mis_a_jour.statut
        })
        
    except (ValidationError, PermissionDenied) as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})


@login_required
def modifier_test_view(request, projet_id, etape_id, test_id):
    """Vue de modification d'un test (placeholder pour V2)"""
    messages.info(request, 'Fonctionnalité de modification des tests disponible en V2.')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)

# ============================================================================
# VUES POUR LA HIÉRARCHIE CASTEST
# ============================================================================

@login_required
@require_http_methods(["POST"])
def creer_cas_test_view(request, projet_id, etape_id, test_id):
    """Vue de création d'un cas de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache_test = get_object_or_404(TacheTest, id=test_id, etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_creer_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        priorite = request.POST.get('priorite', 'MOYENNE')
        donnees_entree = request.POST.get('donnees_entree', '').strip()
        preconditions = request.POST.get('preconditions', '').strip()
        etapes_execution = request.POST.get('etapes_execution', '').strip()
        resultats_attendus = request.POST.get('resultats_attendus', '').strip()
        
        # Validation
        if not nom:
            return JsonResponse({'success': False, 'error': 'Le nom du cas de test est obligatoire'})
        if not description:
            return JsonResponse({'success': False, 'error': 'La description est obligatoire'})
        if not etapes_execution:
            return JsonResponse({'success': False, 'error': 'Les étapes d\'exécution sont obligatoires'})
        if not resultats_attendus:
            return JsonResponse({'success': False, 'error': 'Les résultats attendus sont obligatoires'})
        
        # Créer le cas de test
        from .models import CasTest
        cas_test = CasTest.objects.create(
            tache_test=tache_test,
            nom=nom,
            description=description,
            priorite=priorite,
            donnees_entree=donnees_entree,
            preconditions=preconditions,
            etapes_execution=etapes_execution,
            resultats_attendus=resultats_attendus,
            createur=user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Cas de test "{cas_test.numero_cas}" créé avec succès',
            'cas_test': {
                'id': str(cas_test.id),
                'numero_cas': cas_test.numero_cas,
                'nom': cas_test.nom
            }
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors de la création : {str(e)}'})


@login_required
@require_http_methods(["POST"])
def executer_cas_test_view(request, projet_id, etape_id, cas_test_id):
    """Vue d'exécution d'un cas de test (marquer comme passé/échoué)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    from .models import CasTest
    cas_test = get_object_or_404(CasTest, id=cas_test_id, tache_test__etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_executer_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        statut = request.POST.get('statut')
        resultats_obtenus = request.POST.get('resultats_obtenus', '')
        
        if statut not in ['PASSE', 'ECHEC']:
            return JsonResponse({'success': False, 'error': 'Statut invalide'})
        
        # Marquer le cas de test
        if statut == 'PASSE':
            cas_test.marquer_comme_passe(user, resultats_obtenus)
            message = f'Cas de test "{cas_test.numero_cas}" marqué comme réussi'
        else:
            cas_test.marquer_comme_echec(user, resultats_obtenus)
            message = f'Cas de test "{cas_test.numero_cas}" marqué comme échoué'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'nouveau_statut': cas_test.statut,
            'statut_tache_test': cas_test.tache_test.statut
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors de l\'exécution : {str(e)}'})


@login_required
def details_cas_test_view(request, projet_id, etape_id, cas_test_id):
    """Vue des détails d'un cas de test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    from .models import CasTest
    cas_test = get_object_or_404(CasTest, id=cas_test_id, tache_test__etape=etape)
    
    # Vérifier les permissions
    if not ServiceTests._peut_voir_tests(user, projet):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        return JsonResponse({
            'success': True,
            'cas': {
                'id': str(cas_test.id),
                'numero_cas': cas_test.numero_cas,
                'nom': cas_test.nom,
                'description': cas_test.description,
                'priorite': cas_test.priorite,
                'priorite_display': cas_test.get_priorite_display(),
                'statut': cas_test.statut,
                'statut_display': cas_test.get_statut_display(),
                'donnees_entree': cas_test.donnees_entree,
                'preconditions': cas_test.preconditions,
                'etapes_execution': cas_test.etapes_execution,
                'resultats_attendus': cas_test.resultats_attendus,
                'resultats_obtenus': cas_test.resultats_obtenus,
                'date_creation': cas_test.date_creation.strftime('%d/%m/%Y à %H:%M'),
                'date_execution': cas_test.date_execution.strftime('%d/%m/%Y à %H:%M') if cas_test.date_execution else None,
                'executeur': cas_test.executeur.get_full_name() if cas_test.executeur else None,
                'createur': cas_test.createur.get_full_name() if cas_test.createur else None,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors du chargement : {str(e)}'})