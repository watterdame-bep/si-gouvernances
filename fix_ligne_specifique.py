#!/usr/bin/env python
"""
Correction spécifique de la ligne problématique
"""

def fix_ligne_specifique():
    print("🔧 CORRECTION : Ligne spécifique problématique")
    print("=" * 50)
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Chercher et corriger la ligne problématique
    for i, line in enumerate(lines):
        if 'taches_etape.order_by(' in line and 'taches_etape =' not in line:
            print(f"🔍 Ligne {i+1} problématique trouvée:")
            print(f"   Avant: {line.strip()}")
            
            # Corriger la ligne
            lines[i] = "    taches_etape = etape.taches_etape.all().order_by('-date_creation')\n"
            
            print(f"   Après: {lines[i].strip()}")
            break
    
    # Sauvegarder
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ Correction appliquée")

if __name__ == "__main__":
    fix_ligne_specifique()