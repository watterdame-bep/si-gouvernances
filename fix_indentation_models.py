#!/usr/bin/env python3
"""
Script pour corriger les erreurs d'indentation dans core/models.py
"""

import os

def fix_indentation():
    """Corriger les erreurs d'indentation dans core/models.py"""
    
    print("🔧 Correction des erreurs d'indentation")
    print("=" * 50)
    
    models_file = 'core/models.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(models_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✅ Fichier lu avec succès ({len(lines)} lignes)")
        
        # Corriger les problèmes d'indentation autour de la ligne 2013
        corrected_lines = []
        in_class = False
        class_indent = 0
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Détecter le début d'une classe
            if line.strip().startswith('class ') and line.strip().endswith(':'):
                in_class = True
                class_indent = len(line) - len(line.lstrip())
                corrected_lines.append(line)
                continue
            
            # Si on est dans une classe
            if in_class:
                # Détecter la fin de la classe (nouvelle classe ou fin de fichier)
                if line.strip().startswith('class ') and line.strip().endswith(':'):
                    in_class = True
                    class_indent = len(line) - len(line.lstrip())
                    corrected_lines.append(line)
                    continue
                
                # Ligne vide ou commentaire
                if not line.strip() or line.strip().startswith('#'):
                    corrected_lines.append(line)
                    continue
                
                # Méthode ou propriété de classe
                if line.strip().startswith('def ') or line.strip().startswith('@'):
                    # Indentation de méthode = indentation de classe + 4
                    correct_indent = ' ' * (class_indent + 4)
                    corrected_line = correct_indent + line.strip() + '\n'
                    corrected_lines.append(corrected_line)
                    continue
                
                # Contenu de méthode ou attribut de classe
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= class_indent and line.strip():
                    # Probablement un attribut de classe
                    correct_indent = ' ' * (class_indent + 4)
                    corrected_line = correct_indent + line.strip() + '\n'
                    corrected_lines.append(corrected_line)
                    continue
            
            # Garder la ligne telle quelle si pas de problème détecté
            corrected_lines.append(line)
        
        # Écrire le fichier corrigé
        with open(models_file, 'w', encoding='utf-8') as f:
            f.writelines(corrected_lines)
        
        print("✅ Indentation corrigée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def validate_syntax():
    """Valider la syntaxe du fichier Python"""
    
    print("\n🔍 Validation de la syntaxe")
    print("=" * 30)
    
    models_file = 'core/models.py'
    
    try:
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Essayer de compiler le code
        compile(content, models_file, 'exec')
        print("✅ Syntaxe Python valide")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe à la ligne {e.lineno}: {e.msg}")
        print(f"   Texte: {e.text.strip() if e.text else 'N/A'}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la validation: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Correction des erreurs d'indentation dans models.py")
    print("=" * 60)
    
    success1 = fix_indentation()
    success2 = validate_syntax()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ CORRECTIONS APPLIQUÉES AVEC SUCCÈS!")
        print("\n💡 Prochaines étapes:")
        print("   1. Tester la création de migration:")
        print("      python manage.py makemigrations")
    else:
        print("❌ CORRECTIONS PARTIELLES OU ÉCHEC")
        print("Vérifiez les erreurs ci-dessus.")