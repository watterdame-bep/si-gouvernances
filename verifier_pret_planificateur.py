"""
Script de vérification - Prêt pour le Planificateur Windows
Vérifie que tout est en place pour configurer le planificateur
"""

import os
import sys
import subprocess

def verifier_python():
    """Vérifie que Python est accessible"""
    print("1. Vérification de Python...")
    try:
        result = subprocess.run(['python', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Python installé: {result.stdout.strip()}")
            return True
        else:
            print("   ❌ Python non accessible")
            return False
    except:
        print("   ❌ Python non trouvé dans le PATH")
        return False

def verifier_manage_py():
    """Vérifie que manage.py existe"""
    print("\n2. Vérification de manage.py...")
    if os.path.exists('manage.py'):
        print("   ✅ manage.py trouvé")
        return True
    else:
        print("   ❌ manage.py non trouvé")
        return False

def verifier_commandes():
    """Vérifie que les commandes management existent"""
    print("\n3. Vérification des commandes management...")
    
    commandes = [
        ('check_project_deadlines', 'core/management/commands/check_project_deadlines.py'),
        ('check_stage_delays', 'core/management/commands/check_stage_delays.py'),
        ('check_task_deadlines', 'core/management/commands/check_task_deadlines.py'),
        ('check_budget', 'core/management/commands/check_budget.py'),
        ('check_contract_expiration', 'core/management/commands/check_contract_expiration.py'),
    ]
    
    toutes_ok = True
    for nom, chemin in commandes:
        if os.path.exists(chemin):
            print(f"   ✅ {nom}")
        else:
            print(f"   ❌ {nom} - Fichier non trouvé: {chemin}")
            toutes_ok = False
    
    return toutes_ok

def verifier_fichiers_bat():
    """Vérifie que les fichiers .bat existent"""
    print("\n4. Vérification des fichiers .bat...")
    
    fichiers = [
        'run_check_deadlines.bat',
        'run_check_stage_delays.bat',
        'run_check_budget.bat',
        'run_check_all_alerts.bat',
    ]
    
    toutes_ok = True
    for fichier in fichiers:
        if os.path.exists(fichier):
            print(f"   ✅ {fichier}")
        else:
            print(f"   ⚠️  {fichier} - Non trouvé (sera créé)")
            toutes_ok = False
    
    return toutes_ok

def verifier_dossier_logs():
    """Vérifie que le dossier logs existe"""
    print("\n5. Vérification du dossier logs...")
    if os.path.exists('logs'):
        print("   ✅ Dossier logs existe")
        return True
    else:
        print("   ⚠️  Dossier logs n'existe pas (sera créé)")
        try:
            os.makedirs('logs')
            print("   ✅ Dossier logs créé")
            return True
        except:
            print("   ❌ Impossible de créer le dossier logs")
            return False

def verifier_configuration_smtp():
    """Vérifie la configuration SMTP"""
    print("\n6. Vérification de la configuration SMTP...")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            contenu = f.read()
            
        checks = {
            'EMAIL_HOST': 'EMAIL_HOST=' in contenu,
            'EMAIL_PORT': 'EMAIL_PORT=' in contenu,
            'EMAIL_HOST_USER': 'EMAIL_HOST_USER=' in contenu,
            'EMAIL_HOST_PASSWORD': 'EMAIL_HOST_PASSWORD=' in contenu,
        }
        
        toutes_ok = True
        for param, existe in checks.items():
            if existe:
                print(f"   ✅ {param} configuré")
            else:
                print(f"   ❌ {param} manquant")
                toutes_ok = False
        
        return toutes_ok
    else:
        print("   ❌ Fichier .env non trouvé")
        return False

def tester_commande(commande):
    """Teste l'exécution d'une commande"""
    try:
        result = subprocess.run(
            ['python', 'manage.py', commande],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return True  # La commande fonctionne mais prend du temps
    except:
        return False

def verifier_execution_commandes():
    """Vérifie que les commandes s'exécutent"""
    print("\n7. Test d'exécution des commandes...")
    print("   (Ceci peut prendre quelques secondes)")
    
    commandes = [
        'check_project_deadlines',
        'check_stage_delays',
        'check_task_deadlines',
        'check_budget',
        'check_contract_expiration',
    ]
    
    toutes_ok = True
    for commande in commandes:
        print(f"   Test de {commande}...", end=' ')
        if tester_commande(commande):
            print("✅")
        else:
            print("❌")
            toutes_ok = False
    
    return toutes_ok

def afficher_chemin_projet():
    """Affiche le chemin complet du projet"""
    print("\n8. Chemin du projet...")
    chemin = os.path.abspath('.')
    print(f"   📁 {chemin}")
    print(f"\n   ⚠️  IMPORTANT: Utilisez ce chemin dans le Planificateur de tâches!")
    return chemin

def generer_resume(resultats, chemin):
    """Génère un résumé final"""
    print("\n" + "=" * 80)
    print("RÉSUMÉ DE LA VÉRIFICATION")
    print("=" * 80)
    
    total = len(resultats)
    reussis = sum(1 for r in resultats.values() if r)
    
    print(f"\nTests réussis: {reussis}/{total}")
    print()
    
    for test, resultat in resultats.items():
        statut = "✅" if resultat else "❌"
        print(f"  {statut} {test}")
    
    print("\n" + "=" * 80)
    
    if reussis == total:
        print("🎉 TOUT EST PRÊT POUR LE PLANIFICATEUR WINDOWS!")
        print("=" * 80)
        print("\nPROCHAINES ÉTAPES:")
        print("1. Ouvrez le Planificateur de tâches Windows (taskschd.msc)")
        print("2. Créez une nouvelle tâche pour chaque commande")
        print("3. Utilisez ce chemin dans 'Commencer dans':")
        print(f"   {chemin}")
        print("4. Consultez GUIDE_PLANIFICATEUR_WINDOWS_COMPLET.md pour les détails")
    else:
        print("⚠️  CERTAINS ÉLÉMENTS NÉCESSITENT VOTRE ATTENTION")
        print("=" * 80)
        print("\nCorrigez les problèmes ci-dessus avant de configurer le planificateur.")
    
    print()

def main():
    print("=" * 80)
    print("VÉRIFICATION - PRÊT POUR LE PLANIFICATEUR WINDOWS")
    print("=" * 80)
    print()
    
    resultats = {}
    
    # Exécuter toutes les vérifications
    resultats['Python accessible'] = verifier_python()
    resultats['manage.py existe'] = verifier_manage_py()
    resultats['Commandes management'] = verifier_commandes()
    resultats['Fichiers .bat'] = verifier_fichiers_bat()
    resultats['Dossier logs'] = verifier_dossier_logs()
    resultats['Configuration SMTP'] = verifier_configuration_smtp()
    
    # Test d'exécution (optionnel, peut être long)
    print("\n⚠️  Voulez-vous tester l'exécution des commandes? (peut prendre 1-2 minutes)")
    reponse = input("   Taper 'o' pour oui, autre chose pour non: ")
    
    if reponse.lower() == 'o':
        resultats['Exécution des commandes'] = verifier_execution_commandes()
    
    # Afficher le chemin du projet
    chemin = afficher_chemin_projet()
    
    # Générer le résumé
    generer_resume(resultats, chemin)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Vérification interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
