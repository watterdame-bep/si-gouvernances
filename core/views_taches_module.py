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
    
    # Détecter si on vient de "Mes Modules"
    from_mes_modules = request.GET.get('from') == 'mes_modules'
    
    # Vérifier les permissions d'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Vérifier les permissions de gestion des tâches du module
    peut_gerer_taches = False
    peut_creer_taches = False  # SEUL le responsable du module peut créer des tâches
    peut_modifier_taches = False  # Nouvelle variable pour la permission de modification
    est_membre_simple = False  # Nouveau flag pour identifier les membres simples
    est_responsable_module = False  # Flag pour identifier le responsable du module
    
    # Super admin peut tout faire
    if user.est_super_admin():
        peut_gerer_taches = True
        peut_creer_taches = True
        peut_modifier_taches = True
    # Créateur du projet peut tout faire
    elif projet.createur == user:
        peut_gerer_taches = True
        peut_creer_taches = True
        peut_modifier_taches = True
    # Responsable principal du projet peut tout faire
    else:
        affectation_projet = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        if affectation_projet:
            peut_gerer_taches = True
            peut_creer_taches = True
            peut_modifier_taches = True
    
    # Vérifier si l'utilisateur est responsable du module (indépendamment des permissions projet)
    affectation_module = module.affectations.filter(
        utilisateur=user,
        role_module='RESPONSABLE',
        date_fin_affectation__isnull=True
    ).first()
    
    if affectation_module:
        peut_gerer_taches = True
        peut_creer_taches = True  # SEUL le responsable peut créer
        peut_modifier_taches = True  # Responsable peut modifier toutes les tâches
        est_responsable_module = True
    else:
        # Contributeurs et consultants peuvent voir leurs tâches mais pas en créer
        affectation_membre = module.affectations.filter(
            utilisateur=user,
            date_fin_affectation__isnull=True
        ).first()
        if affectation_membre:
            peut_gerer_taches = True
            # Membre simple seulement s'il n'est pas responsable
            est_membre_simple = affectation_membre.role_module != 'RESPONSABLE'
            # Les contributeurs NE PEUVENT PAS créer de tâches
            peut_creer_taches = False
            # Membre simple peut modifier ses propres tâches
            peut_modifier_taches = False  # Sera vérifié au niveau de chaque tâche
    
    if not peut_gerer_taches:
        messages.error(request, 'Vous n\'avez pas les permissions pour gérer les tâches de ce module.')
        return redirect('mes_modules', projet_id=projet.id) if from_mes_modules else redirect('gestion_modules', projet_id=projet.id)
    
    # Récupérer les tâches du module
    # RÈGLE: Si on vient de "Mes Modules" ET qu'on n'est PAS responsable du module,
    # on ne voit que ses propres tâches (même si on est responsable du projet)
    if from_mes_modules and not est_responsable_module:
        taches = module.taches.filter(responsable=user).select_related('responsable', 'createur').order_by('-date_creation')
    else:
        # Sinon, on voit toutes les tâches du module
        taches = module.taches.all().select_related('responsable', 'createur').order_by('-date_creation')
    
    # Récupérer l'équipe du module pour les assignations
    equipe_module = []
    for affectation in module.affectations.filter(date_fin_affectation__isnull=True).select_related('utilisateur'):
        equipe_module.append({
            'utilisateur': affectation.utilisateur,
            'role': affectation.get_role_module_display(),
            'peut_creer_taches': affectation.peut_creer_taches,
            'peut_voir_toutes_taches': affectation.peut_voir_toutes_taches
        })
    
    # Statistiques des tâches (basées sur les tâches filtrées)
    stats = {
        'total_taches': taches.count(),
        'taches_en_attente': taches.filter(statut='A_FAIRE').count(),
        'taches_en_cours': taches.filter(statut='EN_COURS').count(),
        'taches_terminees': taches.filter(statut='TERMINEE').count(),
        'taches_en_pause': taches.filter(statut='EN_PAUSE').count(),
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
        'peut_creer_taches': peut_creer_taches,  # Nouvelle permission
        'peut_modifier_taches': peut_modifier_taches,  # Permission de modification
        'stats': stats,
        'user': user,
        'from_mes_modules': from_mes_modules,  # Passer le flag au template
        'est_membre_simple': est_membre_simple,  # Pour adapter l'interface
    }
    
    return render(request, 'core/gestion_taches_module.html', context)


@login_required
@require_http_methods(["POST"])
def creer_tache_module_nouvelle_view(request, projet_id, module_id):
    """Créer une nouvelle tâche dans un module avec permissions"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    
    # Vérifier si le module est clôturé
    if module.est_cloture:
        return JsonResponse({
            'success': False,
            'error': 'Impossible de créer une tâche dans un module clôturé.'
        })
    
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
            responsable=responsable,
            createur=user,
            statut='A_FAIRE'
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
                'responsable': responsable.get_full_name() if responsable else None
            }
        )
        
        # Créer une notification si un responsable est assigné
        if responsable and responsable != user:
            try:
                NotificationModule.objects.create(
                    destinataire=responsable,
                    type_notification='NOUVELLE_TACHE',
                    titre=f'Nouvelle tâche assignée',
                    message=f'La tâche "{nom}" vous a été assignée dans le module "{module.nom}"',
                    module=module,
                    emetteur=user,
                    donnees_contexte={
                        'tache_id': str(tache.id),
                        'tache_nom': nom,
                        'module_id': str(module.id),
                        'module_nom': module.nom,
                    }
                )
            except Exception as e:
                # Les notifications ne doivent pas faire échouer la création
                print(f"Erreur création notification: {e}")
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
    
    # Vérifier les permissions
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
            if affectation_module:
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
        
        # Vérifier que le responsable existe et fait partie de l'équipe
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
        
        # Créer une notification
        if responsable != user:
            try:
                NotificationModule.objects.create(
                    destinataire=responsable,
                    type_notification='NOUVELLE_TACHE',
                    titre=f'Tâche assignée',
                    message=f'La tâche "{tache.nom}" vous a été assignée dans le module "{module.nom}"',
                    module=module,
                    emetteur=user,
                    donnees_contexte={
                        'tache_id': str(tache.id),
                        'tache_nom': tache.nom,
                        'module_id': str(module.id),
                        'module_nom': module.nom,
                    }
                )
            except Exception as e:
                print(f"Erreur création notification: {e}")
                pass
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
    
    # Vérifier les permissions
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
        
        if nouveau_statut not in ['EN_ATTENTE', 'EN_COURS', 'TERMINEE', 'BLOQUEE']:
            return JsonResponse({
                'success': False,
                'error': 'Statut invalide.'
            })
        
        ancien_statut = tache.statut
        tache.statut = nouveau_statut
        tache.save()
        
        # Si la tâche est terminée, notifier le responsable du module ET le responsable du projet
        if nouveau_statut == 'TERMINEE' and ancien_statut != 'TERMINEE':
            try:
                from .models import NotificationModule
                
                # 1. Notifier le responsable du module
                affectation_responsable = module.affectations.filter(
                    role_module='RESPONSABLE',
                    date_fin_affectation__isnull=True
                ).first()
                
                if affectation_responsable and affectation_responsable.utilisateur != user:
                    NotificationModule.objects.create(
                        destinataire=affectation_responsable.utilisateur,
                        module=module,
                        type_notification='TACHE_TERMINEE',
                        titre=f'Tâche terminée: {tache.nom}',
                        message=f'✅ {user.get_full_name()} a terminé la tâche "{tache.nom}" dans le module "{module.nom}" du projet {projet.nom}',
                        emetteur=user,
                        donnees_contexte={
                            'tache_id': str(tache.id),
                            'tache_nom': tache.nom,
                            'module_id': str(module.id),
                            'module_nom': module.nom,
                            'projet_id': str(projet.id),
                            'projet_nom': projet.nom,
                        }
                    )
                
                # 2. Notifier le responsable du projet
                responsable_projet = projet.get_responsable_principal()
                if responsable_projet and responsable_projet != user:
                    # Ne pas notifier deux fois si le responsable projet est aussi responsable module
                    if not affectation_responsable or affectation_responsable.utilisateur != responsable_projet:
                        NotificationModule.objects.create(
                            destinataire=responsable_projet,
                            module=module,
                            type_notification='TACHE_TERMINEE',
                            titre=f'Tâche module terminée: {tache.nom}',
                            message=f'✅ {user.get_full_name()} a terminé la tâche "{tache.nom}" dans le module "{module.nom}" du projet {projet.nom}',
                            emetteur=user,
                            donnees_contexte={
                                'tache_id': str(tache.id),
                                'tache_nom': tache.nom,
                                'module_id': str(module.id),
                                'module_nom': module.nom,
                                'projet_id': str(projet.id),
                                'projet_nom': projet.nom,
                            }
                        )
            except Exception as e:
                print(f"Erreur création notification tâche terminée: {e}")
        
        # Notification CHANGEMENT_STATUT pour tous les changements de statut (sauf terminaison qui a déjà sa notification)
        elif ancien_statut != nouveau_statut:
            try:
                from .models import NotificationModule
                
                # Notifier le responsable de la tâche si ce n'est pas lui qui fait le changement
                if tache.responsable and tache.responsable != user:
                    ancien_statut_display = tache.get_statut_display_from_value(ancien_statut)
                    nouveau_statut_display = tache.get_statut_display_from_value(nouveau_statut)
                    
                    NotificationModule.objects.create(
                        destinataire=tache.responsable,
                        module=module,
                        type_notification='CHANGEMENT_STATUT',
                        titre=f'Changement de statut: {tache.nom}',
                        message=f'Le statut de votre tâche "{tache.nom}" a été modifié de "{ancien_statut_display}" vers "{nouveau_statut_display}" par {user.get_full_name()}',
                        emetteur=user,
                        donnees_contexte={
                            'tache_id': str(tache.id),
                            'tache_nom': tache.nom,
                            'ancien_statut': ancien_statut,
                            'nouveau_statut': nouveau_statut,
                            'ancien_statut_display': ancien_statut_display,
                            'nouveau_statut_display': nouveau_statut_display,
                            'module_id': str(module.id),
                            'module_nom': module.nom,
                            'projet_id': str(projet.id),
                            'projet_nom': projet.nom,
                        }
                    )
            except Exception as e:
                print(f"Erreur création notification changement statut: {e}")
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_STATUT_TACHE_MODULE',
            description=f'Modification du statut de la tâche "{tache.nom}" de {ancien_statut} vers {nouveau_statut}',
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
                    destinataire=responsable,
                    type_notification='NOUVELLE_TACHE',
                    titre=f'Tâche assignée',
                    message=f'La tâche "{tache.nom}" vous a été assignée dans le module "{module.nom}"',
                    module=module,
                    emetteur=user,
                    donnees_contexte={
                        'tache_id': str(tache.id),
                        'tache_nom': tache.nom,
                        'module_id': str(module.id),
                        'module_nom': module.nom,
                    }
                )
            except Exception as e:
                print(f"Erreur création notification: {e}")
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
    
    # Vérifier que le projet est démarré
    if not projet.date_debut:
        return JsonResponse({
            'success': False, 
            'error': 'Le projet n\'est pas encore démarré. Impossible de modifier le statut d\'une tâche.'
        })
    
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


@login_required
@require_http_methods(["POST"])
def mettre_a_jour_progression_tache_module_view(request, projet_id, tache_id):
    """Mettre à jour la progression d'une tâche de module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
    module = tache.module
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    # Vérifier que le projet est démarré
    if not projet.date_debut:
        return JsonResponse({
            'success': False, 
            'error': 'Le projet n\'est pas encore démarré. Impossible de mettre à jour la progression d\'une tâche.'
        })
    
    try:
        import json
        from django.utils import timezone
        
        # Récupérer le pourcentage depuis la requête
        pourcentage = int(request.POST.get('pourcentage', 0))
        
        # Valider le pourcentage
        if pourcentage < 0 or pourcentage > 100:
            return JsonResponse({'success': False, 'error': 'Le pourcentage doit être entre 0 et 100'})
        
        # RÈGLE: Seul le responsable de la tâche peut mettre à jour la progression
        if not tache.responsable:
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})
        
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut mettre à jour la progression'})
        
        # CONTRAINTE: La tâche doit être EN_COURS pour mettre à jour la progression
        if tache.statut != 'EN_COURS':
            return JsonResponse({'success': False, 'error': 'Vous devez d\'abord démarrer la tâche pour mettre à jour la progression'})
        
        # Sauvegarder l'ancien pourcentage
        ancien_pourcentage = tache.pourcentage_completion
        
        # Mettre à jour la progression
        tache.pourcentage_completion = pourcentage
        
        # Si la progression passe à 100%, marquer comme terminée
        if pourcentage == 100:
            tache.statut = 'TERMINEE'
        
        tache.save()
        
        # Récupérer le responsable du module
        responsable_module = module.affectations.filter(
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        ).first()
        
        # Notifier le responsable du module si changement significatif (tous les 25%)
        if responsable_module and responsable_module.utilisateur != user:
            # Notifier seulement aux paliers de 25%, 50%, 75%, 100%
            if pourcentage % 25 == 0 and ancien_pourcentage != pourcentage:
                # Si 100%, utiliser le message de tâche terminée
                if pourcentage == 100:
                    NotificationModule.objects.create(
                        destinataire=responsable_module.utilisateur,
                        module=module,
                        type_notification='TACHE_TERMINEE',
                        titre=f"✅ Tâche terminée: {tache.nom}",
                        message=f"{user.get_full_name()} a terminé la tâche '{tache.nom}' dans votre module '{module.nom}'",
                        emetteur=user,
                        donnees_contexte={
                            'tache_id': str(tache.id),
                            'type_tache': 'module',
                            'projet_id': str(projet.id),
                            'module_id': module.id,
                            'ancien_pourcentage': ancien_pourcentage,
                            'nouveau_pourcentage': pourcentage
                        }
                    )
                else:
                    NotificationModule.objects.create(
                        destinataire=responsable_module.utilisateur,
                        module=module,
                        type_notification='TACHE_TERMINEE',
                        titre=f"📊 Progression: {tache.nom} ({pourcentage}%)",
                        message=f"{user.get_full_name()} a mis à jour la progression de '{tache.nom}' dans votre module '{module.nom}' à {pourcentage}%",
                        emetteur=user,
                        donnees_contexte={
                            'tache_id': str(tache.id),
                            'type_tache': 'module',
                            'projet_id': str(projet.id),
                            'module_id': module.id,
                            'ancien_pourcentage': ancien_pourcentage,
                            'nouveau_pourcentage': pourcentage
                        }
                    )
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_PROGRESSION_TACHE_MODULE',
            description=f'Mise à jour de la progression de la tâche "{tache.nom}" à {pourcentage}%',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'ancien_pourcentage': ancien_pourcentage,
                'nouveau_pourcentage': pourcentage,
                'statut': tache.statut
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Progression mise à jour à {pourcentage}%',
            'nouveau_statut': tache.statut
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Erreur mise à jour progression: {error_trace}")
        
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la mise à jour : {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def demarrer_tache_module_view(request, projet_id, tache_id):
    """Démarrer une tâche de module (passer de A_FAIRE à EN_COURS)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
    module = tache.module
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        from django.utils import timezone
        
        # NOUVELLE RÈGLE: Vérifier que le projet est démarré
        if not projet.date_debut:
            return JsonResponse({
                'success': False, 
                'error': 'Le projet n\'est pas encore démarré. Impossible de démarrer une tâche.'
            })
        
        # RÈGLE: Seul le responsable de la tâche peut la démarrer
        if not tache.responsable:
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})
        
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la démarrer'})
        
        # Vérifier que la tâche est bien à faire
        if tache.statut != 'A_FAIRE':
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'est pas à faire'})
        
        # Mettre en cours
        tache.statut = 'EN_COURS'
        tache.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='DEMARRAGE_TACHE_MODULE',
            description=f'Démarrage de la tâche "{tache.nom}"',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'statut': tache.statut
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tâche démarrée avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du démarrage : {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def terminer_tache_module_view(request, projet_id, tache_id):
    """Terminer une tâche de module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
    module = tache.module
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        from django.utils import timezone
        
        # NOUVELLE RÈGLE: Vérifier que le projet est démarré
        if not projet.date_debut:
            return JsonResponse({
                'success': False, 
                'error': 'Le projet n\'est pas encore démarré. Impossible de terminer une tâche.'
            })
        
        # RÈGLE: Seul le responsable de la tâche peut la terminer
        if not tache.responsable:
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})
        
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la terminer'})
        
        # Vérifier que la tâche n'est pas déjà terminée
        if tache.statut == 'TERMINEE':
            return JsonResponse({'success': False, 'error': 'Cette tâche est déjà terminée'})
        
        # Terminer la tâche
        ancien_statut = tache.statut
        tache.statut = 'TERMINEE'
        tache.pourcentage_completion = 100
        tache.save()
        
        # Notifier UNIQUEMENT le responsable du module
        responsable_module = module.affectations.filter(
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        ).first()
        
        if responsable_module and responsable_module.utilisateur != user:
            NotificationModule.objects.create(
                destinataire=responsable_module.utilisateur,
                module=module,
                type_notification='TACHE_TERMINEE',
                titre=f"✅ Tâche terminée: {tache.nom}",
                message=f"{user.get_full_name()} a terminé la tâche '{tache.nom}' dans votre module '{module.nom}'",
                emetteur=user,
                donnees_contexte={
                    'tache_id': str(tache.id),
                    'type_tache': 'module',
                    'projet_id': str(projet.id),
                    'module_id': module.id,
                    'ancien_statut': ancien_statut
                }
            )
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='TERMINAISON_TACHE_MODULE',
            description=f'Terminaison de la tâche "{tache.nom}"',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'ancien_statut': ancien_statut,
                'nouveau_statut': 'TERMINEE'
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tâche terminée avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la terminaison : {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def mettre_en_pause_tache_module_view(request, projet_id, tache_id):
    """Mettre en pause une tâche de module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
    module = tache.module
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        # RÈGLE: Seul le responsable de la tâche peut la mettre en pause
        if not tache.responsable:
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'a pas de responsable assigné'})
        
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Seul le responsable de la tâche peut la mettre en pause'})
        
        # Vérifier que la tâche est bien en cours
        if tache.statut != 'EN_COURS':
            return JsonResponse({'success': False, 'error': 'Cette tâche n\'est pas en cours'})
        
        # Mettre en pause
        tache.statut = 'EN_PAUSE'
        tache.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='PAUSE_TACHE_MODULE',
            description=f'Mise en pause de la tâche "{tache.nom}"',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'statut': tache.statut
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Tâche mise en pause avec succès'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la mise en pause : {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def transferer_tache_module_view(request, projet_id, tache_id):
    """Transférer une tâche de module à un autre membre de l'équipe"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
    module = tache.module
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        # RÈGLE: Seul le responsable du module peut transférer une tâche
        est_responsable_module = module.affectations.filter(
            utilisateur=user,
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        ).exists()
        
        # Super admin et créateur du projet peuvent aussi transférer
        peut_transferer = user.est_super_admin() or projet.createur == user or est_responsable_module
        
        if not peut_transferer:
            return JsonResponse({
                'success': False,
                'error': 'Seul le responsable du module peut transférer une tâche'
            })
        
        # Récupérer le nouveau responsable
        nouveau_responsable_id = request.POST.get('nouveau_responsable_id')
        
        if not nouveau_responsable_id:
            return JsonResponse({
                'success': False,
                'error': 'Veuillez sélectionner un nouveau responsable'
            })
        
        # Vérifier que le nouveau responsable existe et fait partie de l'équipe du module
        try:
            nouveau_responsable = Utilisateur.objects.get(id=nouveau_responsable_id)
            
            if not module.affectations.filter(
                utilisateur=nouveau_responsable,
                date_fin_affectation__isnull=True
            ).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Le nouveau responsable doit faire partie de l\'équipe du module'
                })
        except Utilisateur.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Nouveau responsable invalide'
            })
        
        # Vérifier qu'on ne transfère pas à la même personne
        if tache.responsable and tache.responsable.id == nouveau_responsable.id:
            return JsonResponse({
                'success': False,
                'error': 'La tâche est déjà assignée à cette personne'
            })
        
        # Sauvegarder l'ancien responsable
        ancien_responsable = tache.responsable
        
        # Transférer la tâche
        tache.responsable = nouveau_responsable
        tache.save()
        
        # Créer une notification pour le nouveau responsable
        if nouveau_responsable != user:
            try:
                NotificationModule.objects.create(
                    destinataire=nouveau_responsable,
                    module=module,
                    type_notification='NOUVELLE_TACHE',
                    titre=f"📋 Tâche transférée: {tache.nom}",
                    message=f"{user.get_full_name()} vous a transféré la tâche '{tache.nom}' dans le module '{module.nom}'",
                    emetteur=user,
                    donnees_contexte={
                        'tache_id': str(tache.id),
                        'type_tache': 'module',
                        'projet_id': str(projet.id),
                        'module_id': module.id,
                        'ancien_responsable': ancien_responsable.get_full_name() if ancien_responsable else None
                    }
                )
            except Exception as e:
                print(f"Erreur création notification transfert: {e}")
        
        # Notifier l'ancien responsable si différent de l'utilisateur actuel
        if ancien_responsable and ancien_responsable != user and ancien_responsable != nouveau_responsable:
            try:
                NotificationModule.objects.create(
                    destinataire=ancien_responsable,
                    module=module,
                    type_notification='TACHE_TERMINEE',
                    titre=f"🔄 Tâche retirée: {tache.nom}",
                    message=f"{user.get_full_name()} a transféré votre tâche '{tache.nom}' à {nouveau_responsable.get_full_name()}",
                    emetteur=user,
                    donnees_contexte={
                        'tache_id': str(tache.id),
                        'type_tache': 'module',
                        'projet_id': str(projet.id),
                        'module_id': module.id,
                        'nouveau_responsable': nouveau_responsable.get_full_name()
                    }
                )
            except Exception as e:
                print(f"Erreur création notification ancien responsable: {e}")
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='TRANSFERT_TACHE_MODULE',
            description=f'Transfert de la tâche "{tache.nom}" de {ancien_responsable.get_full_name() if ancien_responsable else "Non assignée"} vers {nouveau_responsable.get_full_name()}',
            projet=projet,
            request=request,
            donnees_apres={
                'tache_id': str(tache.id),
                'tache_nom': tache.nom,
                'ancien_responsable': ancien_responsable.get_full_name() if ancien_responsable else None,
                'nouveau_responsable': nouveau_responsable.get_full_name(),
                'module_id': module.id,
                'module_nom': module.nom
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Tâche transférée à {nouveau_responsable.get_full_name()} avec succès'
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Erreur transfert tâche: {error_trace}")
        
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du transfert : {str(e)}'
        })
