"""
Vérifier la structure de la table core_castest dans la base de données
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.db import connection

def check_table():
    print("=" * 80)
    print("VÉRIFICATION DE LA TABLE core_castest")
    print("=" * 80)
    
    with connection.cursor() as cursor:
        # Vérifier si la table existe
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = DATABASE()
            AND table_name = 'core_castest'
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            print("\n✓ La table core_castest existe")
            
            # Lister les colonnes
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM information_schema.COLUMNS
                WHERE table_schema = DATABASE()
                AND table_name = 'core_castest'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print(f"\n✓ {len(columns)} colonnes trouvées:\n")
            print(f"{'Colonne':<30} {'Type':<20} {'Nullable':<10} {'Clé':<10}")
            print("-" * 80)
            for col in columns:
                print(f"{col[0]:<30} {col[1]:<20} {col[2]:<10} {col[3]:<10}")
            
            # Vérifier spécifiquement tache_test_id
            print("\n" + "=" * 80)
            has_tache_test_id = any(col[0] == 'tache_test_id' for col in columns)
            has_tache_etape_id = any(col[0] == 'tache_etape_id' for col in columns)
            
            if has_tache_test_id:
                print("✓ La colonne 'tache_test_id' existe")
            else:
                print("❌ La colonne 'tache_test_id' N'EXISTE PAS")
            
            if has_tache_etape_id:
                print("✓ La colonne 'tache_etape_id' existe")
            else:
                print("⚠ La colonne 'tache_etape_id' n'existe pas")
            
            # Compter les enregistrements
            cursor.execute("SELECT COUNT(*) FROM core_castest")
            count = cursor.fetchone()[0]
            print(f"\n✓ {count} enregistrement(s) dans la table")
            
        else:
            print("\n❌ La table core_castest N'EXISTE PAS dans la base de données")
            print("\n⚠ Le modèle CasTest existe dans le code mais n'a jamais été migré")
            print("⚠ Il faut créer et appliquer une migration")

if __name__ == '__main__':
    check_table()
