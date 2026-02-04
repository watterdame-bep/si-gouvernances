# Generated manually for role system migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # Supprimer le champ role_principal du modèle Utilisateur
        migrations.RemoveField(
            model_name='utilisateur',
            name='role_principal',
        ),
        
        # Améliorer le modèle Affectation
        migrations.AddField(
            model_name='affectation',
            name='notes',
            field=models.TextField(blank=True, help_text="Notes sur l'affectation"),
        ),
        
        # Ajouter des index pour les performances
        migrations.AddIndex(
            model_name='affectation',
            index=models.Index(fields=['utilisateur', 'projet', 'date_fin'], name='core_affectation_user_proj_end_idx'),
        ),
        
        migrations.AddIndex(
            model_name='affectation',
            index=models.Index(fields=['projet', 'date_fin'], name='core_affectation_proj_end_idx'),
        ),
        
        # Modifier le verbose_name du champ role_sur_projet
        migrations.AlterField(
            model_name='affectation',
            name='role_sur_projet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.role', verbose_name='Rôle sur le projet'),
        ),
    ]