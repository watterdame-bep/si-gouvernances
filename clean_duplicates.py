#!/usr/bin/env python3
"""
Script pour nettoyer les fonctions dupliquées dans views.py
"""
import re

def clean_duplicate_functions():
    """Nettoie les fonctions dupliquées dans core/views.py"""
    
    print("🧹 Nettoyage des fonctions dupliquées dans core/views.py")
    print("=" * 55)
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Taille du fichier: {len(content)} caractères")
    
    # Chercher les fonctions dupliquées
    pattern_creer_module = r'@login_required\s*\n@require_http_methods\(\["POST"\]\)\s*\ndef creer_module_view\(request, projet_id\):\s*\n\s*"""Créer un nouveau module"""'
    
    matches = list(re.finditer(pattern_creer_module, content, re.MULTILINE))
    print(f"🔍 Fonctions creer_module_view avec @require_http_methods trouvées: {len(matches)}")
    
    if matches:
        for i, match in enumerate(matches):
            start = match.start()
            print(f"   Match {i+1}: position {start}")
            
            # Trouver la fin de la fonction (prochaine fonction ou fin de fichier)
            # Chercher la prochaine définition de fonction
            next_func_pattern = r'\n@[a-zA-Z_]+\s*\ndef [a-zA-Z_]+\('
            next_match = re.search(next_func_pattern, content[start + len(match.group()):])
            
            if next_match:
                end = start + len(match.group()) + next_match.start()
                print(f"   Fin de fonction: position {end}")
                
                # Extraire la fonction
                func_content = content[start:end]
                print(f"   Taille de la fonction: {len(func_content)} caractères")
                print(f"   Aperçu: {func_content[:100]}...")
                
                # Supprimer la fonction
                content = content[:start] + content[end:]
                print(f"   ✅ Fonction supprimée")
            else:
                print(f"   ⚠️  Fin de fonction non trouvée")
    
    # Sauvegarder le fichier nettoyé
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"💾 Fichier sauvegardé - Nouvelle taille: {len(content)} caractères")
    print("✅ Nettoyage terminé")

if __name__ == '__main__':
    clean_duplicate_functions()