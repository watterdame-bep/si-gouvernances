#!/usr/bin/env python
"""
Script pour corriger définitivement la fonction modifier_profil_view
"""
import re

def fix_modifier_profil_view():
    print("🔧 Correction de la fonction modifier_profil_view")
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Trouver la fonction modifier_profil_view
    pattern = r'(def modifier_profil_view\(request\):.*?)(        # Appliquer les modifications\s+user\.first_name = first_name\s+user\.last_name = last_name\s+user\.telephone = telephone\s+user\.save\(\))'
    
    replacement = r'''\1        # Stratégie de mise à jour selon le profil utilisateur
        if hasattr(user, 'membre') and user.membre:
            # Cas 1: L'utilisateur a un profil membre
            # Mettre à jour le membre et l'utilisateur de manière coordonnée
            membre = user.membre
            
            # Mettre à jour le membre
            membre.prenom = first_name
            membre.nom = last_name
            if telephone:
                membre.telephone = telephone
            membre.save()
            
            # Mettre à jour l'utilisateur en empêchant la synchronisation automatique
            user.first_name = first_name
            user.last_name = last_name
            user.telephone = telephone
            user.save(sync_from_membre=True)
        else:
            # Cas 2: L'utilisateur n'a pas de profil membre (admin sans profil)
            user.first_name = first_name
            user.last_name = last_name
            user.telephone = telephone
            user.save()
        
        # Recharger l'utilisateur pour s'assurer d'avoir les dernières données
        user.refresh_from_db()'''
    
    # Appliquer le remplacement
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        # Sauvegarder le fichier modifié
        with open('core/views.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Fonction modifier_profil_view corrigée avec succès")
        return True
    else:
        print("❌ Impossible de trouver le pattern à remplacer")
        
        # Essayer une approche plus simple
        print("🔍 Recherche manuelle du pattern...")
        
        # Chercher la ligne exacte
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'def modifier_profil_view' in line:
                print(f"Fonction trouvée à la ligne {i+1}")
                
                # Chercher la section à remplacer
                for j in range(i, min(len(lines), i+50)):
                    if '# Appliquer les modifications' in lines[j]:
                        print(f"Section trouvée à la ligne {j+1}")
                        
                        # Remplacer les 4 lignes suivantes
                        if (j+4 < len(lines) and 
                            'user.first_name = first_name' in lines[j+1] and
                            'user.last_name = last_name' in lines[j+2] and
                            'user.telephone = telephone' in lines[j+3] and
                            'user.save()' in lines[j+4]):
                            
                            # Remplacer ces lignes
                            new_lines = lines[:j] + [
                                '        # Stratégie de mise à jour selon le profil utilisateur',
                                '        if hasattr(user, \'membre\') and user.membre:',
                                '            # Cas 1: L\'utilisateur a un profil membre',
                                '            # Mettre à jour le membre et l\'utilisateur de manière coordonnée',
                                '            membre = user.membre',
                                '            ',
                                '            # Mettre à jour le membre',
                                '            membre.prenom = first_name',
                                '            membre.nom = last_name',
                                '            if telephone:',
                                '                membre.telephone = telephone',
                                '            membre.save()',
                                '            ',
                                '            # Mettre à jour l\'utilisateur en empêchant la synchronisation automatique',
                                '            user.first_name = first_name',
                                '            user.last_name = last_name',
                                '            user.telephone = telephone',
                                '            user.save(sync_from_membre=True)',
                                '        else:',
                                '            # Cas 2: L\'utilisateur n\'a pas de profil membre (admin sans profil)',
                                '            user.first_name = first_name',
                                '            user.last_name = last_name',
                                '            user.telephone = telephone',
                                '            user.save()',
                                '        ',
                                '        # Recharger l\'utilisateur pour s\'assurer d\'avoir les dernières données',
                                '        user.refresh_from_db()'
                            ] + lines[j+5:]
                            
                            # Sauvegarder
                            with open('core/views.py', 'w', encoding='utf-8') as f:
                                f.write('\n'.join(new_lines))
                            
                            print("✅ Correction manuelle réussie")
                            return True
                        break
                break
        
        print("❌ Impossible de corriger automatiquement")
        return False

if __name__ == '__main__':
    success = fix_modifier_profil_view()
    if success:
        print("\n🎉 La fonction modifier_profil_view a été corrigée !")
        print("📋 Changements apportés :")
        print("   • Gestion de la synchronisation utilisateur/membre")
        print("   • Support des admins avec et sans profil membre")
        print("   • Prévention des conflits de synchronisation")
    else:
        print("\n❌ Échec de la correction automatique")
        print("🔧 Correction manuelle nécessaire")