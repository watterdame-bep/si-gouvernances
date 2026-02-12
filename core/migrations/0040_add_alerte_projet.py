# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_add_fichier_description_projet'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlerteProjet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_alerte', models.CharField(choices=[('ECHEANCE_J7', 'Échéance dans 7 jours'), ('ECHEANCE_J3', 'Échéance dans 3 jours'), ('ECHEANCE_J1', 'Échéance dans 1 jour'), ('ECHEANCE_DEPASSEE', 'Échéance dépassée'), ('BUDGET_DEPASSE', 'Budget dépassé'), ('TACHES_EN_RETARD', 'Tâches en retard')], max_length=30)),
                ('niveau', models.CharField(choices=[('INFO', 'Information'), ('WARNING', 'Avertissement'), ('DANGER', 'Critique')], default='WARNING', max_length=10)),
                ('titre', models.CharField(help_text="Titre de l'alerte", max_length=200)),
                ('message', models.TextField(help_text="Contenu de l'alerte")),
                ('lue', models.BooleanField(default=False)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_lecture', models.DateTimeField(blank=True, null=True)),
                ('donnees_contexte', models.JSONField(blank=True, help_text='Données contextuelles (jours restants, etc.)', null=True)),
                ('destinataire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertes_projets', to=settings.AUTH_USER_MODEL)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertes', to='core.projet')),
            ],
            options={
                'verbose_name': 'Alerte de Projet',
                'verbose_name_plural': 'Alertes de Projets',
                'ordering': ['-date_creation'],
                'indexes': [
                    models.Index(fields=['destinataire', 'lue', '-date_creation'], name='core_alerte_destina_idx'),
                    models.Index(fields=['projet', '-date_creation'], name='core_alerte_projet_idx'),
                    models.Index(fields=['type_alerte', '-date_creation'], name='core_alerte_type_al_idx'),
                ],
            },
        ),
    ]
