#!/usr/bin/env python3
"""
Script pour corriger les URLs dans le template gestion_etapes.html
"""

def fix_urls():
    """Corrige les URLs dans le template"""
    
    # Lire le fichier
    with open('templates/core/gestion_etapes.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer toutes les occurrences
    new_content = content.replace('gestion_taches_etape_view', 'gestion_taches_etape')
    
    # Écrire le fichier corrigé
    with open('templates/core/gestion_etapes.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ URLs corrigées dans le template gestion_etapes.html")

if __name__ == '__main__':
    fix_urls()