# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0041_add_contrat_expiration_alert_type'),
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
                    ('CONTRAT_EXPIRE', 'Contrat expiré'),
                ],
                max_length=30
            ),
        ),
    ]
