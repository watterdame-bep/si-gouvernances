#!/usr/bin/env python
"""
Correction de toutes les lignes problématiques
"""

def fix_toutes_lignes():
    print("🔧 CORRECTION : Toutes les lignes problématiques")
    print("=" * 50)
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrections = 0
    
    # Chercher et corriger toutes les lignes problématiques
    for i, line in enumerate(lines):
        original_line = line
        
        # Pattern 1: taches.order_by('-date_creation') sans assignation
        if 'taches.order_by(' in line and 'taches =' not in line and '=' not in line.split('taches.order_by')[0]:
            print(f"🔍 Ligne {i+1} problématique trouvée:")
            print(f"   Avant: {line.strip()}")
            
            # Déterminer le bon nom de variable selon le contexte
            if 'etape' in lines[max(0, i-5):i+1]:
                lines[i] = "    taches = etape.taches_etape.all().order_by('-date_creation')\n"
            else:
                lines[i] = "    taches = module.taches.all().order_by('-date_creation')\n"
            
            print(f"   Après: {lines[i].strip()}")
            corrections += 1
        
        # Pattern 2: taches_etape.order_by('-date_creation') sans assignation
        elif 'taches_etape.order_by(' in line and 'taches_etape =' not in line:
            print(f"🔍 Ligne {i+1} problématique trouvée:")
            print(f"   Avant: {line.strip()}")
            
            lines[i] = "    taches_etape = etape.taches_etape.all().order_by('-date_creation')\n"
            
            print(f"   Après: {lines[i].strip()}")
            corrections += 1
    
    if corrections > 0:
        # Sauvegarder
        with open('core/views.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ {corrections} correction(s) appliquée(s)")
    else:
        print("✅ Aucune correction nécessaire")

if __name__ == "__main__":
    fix_toutes_lignes()