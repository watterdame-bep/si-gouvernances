# Generated migration for deployment functionality

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0020_castest_notificationetape_cas_test_and_more'),
    ]

    operations = [
        # Ajouter statut ECHEC
        migrations.AlterField(
            model_name='tacheetape',
            name='statut',
            field=models.CharField(
                choices=[
                    ('A_FAIRE', 'À faire'),
                    ('EN_COURS', 'En cours'),
                    ('TERMINEE', 'Terminée'),
                    ('BLOQUEE', 'Bloquée'),
                    ('ECHEC', 'Échec')
                ],
                default='A_FAIRE',
                max_length=20
            ),
        ),
        
        # Champs spécifiques déploiement
        migrations.AddField(
            model_name='tacheetape',
            name='version_deploiement',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name='Version à déployer',
                help_text='Ex: v1.2.0, 2024.02.06'
            ),
        ),
        migrations.AddField(
            model_name='tacheetape',
            name='environnement_deploiement',
            field=models.CharField(
                blank=True,
                choices=[
                    ('DEV', 'Développement'),
                    ('TEST', 'Test'),
                    ('PREPROD', 'Pré-production'),
                    ('PROD', 'Production')
                ],
                max_length=20,
                null=True,
                verbose_name='Environnement cible'
            ),
        ),
        migrations.AddField(
            model_name='tacheetape',
            name='logs_deploiement',
            field=models.TextField(
                blank=True,
                null=True,
                verbose_name='Logs de déploiement',
                help_text='Détails techniques du déploiement'
            ),
        ),
        migrations.AddField(
            model_name='tacheetape',
            name='deploiement_autorise_par',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='deploiements_autorises',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Autorisé par'
            ),
        ),
        migrations.AddField(
            model_name='tacheetape',
            name='date_autorisation_deploiement',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Date d\'autorisation'
            ),
        ),
    ]
