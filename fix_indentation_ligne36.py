#!/usr/bin/env python3
"""
Script pour corriger l'erreur d'indentation à la ligne 36 de core/models.py
"""

import os

def fix_line_36_indentation():
    """Corriger l'erreur d'indentation à la ligne 36"""
    
    print("🔧 Correction de l'erreur d'indentation ligne 36")
    print("=" * 50)
    
    models_file = 'core/models.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    try:
        # Lire le fichier ligne par ligne
        with open(models_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✅ Fichier lu avec succès ({len(lines)} lignes)")
        
        # Corriger les lignes problématiques autour de la ligne 36
        corrected_lines = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Ligne 35-40 : corriger la structure de la classe
            if line_num == 35 and 'def __str__(self):' in line:
                # Corriger l'indentation de __str__ (doit être au niveau classe, pas Meta)
                corrected_lines.append('    \n')  # Fermer Meta
                corrected_lines.append('    def __str__(self):\n')
                print(f"✅ Ligne {line_num}: Indentation de __str__ corrigée")
                continue
            
            elif line_num == 36 and 'return self.get_nom_display()' in line:
                # Corriger l'indentation du return
                corrected_lines.append('        return self.get_nom_display()\n')
                print(f"✅ Ligne {line_num}: Indentation du return corrigée")
                continue
            
            # Supprimer les méthodes mal placées qui ont été ajoutées par erreur
            elif 'def mettre_a_jour_statut(self):' in line and 'cas_test' in ''.join(lines[i:i+10]):
                print(f"⚠️  Ligne {line_num}: Méthode mal placée supprimée")
                # Ignorer cette méthode et les lignes suivantes jusqu'à la prochaine classe/méthode
                j = i + 1
                while j < len(lines) and not (lines[j].strip().startswith('class ') or 
                                            (lines[j].strip().startswith('def ') and not lines[j].startswith('        '))):
                    j += 1
                # Sauter toutes ces lignes
                for _ in range(j - i):
                    if i < len(lines) - 1:
                        i += 1
                continue
            
            # Garder les autres lignes telles quelles
            corrected_lines.append(line)
        
        # Écrire le fichier corrigé
        with open(models_file, 'w', encoding='utf-8') as f:
            f.writelines(corrected_lines)
        
        print("✅ Fichier core/models.py corrigé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_python_syntax():
    """Tester la syntaxe Python du fichier corrigé"""
    
    print("\n🔍 Test de la syntaxe Python")
    print("=" * 30)
    
    try:
        with open('core/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Essayer de compiler le code
        compile(content, 'core/models.py', 'exec')
        print("✅ Syntaxe Python valide")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        if e.text:
            print(f"   Texte: {e.text.strip()}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def test_django_import():
    """Tester que Django peut importer les modèles"""
    
    print("\n🔍 Test d'import Django")
    print("=" * 25)
    
    try:
        import os
        import sys
        import django
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
        django.setup()
        
        # Essayer d'importer les modèles
        from core.models import RoleSysteme, TacheTest
        
        print("✅ Import des modèles Django réussi")
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import Django: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Correction de l'erreur d'indentation ligne 36")
    print("=" * 60)
    
    success1 = fix_line_36_indentation()
    success2 = test_python_syntax()
    success3 = test_django_import()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)
    
    if success1 and success2 and success3:
        print("✅ CORRECTION RÉUSSIE!")
        print("\n💡 Prochaines étapes:")
        print("   1. Ajouter le modèle CasTest proprement")
        print("   2. Créer la migration:")
        print("      python manage.py makemigrations")
        print("   3. Appliquer la migration:")
        print("      python manage.py migrate")
    else:
        print("❌ CORRECTION PARTIELLE")
        if not success1:
            print("   - Correction du fichier échouée")
        if not success2:
            print("   - Syntaxe Python invalide")
        if not success3:
            print("   - Import Django échoué")