"""
Code à ajouter dans core/views.py pour implémenter le transfert de responsabilité
et permettre la suppression de n'importe quel membre
"""

CODE_A_AJOUTER = '''
@login_required
@require_http_methods(["POST"])
def transferer_responsabilite(request, projet_id):
    """
    Transférer la responsabilité d'un projet à un autre membre de l'équipe
    """
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions (admin ou responsable actuel)
    can_transfer = user.est_super_admin() or projet.createur == user
    if not can_transfer:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_transfer = affectation_user is not None
    
    if not can_transfer:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        nouveau_responsable_id = request.POST.get('nouveau_responsable_id')
        
        if not nouveau_responsable_id:
            return JsonResponse({'success': False, 'error': 'Nouveau responsable requis'})
        
        # Récupérer le nouveau responsable
        nouveau_responsable = get_object_or_404(Utilisateur, id=nouveau_responsable_id, statut_actif=True)
        
        # Vérifier que le nouveau responsable est membre de l'équipe
        affectation_nouveau = projet.affectations.filter(
            utilisateur=nouveau_responsable,
            date_fin__isnull=True
        ).first()
        
        if not affectation_nouveau:
            return JsonResponse({'success': False, 'error': 'Le nouveau responsable doit être membre de l\'équipe'})
        
        # Vérifier qu'il n'est pas déjà responsable
        if affectation_nouveau.est_responsable_principal:
            return JsonResponse({'success': False, 'error': 'Cet utilisateur est déjà responsable'})
        
        # Récupérer l'ancien responsable
        ancien_responsable_aff = projet.affectations.filter(
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        
        ancien_responsable_nom = ancien_responsable_aff.utilisateur.get_full_name() if ancien_responsable_aff else "Aucun"
        
        # Transaction atomique pour garantir la cohérence
        from django.db import transaction
        
        with transaction.atomic():
            # Retirer la responsabilité de l'ancien responsable (devient membre)
            if ancien_responsable_aff:
                ancien_responsable_aff.est_responsable_principal = False
                # Mettre à jour le rôle
                try:
                    role_membre = RoleProjet.objects.get(nom='MEMBRE')
                    ancien_responsable_aff.role_projet = role_membre
                except RoleProjet.DoesNotExist:
                    pass
                ancien_responsable_aff.save()
            
            # Donner la responsabilité au nouveau responsable
            affectation_nouveau.est_responsable_principal = True
            # Mettre à jour le rôle
            try:
                role_responsable = RoleProjet.objects.get(nom='RESPONSABLE_PRINCIPAL')
                affectation_nouveau.role_projet = role_responsable
            except RoleProjet.DoesNotExist:
                pass
            affectation_nouveau.save()
            
            # Le signal notifier_responsable_projet se déclenchera automatiquement
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='TRANSFERT_RESPONSABILITE',
            description=f'Transfert de responsabilité du projet {projet.nom}: {ancien_responsable_nom} → {nouveau_responsable.get_full_name()}',
            projet=projet,
            request=request,
            donnees_avant={'responsable': ancien_responsable_nom},
            donnees_apres={'responsable': nouveau_responsable.get_full_name()}
        )
        
        messages.success(request, f'Responsabilité transférée à {nouveau_responsable.get_full_name()} avec succès !')
        return JsonResponse({
            'success': True, 
            'message': 'Responsabilité transférée avec succès',
            'nouveau_responsable': nouveau_responsable.get_full_name()
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def retirer_membre_projet_v2(request, projet_id):
    """
    Retirer un membre de l'équipe du projet (version améliorée)
    Permet à l'admin de retirer n'importe quel membre, y compris le responsable
    """
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        affectation_id = request.POST.get('affectation_id')
        
        if not affectation_id:
            return JsonResponse({'success': False, 'error': 'Affectation requise'})
        
        affectation = get_object_or_404(Affectation, id=affectation_id, projet=projet, date_fin__isnull=True)
        
        # L'admin peut retirer n'importe qui, même le responsable
        # Les autres ne peuvent pas retirer le créateur du projet
        if not user.est_super_admin():
            if affectation.utilisateur == projet.createur:
                return JsonResponse({'success': False, 'error': 'Le créateur du projet ne peut pas être retiré'})
            
            # Ne pas permettre de se retirer soi-même si on est le seul responsable
            if affectation.utilisateur == user and affectation.est_responsable_principal:
                autres_responsables = projet.affectations.filter(
                    est_responsable_principal=True,
                    date_fin__isnull=True
                ).exclude(id=affectation.id).exists()
                
                if not autres_responsables:
                    return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous retirer en tant que seul responsable'})
        
        # Sauvegarder les infos avant suppression
        utilisateur_nom = affectation.utilisateur.get_full_name()
        etait_responsable = affectation.est_responsable_principal
        
        # Terminer l'affectation
        affectation.terminer_affectation()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='RETRAIT_UTILISATEUR',
            description=f'Retrait de {utilisateur_nom} du projet {projet.nom}' + (' (était responsable principal)' if etait_responsable else ''),
            projet=projet,
            request=request,
            donnees_avant={
                'utilisateur': utilisateur_nom,
                'est_responsable': etait_responsable
            }
        )
        
        message = f'{utilisateur_nom} retiré de l\'équipe avec succès !'
        if etait_responsable:
            message += ' Le projet n\'a plus de responsable. Veuillez en désigner un nouveau.'
        
        messages.success(request, message)
        return JsonResponse({'success': True, 'message': message, 'etait_responsable': etait_responsable})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
'''

print("=" * 80)
print("IMPLÉMENTATION: Transfert de Responsabilité")
print("=" * 80)
print("\nCODE À AJOUTER DANS core/views.py:")
print("\n" + CODE_A_AJOUTER)
print("\n" + "=" * 80)
print("URL À AJOUTER DANS core/urls.py:")
print("=" * 80)
print("""
# Gestion d'équipe avancée
path('projets/<uuid:projet_id>/transferer-responsabilite/', views.transferer_responsabilite, name='transferer_responsabilite'),
path('projets/<uuid:projet_id>/retirer-membre-v2/', views.retirer_membre_projet_v2, name='retirer_membre_projet_v2'),
""")
