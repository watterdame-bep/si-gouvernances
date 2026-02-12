# Migration manuelle pour ajouter les champs de Maintenance V2

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_remove_projet_core_projet_date_fin_idx_and_more'),
    ]

    operations = [
        # Ajouter les nouveaux champs à TicketMaintenance
        migrations.AddField(
            model_name='ticketmaintenance',
            name='type_demande',
            field=models.CharField(
                choices=[
                    ('BUG', '🐛 Bug / Anomalie'),
                    ('AMELIORATION', '✨ Amélioration'),
                    ('QUESTION', '❓ Question / Support'),
                    ('AUTRE', '📋 Autre')
                ],
                default='BUG',
                max_length=20,
                verbose_name='Type de demande'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='priorite',
            field=models.CharField(
                choices=[
                    ('BASSE', 'Basse'),
                    ('NORMALE', 'Normale'),
                    ('HAUTE', 'Haute'),
                    ('CRITIQUE', 'Critique')
                ],
                default='NORMALE',
                max_length=20,
                verbose_name='Priorité'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='date_debut_travail',
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name='Date de début du travail'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='temps_estime',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Estimation initiale du temps nécessaire',
                max_digits=5,
                null=True,
                verbose_name='Temps estimé (heures)'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='temps_passe',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Temps réel passé sur le ticket',
                max_digits=5,
                verbose_name='Temps passé (heures)'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='solution',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Description de la solution et des actions effectuées',
                verbose_name='Solution apportée'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='fichiers_modifies',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Liste des fichiers modifiés (un par ligne)',
                verbose_name='Fichiers modifiés'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='est_sous_garantie',
            field=models.BooleanField(
                default=True,
                help_text='True si couvert par un contrat actif',
                verbose_name='Sous garantie'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='modifie_par',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tickets_modifies',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Modifié par'
            ),
        ),
        migrations.AddField(
            model_name='ticketmaintenance',
            name='date_modification',
            field=models.DateTimeField(
                auto_now=True,
                verbose_name='Date de modification'
            ),
        ),
        
        # Modifier le champ gravite pour ajouter BLOQUANT
        migrations.AlterField(
            model_name='ticketmaintenance',
            name='gravite',
            field=models.CharField(
                choices=[
                    ('MINEUR', 'Mineur - Impact faible'),
                    ('MAJEUR', 'Majeur - Impact modéré'),
                    ('CRITIQUE', 'Critique - Impact sévère'),
                    ('BLOQUANT', 'Bloquant - Système inutilisable')
                ],
                default='MAJEUR',
                max_length=20,
                verbose_name='Gravité'
            ),
        ),
        
        # Modifier le champ statut pour ajouter les emojis
        migrations.AlterField(
            model_name='ticketmaintenance',
            name='statut',
            field=models.CharField(
                choices=[
                    ('OUVERT', '🆕 Ouvert'),
                    ('EN_COURS', '🔵 En cours'),
                    ('RESOLU', '✅ Résolu'),
                    ('FERME', '🔒 Fermé'),
                    ('REJETE', '❌ Rejeté')
                ],
                default='OUVERT',
                max_length=20,
                verbose_name='Statut'
            ),
        ),
        
        # Créer le modèle CommentaireTicket
        migrations.CreateModel(
            name='CommentaireTicket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('contenu', models.TextField(verbose_name='Commentaire')),
                ('est_interne', models.BooleanField(
                    default=False,
                    help_text='Si True, visible seulement par l\'équipe technique',
                    verbose_name='Commentaire interne'
                )),
                ('fichier', models.FileField(
                    blank=True,
                    null=True,
                    upload_to='tickets/commentaires/',
                    verbose_name='Pièce jointe'
                )),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('modifie', models.BooleanField(default=False, verbose_name='Modifié')),
                ('date_modification', models.DateTimeField(blank=True, null=True, verbose_name='Date de modification')),
                ('auteur', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='commentaires_tickets',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Auteur'
                )),
                ('ticket', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='commentaires',
                    to='core.ticketmaintenance',
                    verbose_name='Ticket'
                )),
            ],
            options={
                'verbose_name': 'Commentaire de Ticket',
                'verbose_name_plural': 'Commentaires de Tickets',
                'ordering': ['date_creation'],
            },
        ),
        
        # Créer le modèle PieceJointeTicket
        migrations.CreateModel(
            name='PieceJointeTicket',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fichier', models.FileField(upload_to='tickets/pieces_jointes/', verbose_name='Fichier')),
                ('nom_fichier', models.CharField(max_length=255, verbose_name='Nom du fichier')),
                ('taille_fichier', models.IntegerField(verbose_name='Taille (octets)')),
                ('type_mime', models.CharField(blank=True, max_length=100, verbose_name='Type MIME')),
                ('description', models.TextField(
                    blank=True,
                    help_text='Description optionnelle de la pièce jointe',
                    verbose_name='Description'
                )),
                ('date_upload', models.DateTimeField(auto_now_add=True, verbose_name='Date d\'upload')),
                ('ticket', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pieces_jointes',
                    to='core.ticketmaintenance',
                    verbose_name='Ticket'
                )),
                ('uploade_par', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pieces_jointes_uploadees',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Uploadé par'
                )),
            ],
            options={
                'verbose_name': 'Pièce Jointe',
                'verbose_name_plural': 'Pièces Jointes',
                'ordering': ['-date_upload'],
            },
        ),
        
        # Ajouter des index pour la performance
        migrations.AddIndex(
            model_name='ticketmaintenance',
            index=models.Index(fields=['numero_ticket'], name='core_ticket_numero_idx'),
        ),
        migrations.AddIndex(
            model_name='ticketmaintenance',
            index=models.Index(fields=['statut'], name='core_ticket_statut_idx'),
        ),
        migrations.AddIndex(
            model_name='ticketmaintenance',
            index=models.Index(fields=['priorite'], name='core_ticket_priorite_idx'),
        ),
        migrations.AddIndex(
            model_name='ticketmaintenance',
            index=models.Index(fields=['-date_creation'], name='core_ticket_date_idx'),
        ),
    ]
