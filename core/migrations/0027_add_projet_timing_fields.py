# Generated manually on 2026-02-09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_add_alert_notification_types'),
    ]

    operations = [
        # Ajouter le champ durée du projet (en jours)
        migrations.AddField(
            model_name='projet',
            name='duree_projet',
            field=models.IntegerField(
                null=True,
                blank=True,
                help_text="Durée prévue du projet en jours",
                verbose_name="Durée du projet (jours)"
            ),
        ),
        
        # Ajouter le champ date de début (NULL tant que non démarré)
        migrations.AddField(
            model_name='projet',
            name='date_debut',
            field=models.DateField(
                null=True,
                blank=True,
                help_text="Date de démarrage effectif du projet",
                verbose_name="Date de début"
            ),
        ),
        
        # Ajouter le champ date de fin (calculée automatiquement au démarrage)
        migrations.AddField(
            model_name='projet',
            name='date_fin',
            field=models.DateField(
                null=True,
                blank=True,
                help_text="Date de fin prévue du projet (calculée automatiquement)",
                verbose_name="Date de fin prévue"
            ),
        ),
        
        # Ajouter un index sur date_fin pour les requêtes d'alertes
        migrations.AddIndex(
            model_name='projet',
            index=models.Index(fields=['date_fin', 'statut'], name='core_projet_date_fin_idx'),
        ),
    ]
