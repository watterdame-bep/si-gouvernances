# Generated manually on 2026-02-09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_add_projet_timing_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationProjet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_notification', models.CharField(choices=[
                    ('AFFECTATION_RESPONSABLE', 'Affectation comme responsable'),
                    ('PROJET_DEMARRE', 'Projet démarré'),
                    ('ALERTE_FIN_PROJET', 'Alerte fin de projet (J-7)'),
                    ('PROJET_TERMINE', 'Projet terminé'),
                    ('PROJET_SUSPENDU', 'Projet suspendu'),
                    ('CHANGEMENT_ECHEANCE', "Changement d'échéance"),
                ], max_length=30)),
                ('titre', models.CharField(help_text='Titre de la notification', max_length=200)),
                ('message', models.TextField(help_text='Contenu de la notification')),
                ('lue', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_lecture', models.DateTimeField(blank=True, null=True)),
                ('donnees_contexte', models.JSONField(blank=True, help_text='Données contextuelles', null=True)),
                ('destinataire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_projets', to=settings.AUTH_USER_MODEL)),
                ('emetteur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='notifications_projets_emises', to=settings.AUTH_USER_MODEL)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.projet')),
            ],
            options={
                'verbose_name': 'Notification de Projet',
                'verbose_name_plural': 'Notifications de Projets',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.AddIndex(
            model_name='notificationprojet',
            index=models.Index(fields=['destinataire', 'lue', '-date_creation'], name='core_notifi_destina_idx'),
        ),
        migrations.AddIndex(
            model_name='notificationprojet',
            index=models.Index(fields=['projet', '-date_creation'], name='core_notifi_projet_idx'),
        ),
    ]
