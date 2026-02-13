# Generated migration for secure account activation system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_add_contrat_expire_alert_type'),
    ]

    operations = [
        # Création de la table AccountActivationToken
        migrations.CreateModel(
            name='AccountActivationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_hash', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='Hash du token')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('expires_at', models.DateTimeField(db_index=True, verbose_name="Date d'expiration")),
                ('is_used', models.BooleanField(db_index=True, default=False, verbose_name='Token utilisé')),
                ('used_at', models.DateTimeField(blank=True, null=True, verbose_name="Date d'utilisation")),
                ('invalidated_at', models.DateTimeField(blank=True, null=True, verbose_name="Date d'invalidation")),
                ('attempts', models.IntegerField(default=0, verbose_name='Nombre de tentatives')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='Adresse IP de création')),
                ('last_attempt_ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='Dernière IP de tentative')),
                ('last_attempt_at', models.DateTimeField(blank=True, null=True, verbose_name='Dernière tentative')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activation_tokens', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': "Token d'activation",
                'verbose_name_plural': "Tokens d'activation",
                'ordering': ['-created_at'],
            },
        ),
        
        # Création de la table AccountActivationLog
        migrations.CreateModel(
            name='AccountActivationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[
                    ('TOKEN_CREATED', 'Token créé'),
                    ('TOKEN_SENT', 'Email envoyé'),
                    ('ACTIVATION_ATTEMPT', "Tentative d'activation"),
                    ('ACTIVATION_SUCCESS', 'Activation réussie'),
                    ('ACTIVATION_FAILED', 'Activation échouée'),
                    ('TOKEN_EXPIRED', 'Token expiré'),
                    ('TOKEN_RESENT', 'Token renvoyé'),
                    ('TOO_MANY_ATTEMPTS', 'Trop de tentatives'),
                ], max_length=50)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True, default='')),
                ('details', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('token', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.accountactivationtoken')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activation_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Log d'activation",
                'verbose_name_plural': "Logs d'activation",
                'ordering': ['-created_at'],
            },
        ),
        
        # Index composites pour AccountActivationToken (optimisation des requêtes)
        migrations.AddIndex(
            model_name='accountactivationtoken',
            index=models.Index(fields=['user', 'is_used', 'expires_at'], name='core_accoun_user_id_is_used_expires_idx'),
        ),
        migrations.AddIndex(
            model_name='accountactivationtoken',
            index=models.Index(fields=['token_hash'], name='core_accoun_token_hash_idx'),
        ),
        migrations.AddIndex(
            model_name='accountactivationtoken',
            index=models.Index(fields=['expires_at'], name='core_accoun_expires_at_idx'),
        ),
        
        # Index composites pour AccountActivationLog (optimisation des requêtes d'audit)
        migrations.AddIndex(
            model_name='accountactivationlog',
            index=models.Index(fields=['user', '-created_at'], name='core_accoun_user_id_created_at_idx'),
        ),
        migrations.AddIndex(
            model_name='accountactivationlog',
            index=models.Index(fields=['action', '-created_at'], name='core_accoun_action_created_at_idx'),
        ),
    ]
