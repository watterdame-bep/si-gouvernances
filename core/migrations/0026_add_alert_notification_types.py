# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_add_notifications_admin_projet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtache',
            name='type_notification',
            field=models.CharField(
                choices=[
                    ('ASSIGNATION', 'Assignation de tâche'),
                    ('CHANGEMENT_STATUT', 'Changement de statut'),
                    ('COMMENTAIRE', 'Nouveau commentaire'),
                    ('MENTION', 'Mention dans un commentaire'),
                    ('ECHEANCE', 'Échéance approchante'),
                    ('RETARD', 'Tâche en retard'),
                    ('PIECE_JOINTE', 'Nouvelle pièce jointe'),
                    ('ALERTE_ECHEANCE', 'Alerte échéance (2j ou 1j)'),
                    ('ALERTE_CRITIQUE', 'Alerte critique (jour J)'),
                    ('ALERTE_RETARD', 'Alerte retard'),
                ],
                max_length=20
            ),
        ),
    ]
