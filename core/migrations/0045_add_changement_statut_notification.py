# Generated manually on 2026-02-14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_rename_core_accoun_user_id_created_at_idx_core_accoun_user_id_70ef7b_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationmodule',
            name='type_notification',
            field=models.CharField(
                choices=[
                    ('AFFECTATION_MODULE', 'Affectation au module'),
                    ('RETRAIT_MODULE', 'Retrait du module'),
                    ('NOUVELLE_TACHE', 'Nouvelle tâche assignée'),
                    ('TACHE_TERMINEE', 'Tâche terminée'),
                    ('CHANGEMENT_ROLE', 'Changement de rôle'),
                    ('MODULE_TERMINE', 'Module terminé'),
                    ('CHANGEMENT_STATUT', 'Changement de statut de tâche'),
                ],
                max_length=20
            ),
        ),
    ]
