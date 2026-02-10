# Migration pour ajouter le statut EN_PAUSE

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_add_progression_taches'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tacheetape',
            name='statut',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('A_FAIRE', 'À faire'),
                    ('EN_COURS', 'En cours'),
                    ('EN_PAUSE', 'En pause'),
                    ('TERMINEE', 'Terminée'),
                ],
                default='A_FAIRE'
            ),
        ),
        migrations.AlterField(
            model_name='tachemodule',
            name='statut',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('A_FAIRE', 'À faire'),
                    ('EN_COURS', 'En cours'),
                    ('EN_PAUSE', 'En pause'),
                    ('TERMINEE', 'Terminée'),
                ],
                default='A_FAIRE'
            ),
        ),
    ]
