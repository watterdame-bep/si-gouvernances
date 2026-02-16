# Generated migration for LigneBudget model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_fix_audit_projet_deletion'),
    ]

    operations = [
        migrations.CreateModel(
            name='LigneBudget',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type_ligne', models.CharField(choices=[('MATERIEL', 'Matériel'), ('SERVICE', 'Service')], max_length=20, verbose_name='Type de dépense')),
                ('montant', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Montant')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('date_ajout', models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")),
                ('ajoute_par', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lignes_budget_ajoutees', to=settings.AUTH_USER_MODEL)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes_budget', to='core.projet')),
            ],
            options={
                'verbose_name': 'Ligne Budgétaire',
                'verbose_name_plural': 'Lignes Budgétaires',
                'ordering': ['-date_ajout'],
            },
        ),
        migrations.AddIndex(
            model_name='lignebudget',
            index=models.Index(fields=['projet', 'type_ligne'], name='core_ligneb_projet__idx'),
        ),
        migrations.AddIndex(
            model_name='lignebudget',
            index=models.Index(fields=['date_ajout'], name='core_ligneb_date_aj_idx'),
        ),
    ]
