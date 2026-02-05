#!/usr/bin/env python
"""
Script pour corriger l'ordre des tâches dans toutes les vues
"""
import os
import re

def fix_ordre_taches():
    print("🔧 CORRECTION : Ordre des tâches dans les vues")
    print("=" * 50)
    
    # Lire le fichier views.py
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns à corriger
    patterns_to_fix = [
        # Pattern 1: order_by('statut', 'priorite', 'date_creation')
        (
            r"taches.*\.order_by\('statut',\s*'priorite',\s*'date_creation'\)",
            "taches.order_by('-date_creation')"
        ),
        # Pattern 2: order_by('priorite', 'date_creation')
        (
            r"taches_etape.*\.order_by\('priorite',\s*'date_creation'\)",
            "taches_etape.order_by('-date_creation')"
        ),
        # Pattern 3: order_by('statut', 'date_creation')
        (
            r"taches.*\.order_by\('statut',\s*'date_creation'\)",
            "taches.order_by('-date_creation')"
        )
    ]
    
    original_content = content
    corrections = 0
    
    for pattern, replacement in patterns_to_fix:
        matches = re.findall(pattern, content)
        if matches:
            print(f"🔍 Trouvé {len(matches)} occurrence(s) de: {pattern}")
            content = re.sub(pattern, replacement, content)
            corrections += len(matches)
    
    if corrections > 0:
        # Sauvegarder le fichier corrigé
        with open('core/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {corrections} correction(s) appliquée(s)")
        
        # Afficher les différences
        print(f"\n📝 Corrections appliquées:")
        lines_original = original_content.split('\n')
        lines_new = content.split('\n')
        
        for i, (old_line, new_line) in enumerate(zip(lines_original, lines_new)):
            if old_line != new_line and 'order_by' in old_line:
                print(f"  Ligne {i+1}:")
                print(f"    - {old_line.strip()}")
                print(f"    + {new_line.strip()}")
    else:
        print("✅ Aucune correction nécessaire - l'ordre est déjà correct")
    
    print(f"\n🎯 Vérification finale...")
    
    # Vérifier les patterns restants
    remaining_issues = []
    
    # Chercher les order_by problématiques
    problematic_patterns = [
        r"taches.*\.order_by\([^)]*'date_creation'[^)]*\)",
        r"taches_etape.*\.order_by\([^)]*'date_creation'[^)]*\)"
    ]
    
    for pattern in problematic_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if not match.startswith("order_by('-date_creation')"):
                remaining_issues.append(match)
    
    if remaining_issues:
        print(f"⚠️ Problèmes restants à vérifier manuellement:")
        for issue in remaining_issues:
            print(f"  - {issue}")
    else:
        print(f"✅ Tous les ordres de tâches sont corrects")

if __name__ == "__main__":
    fix_ordre_taches()