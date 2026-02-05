#!/usr/bin/env python3
"""
Script pour ajouter le modèle CasTest et modifier la structure hiérarchique des tests
"""

import os
import re

def add_cas_test_model():
    """Ajouter le modèle CasTest dans core/models.py"""
    
    print("🏗️ Ajout du modèle CasTest pour la structure hiérarchique")
    print("=" * 60)
    
    models_file = 'core/models.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier models.py lu avec succès")
        
        # Nouveau modèle CasTest à ajouter après TacheTest
        cas_test_model = '''

class CasTest(models.Model):
    """Cas de test individuel dans une tâche de test"""
    
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
    
    # Relations
    tache_test = models.ForeignKey(TacheTest, on_delete=models.CASCADE, related_name='cas_tests')
    
    # Informations du cas
    nom = models.CharField(max_length=200, help_text="Ex: Connexion avec email valide")
    description = models.TextField(help_text="Description détaillée du cas de test")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Données de test
    donnees_entree = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Données d'entrée du test (JSON)"
    )
    preconditions = models.TextField(
        blank=True,
        help_text="Conditions préalables à remplir"
    )
    
    # Étapes d'exécution
    etapes_execution = models.TextField(
        help_text="Étapes détaillées pour exécuter ce cas"
    )
    
    # Résultats
    resultats_attendus = models.TextField(
        help_text="Résultats attendus pour ce cas spécifique"
    )
    resultats_obtenus = models.TextField(
        blank=True,
        help_text="Résultats obtenus lors de l'exécution"
    )
    
    # Statut et exécution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_execution = models.DateTimeField(null=True, blank=True)
    duree_execution = models.DurationField(
        null=True, 
        blank=True,
        help_text="Durée d'exécution du cas"
    )
    
    # Assignation et exécution
    executeur = models.ForeignKey(
        Utilisateur, 
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
        Utilisateur, 
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
        # Auto-générer le numéro de cas si pas défini
        if not self.numero_cas:
            # Prendre le préfixe de la tâche parent et ajouter un numéro séquentiel
            prefix = self.tache_test.nom[:4].upper().replace(' ', '')
            existing_count = CasTest.objects.filter(
                tache_test=self.tache_test
            ).count()
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
    
    def marquer_comme_echec(self, executeur, resultats_obtenus="", creer_bug=True):
        """Marquer le cas comme échoué et optionnellement créer un bug"""
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Créer un bug automatiquement si demandé
        if creer_bug:
            self.creer_bug_automatique()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()
    
    def creer_bug_automatique(self):
        """Créer automatiquement un bug pour ce cas échoué"""
        bug = BugTest.objects.create(
            cas_test=self,
            etape=self.tache_test.etape,
            titre=f"Échec du cas {self.numero_cas}: {self.nom}",
            description=f"Le cas de test '{self.nom}' a échoué.\\n\\n"
                       f"Résultats attendus:\\n{self.resultats_attendus}\\n\\n"
                       f"Résultats obtenus:\\n{self.resultats_obtenus}",
            gravite='MAJEUR' if self.priorite == 'HAUTE' else 'CRITIQUE' if self.priorite == 'CRITIQUE' else 'MINEUR',
            createur=self.executeur,
            statut='OUVERT'
        )
        return bug
'''

        # Trouver où insérer le nouveau modèle (après TacheTest)
        pattern = r'(class TacheTest\(models\.Model\):.*?def __str__\(self\):.*?return.*?\n)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            # Insérer le nouveau modèle après TacheTest
            insert_position = match.end()
            new_content = content[:insert_position] + cas_test_model + content[insert_position:]
            
            print("✅ Modèle CasTest ajouté après TacheTest")
        else:
            # Si on ne trouve pas TacheTest, ajouter à la fin des modèles de test
            if 'class BugTest(models.Model):' in content:
                insert_position = content.find('class BugTest(models.Model):')
                new_content = content[:insert_position] + cas_test_model + '\n\n' + content[insert_position:]
                print("✅ Modèle CasTest ajouté avant BugTest")
            else:
                print("❌ Position d'insertion non trouvée")
                return False
        
        # Modifier le modèle TacheTest pour ajouter les méthodes de calcul de statut
        tache_test_methods = '''
    
    def mettre_a_jour_statut(self):
        """Mettre à jour le statut de la tâche basé sur ses cas de test"""
        cas_tests = self.cas_tests.all()
        
        if not cas_tests.exists():
            # Pas de cas de test, garder le statut actuel
            return
        
        total_cas = cas_tests.count()
        cas_passes = cas_tests.filter(statut='PASSE').count()
        cas_echecs = cas_tests.filter(statut='ECHEC').count()
        cas_en_cours = cas_tests.filter(statut='EN_COURS').count()
        cas_en_attente = cas_tests.filter(statut='EN_ATTENTE').count()
        
        # Logique de calcul du statut global
        if cas_echecs > 0:
            self.statut = 'ECHEC'
        elif cas_passes == total_cas:
            self.statut = 'PASSE'
        elif cas_en_cours > 0 or (cas_passes > 0 and cas_en_attente > 0):
            self.statut = 'EN_COURS'
        else:
            self.statut = 'EN_ATTENTE'
        
        self.save()
    
    @property
    def statistiques_cas(self):
        """Retourne les statistiques des cas de test"""
        cas_tests = self.cas_tests.all()
        return {
            'total': cas_tests.count(),
            'passes': cas_tests.filter(statut='PASSE').count(),
            'echecs': cas_tests.filter(statut='ECHEC').count(),
            'en_cours': cas_tests.filter(statut='EN_COURS').count(),
            'en_attente': cas_tests.filter(statut='EN_ATTENTE').count(),
        }
    
    @property
    def progression_pourcentage(self):
        """Calcule le pourcentage de progression"""
        stats = self.statistiques_cas
        if stats['total'] == 0:
            return 0
        return round((stats['passes'] / stats['total']) * 100, 1)
    
    @property
    def a_cas_critiques_echec(self):
        """Vérifie s'il y a des cas critiques en échec"""
        return self.cas_tests.filter(
            priorite='CRITIQUE',
            statut='ECHEC'
        ).exists()
'''

        # Ajouter les méthodes à TacheTest
        pattern = r'(def __str__\(self\):.*?return.*?\n)(.*?class [A-Z])'
        match = re.search(pattern, new_content, re.DOTALL)
        
        if match:
            before_str = match.group(1)
            after_class = match.group(2)
            new_content = new_content.replace(
                match.group(0),
                before_str + tache_test_methods + '\n\n' + after_class
            )
            print("✅ Méthodes ajoutées à TacheTest")
        
        # Modifier BugTest pour ajouter la relation avec CasTest
        bug_test_modification = '''
    # Relation avec le cas de test (nouveau)
    cas_test = models.ForeignKey(
        'CasTest', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='bugs',
        help_text="Cas de test qui a généré ce bug"
    )
'''
        
        # Insérer la nouvelle relation dans BugTest après etape
        pattern = r'(etape = models\.ForeignKey\(EtapeProjet.*?\n)'
        new_content = re.sub(
            pattern,
            r'\1' + bug_test_modification,
            new_content
        )
        
        print("✅ Relation cas_test ajoutée à BugTest")
        
        # Écrire le fichier modifié
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fichier core/models.py mis à jour avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout du modèle: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Implémentation de la structure hiérarchique des tests")
    print("=" * 70)
    
    success = add_cas_test_model()
    
    print("\n" + "=" * 70)
    print("📊 RÉSULTAT")
    print("=" * 70)
    
    if success:
        print("✅ STRUCTURE HIÉRARCHIQUE AJOUTÉE!")
        print("\n🏗️ Nouvelle architecture:")
        print("   TacheTest (Sujet de test)")
        print("   └── CasTest (Cas de test individuel)")
        print("       └── BugTest (Bug lié au cas)")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Créer et appliquer la migration:")
        print("      python manage.py makemigrations")
        print("      python manage.py migrate")
        print("   2. Mettre à jour les vues et templates")
        print("   3. Tester la nouvelle structure")
    else:
        print("❌ ÉCHEC DE L'IMPLÉMENTATION")
        print("Vérifiez les erreurs ci-dessus.")