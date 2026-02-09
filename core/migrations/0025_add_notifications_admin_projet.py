# Generated manually on 2026-02-09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_add_systeme_maintenance'),
    ]

    operations = [
        migrations.AddField(
            model_name='projet',
            name='notifications_admin_activees',
            field=models.BooleanField(
                default=False,
                help_text="Si activé, l'administrateur recevra les notifications liées à ce projet (étapes terminées, tâches importantes, etc.)"
            ),
        ),
    ]
