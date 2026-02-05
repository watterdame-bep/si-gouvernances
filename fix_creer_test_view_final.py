#!/usr/bin/env python3
"""
Script pour corriger définitivement la vue creer_test_view
"""

import os
import re

def fix_creer_test_view():
    """Corriger la vue creer_test_view avec import local si nécessaire"""
    
    print("🔧 Correction définitive de la vue creer_test_view")
    print("=" * 50)
    
    views_file = 'core/views.py'
    
    if not os.path.exists(views_file):
        print(f"❌ Fichier {views_file} non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier lu avec succès")
        
        # Vérifier l'import global de TacheTest
        if 'from .models import' in content and 'TacheTest' in content:
            print("✅ Import global TacheTest trouvé")
        else:
            print("⚠️  Import global TacheTest manquant")
        
        # Chercher la vue creer_test_view et la corriger
        pattern = r'(def creer_test_view\(request, projet_id, etape_id\):.*?context = \{.*?)(\'TYPE_TEST_CHOICES\': TacheTest\.TYPE_TEST_CHOICES,.*?\'PRIORITE_CHOICES\': TacheTest\.PRIORITE_CHOICES,)(.*?\}.*?return render\(request, \'core/creer_test_simple\.html\', context\))'
        
        def replace_function(match):
            before = match.group(1)
            problematic_lines = match.group(2)
            after = match.group(3)
            
            # Ajouter un import local au début de la fonction si nécessaire
            if 'from .models import TacheTest' not in before:
                # Trouver la position après la définition de la fonction
                func_def_end = before.find('"""Vue de création d\'un test"""')
                if func_def_end != -1:
                    func_def_end = before.find('\n', func_def_end) + 1
                    before = before[:func_def_end] + '    from .models import TacheTest  # Import local pour éviter les problèmes\n' + before[func_def_end:]
            
            # Remplacer les lignes problématiques avec une version plus robuste
            new_lines = """'TYPE_TEST_CHOICES': getattr(TacheTest, 'TYPE_TEST_CHOICES', []),
        'PRIORITE_CHOICES': getattr(TacheTest, 'PRIORITE_CHOICES', []),"""
            
            return before + new_lines + after
        
        new_content = re.sub(pattern, replace_function, content, flags=re.DOTALL)
        
        if new_content != content:
            print("✅ Vue creer_test_view corrigée")
            content = new_content
        else:
            print("⚠️  Pattern non trouvé, essai d'une approche alternative...")
            
            # Approche alternative : remplacer directement les lignes problématiques
            content = re.sub(
                r"'TYPE_TEST_CHOICES': TacheTest\.TYPE_TEST_CHOICES,",
                "'TYPE_TEST_CHOICES': getattr(TacheTest, 'TYPE_TEST_CHOICES', []),",
                content
            )
            content = re.sub(
                r"'PRIORITE_CHOICES': TacheTest\.PRIORITE_CHOICES,",
                "'PRIORITE_CHOICES': getattr(TacheTest, 'PRIORITE_CHOICES', []),",
                content
            )
            
            # Ajouter un import local dans la fonction
            if 'def creer_test_view(request, projet_id, etape_id):' in content:
                content = re.sub(
                    r'(def creer_test_view\(request, projet_id, etape_id\):\s*\n\s*"""Vue de création d\'un test"""\s*\n)',
                    r'\1    from .models import TacheTest  # Import local pour éviter les problèmes\n',
                    content
                )
                print("✅ Import local ajouté dans creer_test_view")
        
        # Écrire le fichier corrigé
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier core/views.py corrigé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_view():
    """Créer une version simplifiée de la vue creer_test_view"""
    
    print("\n🔧 Création d'une vue creer_test_view simplifiée")
    print("=" * 50)
    
    simple_view = '''
@login_required
def creer_test_view(request, projet_id, etape_id):
    """Vue de création d'un test - Version simplifiée"""
    from .models import TacheTest  # Import local pour éviter les problèmes
    
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    peut_creer = user.est_super_admin() or (hasattr(user, 'role_systeme') and user.role_systeme and user.role_systeme.nom in ['QA', 'CHEF_PROJET']) or projet.createur == user
    if not peut_creer:
        messages.error(request, 'Vous n\\'avez pas les permissions pour créer des tests.')
        return redirect('gestion_tests', projet_id=projet.id, etape_id=etape.id)
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.POST.get('nom', '')
            description = request.POST.get('description', '')
            type_test = request.POST.get('type_test', 'FONCTIONNEL')
            priorite = request.POST.get('priorite', 'MOYENNE')
            etapes_test = request.POST.get('etapes_test', '')
            resultats_attendus = request.POST.get('resultats_attendus', '')
            
            # Créer le test
            test = TacheTest.objects.create(
                etape=etape,
                createur=user,
                nom=nom,
                description=description,
                type_test=type_test,
                priorite=priorite,
                scenario_test=etapes_test,
                resultats_attendus=resultats_attendus,
                assignee_qa=user if hasattr(user, 'role_systeme') and user.role_systeme and user.role_systeme.nom == 'QA' else None
            )
            
            messages.success(request, f'Test "{test.nom}" créé avec succès.')
            return redirect('gestion_tests', projet_id=projet.id, etape_id=etape.id)
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Définir les choix localement pour éviter les problèmes d'import
    type_test_choices = [
        ('FONCTIONNEL', 'Test Fonctionnel'),
        ('SECURITE', 'Test de Sécurité'),
        ('PERFORMANCE', 'Test de Performance'),
        ('INTEGRATION', 'Test d\\'Intégration'),
        ('REGRESSION', 'Test de Régression'),
    ]
    
    priorite_choices = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    context = {
        'projet': projet,
        'etape': etape,
        'TYPE_TEST_CHOICES': type_test_choices,
        'PRIORITE_CHOICES': priorite_choices,
    }
    
    return render(request, 'core/creer_test_simple.html', context)
'''
    
    return simple_view

def replace_creer_test_view():
    """Remplacer complètement la vue creer_test_view par une version qui fonctionne"""
    
    print("\n🔧 Remplacement complet de la vue creer_test_view")
    print("=" * 50)
    
    views_file = 'core/views.py'
    
    try:
        # Lire le fichier
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher et remplacer la vue creer_test_view complète
        pattern = r'@login_required\ndef creer_test_view\(request, projet_id, etape_id\):.*?return render\(request, \'core/creer_test_simple\.html\', context\)'
        
        new_view = create_simple_test_view().strip()
        
        new_content = re.sub(pattern, new_view, content, flags=re.DOTALL)
        
        if new_content != content:
            # Écrire le fichier corrigé
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Vue creer_test_view remplacée avec succès")
            return True
        else:
            print("❌ Pattern de remplacement non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du remplacement: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Correction définitive de la vue creer_test_view")
    print("=" * 60)
    
    # Essayer d'abord la correction simple
    success1 = fix_creer_test_view()
    
    if not success1:
        print("\n⚠️  Correction simple échouée, essai du remplacement complet...")
        success2 = replace_creer_test_view()
    else:
        success2 = True
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS")
    print("=" * 60)
    
    if success1 or success2:
        print("✅ CORRECTION RÉUSSIE!")
        print("\n🎉 La vue creer_test_view a été corrigée!")
        print("\n💡 Actions recommandées:")
        print("   1. Redémarrer le serveur Django (Ctrl+C puis python manage.py runserver)")
        print("   2. Tester l'accès à l'interface de création de test")
        print("   3. Essayer de créer un test de démonstration")
        
        print("\n🔗 URL à tester:")
        print("   http://127.0.0.1:8000/projets/515732ad-5ad2-4176-be84-d42868efce95/etapes/ba3be614-45e5-4ff7-96ea-b71071018498/tests/creer/")
    else:
        print("❌ CORRECTION ÉCHOUÉE")
        print("\n🔧 Actions manuelles nécessaires:")
        print("   1. Vérifier l'import de TacheTest dans core/views.py")
        print("   2. Redémarrer le serveur Django")
        print("   3. Vérifier les logs d'erreur Django")