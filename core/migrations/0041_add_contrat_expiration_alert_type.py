# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_add_alerte_projet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerteprojet',
            name='type_alerte',
            field=models.CharField(
                choices=[
                    ('ECHEANCE_J7', 'Échéance dans 7 jours'),
                    ('ECHEANCE_J3', 'Échéance dans 3 jours'),
                    ('ECHEANCE_J1', 'Échéance dans 1 jour'),
                    ('ECHEANCE_DEPASSEE', 'Échéance dépassée'),
                    ('BUDGET_DEPASSE', 'Budget dépassé'),
                    ('TACHES_EN_RETARD', 'Tâches en retard'),
                    ('CONTRAT_EXPIRATION', 'Contrat proche expiration'),
                ],
                max_length=30
            ),
        ),
    ]
