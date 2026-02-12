# Migration pour ajouter le champ ManyToMany assignes_a

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_add_maintenance_v2_fields'),
    ]

    operations = [
        # Ajouter le champ ManyToMany assignes_a
        migrations.AddField(
            model_name='ticketmaintenance',
            name='assignes_a',
            field=models.ManyToManyField(
                blank=True,
                related_name='tickets_assignes_v2',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Assigné à'
            ),
        ),
    ]
