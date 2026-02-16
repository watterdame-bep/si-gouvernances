# Generated migration for FichierProjet model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_update_ligne_budget_description_required'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichierProjet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='projets/fichiers/%Y/%m/', verbose_name='Fichier')),
                ('nom_original', models.CharField(max_length=255, verbose_name='Nom du fichier')),
                ('taille', models.BigIntegerField(default=0, verbose_name='Taille (octets)')),
                ('type_mime', models.CharField(blank=True, max_length=100, verbose_name='Type MIME')),
                ('date_ajout', models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date d'ajout")),
                ('ajoute_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fichiers_ajoutes', to=settings.AUTH_USER_MODEL, verbose_name='Ajouté par')),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fichiers', to='core.projet')),
            ],
            options={
                'verbose_name': 'Fichier de projet',
                'verbose_name_plural': 'Fichiers de projet',
                'db_table': 'core_fichierprojet',
                'ordering': ['-date_ajout'],
            },
        ),
    ]
