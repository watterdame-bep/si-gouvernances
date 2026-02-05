#!/usr/bin/env python3
"""
Script pour corriger l'import de TacheTest et nettoyer les doublons dans core/views.py
"""

import os
import re

def fix_tachetest_import():
    """Corriger l'import de TacheTest dans core/views.py"""
    
    print("🔧 Correction de l'import TacheTest dans core/views.py")
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
        
        # Vérifier si TacheTest est dans les imports
        import_line = "from .models import Utilisateur, Projet, Affectation, ActionAudit, RoleSysteme, RoleProjet, StatutProjet, Membre, TypeEtape, EtapeProjet, ModuleProjet, TacheModule, TacheEtape, NotificationModule, TacheTest, BugTest, ValidationTest"
        
        if import_line in content:
            print("✅ Import TacheTest déjà présent")
        else:
            print("⚠️  Import TacheTest manquant, ajout en cours...")
            # Chercher la ligne d'import des modèles et l'ajouter
            pattern = r'from \.models import.*'
            match = re.search(pattern, content)
            if match:
                old_import = match.group(0)
                if 'TacheTest' not in old_import:
                    new_import = old_import.rstrip() + ', TacheTest, BugTest, ValidationTest'
                    content = content.replace(old_import, new_import)
                    print("✅ Import TacheTest ajouté")
        
        # Chercher et corriger les doublons dans TYPE_TEST_CHOICES
        lines = content.split('\n')
        new_lines = []
        prev_line = ""
        
        for line in lines:
            # Éviter les doublons de TYPE_TEST_CHOICES
            if "'TYPE_TEST_CHOICES': TacheTest.TYPE_TEST_CHOICES," in line and "'TYPE_TEST_CHOICES': TacheTest.TYPE_TEST_CHOICES," in prev_line:
                print("🧹 Doublon TYPE_TEST_CHOICES supprimé")
                continue
            new_lines.append(line)
            prev_line = line
        
        content = '\n'.join(new_lines)
        
        # Vérifier que la vue creer_test_view utilise bien le bon template
        if 'def creer_test_view' in content:
            print("✅ Vue creer_test_view trouvée")
            
            # S'assurer que le template correct est utilisé
            if "render(request, 'core/creer_test_simple.html'" in content:
                print("✅ Template creer_test_simple.html utilisé")
            else:
                print("⚠️  Template creer_test_simple.html non trouvé, correction...")
                content = re.sub(
                    r"render\(request, 'core/creer_test\.html'",
                    "render(request, 'core/creer_test_simple.html'",
                    content
                )
        
        # Écrire le fichier corrigé
        with open(views_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier core/views.py corrigé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        return False

def verify_tachetest_model():
    """Vérifier que le modèle TacheTest existe et a les bonnes propriétés"""
    
    print("\n🔍 Vérification du modèle TacheTest")
    print("=" * 40)
    
    try:
        import os
        import sys
        import django
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
        django.setup()
        
        from core.models import TacheTest
        
        print("✅ Modèle TacheTest importé avec succès")
        
        # Vérifier les choix
        if hasattr(TacheTest, 'TYPE_TEST_CHOICES'):
            print(f"✅ TYPE_TEST_CHOICES disponible: {len(TacheTest.TYPE_TEST_CHOICES)} options")
        else:
            print("❌ TYPE_TEST_CHOICES manquant")
            return False
        
        if hasattr(TacheTest, 'PRIORITE_CHOICES'):
            print(f"✅ PRIORITE_CHOICES disponible: {len(TacheTest.PRIORITE_CHOICES)} options")
        else:
            print("❌ PRIORITE_CHOICES manquant")
            return False
        
        # Vérifier les champs principaux
        fields = ['nom', 'description', 'type_test', 'priorite', 'etape', 'createur']
        for field in fields:
            if hasattr(TacheTest, field):
                print(f"✅ Champ {field} présent")
            else:
                print(f"❌ Champ {field} manquant")
                return False
        
        print("✅ Modèle TacheTest correctement configuré")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Correction de l'import TacheTest")
    print("=" * 50)
    
    success1 = fix_tachetest_import()
    success2 = verify_tachetest_model()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    
    if success1:
        print("✅ Correction du fichier views.py: RÉUSSIE")
    else:
        print("❌ Correction du fichier views.py: ÉCHEC")
    
    if success2:
        print("✅ Vérification du modèle TacheTest: RÉUSSIE")
    else:
        print("❌ Vérification du modèle TacheTest: ÉCHEC")
    
    if success1 and success2:
        print("\n🎉 CORRECTION TERMINÉE!")
        print("L'interface de création de tests devrait maintenant fonctionner.")
        print("\n💡 Prochaines étapes:")
        print("   1. Redémarrer le serveur Django")
        print("   2. Tester l'accès à l'interface de gestion des tests")
        print("   3. Tester la création d'un nouveau test")
    else:
        print("\n⚠️  CORRECTION PARTIELLE")
        print("Certains problèmes persistent. Vérifiez les erreurs ci-dessus.")