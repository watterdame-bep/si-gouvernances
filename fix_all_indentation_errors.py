#!/usr/bin/env python3
"""
Script pour corriger toutes les erreurs d'indentation dans models.py
"""

import re

def fix_indentation_errors():
    """Corriger toutes les erreurs d'indentation dans models.py"""
    
    print("🔧 Correction des erreurs d'indentation dans models.py")
    print("=" * 60)
    
    try:
        # Lire le fichier
        with open('core/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns à corriger
        patterns = [
            # Méthodes mal indentées dans les classes
            (r'(\n    class Meta:.*?\n)\s{8}def ', r'\1    def '),
            (r'(\n    )\s{4}def ', r'\1def '),
            # Corriger les méthodes qui commencent par 8 espaces au lieu de 4
            (r'\n        def ([^:]+):\n        """', r'\n    def \1:\n        """'),
            (r'\n        def ([^:]+):\n        ([^"])', r'\n    def \1:\n        \2'),
            # Corriger les méthodes sans docstring
            (r'\n        def ([^:]+):\n        ([^"\s])', r'\n    def \1:\n        \2'),
        ]
        
        # Appliquer les corrections
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Corrections spécifiques pour les méthodes communes
        specific_fixes = [
            # __str__ methods
            ('    class Meta:\n        verbose_name', '    class Meta:\n        verbose_name'),
            ('    \n        def __str__(self):', '    \n    def __str__(self):'),
            ('    \n        def clean(self):', '    \n    def clean(self):'),
            ('    \n        def save(self, *args, **kwargs):', '    \n    def save(self, *args, **kwargs):'),
            ('    \n        def get_', '    \n    def get_'),
            ('    \n        def peut_', '    \n    def peut_'),
            ('    \n        def a_', '    \n    def a_'),
            ('    \n        def est_', '    \n    def est_'),
            ('    \n        @property', '    \n    @property'),
        ]
        
        for old, new in specific_fixes:
            content = content.replace(old, new)
        
        # Écrire le fichier corrigé
        with open('core/models.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Corrections appliquées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    success = fix_indentation_errors()
    
    if success:
        print("\n🎯 Prochaines étapes:")
        print("1. Vérifier la syntaxe: python -m py_compile core/models.py")
        print("2. Appliquer la migration: python manage.py migrate")
        print("3. Tester la hiérarchie CasTest")
    else:
        print("\n❌ Échec de la correction automatique")
        print("Correction manuelle nécessaire")