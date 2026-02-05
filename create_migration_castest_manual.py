#!/usr/bin/env python3
"""
Script pour créer manuellement la migration du modèle CasTest
sans modifier models.py pour l'instant
"""

import os
from datetime import datetime

def create_manual_migration():
    """Créer manuellement la migration pour CasTest"""
    
    print("🏗️ Création manuelle de la migration CasTest")
    print("=" * 50)
    
    # Créer le répertoire migrations s'il n'existe pas
    migrations_dir = 'core/migrations'
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)
        print(f"✅ Répertoire {migrations_dir} créé")
    
    # Générer le nom de fichier de migration
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    migration_file = f'{migrations_dir}/0020_add_castest_hierarchique_{timestamp}.py'
    
    # Contenu de la migration
    migration_content = f'''# Generated manually on {datetime.now().strftime('%Y-%m-%d %H:%M')}

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_add_systeme_tests_v1'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasTest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('numero_cas', models.CharField(help_text='Auto-généré: AUTH-001, AUTH-002, etc.', max_length=30)),
                ('nom', models.CharField(help_text='Ex: Connexion avec email valide', max_length=200)),
                ('description', models.TextField(help_text='Description détaillée du cas de test')),
                ('priorite', models.CharField(choices=[('CRITIQUE', 'Critique'), ('HAUTE', 'Haute'), ('MOYENNE', 'Moyenne'), ('BASSE', 'Basse')], default='MOYENNE', max_length=20)),
                ('donnees_entree', models.TextField(blank=True, help_text='Données d\\'entrée du test')),
                ('preconditions', models.TextField(blank=True, help_text='Conditions préalables à remplir')),
                ('etapes_execution', models.TextField(help_text='Étapes détaillées pour exécuter ce cas')),
                ('resultats_attendus', models.TextField(help_text='Résultats attendus pour ce cas spécifique')),
                ('resultats_obtenus', models.TextField(blank=True, help_text='Résultats obtenus lors de l\\'exécution')),
                ('statut', models.CharField(choices=[('EN_ATTENTE', 'En attente'), ('EN_COURS', 'En cours'), ('PASSE', 'Passé'), ('ECHEC', 'Échec'), ('BLOQUE', 'Bloqué')], default='EN_ATTENTE', max_length=20)),
                ('date_execution', models.DateTimeField(blank=True, null=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
                ('ordre', models.PositiveIntegerField(default=1)),
                ('createur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cas_tests_crees', to='core.utilisateur')),
                ('executeur', models.ForeignKey(blank=True, help_text='QA qui a exécuté ce cas', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cas_tests_executes', to='core.utilisateur')),
                ('tache_test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cas_tests', to='core.tachetest')),
            ],
            options={{
                'verbose_name': 'Cas de test',
                'verbose_name_plural': 'Cas de tests',
                'ordering': ['ordre', 'date_creation'],
            }},
        ),
        migrations.AlterUniqueTogether(
            name='castest',
            unique_together={{('tache_test', 'numero_cas')}},
        ),
        migrations.AddField(
            model_name='bugtest',
            name='cas_test',
            field=models.ForeignKey(blank=True, help_text='Cas de test qui a généré ce bug', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bugs_lies', to='core.castest'),
        ),
    ]
'''
    
    try:
        # Écrire le fichier de migration
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        
        print(f"✅ Migration créée: {migration_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {str(e)}")
        return False

def create_castest_in_separate_file():
    """Créer le modèle CasTest dans un fichier séparé pour l'instant"""
    
    print("\n📄 Création du modèle CasTest dans un fichier séparé")
    print("=" * 50)
    
    castest_model_file = 'core/models_castest_final.py'
    
    castest_content = '''"""
Modèle CasTest pour la hiérarchie des tests - Version finale
À intégrer dans models.py une fois les problèmes de syntaxe résolus
"""

import uuid
from django.db import models
from django.utils import timezone


class CasTest(models.Model):
    """Cas de test individuel dans une tâche de test - UNIQUEMENT pour l'étape TEST"""
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('PASSE', 'Passé'),
        ('ECHEC', 'Échec'),
        ('BLOQUE', 'Bloqué'),
    ]
    
    PRIORITE_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_cas = models.CharField(max_length=30, help_text="Auto-généré: AUTH-001, AUTH-002, etc.")
    
    # Relations - UNIQUEMENT pour les TacheTest de l'étape TEST
    tache_test = models.ForeignKey('TacheTest', on_delete=models.CASCADE, related_name='cas_tests')
    
    # Informations du cas
    nom = models.CharField(max_length=200, help_text="Ex: Connexion avec email valide")
    description = models.TextField(help_text="Description détaillée du cas de test")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Données de test
    donnees_entree = models.TextField(blank=True, help_text="Données d'entrée du test")
    preconditions = models.TextField(blank=True, help_text="Conditions préalables à remplir")
    
    # Étapes d'exécution
    etapes_execution = models.TextField(help_text="Étapes détaillées pour exécuter ce cas")
    
    # Résultats
    resultats_attendus = models.TextField(help_text="Résultats attendus pour ce cas spécifique")
    resultats_obtenus = models.TextField(blank=True, help_text="Résultats obtenus lors de l'exécution")
    
    # Statut et exécution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_execution = models.DateTimeField(null=True, blank=True)
    
    # Assignation et exécution
    executeur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cas_tests_executes',
        help_text="QA qui a exécuté ce cas"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cas_tests_crees'
    )
    
    # Ordre dans la tâche
    ordre = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['ordre', 'date_creation']
        unique_together = ['tache_test', 'numero_cas']
        verbose_name = "Cas de test"
        verbose_name_plural = "Cas de tests"
    
    def __str__(self):
        return f"{self.numero_cas} - {self.nom}"
    
    def save(self, *args, **kwargs):
        # Vérifier que la tâche parent est bien dans une étape TEST
        if self.tache_test and self.tache_test.etape.type_etape.nom != 'TESTS':
            raise ValueError("Les cas de test ne peuvent être créés que pour l'étape TEST")
        
        # Auto-générer le numéro de cas si pas défini
        if not self.numero_cas:
            prefix = self.tache_test.nom[:4].upper().replace(' ', '')
            existing_count = CasTest.objects.filter(tache_test=self.tache_test).count()
            self.numero_cas = f"{prefix}-{existing_count + 1:03d}"
        
        super().save(*args, **kwargs)
    
    @property
    def est_critique(self):
        """Vérifie si ce cas est critique"""
        return self.priorite == 'CRITIQUE'
    
    @property
    def peut_etre_execute(self):
        """Vérifie si ce cas peut être exécuté"""
        return self.statut in ['EN_ATTENTE', 'ECHEC']
    
    @property
    def est_termine(self):
        """Vérifie si ce cas est terminé (passé ou échoué)"""
        return self.statut in ['PASSE', 'ECHEC']
    
    def marquer_comme_passe(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme passé"""
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()
    
    def marquer_comme_echec(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme échoué"""
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()


# Méthodes à ajouter à TacheTest (pour l'étape TEST uniquement)
def mettre_a_jour_statut_tache_test(self):
    """Mettre à jour le statut de la tâche basé sur ses cas de test - UNIQUEMENT pour étape TEST"""
    # Vérifier que c'est bien une étape TEST
    if self.etape.type_etape.nom != 'TESTS':
        return  # Ne pas traiter si ce n'est pas l'étape TEST
    
    cas_tests = self.cas_tests.all()
    
    if not cas_tests.exists():
        return
    
    total_cas = cas_tests.count()
    cas_passes = cas_tests.filter(statut='PASSE').count()
    cas_echecs = cas_tests.filter(statut='ECHEC').count()
    cas_en_cours = cas_tests.filter(statut='EN_COURS').count()
    
    if cas_echecs > 0:
        self.statut = 'ECHEC'
    elif cas_passes == total_cas:
        self.statut = 'PASSE'
    elif cas_en_cours > 0 or cas_passes > 0:
        self.statut = 'EN_COURS'
    else:
        self.statut = 'EN_ATTENTE'
    
    self.save()

def statistiques_cas_tache_test(self):
    """Retourne les statistiques des cas de test - UNIQUEMENT pour étape TEST"""
    if self.etape.type_etape.nom != 'TESTS':
        return {'total': 0, 'passes': 0, 'echecs': 0, 'en_cours': 0, 'en_attente': 0}
    
    cas_tests = self.cas_tests.all()
    return {
        'total': cas_tests.count(),
        'passes': cas_tests.filter(statut='PASSE').count(),
        'echecs': cas_tests.filter(statut='ECHEC').count(),
        'en_cours': cas_tests.filter(statut='EN_COURS').count(),
        'en_attente': cas_tests.filter(statut='EN_ATTENTE').count(),
    }

def progression_pourcentage_tache_test(self):
    """Calcule le pourcentage de progression - UNIQUEMENT pour étape TEST"""
    stats = self.statistiques_cas
    if stats['total'] == 0:
        return 0
    return round((stats['passes'] / stats['total']) * 100, 1)
'''
    
    try:
        with open(castest_model_file, 'w', encoding='utf-8') as f:
            f.write(castest_content)
        
        print(f"✅ Modèle CasTest créé: {castest_model_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Création manuelle de la migration CasTest")
    print("=" * 60)
    
    success1 = create_manual_migration()
    success2 = create_castest_in_separate_file()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ MIGRATION ET MODÈLE CRÉÉS!")
        print("\n🏗️ Structure hiérarchique (UNIQUEMENT pour étape TEST):")
        print("   TacheTest (Sujet de test)")
        print("   └── CasTest (Cas de test individuel)")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Appliquer la migration:")
        print("      python manage.py migrate")
        print("   2. Tester la création de cas de test")
        print("   3. Implémenter les vues hiérarchiques")
        
        print("\n⚠️  Note importante:")
        print("   La hiérarchie CasTest ne s'applique QUE pour l'étape TEST")
        print("   Les autres étapes gardent leur structure actuelle")
    else:
        print("❌ ÉCHEC DE LA CRÉATION")
        print("Vérifiez les erreurs ci-dessus.")