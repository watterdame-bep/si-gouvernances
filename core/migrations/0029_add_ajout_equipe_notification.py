# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_add_notification_projet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationprojet',
            name='type_notification',
            field=models.CharField(
                choices=[
                    ('AFFECTATION_RESPONSABLE', 'Affectation comme responsable'),
                    ('AJOUT_EQUIPE', "Ajout à l'équipe du projet"),
                    ('PROJET_DEMARRE', 'Projet démarré'),
                    ('ALERTE_FIN_PROJET', 'Alerte fin de projet (J-7)'),
                    ('PROJET_TERMINE', 'Projet terminé'),
                    ('PROJET_SUSPENDU', 'Projet suspendu'),
                    ('CHANGEMENT_ECHEANCE', "Changement d'échéance"),
                ],
                max_length=30
            ),
        ),
    ]
