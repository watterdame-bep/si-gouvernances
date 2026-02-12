# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_add_module_cloture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationetape',
            name='type_notification',
            field=models.CharField(
                choices=[
                    ('ETAPE_TERMINEE', 'Étape terminée'),
                    ('ETAPE_ACTIVEE', 'Étape activée'),
                    ('MODULES_DISPONIBLES', 'Modules disponibles'),
                    ('RETARD_ETAPE', "Retard d'étape"),
                    ('CHANGEMENT_STATUT', 'Changement de statut'),
                    ('CAS_TEST_PASSE', 'Cas de test passé'),
                ],
                max_length=20
            ),
        ),
    ]
