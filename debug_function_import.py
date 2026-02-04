#!/usr/bin/env python3
"""
Debug de l'importation de la fonction affecter_module_view
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

def debug_function_import():
    """Debug de l'importation de la fonction"""
    
    print("🔍 Debug de l'importation de affecter_module_view")
    print("=" * 50)
    
    try:
        # Lire le fichier et analyser
        with open('core/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Taille du fichier: {len(content)} caractères")
        
        # Chercher la fonction
        import re
        pattern = r'def affecter_module_view\('
        matches = list(re.finditer(pattern, content))
        
        print(f"🔍 Occurrences de 'def affecter_module_view(': {len(matches)}")
        
        for i, match in enumerate(matches):
            start = match.start()
            # Trouver le début de la ligne
            line_start = content.rfind('\n', 0, start) + 1
            line_num = content[:start].count('\n') + 1
            
            print(f"   Match {i+1}: ligne {line_num}, position {start}")
            
            # Extraire quelques lignes autour
            lines = content[line_start:start+200].split('\n')
            for j, line in enumerate(lines[:5]):
                print(f"     {line_num + j - 1}: {line}")
        
        # Essayer d'importer le module
        print("\n📦 Test d'importation:")
        try:
            import core.views as views
            print("✅ Module importé avec succès")
            
            # Vérifier les fonctions disponibles
            functions = [name for name in dir(views) if name.endswith('_view')]
            print(f"📋 Fonctions *_view trouvées: {len(functions)}")
            
            for func_name in sorted(functions):
                if 'module' in func_name:
                    print(f"   📌 {func_name}")
            
            # Test spécifique
            if hasattr(views, 'affecter_module_view'):
                print("✅ affecter_module_view trouvée!")
                func = getattr(views, 'affecter_module_view')
                print(f"   Type: {type(func)}")
            else:
                print("❌ affecter_module_view non trouvée")
                
                # Chercher des noms similaires
                similar = [name for name in dir(views) if 'affecter' in name.lower()]
                if similar:
                    print(f"   Fonctions similaires: {similar}")
            
        except Exception as e:
            print(f"❌ Erreur d'importation: {str(e)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_function_import()