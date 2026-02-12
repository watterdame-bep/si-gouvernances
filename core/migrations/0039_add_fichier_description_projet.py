# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_add_ticket_resolu_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='projet',
            name='fichier_description',
            field=models.FileField(
                blank=True,
                help_text='Fichier de description du projet (PDF, Word)',
                null=True,
                upload_to='projets/descriptions/',
                verbose_name='Fichier de description'
            ),
        ),
    ]
