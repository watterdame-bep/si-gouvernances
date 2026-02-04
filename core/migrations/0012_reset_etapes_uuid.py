# Generated manually

from django.db import migrations
from django.db import connection

def reset_etapes_with_uuid(apps, schema_editor):
    """Supprime toutes les étapes existantes pour permettre la recréation avec UUID"""
    with connection.cursor() as cursor:
        # Supprimer dans l'ordre des dépendances
        cursor.execute("DELETE FROM core_tacheetape")
        cursor.execute("DELETE FROM core_tachemodule") 
        cursor.execute("DELETE FROM core_moduleprojet")
        cursor.execute("DELETE FROM core_etapeprojet")

def reverse_reset_etapes(apps, schema_editor):
    """Fonction de retour - ne fait rien car on ne peut pas récupérer les données"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_etapeprojet_id_alter_tacheetape_id'),
    ]

    operations = [
        migrations.RunPython(reset_etapes_with_uuid, reverse_reset_etapes),
    ]