"""
Vues pour la gestion des tâches de modules
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from .models import Projet, ModuleProjet, TacheModule, Utilisateur, NotificationModule
from .utils import enregistrer_audit

@login_required
def gestion_taches_module_view(request, projet_id, module_id):
    """Vue de gestion des tâches d'un module avec l'URL complète projet/module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    
    # Vérifier les permissions d'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Vérifier les permissions de gestion des tâches du module
    peut_gerer_taches = False
    
    # Super admin peut tout faire
    if user.est_super_admin():
        peut_gerer_taches = True
    # Créateur du projet peut tout faire
    elif projet.createur == user:
        peut_gerer_taches = True
    # Responsable principal du projet peut tout faire
    else:
        affectation_projet = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        if affectation_projet:
            peut_gerer_taches = True
        else:
            # Responsable du module peut gérer les tâches
            affectation_module = module.affectations.filter(
                utilisateur=user,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).first()
            if affectation_module:
                peut_gerer_taches = True
    
    if not peut_gerer_taches:
        messages.error(request, 'Vous n\'avez pas les permissions pour gérer les tâches de ce module.')
        return redirect('gestion_modules', projet_id=projet.id)
    
    # Récupérer les tâches du module
    taches = module.taches.all().select_related('responsable').order_by('-date_creation')
    
    # Récupérer l'équipe du module pour les assignations
    equipe_module = []
    for affectation in module.affectations.filter(date_fin_affectation__isnull=True).select_related('utilisateur'):
        equipe_module.append({
            'utilisateur': affectation.utilisateur,
            'role': affectation.get_role_module_display(),
            'peut_creer_taches': affectation.peut_creer_taches,
            'peut_voir_toutes_taches': affectation.peut_voir_toutes_taches
        })
    
    # Statistiques des tâches
    stats = {
        'total_taches': taches.count(),
        'taches_en_attente': taches.filter(statut='EN_ATTENTE').count(),
        'taches_en_cours': taches.filter(statut='EN_COURS').count(),
        'taches_terminees': taches.filter(statut='TERMINEE').count(),
        'taches_bloquees': taches.filter(statut='BLOQUEE').count(),
    }
    
    # Calculer la progression
    if stats['total_taches'] > 0:
        stats['progression'] = round((stats['taches_terminees'] / stats['total_taches']) * 100, 1)
    else:
        stats['progression'] = 0
    
    context = {
        'projet': projet,
        'module': module,
        'taches': taches,
        'equipe_module': equipe_module,
        'peut_gerer_taches': peut_gerer_taches,
        'stats': stats,
        'user': user,
    }
    
    return render(request, 'core/gestion_taches_module.html', context)


@login_required
@require_http_methods(["POST"])
def creer_tache_module_nouvelle_view(request, projet_id, module_id):
    """Créer une nouvelle tâche dans un module avec permissions"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    
    # Vérifier les permissions
    peut_creer_taches = False
    
    # Super admin peut tout faire
    if user.est_super_admin():
        peut_creer_taches = True
    # Créateur du projet peut tout faire
    elif projet.createur == user:
        peut_creer_taches = True
    # Responsable principal du projet peut tout faire
    else:
        affectation_projet = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        if affectation_projet:
            peut_creer_taches = True
        else:
            # Responsable du module peut créer des tâches
            affectation_module = module.affectations.filter(
                utilisateur=user,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).first()
            if affectation_module and affectation_module.peut_creer_taches:
                peut_creer_taches = True
    
    if not peut_creer_taches:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas les permissions pour créer des tâches dans ce module.'
        })
    
    try:
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        priorite = request.POST.get('priorite', 'MOYENNE')
        responsable_id = request.POST.get('responsable_id')
        
        # Validation
        if not nom:
            return JsonResponse({
                'success': False,
                'error': 'Le nom de la tâche est obligatoire.'
            })
        
        # Vérifier que le responsable fait partie de l'équipe du module (si spécifié)
        responsable = None
        if responsable_id:
            try:
                responsable = Utilisateur.objects.get(id=responsable_id)
                # Vérifier que le responsable fait partie de l'équipe du module
                if not module.affectations.filter(
                    utilisateur=responsable,
                    date_fin_affectation__isnull=True
                ).exists():
                    return JsonResponse({
                        'success': False,
                        'error': 'Le responsable sélectionné ne fait pas partie de l\'équipe du module.'
                    })
            except Utilisateur.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Responsable invalide.'
                })
        
        # Créer la tâche
        tache = TacheModule.objects.create(
            module=module,
            nom=nom,
            description=description,
            priorite=priorite,
            responsable=responsable,
            createur=user,
            statut='EN_ATTENTE'
        )
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='CREATION_TACHE_MODULE',
            description=f'Création de la tâche "{nom}" dans le module "{module.nom}"',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': nom,
                'module_id': module.id,
                'module_nom': module.nom,
                'priorite': priorite,
                'responsable': responsable.get_full_name() if responsable else None
            }
        )
        
        # Créer une notification si un responsable est assigné
        if responsable and responsable != user:
            try:
                NotificationModule.objects.create(
                    utilisateur=responsable,
                    type_notification='TACHE_ASSIGNEE',
                    titre=f'Nouvelle tâche assignée',
                    message=f'La tâche "{nom}" vous a été assignée dans le module "{module.nom}"',
                    module=module,
                    tache_module=tache,
                    createur=user
                )
            except Exception as e:
                # Les notifications ne doivent pas faire échouer la création
                pass
        
        return JsonResponse({
            'success': True,
            'message': f'Tâche "{nom}" créée avec succès !',
            'data': {
                'tache_id': str(tache.id),
                'tache_nom': nom,
                'responsable': responsable.get_full_name() if responsable else None
            }
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la création de la tâche : {str(e)}',
            'debug': error_trace if user.est_super_admin() else None
        })


@login_required
@require_http_methods(["POST"])
def assigner_tache_module_view(request, projet_id, module_id, tache_id):
    """Assigner une tâche à un membre de l'équipe du module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    tache = get_object_or_404(TacheModule, id=tache_id, module=module)
    
    # Vérifier les permissions (même logique que pour créer)
    peut_gerer_taches = False
    
    if user.est_super_admin():
        peut_gerer_taches = True
    elif projet.createur == user:
        peut_gerer_taches = True
    else:
        affectation_projet = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        if affectation_projet:
            peut_gerer_taches = True
        else:
            affectation_module = module.affectations.filter(
                utilisateur=user,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).first()
            if affectation_module and affectation_module.peut_creer_taches:
                peut_gerer_taches = True
    
    if not peut_gerer_taches:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas les permissions pour assigner cette tâche.'
        })
    
    try:
        responsable_id = request.POST.get('responsable_id')
        
        if not responsable_id:
            return JsonResponse({
                'success': False,
                'error': 'Veuillez sélectionner un responsable.'
            })
        
        # Vérifier que le responsable fait partie de l'équipe du module
        try:
            responsable = Utilisateur.objects.get(id=responsable_id)
            if not module.affectations.filter(
                utilisateur=responsable,
                date_fin_affectation__isnull=True
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Le responsable sélectionné ne fait pas partie de l\'équipe du module.'
                })
        except Utilisateur.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Responsable invalide.'
            })
        
        # Assigner la tâche
        ancien_responsable = tache.responsable
        tache.responsable = responsable
        tache.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='ASSIGNATION_TACHE_MODULE',
            description=f'Assignation de la tâche "{tache.nom}" à {responsable.get_full_name()}',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'nouveau_responsable': responsable.get_full_name(),
                'ancien_responsable': ancien_responsable.get_full_name() if ancien_responsable else None
            }
        )
        
        # Notification
        if responsable != user:
            try:
                NotificationModule.objects.create(
                    utilisateur=responsable,
                    type_notification='TACHE_ASSIGNEE',
                    titre=f'Tâche assignée',
                    message=f'La tâche "{tache.nom}" vous a été assignée dans le module "{module.nom}"',
                    module=module,
                    tache_module=tache,
                    createur=user
                )
            except Exception:
                pass
        
        return JsonResponse({
            'success': True,
            'message': f'Tâche assignée à {responsable.get_full_name()} avec succès !'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'assignation : {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def modifier_statut_tache_module_view(request, projet_id, module_id, tache_id):
    """Modifier le statut d'une tâche de module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    tache = get_object_or_404(TacheModule, id=tache_id, module=module)
    
    # Vérifier les permissions (responsable de la tâche ou gestionnaire du module)
    peut_modifier = False
    
    if user.est_super_admin():
        peut_modifier = True
    elif projet.createur == user:
        peut_modifier = True
    elif tache.responsable == user:
        peut_modifier = True
    else:
        affectation_projet = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        if affectation_projet:
            peut_modifier = True
        else:
            affectation_module = module.affectations.filter(
                utilisateur=user,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).first()
            if affectation_module:
                peut_modifier = True
    
    if not peut_modifier:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas les permissions pour modifier cette tâche.'
        })
    
    try:
        nouveau_statut = request.POST.get('statut')
        commentaire = request.POST.get('commentaire', '').strip()
        
        if not nouveau_statut:
            return JsonResponse({
                'success': False,
                'error': 'Veuillez sélectionner un statut.'
            })
        
        # Vérifier que le statut est valide
        statuts_valides = ['EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'BLOQUEE']
        if nouveau_statut not in statuts_valides:
            return JsonResponse({
                'success': False,
                'error': 'Statut invalide.'
            })
        
        ancien_statut = tache.statut
        tache.statut = nouveau_statut
        tache.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_STATUT_TACHE_MODULE',
            description=f'Modification du statut de la tâche "{tache.nom}" : {ancien_statut} → {nouveau_statut}',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'ancien_statut': ancien_statut,
                'nouveau_statut': nouveau_statut,
                'commentaire': commentaire
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Statut modifié avec succès !'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la modification : {str(e)}'
        })