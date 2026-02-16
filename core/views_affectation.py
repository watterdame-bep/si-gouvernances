"""
Vues spécialisées pour l'affectation de modules
Fichier séparé pour éviter les problèmes de cache
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Utilisateur, Projet, ModuleProjet
from .utils import enregistrer_audit


@login_required
@require_http_methods(["POST"])
def affecter_module_nouveau(request, projet_id, module_id):
    """Nouvelle vue d'affectation de module - Approche fraîche et moderne"""
    user = request.user
    
    try:
        # Import dynamique du modèle pour éviter les problèmes
        from django.apps import apps
        AffectationModule = apps.get_model('core', 'AffectationModule')
        
        # Récupération des objets de base
        projet = get_object_or_404(Projet, id=projet_id)
        module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
        
        # Vérification des permissions - SEULEMENT responsable du module et responsable du projet
        can_manage = (
            user.est_super_admin() or 
            projet.createur == user or
            projet.affectations.filter(
                utilisateur=user, 
                est_responsable_principal=True,
                date_fin__isnull=True
            ).exists() or
            # SEULEMENT le responsable du module (pas les contributeurs)
            AffectationModule.objects.filter(
                module=module,
                utilisateur=user,
                role_module='RESPONSABLE',  # SEULEMENT RESPONSABLE
                date_fin_affectation__isnull=True
            ).exists()
        )
        
        if not can_manage:
            return JsonResponse({
                'success': False, 
                'error': 'Vous n\'avez pas les permissions pour affecter des modules.',
                'type': 'permission'
            })
        
        # Récupération des données du formulaire
        utilisateur_id = request.POST.get('utilisateur_id')
        role_module = request.POST.get('role_module', 'CONTRIBUTEUR')
        
        if not utilisateur_id:
            return JsonResponse({
                'success': False, 
                'error': 'Veuillez sélectionner un membre de l\'équipe.',
                'type': 'validation'
            })
        
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
        
        # Vérifier que l'utilisateur fait partie de l'équipe du projet
        if not projet.affectations.filter(utilisateur=utilisateur, date_fin__isnull=True).exists():
            return JsonResponse({
                'success': False, 
                'error': f'{utilisateur.get_full_name()} doit d\'abord être membre de l\'équipe du projet.',
                'type': 'validation'
            })
        
        # Vérifier les affectations existantes
        affectations_existantes = AffectationModule.objects.filter(
            module=module,
            date_fin_affectation__isnull=True
        )
        
        affectation_existante = affectations_existantes.filter(utilisateur=utilisateur).first()
        
        if affectation_existante:
            return JsonResponse({
                'success': False, 
                'error': f'{utilisateur.get_full_name()} est déjà affecté à ce module.',
                'type': 'duplicate'
            })
        
        # NOUVELLE VALIDATION: Vérifier qu'un responsable est nommé en premier
        if not affectations_existantes.exists() and role_module != 'RESPONSABLE':
            return JsonResponse({
                'success': False, 
                'error': 'Le premier membre affecté à un module doit être le responsable. Veuillez sélectionner le rôle "Responsable" pour cette première affectation.',
                'type': 'validation',
                'action_required': 'select_responsable'
            })
        
        # Vérifier qu'il n'y a pas déjà un responsable si on veut affecter un responsable
        if role_module == 'RESPONSABLE':
            responsable_existant = affectations_existantes.filter(role_module='RESPONSABLE').first()
            
            if responsable_existant:
                return JsonResponse({
                    'success': False, 
                    'error': f'Le module a déjà un responsable : {responsable_existant.utilisateur.get_full_name()}. Un seul responsable par module est autorisé.',
                    'type': 'validation'
                })
        
        # Si c'est un contributeur et qu'il n'y a pas de responsable, erreur
        if role_module == 'CONTRIBUTEUR' and not affectations_existantes.filter(role_module='RESPONSABLE').exists():
            return JsonResponse({
                'success': False, 
                'error': 'Impossible d\'affecter un contributeur sans responsable. Veuillez d\'abord nommer un responsable pour ce module.',
                'type': 'validation',
                'action_required': 'need_responsable'
            })
        
        # Configuration des permissions selon le rôle
        permissions = {
            'RESPONSABLE': {
                'peut_creer_taches': True,
                'peut_voir_toutes_taches': True
            },
            'CONTRIBUTEUR': {
                'peut_creer_taches': False,
                'peut_voir_toutes_taches': False
            }
        }
        
        role_permissions = permissions.get(role_module, permissions['CONTRIBUTEUR'])
        
        # Créer la nouvelle affectation
        nouvelle_affectation = AffectationModule.objects.create(
            module=module,
            utilisateur=utilisateur,
            role_module=role_module,
            peut_creer_taches=role_permissions['peut_creer_taches'],
            peut_voir_toutes_taches=role_permissions['peut_voir_toutes_taches'],
            affecte_par=user
        )
        
        # Enregistrer l'audit
        enregistrer_audit(
            utilisateur=user,
            type_action='AFFECTATION_MODULE',
            description=f'Affectation de {utilisateur.get_full_name()} au module "{module.nom}" avec le rôle {role_module}',
            projet=projet,
            donnees_apres={
                'module_id': module.id,
                'module_nom': module.nom,
                'utilisateur_id': str(utilisateur.id),
                'utilisateur_nom': utilisateur.get_full_name(),
                'role': role_module,
                'permissions': role_permissions
            },
            request=request
        )
        
        # Créer les notifications
        try:
            from .utils import creer_notification_affectation_module, envoyer_notification_affectation_module
            
            # Notification in-app
            creer_notification_affectation_module(module, [nouvelle_affectation], user)
            
            # Notification par email
            envoyer_notification_affectation_module(module, [nouvelle_affectation], user, request)
            
        except Exception as e:
            # Les notifications ne doivent pas faire échouer l'affectation
            pass
        
        # Message de succès
        messages.success(
            request, 
            f'✅ {utilisateur.get_full_name()} a été affecté au module "{module.nom}" avec le rôle {role_module}.'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'{utilisateur.get_full_name()} affecté avec succès !',
            'data': {
                'affectation_id': nouvelle_affectation.id,
                'utilisateur': {
                    'id': str(utilisateur.id),
                    'nom': utilisateur.get_full_name(),
                    'initiales': f"{utilisateur.first_name[0]}{utilisateur.last_name[0]}" if utilisateur.first_name and utilisateur.last_name else "??"
                },
                'role': {
                    'code': role_module,
                    'libelle': nouvelle_affectation.get_role_module_display()
                },
                'permissions': role_permissions,
                'module': {
                    'id': module.id,
                    'nom': module.nom
                }
            }
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Une erreur inattendue s\'est produite : {str(e)}',
            'type': 'system',
            'debug': error_trace if request.user.est_super_admin() else None
        })

@login_required
@require_http_methods(["GET"])
def get_equipe_module_view(request, projet_id, module_id):
    """API endpoint pour récupérer l'équipe complète d'un module"""
    try:
        from django.apps import apps
        
        # Récupérer les modèles
        Projet = apps.get_model('core', 'Projet')
        ModuleProjet = apps.get_model('core', 'ModuleProjet')
        AffectationModule = apps.get_model('core', 'AffectationModule')
        
        # Vérifier les permissions
        projet = get_object_or_404(Projet, id=projet_id)
        module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
        
        user = request.user
        if not user.est_super_admin():
            # Vérifier que l'utilisateur fait partie du projet
            if not projet.affectations.filter(utilisateur=user, date_fin__isnull=True).exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Vous n\'avez pas accès à ce projet'
                })
        
        # Récupérer toutes les affectations actives du module
        affectations = AffectationModule.objects.filter(
            module=module,
            date_fin_affectation__isnull=True
        ).select_related('utilisateur').order_by('role_module', 'utilisateur__first_name')
        
        # Construire la réponse
        equipe_data = []
        for affectation in affectations:
            try:
                utilisateur = affectation.utilisateur
                equipe_data.append({
                    'id': str(affectation.id),
                    'utilisateur': {
                        'id': str(utilisateur.id),
                        'nom': utilisateur.get_full_name(),
                        'email': utilisateur.email,
                        'initiales': f"{utilisateur.first_name[0].upper()}{utilisateur.last_name[0].upper()}" if utilisateur.first_name and utilisateur.last_name else "??",
                    },
                    'role_module': affectation.role_module,
                    'role_display': affectation.get_role_module_display(),
                    'date_affectation': affectation.date_affectation.strftime('%d/%m/%Y'),
                    'permissions': {
                        'peut_creer_taches': affectation.peut_creer_taches,
                        'peut_voir_toutes_taches': affectation.peut_voir_toutes_taches,
                    }
                })
            except Exception as e:
                # Ignorer les affectations avec des utilisateurs invalides
                continue
        
        return JsonResponse({
            'success': True,
            'data': {
                'module': {
                    'id': module.id,
                    'nom': module.nom,
                    'description': module.description,
                },
                'equipe': equipe_data,
                'total_membres': len(equipe_data),
                'responsables': [m for m in equipe_data if m['role_module'] == 'RESPONSABLE'],
                'contributeurs': [m for m in equipe_data if m['role_module'] == 'CONTRIBUTEUR'],
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la récupération de l\'équipe: {str(e)}',
            'debug': {
                'traceback': traceback.format_exc(),
                'module_id': module_id,
                'projet_id': str(projet_id)
            }
        })

@login_required
@require_http_methods(["POST"])
def retirer_membre_module_view(request, projet_id, module_id):
    """Retirer un membre d'un module - Permissions: Responsable du module ou responsable du projet"""
    try:
        from django.apps import apps
        
        # Récupérer les modèles
        Projet = apps.get_model('core', 'Projet')
        ModuleProjet = apps.get_model('core', 'ModuleProjet')
        AffectationModule = apps.get_model('core', 'AffectationModule')
        
        # Vérifier les objets de base
        projet = get_object_or_404(Projet, id=projet_id)
        module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
        
        user = request.user
        
        # Vérifier les permissions - SEULEMENT responsable du module et responsable du projet
        can_remove = False
        
        # 1. Super admin peut toujours retirer
        if user.est_super_admin():
            can_remove = True
        
        # 2. Responsable principal du projet peut retirer
        elif projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).exists():
            can_remove = True
        
        # 3. SEULEMENT le responsable du module peut retirer (pas les contributeurs)
        elif AffectationModule.objects.filter(
            module=module,
            utilisateur=user,
            role_module='RESPONSABLE',  # SEULEMENT RESPONSABLE
            date_fin_affectation__isnull=True
        ).exists():
            can_remove = True
        
        if not can_remove:
            return JsonResponse({
                'success': False,
                'error': 'Vous n\'avez pas les permissions pour retirer des membres de ce module.',
                'type': 'permission'
            })
        
        # Récupérer l'ID de l'affectation à retirer
        affectation_id = request.POST.get('affectation_id')
        if not affectation_id:
            return JsonResponse({
                'success': False,
                'error': 'ID d\'affectation manquant.',
                'type': 'validation'
            })
        
        # Récupérer l'affectation
        try:
            affectation = AffectationModule.objects.get(
                id=affectation_id,
                module=module,
                date_fin_affectation__isnull=True
            )
        except AffectationModule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Affectation non trouvée ou déjà terminée.',
                'type': 'validation'
            })
        
        # Vérifier qu'on ne retire pas soi-même si on est le seul responsable
        if (affectation.utilisateur == user and 
            affectation.role_module == 'RESPONSABLE' and
            AffectationModule.objects.filter(
                module=module,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).count() == 1):
            return JsonResponse({
                'success': False,
                'error': 'Vous ne pouvez pas vous retirer si vous êtes le seul responsable du module.',
                'type': 'validation'
            })
        
        # Sauvegarder les informations pour l'audit
        utilisateur_retire = affectation.utilisateur
        role_retire = affectation.get_role_module_display()
        
        # Terminer l'affectation
        affectation.terminer_affectation()
        
        # Enregistrer l'audit
        from .utils import enregistrer_audit
        enregistrer_audit(
            utilisateur=user,
            type_action='RETRAIT_MODULE',
            description=f'Retrait de {utilisateur_retire.get_full_name()} du module "{module.nom}" (rôle: {role_retire})',
            projet=projet,
            donnees_avant={
                'module_id': module.id,
                'module_nom': module.nom,
                'utilisateur_id': str(utilisateur_retire.id),
                'utilisateur_nom': utilisateur_retire.get_full_name(),
                'role': affectation.role_module,
                'date_affectation': affectation.date_affectation.isoformat()
            },
            donnees_apres={
                'date_fin_affectation': affectation.date_fin_affectation.isoformat(),
                'retire_par': user.get_full_name()
            },
            request=request
        )
        
        # Créer une notification pour l'utilisateur retiré (si ce n'est pas lui-même)
        if utilisateur_retire != user:
            try:
                from .utils import creer_notification_retrait_module
                creer_notification_retrait_module(module, affectation, user)
            except Exception as e:
                # Les notifications ne doivent pas faire échouer l'opération
                pass
        
        return JsonResponse({
            'success': True,
            'message': f'{utilisateur_retire.get_full_name()} a été retiré du module avec succès.',
            'data': {
                'affectation_id': str(affectation.id),
                'utilisateur_retire': {
                    'id': str(utilisateur_retire.id),
                    'nom': utilisateur_retire.get_full_name(),
                    'role': role_retire
                },
                'retire_par': user.get_full_name()
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du retrait du membre: {str(e)}',
            'debug': {
                'traceback': traceback.format_exc(),
                'module_id': module_id,
                'projet_id': str(projet_id)
            }
        })


@login_required
@require_http_methods(["POST"])
def modifier_role_module_view(request, projet_id, module_id, affectation_id):
    """Modifier le rôle d'un membre sur un module"""
    try:
        from django.apps import apps
        AffectationModule = apps.get_model('core', 'AffectationModule')
        NotificationModule = apps.get_model('core', 'NotificationModule')
        
        # Récupération des objets
        projet = get_object_or_404(Projet, id=projet_id)
        module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
        affectation = get_object_or_404(AffectationModule, id=affectation_id, module=module)
        
        # Vérification des permissions - Seulement responsable du projet
        user = request.user
        can_manage = (
            user.est_super_admin() or 
            projet.createur == user or
            projet.affectations.filter(
                utilisateur=user, 
                est_responsable_principal=True,
                date_fin__isnull=True
            ).exists()
        )
        
        if not can_manage:
            return JsonResponse({
                'success': False, 
                'error': 'Seul le responsable du projet peut modifier les rôles.'
            })
        
        # Récupérer le nouveau rôle
        nouveau_role = request.POST.get('role_module')
        if not nouveau_role or nouveau_role not in ['RESPONSABLE', 'CONTRIBUTEUR', 'CONSULTANT']:
            return JsonResponse({
                'success': False,
                'error': 'Rôle invalide.'
            })
        
        # Sauvegarder l'ancien rôle
        ancien_role = affectation.role_module
        
        # Si pas de changement
        if ancien_role == nouveau_role:
            return JsonResponse({
                'success': True,
                'message': 'Aucun changement de rôle.'
            })
        
        # Vérifier qu'on ne retire pas le seul responsable
        if ancien_role == 'RESPONSABLE' and nouveau_role != 'RESPONSABLE':
            autres_responsables = AffectationModule.objects.filter(
                module=module,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).exclude(id=affectation.id).exists()
            
            if not autres_responsables:
                return JsonResponse({
                    'success': False,
                    'error': 'Impossible de retirer le seul responsable du module. Nommez d\'abord un autre responsable.'
                })
        
        # Vérifier qu'il n'y a pas déjà un autre responsable si on veut promouvoir
        if nouveau_role == 'RESPONSABLE':
            autre_responsable = AffectationModule.objects.filter(
                module=module,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).exclude(id=affectation.id).first()
            
            if autre_responsable:
                return JsonResponse({
                    'success': False,
                    'error': f'Le module a déjà un responsable : {autre_responsable.utilisateur.get_full_name()}.'
                })
        
        # Mettre à jour le rôle
        affectation.role_module = nouveau_role
        
        # Mettre à jour les permissions selon le rôle
        if nouveau_role == 'RESPONSABLE':
            affectation.peut_creer_taches = True
            affectation.peut_voir_toutes_taches = True
        else:
            affectation.peut_creer_taches = False
            affectation.peut_voir_toutes_taches = False
        
        affectation.save()
        
        # Créer la notification CHANGEMENT_ROLE
        NotificationModule.objects.create(
            destinataire=affectation.utilisateur,
            module=module,
            type_notification='CHANGEMENT_ROLE',
            titre=f"Changement de rôle: {module.nom}",
            message=f"Votre rôle sur le module '{module.nom}' a été modifié de {affectation.get_role_module_display_from_value(ancien_role)} à {affectation.get_role_module_display()}.",
            emetteur=user,
            donnees_contexte={
                'ancien_role': ancien_role,
                'nouveau_role': nouveau_role,
                'date_changement': timezone.now().isoformat()
            }
        )
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_ROLE_MODULE',
            description=f'Modification du rôle de {affectation.utilisateur.get_full_name()} sur le module "{module.nom}"',
            projet=projet,
            donnees_avant={
                'role': ancien_role
            },
            donnees_apres={
                'role': nouveau_role,
                'peut_creer_taches': affectation.peut_creer_taches,
                'peut_voir_toutes_taches': affectation.peut_voir_toutes_taches
            },
            request=request
        )
        
        messages.success(
            request,
            f'Rôle de {affectation.utilisateur.get_full_name()} modifié avec succès.'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Rôle modifié de {ancien_role} à {nouveau_role}.',
            'data': {
                'ancien_role': ancien_role,
                'nouveau_role': nouveau_role,
                'utilisateur': affectation.utilisateur.get_full_name()
            }
        })
        
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Erreur: {str(e)}',
            'debug': traceback.format_exc()
        })
