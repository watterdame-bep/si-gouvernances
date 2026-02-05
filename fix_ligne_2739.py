#!/usr/bin/env python3
"""
Script pour corriger la ligne 2739 dans core/views.py
Remplace module.taches par etape.taches_etape dans gestion_taches_etape_view
"""

import re

def fix_line_2739():
    """Corrige la ligne problématique dans gestion_taches_etape_view"""
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher la fonction gestion_taches_etape_view
    pattern = r'(def gestion_taches_etape_view\(.*?\):.*?)(taches = module\.taches\.all\(\)\.order_by\(\'-date_creation\'\))'
    
    # Remplacer module.taches par etape.taches_etape dans cette fonction
    def replace_func(match):
        function_part = match.group(1)
        problematic_line = match.group(2)
        fixed_line = problematic_line.replace('module.taches', 'etape.taches_etape')
        return function_part + fixed_line
    
    # Appliquer le remplacement
    new_content = re.sub(pattern, replace_func, content, flags=re.DOTALL)
    
    # Si pas de match avec la première approche, essayer une approche plus simple
    if new_content == content:
        print("Première approche échouée, essai d'une approche plus directe...")
        
        # Chercher toutes les occurrences de module.taches dans le fichier
        lines = content.split('\n')
        
        # Chercher la fonction gestion_taches_etape_view
        in_gestion_taches_etape = False
        function_start = -1
        
        for i, line in enumerate(lines):
            if 'def gestion_taches_etape_view(' in line:
                in_gestion_taches_etape = True
                function_start = i
                print(f"Trouvé gestion_taches_etape_view à la ligne {i+1}")
                continue
            
            # Si on trouve une nouvelle fonction, on sort de gestion_taches_etape_view
            if in_gestion_taches_etape and line.startswith('def ') and 'gestion_taches_etape_view' not in line:
                in_gestion_taches_etape = False
                print(f"Fin de gestion_taches_etape_view à la ligne {i}")
                continue
            
            # Si on est dans la fonction et qu'on trouve module.taches
            if in_gestion_taches_etape and 'module.taches.all().order_by(' in line:
                print(f"Ligne problématique trouvée à la ligne {i+1}: {line.strip()}")
                # Remplacer module.taches par etape.taches_etape
                lines[i] = line.replace('module.taches', 'etape.taches_etape')
                print(f"Ligne corrigée: {lines[i].strip()}")
        
        new_content = '\n'.join(lines)
    
    # Écrire le fichier corrigé
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Correction appliquée avec succès!")
    
    # Vérifier que la correction a été appliquée
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content_check = f.read()
    
    if 'etape.taches_etape.all().order_by(\'-date_creation\')' in content_check:
        print("✅ Vérification: La correction est présente dans le fichier")
    else:
        print("❌ Erreur: La correction n'a pas été appliquée correctement")

if __name__ == '__main__':
    fix_line_2739()