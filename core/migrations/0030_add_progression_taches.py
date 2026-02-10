# Generated migration for adding progression field to TacheModule

from django.db import migrations, models
from django.core.validators import MaxValueValidator


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_add_ajout_equipe_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='tachemodule',
            name='pourcentage_completion',
            field=models.PositiveIntegerField(
                default=0,
                validators=[MaxValueValidator(100)],
                help_text='Pourcentage de completion de la tâche (0-100)'
            ),
        ),
    ]
