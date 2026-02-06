# Migration pour supprimer les anciens champs de déploiement de TacheEtape

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_deploiement_model'),
    ]

    operations = [
        # Supprimer les anciens champs de déploiement de TacheEtape
        migrations.RemoveField(
            model_name='tacheetape',
            name='version_deploiement',
        ),
        migrations.RemoveField(
            model_name='tacheetape',
            name='environnement_deploiement',
        ),
        migrations.RemoveField(
            model_name='tacheetape',
            name='logs_deploiement',
        ),
        migrations.RemoveField(
            model_name='tacheetape',
            name='deploiement_autorise_par',
        ),
        migrations.RemoveField(
            model_name='tacheetape',
            name='date_autorisation_deploiement',
        ),
    ]
