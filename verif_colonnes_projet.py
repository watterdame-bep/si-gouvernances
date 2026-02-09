import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SHOW COLUMNS FROM core_projet")
colonnes = cursor.fetchall()

print("Colonnes de la table core_projet :")
for col in colonnes:
    print(f"  - {col[0]}")

# Chercher spécifiquement nos colonnes
colonnes_noms = [col[0] for col in colonnes]
print("\nRecherche de nos colonnes :")
print(f"  duree_projet: {'✅ OUI' if 'duree_projet' in colonnes_noms else '❌ NON'}")
print(f"  date_debut: {'✅ OUI' if 'date_debut' in colonnes_noms else '❌ NON'}")
print(f"  date_fin: {'✅ OUI' if 'date_fin' in colonnes_noms else '❌ NON'}")
