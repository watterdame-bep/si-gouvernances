#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

print("🔍 Vérification complète du modèle AffectationModule...")

# 1. Vérifier si le modèle existe dans models.py
print("\n1. Vérification dans models.py:")
try:
    with open('core/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'class AffectationModule' in content:
            print("✅ Classe AffectationModule trouvée dans models.py")
        else:
            print("❌ Classe AffectationModule NOT trouvée dans models.py")
except Exception as e:
    print(f"❌ Erreur lecture models.py: {e}")

# 2. Vérifier l'import
print("\n2. Test d'import:")
try:
    from core.models import AffectationModule
    print("✅ Import réussi")
    print(f"✅ Classe: {AffectationModule}")
    print(f"✅ Table DB: {AffectationModule._meta.db_table}")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Autre erreur: {e}")

# 3. Vérifier la table en base de données
print("\n3. Vérification table en base:")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%affectation%';")
        tables = cursor.fetchall()
        print(f"✅ Tables avec 'affectation': {tables}")
        
        # Vérifier spécifiquement core_affectationmodule
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_affectationmodule';")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Table core_affectationmodule existe")
            
            # Vérifier la structure
            cursor.execute("PRAGMA table_info(core_affectationmodule);")
            columns = cursor.fetchall()
            print(f"✅ Colonnes: {[col[1] for col in columns]}")
        else:
            print("❌ Table core_affectationmodule N'EXISTE PAS")
            
except Exception as e:
    print(f"❌ Erreur DB: {e}")

# 4. Vérifier les migrations
print("\n4. Vérification migrations:")
try:
    from django.core.management import execute_from_command_line
    import subprocess
    result = subprocess.run(['python', 'manage.py', 'showmigrations', 'core'], 
                          capture_output=True, text=True)
    print("Migrations core:")
    print(result.stdout)
except Exception as e:
    print(f"❌ Erreur migrations: {e}")

# 5. Test de création d'objet
print("\n5. Test création objet:")
try:
    from core.models import AffectationModule, ModuleProjet, Utilisateur
    
    # Compter les objets existants
    count = AffectationModule.objects.count()
    print(f"✅ Nombre d'affectations existantes: {count}")
    
    # Test de création (sans sauvegarder)
    test_obj = AffectationModule(role_module='CONTRIBUTEUR')
    print(f"✅ Objet test créé: {test_obj}")
    
except Exception as e:
    print(f"❌ Erreur création objet: {e}")

print("\n🎯 Diagnostic terminé!")