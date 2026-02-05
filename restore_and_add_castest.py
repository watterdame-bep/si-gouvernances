#!/usr/bin/env python3
"""
Script pour restaurer models.py et ajouter proprement le modèle CasTest
"""

import os
import re

def restore_models_and_add_castest():
    """Restaurer models.py et ajouter CasTest proprement"""
    
    print("🔧 Restauration et ajout du modèle CasTest")
    print("=" * 50)
    
    models_file = 'core/models.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    try:
        # Lire le fichier
        with open(models_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ Fichier models.py lu avec succès")
        
        # Supprimer tout ce qui a été ajouté incorrectement après TacheTest
        # Chercher la fin propre de TacheTest
        pattern = r'(class TacheTest\(models\.Model\):.*?def __str__\(self\):.*?return.*?\n)(.*?)(class BugTest\(models\.Model\):)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            before_tachetest = content[:match.start()]
            tachetest_content = match.group(1)
            bugtest_and_after = match.group(3) + content[match.end():]
            
            # Nouveau modèle CasTest propre
            castest_model = '''

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
        # Auto-générer le numéro de cas si pas défini
        if not self.numero_cas:
            # Prendre le préfixe de la tâche parent et ajouter un numéro séquentiel
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
        from django.utils import timezone
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()
    
    def marquer_comme_echec(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme échoué"""
        from django.utils import timezone
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour le statut de la tâche parent
        self.tache_test.mettre_a_jour_statut()

'''
            
            # Méthodes à ajouter à TacheTest
            tachetest_methods = '''
    
    def mettre_a_jour_statut(self):
        """Mettre à jour le statut de la tâche basé sur ses cas de test"""
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
'''
            
            # Reconstruire le contenu
            new_content = before_tachetest + tachetest_content + tachetest_methods + castest_model + '\n\n' + bugtest_and_after
            
            print("✅ Structure restaurée et CasTest ajouté")
        else:
            print("❌ Structure TacheTest non trouvée")
            return False
        
        # Écrire le fichier corrigé
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fichier core/models.py restauré et mis à jour")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_syntax():
    """Tester la syntaxe du fichier"""
    
    print("\n🔍 Test de la syntaxe")
    print("=" * 30)
    
    try:
        with open('core/models.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, 'core/models.py', 'exec')
        print("✅ Syntaxe Python valide")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe ligne {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Restauration et ajout du modèle CasTest")
    print("=" * 60)
    
    success1 = restore_models_and_add_castest()
    success2 = test_syntax()
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTAT")
    print("=" * 60)
    
    if success1 and success2:
        print("✅ MODÈLE CASTEST AJOUTÉ AVEC SUCCÈS!")
        print("\n🏗️ Structure hiérarchique:")
        print("   TacheTest (Sujet de test)")
        print("   └── CasTest (Cas de test individuel)")
        print("       └── BugTest (Bug lié au cas)")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Créer la migration:")
        print("      python manage.py makemigrations")
        print("   2. Appliquer la migration:")
        print("      python manage.py migrate")
    else:
        print("❌ ÉCHEC DE LA RESTAURATION")
        print("Le fichier models.py doit être corrigé manuellement.")