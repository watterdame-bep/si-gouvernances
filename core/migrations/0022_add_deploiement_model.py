# Generated migration for Deploiement model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_add_deploiement_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deploiement',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', models.CharField(max_length=50, verbose_name='Version')),
                ('environnement', models.CharField(
                    choices=[
                        ('DEV', 'Développement'),
                        ('TEST', 'Test'),
                        ('PREPROD', 'Pré-production'),
                        ('PROD', 'Production')
                    ],
                    max_length=20,
                    verbose_name='Environnement'
                )),
                ('description', models.TextField(verbose_name='Description')),
                ('statut', models.CharField(
                    choices=[
                        ('PREVU', 'Prévu'),
                        ('EN_COURS', 'En cours'),
                        ('REUSSI', 'Réussi'),
                        ('ECHEC', 'Échec'),
                        ('ANNULE', 'Annulé')
                    ],
                    default='PREVU',
                    max_length=20
                )),
                ('priorite', models.CharField(
                    choices=[
                        ('BASSE', 'Basse'),
                        ('NORMALE', 'Normale'),
                        ('HAUTE', 'Haute'),
                        ('CRITIQUE', 'Critique')
                    ],
                    default='NORMALE',
                    max_length=20
                )),
                ('date_prevue', models.DateTimeField(blank=True, null=True)),
                ('date_debut', models.DateTimeField(blank=True, null=True)),
                ('date_fin', models.DateTimeField(blank=True, null=True)),
                ('date_autorisation', models.DateTimeField(blank=True, null=True)),
                ('logs_deploiement', models.TextField(blank=True)),
                ('commentaires', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('tache_deploiement', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='deploiements',
                    to='core.tacheetape',
                    verbose_name='Tâche de déploiement'
                )),
                ('responsable', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='deploiements_responsable',
                    to=settings.AUTH_USER_MODEL
                )),
                ('executant', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='deploiements_executes',
                    to=settings.AUTH_USER_MODEL
                )),
                ('autorise_par', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='deploiements_autorises',
                    to=settings.AUTH_USER_MODEL
                )),
                ('incident_cree', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='deploiement_origine_incident',
                    to='core.tacheetape'
                )),
                ('createur', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='deploiements_crees',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'Déploiement',
                'verbose_name_plural': 'Déploiements',
                'ordering': ['-date_creation'],
            },
        ),
    ]
