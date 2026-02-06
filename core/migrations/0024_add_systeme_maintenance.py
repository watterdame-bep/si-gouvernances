# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_remove_old_deploiement_fields'),
    ]

    operations = [
        # Contrat de Garantie
        migrations.CreateModel(
            name='ContratGarantie',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('type_garantie', models.CharField(choices=[('CORRECTIVE', 'Maintenance Corrective'), ('EVOLUTIVE', 'Maintenance Évolutive')], max_length=20)),
                ('date_debut', models.DateField(verbose_name='Date de début')),
                ('date_fin', models.DateField(verbose_name='Date de fin')),
                ('sla_heures', models.IntegerField(help_text='Temps de réponse maximum en heures', verbose_name='SLA en heures')),
                ('description_couverture', models.TextField(help_text='Détails sur ce qui est couvert par la garantie', verbose_name='Description de la couverture')),
                ('exclusions', models.TextField(blank=True, help_text="Ce qui n'est PAS couvert par la garantie", verbose_name='Exclusions')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('cree_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contrats_crees', to=settings.AUTH_USER_MODEL)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contrats_garantie', to='core.projet')),
            ],
            options={
                'verbose_name': 'Contrat de Garantie',
                'verbose_name_plural': 'Contrats de Garantie',
                'ordering': ['-date_debut'],
            },
        ),
        
        # Ticket de Maintenance
        migrations.CreateModel(
            name='TicketMaintenance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_ticket', models.CharField(editable=False, max_length=20, unique=True)),
                ('titre', models.CharField(max_length=200, verbose_name='Titre du problème')),
                ('description_probleme', models.TextField(verbose_name='Description détaillée')),
                ('gravite', models.CharField(choices=[('MINEUR', 'Mineur'), ('MAJEUR', 'Majeur'), ('CRITIQUE', 'Critique')], max_length=20)),
                ('origine', models.CharField(choices=[('CLIENT', 'Client'), ('MONITORING', 'Monitoring'), ('INTERNE', 'Interne')], max_length=20)),
                ('statut', models.CharField(choices=[('OUVERT', 'Ouvert'), ('EN_COURS', 'En cours'), ('RESOLU', 'Résolu'), ('FERME', 'Fermé'), ('REJETE', 'Rejeté')], default='OUVERT', max_length=20)),
                ('est_payant', models.BooleanField(default=False, help_text='True si hors garantie ou garantie inactive', verbose_name='Intervention payante')),
                ('raison_rejet', models.TextField(blank=True, help_text='Pourquoi le ticket a été rejeté', verbose_name='Raison du rejet')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_resolution', models.DateTimeField(blank=True, null=True)),
                ('date_fermeture', models.DateTimeField(blank=True, null=True)),
                ('assigne_a', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets_assignes', to=settings.AUTH_USER_MODEL)),
                ('contrat_garantie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets', to='core.contratgarantie')),
                ('cree_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets_crees', to=settings.AUTH_USER_MODEL)),
                ('projet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_maintenance', to='core.projet')),
            ],
            options={
                'verbose_name': 'Ticket de Maintenance',
                'verbose_name_plural': 'Tickets de Maintenance',
                'ordering': ['-date_creation'],
            },
        ),
        
        # Billet d'Intervention
        migrations.CreateModel(
            name='BilletIntervention',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_billet', models.CharField(editable=False, max_length=20, unique=True)),
                ('type_intervention', models.CharField(choices=[('ANALYSE', 'Analyse du problème'), ('CORRECTION', 'Correction'), ('DEPLOIEMENT_CORRECTIF', 'Déploiement correctif')], max_length=30)),
                ('duree_estimee', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Durée estimée (heures)')),
                ('date_autorisation', models.DateTimeField(auto_now_add=True)),
                ('instructions', models.TextField(blank=True, help_text='Consignes pour le développeur', verbose_name='Instructions spécifiques')),
                ('autorise_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billets_autorises_par', to=settings.AUTH_USER_MODEL)),
                ('developpeur_autorise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billets_autorises', to=settings.AUTH_USER_MODEL)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billets_intervention', to='core.ticketmaintenance')),
            ],
            options={
                'verbose_name': "Billet d'Intervention",
                'verbose_name_plural': "Billets d'Intervention",
                'ordering': ['-date_autorisation'],
            },
        ),
        
        # Intervention de Maintenance
        migrations.CreateModel(
            name='InterventionMaintenance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description_actions', models.TextField(verbose_name='Description des actions effectuées')),
                ('date_debut', models.DateTimeField(verbose_name='Date de début')),
                ('date_fin', models.DateTimeField(blank=True, null=True, verbose_name='Date de fin')),
                ('temps_passe', models.DecimalField(decimal_places=2, help_text="Temps réel passé sur l'intervention", max_digits=5, verbose_name='Temps passé (heures)')),
                ('correctif_applique', models.TextField(blank=True, help_text='Détails techniques du correctif', verbose_name='Correctif appliqué')),
                ('fichiers_modifies', models.TextField(blank=True, help_text='Liste des fichiers modifiés', verbose_name='Fichiers modifiés')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('billet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interventions', to='core.billetintervention')),
            ],
            options={
                'verbose_name': 'Intervention de Maintenance',
                'verbose_name_plural': 'Interventions de Maintenance',
                'ordering': ['-date_debut'],
            },
        ),
        
        # Statut Technique
        migrations.CreateModel(
            name='StatutTechnique',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('probleme_initial', models.TextField(help_text='Description du problème tel que rapporté', verbose_name='Problème initial')),
                ('cause_reelle', models.TextField(help_text='Analyse de la cause racine du problème', verbose_name='Cause réelle (Root Cause)')),
                ('solution_apportee', models.TextField(help_text='Description détaillée de la solution', verbose_name='Solution apportée')),
                ('impact_systeme', models.TextField(help_text='Quels composants sont affectés', verbose_name='Impact sur le système')),
                ('risques_futurs', models.TextField(blank=True, help_text="Risques identifiés pour l'avenir", verbose_name='Risques futurs')),
                ('recommandations', models.TextField(blank=True, help_text='Actions préventives recommandées', verbose_name='Recommandations')),
                ('date_validation', models.DateTimeField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('intervention', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statut_technique', to='core.interventionmaintenance')),
                ('redige_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statuts_rediges', to=settings.AUTH_USER_MODEL)),
                ('valide_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statuts_valides', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Statut Technique',
                'verbose_name_plural': 'Statuts Techniques',
                'ordering': ['-date_creation'],
            },
        ),
    ]
