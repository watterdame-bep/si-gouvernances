#!/usr/bin/env python3
"""
Script pour corriger les conflits de related_name dans les modèles
"""

import os
import re

def fix_related_names():
    """Corriger les conflits de related_name dans core/models.py"""
    
    print("🔧 Correction des conflits de related_name")
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
        
        # Corrections des related_name pour éviter les conflits
        corrections = [
            # Dans BugTest, changer la relation cas_test
            (
                r"cas_test = models\.ForeignKey\(\s*'CasTest',\s*on_delete=models\.CASCADE,\s*null=True,\s*blank=True,\s*related_name='bugs',",
                "cas_test = models.ForeignKey(\n        'CasTest', \n        on_delete=models.CASCADE, \n        null=True, \n        blank=True,\n        related_name='bugs_lies',"
            ),
            
            # Vérifier s'il y a d'autres champs cas_test et les renommer
            (
                r"(\w+)\.cas_test",
                r"\1.cas_test_field"
            )
        ]
        
        # Appliquer les corrections
        for pattern, replacement in corrections:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                print(f"✅ Correction appliquée: {pattern[:30]}...")
        
        # Vérifier s'il y a des champs cas_test dans d'autres modèles et les corriger
        # Chercher tous les modèles qui ont un champ cas_test
        models_with_cas_test = re.findall(r'class (\w+)\(.*?\):.*?cas_test = models\.', content, re.DOTALL)
        
        if models_with_cas_test:
            print(f"⚠️  Modèles avec champ cas_test trouvés: {models_with_cas_test}")
            
            # Pour chaque modèle trouvé, changer le related_name
            for model_name in models_with_cas_test:
                if model_name != 'BugTest':  # On a déjà traité BugTest
                    pattern = f'(class {model_name}.*?cas_test = models\.ForeignKey.*?related_name=\')([^\']+)(\',)'
                    replacement = f'\\1{model_name.lower()}_cas_tests\\3'
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    print(f"✅ Related_name corrigé pour {model_name}")
        
        # Écrire le fichier corrigé
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier core/models.py corrigé avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def check_for_conflicts():
    """Vérifier s'il reste des conflits potentiels"""
    
    print("\n🔍 Vérification des conflits potentiels")
    print("=" * 40)
    
    models_file = 'core/models.py'
    
    try:
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher tous les related_name
        related_names = re.findall(r"related_name='([^']+)'", content)
        
        # Compter les occurrences
        from collections import Counter
        name_counts = Counter(related_names)
        
        conflicts = {name: count for name, count in name_counts.items() if count > 1}
        
        if conflicts:
            print("❌ Conflits détectés:")
            for name, count in conflicts.items():
                print(f"   - '{name}': {count} occurrences")
            return False
        else:
            print("✅ Aucun conflit de related_name détecté")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Correction des conflits de related_name")
    print("=" * 60)
    
    success1 = fix_related_names()
    success2 = check_for_conflicts()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ CORRECTIONS APPLIQUÉES AVEC SUCCÈS!")
        print("\n💡 Prochaines étapes:")
        print("   1. Tester la création de migration:")
        print("      python manage.py makemigrations")
        print("   2. Appliquer la migration:")
        print("      python manage.py migrate")
    else:
        print("❌ CORRECTIONS PARTIELLES OU ÉCHEC")
        print("Vérifiez les erreurs ci-dessus.")