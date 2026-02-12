# Generated migration for module closure functionality

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_add_statut_en_pause'),
    ]

    operations = [
        migrations.AddField(
            model_name='moduleprojet',
            name='est_cloture',
            field=models.BooleanField(default=False, help_text='Indique si le module est clôturé'),
        ),
        migrations.AddField(
            model_name='moduleprojet',
            name='date_cloture',
            field=models.DateTimeField(blank=True, null=True, help_text='Date de clôture du module'),
        ),
        migrations.AddField(
            model_name='moduleprojet',
            name='cloture_par',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='modules_clotures',
                to=settings.AUTH_USER_MODEL,
                help_text='Utilisateur ayant clôturé le module'
            ),
        ),
    ]
