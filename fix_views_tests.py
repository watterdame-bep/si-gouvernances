#!/usr/bin/env python3
"""
Script pour ajouter les vues de tests au fichier views.py
"""

def fix_views_tests():
    """Ajoute les vues de tests au fichier views.py"""
    
    # Lire le fichier actuel
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si les vues sont déjà présentes
    if 'def gestion_tests_view' in content:
        print("✅ Les vues de tests sont déjà présentes")
        return
    
    # Code des vues à ajouter
    vues_tests = '''
# ============================================================================
# SYSTÈME DE TESTS V1 - VUES SIMPLIFIÉES
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
            messages.error(request, 'Vous n\\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Vérifier que c'est bien une étape de tests
    if etape.type_etape.nom != 'TESTS':
        messages.error(request, 'Cette étape n\\'est pas une étape de tests.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Récupérer les tests de cette étape
    tests = etape.taches_test.all().order_by('-date_creation')
    
    # Statistiques simples
    stats = {
        'total': tests.count(),
        'passes': tests.filter(statut='PASSE').count(),
        'echecs': tests.filter(statut='ECHEC').count(),
        'en_attente': tests.filter(statut='EN_ATTENTE').count(),
    }
    
    # Permissions utilisateur
    peut_creer_tests = user.est_super_admin() or user.role_systeme.nom in ['QA', 'CHEF_PROJET'] or projet.createur == user
    peut_executer_tests = user.est_super_admin() or user.role_systeme.nom == 'QA' or projet.createur == user
    
    context = {
        'projet': projet,
        'etape': etape,
        'tests': tests,
        'stats': stats,
        'peut_creer_tests': peut_creer_tests,
        'peut_executer_tests': peut_executer_tests,
    }
    
    return render(request, 'core/gestion_tests_simple.html', context)


@login_required
def creer_test_view(request, projet_id, etape_id):
    """Vue de création d'un test"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    peut_creer = user.est_super_admin() or user.role_systeme.nom in ['QA', 'CHEF_PROJET'] or projet.createur == user
    if not peut_creer:
        messages.error(request, 'Vous n\\'avez pas les permissions pour créer des tests.')
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
            
            # Créer le test
            test = TacheTest.objects.create(
                etape=etape,
                createur=user,
                nom=nom,
                description=description,
                type_test=type_test,
                priorite=priorite,
                scenario_test=scenario_test,
                resultats_attendus=resultats_attendus,
                assignee_qa=user if user.role_systeme.nom == 'QA' else None
            )
            
            messages.success(request, f'Test "{test.nom}" créé avec succès.')
            return redirect('gestion_tests', projet_id=projet.id, etape_id=etape.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'projet': projet,
        'etape': etape,
        'TYPE_TEST_CHOICES': TacheTest.TYPE_TEST_CHOICES,
        'PRIORITE_CHOICES': TacheTest.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/creer_test_simple.html', context)


@login_required
@require_http_methods(["POST"])
def executer_test_view(request, projet_id, etape_id, test_id):
    """Vue d'exécution d'un test (AJAX)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    test = get_object_or_404(TacheTest, id=test_id, etape=etape)
    
    try:
        # Vérifier les permissions
        peut_executer = user.est_super_admin() or user.role_systeme.nom == 'QA' or projet.createur == user
        if not peut_executer:
            return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
        
        # Récupérer les données
        statut_resultat = request.POST.get('statut_resultat')  # 'PASSE' ou 'ECHEC'
        resultats_obtenus = request.POST.get('resultats_obtenus', '')
        
        # Mettre à jour le test
        test.statut = statut_resultat
        test.executeur = user
        test.date_execution = timezone.now()
        test.resultats_obtenus = resultats_obtenus
        test.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Test {test.numero_test} exécuté avec succès',
            'nouveau_statut': test.statut,
            'date_execution': test.date_execution.strftime('%d/%m/%Y %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur : {str(e)}'})


# Placeholders pour les autres vues
@login_required
def gestion_bugs_view(request, projet_id, etape_id):
    messages.info(request, 'Interface de gestion des bugs disponible en V1.1')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)

@login_required
def creer_bug_view(request, projet_id, etape_id):
    messages.info(request, 'Création de bugs disponible en V1.1')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)

@login_required
def validation_test_view(request, projet_id, etape_id):
    messages.info(request, 'Interface de validation disponible en V1.1')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)

@login_required
@require_http_methods(["POST"])
def valider_etape_test_view(request, projet_id, etape_id):
    messages.info(request, 'Validation d\\'étape disponible en V1.1')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)

@login_required
@require_http_methods(["POST"])
def assigner_bug_view(request, projet_id, bug_id):
    return JsonResponse({'success': False, 'error': 'Fonctionnalité disponible en V1.1'})

@login_required
@require_http_methods(["POST"])
def resoudre_bug_view(request, projet_id, bug_id):
    return JsonResponse({'success': False, 'error': 'Fonctionnalité disponible en V1.1'})

@login_required
@require_http_methods(["POST"])
def fermer_bug_view(request, projet_id, bug_id):
    return JsonResponse({'success': False, 'error': 'Fonctionnalité disponible en V1.1'})

@login_required
def modifier_test_view(request, projet_id, etape_id, test_id):
    messages.info(request, 'Modification de tests disponible en V1.1')
    return redirect('gestion_tests', projet_id=projet_id, etape_id=etape_id)
'''
    
    # Ajouter les vues à la fin du fichier
    new_content = content + vues_tests
    
    # Écrire le nouveau contenu
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Vues de tests ajoutées avec succès")

if __name__ == '__main__':
    fix_views_tests()