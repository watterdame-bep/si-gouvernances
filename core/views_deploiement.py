"""
Vues pour la gestion des déploiements
Architecture hiérarchique: TacheEtape → Deploiement
Gouvernance et traçabilité des déploiements de projet
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction

from .models import Projet, EtapeProjet, TacheEtape, Deploiement, Utilisateur


@login_required
def gestion_deploiements_tache_view(request, projet_id, etape_id, tache_id):
    """Vue principale de gestion des déploiements d'une tâche"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        role_projet = user.get_role_sur_projet(projet)
        if not role_projet or (role_projet.nom != 'RESPONSABLE_PRINCIPAL' and not user.a_acces_projet(projet)):
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Vérifier que c'est bien l'étape DEPLOIEMENT
    if etape.type_etape.nom != 'DEPLOIEMENT':
        messages.error(request, 'Cette tâche n\'est pas dans l\'étape DEPLOIEMENT.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Vérifier que l'étape TESTS est terminée
    try:
        etape_tests = projet.etapes.get(type_etape__nom='TESTS')
        tests_valides = etape_tests.statut == 'TERMINEE'
    except EtapeProjet.DoesNotExist:
        tests_valides = False
    
    # Récupérer tous les déploiements de cette tâche
    deploiements = tache.deploiements.all().select_related(
        'responsable', 'executant', 'autorise_par', 'createur'
    ).order_by('-date_creation')
    
    # Calculer les statistiques
    total = deploiements.count()
    reussis = deploiements.filter(statut='REUSSI').count()
    echecs = deploiements.filter(statut='ECHEC').count()
    prevus = deploiements.filter(statut='PREVU').count()
    en_cours = deploiements.filter(statut='EN_COURS').count()
    
    stats = {
        'total': total,
        'reussis': reussis,
        'echecs': echecs,
        'prevus': prevus,
        'en_cours': en_cours,
        'taux_reussite': int((reussis / total) * 100) if total > 0 else 0,
    }
    
    # Permissions
    role_projet = user.get_role_sur_projet(projet)
    peut_creer = user.est_super_admin() or (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL')
    peut_autoriser = user.est_super_admin() or (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL')
    peut_executer = user.est_super_admin() or (user.role_systeme and user.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET'])
    
    # Équipe pour l'assignation
    equipe = projet.get_equipe()
    
    context = {
        'projet': projet,
        'etape': etape,
        'tache': tache,
        'deploiements': deploiements,
        'stats': stats,
        'tests_valides': tests_valides,
        'peut_creer': peut_creer,
        'peut_autoriser': peut_autoriser,
        'peut_executer': peut_executer,
        'equipe': equipe,
    }
    
    return render(request, 'core/gestion_deploiements_tache.html', context)


@login_required
def creer_deploiement_view(request, projet_id, etape_id, tache_id):
    """Créer un nouveau déploiement (GET: formulaire, POST: création)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    role_projet = user.get_role_sur_projet(projet)
    if not user.est_super_admin() and not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
        if request.method == 'POST':
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
        messages.error(request, 'Vous n\'avez pas les permissions pour créer un déploiement.')
        return redirect('gestion_deploiements_tache', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
    
    # Vérifier que TESTS est terminée
    try:
        etape_tests = projet.etapes.get(type_etape__nom='TESTS')
        tests_valides = etape_tests.statut == 'TERMINEE'
    except EtapeProjet.DoesNotExist:
        tests_valides = False
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        equipe = projet.get_equipe()
        
        context = {
            'projet': projet,
            'etape': etape,
            'tache': tache,
            'tests_valides': tests_valides,
            'equipe': equipe,
        }
        
        return render(request, 'core/creer_deploiement.html', context)
    
    # POST: Créer le déploiement
    if not tests_valides:
        messages.error(request, 'L\'étape TESTS doit être terminée avant de créer un déploiement.')
        return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
    
    try:
        # Récupérer les données
        version = request.POST.get('version', '').strip()
        environnement = request.POST.get('environnement')
        description = request.POST.get('description', '').strip()
        responsable_id = request.POST.get('responsable')
        date_prevue = request.POST.get('date_prevue')
        priorite = request.POST.get('priorite', 'NORMALE')
        
        # Validation
        if not version:
            messages.error(request, 'La version est obligatoire.')
            return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
        
        if not environnement or environnement not in ['DEV', 'TEST', 'PREPROD', 'PROD']:
            messages.error(request, 'Environnement invalide.')
            return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
        
        if not description:
            messages.error(request, 'La description est obligatoire.')
            return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
        
        if not responsable_id:
            messages.error(request, 'Le responsable est obligatoire.')
            return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
        
        responsable = get_object_or_404(Utilisateur, id=responsable_id)
        
        # Créer le déploiement
        deploiement = Deploiement.objects.create(
            tache_deploiement=tache,
            version=version,
            environnement=environnement,
            description=description,
            responsable=responsable,
            priorite=priorite,
            date_prevue=date_prevue if date_prevue else None,
            createur=user
        )
        
        messages.success(request, f'Déploiement {version} créé avec succès sur {deploiement.get_environnement_display()}.')
        return redirect('gestion_deploiements_tache', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)
        
    except Exception as e:
        messages.error(request, f'Erreur lors de la création : {str(e)}')
        return redirect('creer_deploiement', projet_id=projet.id, etape_id=etape.id, tache_id=tache.id)


@login_required
@require_http_methods(["POST"])
def autoriser_deploiement_view(request, projet_id, etape_id, tache_id, deploiement_id):
    """Autoriser un déploiement"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    deploiement = get_object_or_404(Deploiement, id=deploiement_id, tache_deploiement__etape__projet=projet)
    
    # Vérifier les permissions
    role_projet = user.get_role_sur_projet(projet)
    if not user.est_super_admin() and not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    # Vérifier qu'il peut être autorisé
    if not deploiement.peut_etre_autorise():
        return JsonResponse({
            'success': False, 
            'error': 'Ce déploiement ne peut pas être autorisé'
        })
    
    try:
        deploiement.autoriser(user)
        
        return JsonResponse({
            'success': True,
            'message': f'Déploiement {deploiement.version} autorisé',
            'autorise_par': user.get_full_name(),
            'date_autorisation': deploiement.date_autorisation.strftime('%d/%m/%Y à %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})


@login_required
@require_http_methods(["POST"])
def executer_deploiement_view(request, projet_id, etape_id, tache_id, deploiement_id):
    """Exécuter un déploiement (marquer comme réussi ou échec)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    deploiement = get_object_or_404(Deploiement, id=deploiement_id, tache_deploiement__etape__projet=projet)
    
    # Vérifier les permissions (Admin ou Développeur)
    if not user.est_super_admin() and not (user.role_systeme and user.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    # Vérifier qu'il peut être exécuté
    if not deploiement.peut_etre_execute():
        return JsonResponse({'success': False, 'error': 'Le déploiement doit être autorisé avant exécution'})
    
    try:
        resultat = request.POST.get('resultat')  # 'REUSSI' ou 'ECHEC'
        logs = request.POST.get('logs', '').strip()
        
        if resultat not in ['REUSSI', 'ECHEC']:
            return JsonResponse({'success': False, 'error': 'Résultat invalide'})
        
        with transaction.atomic():
            # Démarrer le déploiement
            if deploiement.statut == 'PREVU':
                deploiement.demarrer(user)
            
            # Marquer le résultat
            if resultat == 'REUSSI':
                deploiement.marquer_reussi(logs)
                message = f'Déploiement {deploiement.version} marqué comme réussi'
                
            else:  # ECHEC
                incident = deploiement.marquer_echec(logs, creer_incident=True)
                message = f'Déploiement {deploiement.version} marqué comme échoué'
                if incident:
                    message += '. Un incident a été créé automatiquement.'
        
        return JsonResponse({
            'success': True,
            'message': message,
            'statut': deploiement.statut
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})
