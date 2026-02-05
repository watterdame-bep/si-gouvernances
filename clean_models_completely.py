#!/usr/bin/env python3
"""
Script pour nettoyer complètement le fichier models.py et supprimer les ajouts incorrects
"""

import os
import re

def clean_models_file():
    """Nettoyer complètement le fichier models.py"""
    
    print("🧹 Nettoyage complet du fichier models.py")
    print("=" * 50)
    
    models_file = 'core/models.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier models.py lu avec succès")
        
        # Supprimer tout ce qui a été ajouté incorrectement
        # Garder seulement le contenu jusqu'à TacheTest (inclus) et à partir de BugTest
        
        # Trouver la fin de TacheTest (sa méthode __str__)
        tachetest_pattern = r'(class TacheTest\(models\.Model\):.*?def __str__\(self\):.*?return.*?\n)'
        tachetest_match = re.search(tachetest_pattern, content, re.DOTALL)
        
        if not tachetest_match:
            print("❌ Classe TacheTest non trouvée")
            return False
        
        # Trouver le début de BugTest
        bugtest_pattern = r'(class BugTest\(models\.Model\):)'
        bugtest_match = re.search(bugtest_pattern, content)
        
        if not bugtest_match:
            print("❌ Classe BugTest non trouvée")
            return False
        
        # Reconstruire le contenu propre
        before_tachetest = content[:tachetest_match.start()]
        tachetest_content = tachetest_match.group(1)
        bugtest_and_after = content[bugtest_match.start():]
        
        # Nettoyer le contenu avant TacheTest (supprimer les méthodes mal placées)
        lines_before = before_tachetest.split('\n')
        cleaned_before = []
        
        i = 0
        while i < len(lines_before):
            line = lines_before[i]
            
            # Si on trouve une méthode mal placée avec "cas_test", l'ignorer
            if ('def mettre_a_jour_statut' in line or 
                'def statistiques_cas' in line or 
                'def progression_pourcentage' in line) and i > 0:
                print(f"⚠️  Méthode mal placée supprimée: {line.strip()}")
                # Ignorer cette méthode et les lignes suivantes jusqu'à la prochaine classe
                while i < len(lines_before) and not lines_before[i].strip().startswith('class '):
                    i += 1
                i -= 1  # Reculer d'une ligne pour ne pas ignorer la classe
            else:
                cleaned_before.append(line)
            
            i += 1
        
        # Reconstruire le contenu final
        clean_content = '\n'.join(cleaned_before) + tachetest_content + '\n\n' + bugtest_and_after
        
        # Supprimer les doublons de lignes vides
        clean_content = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_content)
        
        # Écrire le fichier nettoyé
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print("✅ Fichier models.py nettoyé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def add_castest_properly():
    """Ajouter le modèle CasTest proprement après le nettoyage"""
    
    print("\n🏗️ Ajout du modèle CasTest proprement")
    print("=" * 40)
    
    models_file = 'core/models.py'
    castest_file = 'core/models_castest.py'
    
    if not os.path.exists(castest_file):
        print(f"❌ Fichier {castest_file} non trouvé")
        return False
    
    try:
        # Lire le modèle CasTest
        with open(castest_file, 'r', encoding='utf-8') as f:
            castest_content = f.read()
        
        # Extraire seulement la classe CasTest (sans les imports)
        start_pos = castest_content.find('class CasTest(models.Model):')
        if start_pos == -1:
            print("❌ Classe CasTest non trouvée")
            return False
        
        castest_class = castest_content[start_pos:]
        
        # Lire le fichier models.py nettoyé
        with open(models_file, 'r', encoding='utf-8') as f:
            models_content = f.read()
        
        # Insérer CasTest avant BugTest
        if 'class BugTest(models.Model):' in models_content:
            insert_pos = models_content.find('class BugTest(models.Model):')
            new_content = (
                models_content[:insert_pos] + 
                '\n\n' + castest_class + '\n\n' + 
                models_content[insert_pos:]
            )
            
            # Écrire le fichier mis à jour
            with open(models_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Modèle CasTest ajouté avec succès")
            return True
        else:
            print("❌ Position d'insertion non trouvée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout: {str(e)}")
        return False

def test_final_syntax():
    """Test final de la syntaxe"""
    
    print("\n🔍 Test final de la syntaxe")
    print("=" * 30)
    
    try:
        with open('core/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, 'core/models.py', 'exec')
        print("✅ Syntaxe Python valide")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Nettoyage complet et ajout du modèle CasTest")
    print("=" * 60)
    
    success1 = clean_models_file()
    success2 = add_castest_properly() if success1 else False
    success3 = test_final_syntax() if success2 else False
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT FINAL")
    print("=" * 60)
    
    if success1 and success2 and success3:
        print("✅ NETTOYAGE ET AJOUT RÉUSSIS!")
        print("\n🏗️ Structure hiérarchique pour l'étape TEST:")
        print("   TacheTest (Sujet de test)")
        print("   └── CasTest (Cas de test individuel)")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Créer la migration:")
        print("      python manage.py makemigrations")
        print("   2. Appliquer la migration:")
        print("      python manage.py migrate")
        print("   3. Implémenter les vues hiérarchiques")
    else:
        print("❌ ÉCHEC DU NETTOYAGE")
        if not success1:
            print("   - Nettoyage du fichier échoué")
        if not success2:
            print("   - Ajout du modèle CasTest échoué")
        if not success3:
            print("   - Syntaxe Python invalide")