#!/usr/bin/env python3
"""
Script pour intégrer le modèle CasTest dans models.py de manière propre
"""

import os

def integrate_castest():
    """Intégrer le modèle CasTest dans models.py"""
    
    print("🔧 Intégration du modèle CasTest")
    print("=" * 40)
    
    models_file = 'core/models.py'
    castest_file = 'core/models_castest.py'
    
    if not os.path.exists(models_file):
        print(f"❌ Fichier {models_file} non trouvé")
        return False
    
    if not os.path.exists(castest_file):
        print(f"❌ Fichier {castest_file} non trouvé")
        return False
    
    try:
        # Lire le modèle CasTest
        with open(castest_file, 'r', encoding='utf-8') as f:
            castest_content = f.read()
        
        # Extraire seulement la classe CasTest
        start_marker = "class CasTest(models.Model):"
        start_pos = castest_content.find(start_marker)
        if start_pos == -1:
            print("❌ Classe CasTest non trouvée")
            return False
        
        # Prendre tout à partir de la classe
        castest_class = castest_content[start_pos:]
        
        # Lire le fichier models.py principal
        with open(models_file, 'r', encoding='utf-8') as f:
            models_content = f.read()
        
        print("✅ Fichiers lus avec succès")
        
        # Trouver où insérer CasTest (après TacheTest, avant BugTest)
        if "class BugTest(models.Model):" in models_content:
            insert_pos = models_content.find("class BugTest(models.Model):")
            
            # Insérer CasTest avant BugTest
            new_content = (
                models_content[:insert_pos] + 
                "\n\n" + castest_class + "\n\n" + 
                models_content[insert_pos:]
            )
            
            print("✅ CasTest inséré avant BugTest")
        else:
            # Ajouter à la fin du fichier
            new_content = models_content + "\n\n" + castest_class
            print("✅ CasTest ajouté à la fin du fichier")
        
        # Ajouter les méthodes à TacheTest si elles n'existent pas
        if "def mettre_a_jour_statut(self):" not in new_content:
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
            
            # Trouver la fin de la classe TacheTest
            tachetest_start = new_content.find("class TacheTest(models.Model):")
            if tachetest_start != -1:
                # Chercher la méthode __str__ de TacheTest
                str_method_pos = new_content.find("def __str__(self):", tachetest_start)
                if str_method_pos != -1:
                    # Chercher la fin de la méthode __str__
                    next_line_pos = new_content.find("\n", str_method_pos)
                    next_line_pos = new_content.find("\n", next_line_pos + 1)  # Ligne suivante
                    
                    # Insérer les méthodes après __str__
                    new_content = (
                        new_content[:next_line_pos] + 
                        tachetest_methods + 
                        new_content[next_line_pos:]
                    )
                    
                    print("✅ Méthodes ajoutées à TacheTest")
        
        # Écrire le fichier mis à jour
        with open(models_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Fichier core/models.py mis à jour avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'intégration: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_django_models():
    """Tester que Django peut charger les modèles"""
    
    print("\n🔍 Test de chargement des modèles Django")
    print("=" * 40)
    
    try:
        import os
        import sys
        import django
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
        django.setup()
        
        # Essayer d'importer les modèles
        from core.models import TacheTest, CasTest
        
        print("✅ Modèles TacheTest et CasTest importés avec succès")
        
        # Vérifier les relations
        if hasattr(TacheTest, 'cas_tests'):
            print("✅ Relation cas_tests trouvée dans TacheTest")
        else:
            print("❌ Relation cas_tests manquante dans TacheTest")
            return False
        
        if hasattr(CasTest, 'tache_test'):
            print("✅ Relation tache_test trouvée dans CasTest")
        else:
            print("❌ Relation tache_test manquante dans CasTest")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        return False

if __name__ == '__main__':
    print("🚀 Intégration du modèle CasTest")
    print("=" * 50)
    
    success1 = integrate_castest()
    success2 = test_django_models()
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTAT")
    print("=" * 50)
    
    if success1 and success2:
        print("✅ INTÉGRATION RÉUSSIE!")
        print("\n🏗️ Structure hiérarchique:")
        print("   TacheTest (Sujet de test)")
        print("   └── CasTest (Cas de test individuel)")
        
        print("\n💡 Prochaines étapes:")
        print("   1. Créer la migration:")
        print("      python manage.py makemigrations")
        print("   2. Appliquer la migration:")
        print("      python manage.py migrate")
        print("   3. Mettre à jour les vues et templates")
    else:
        print("❌ ÉCHEC DE L'INTÉGRATION")
        print("Vérifiez les erreurs ci-dessus.")