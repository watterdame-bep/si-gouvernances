#!/usr/bin/env python
"""
Script pour supprimer la restriction admin dans modifier_profil_view
"""

def fix_admin_restriction():
    """Supprime la restriction admin dans core/views.py"""
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacements à effectuer
    replacements = [
        # Première occurrence
        (
            "    # Les administrateurs ne peuvent pas utiliser cette vue\n    if user.est_super_admin():\n        return JsonResponse({'success': False, 'error': 'Accès non autorisé pour les administrateurs'})",
            "    # Restriction admin supprimée - les administrateurs peuvent maintenant modifier leurs informations"
        ),
        # Deuxième occurrence (dans changer_mot_de_passe_view - on la garde)
        # Troisième occurrence potentielle
        (
            "if user.est_super_admin():\n        return JsonResponse({'success': False, 'error': 'Accès non autorisé pour les administrateurs'})",
            "# Restriction admin supprimée\n        # if user.est_super_admin():\n        #     return JsonResponse({'success': False, 'error': 'Accès non autorisé pour les administrateurs'})"
        )
    ]
    
    # Appliquer les remplacements
    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Remplacement effectué: {old[:50]}...")
    
    # Sauvegarder si modifié
    if modified:
        with open('core/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fichier core/views.py mis à jour")
        return True
    else:
        print("❌ Aucune modification nécessaire")
        return False

if __name__ == '__main__':
    print("🔧 Correction de la restriction admin dans modifier_profil_view")
    success = fix_admin_restriction()
    
    if success:
        print("🎉 Correction appliquée avec succès!")
        print("Les administrateurs peuvent maintenant modifier leurs informations de profil.")
    else:
        print("⚠️  Aucune correction appliquée")