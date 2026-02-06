"""
Démonstration du système de déploiement hiérarchique
Montre comment créer et gérer des déploiements
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.utils import timezone
from core.models import Projet, EtapeProjet, TacheEtape, Deploiement, Utilisateur, TypeEtape

def demo_deploiement():
    """Démonstration complète du workflow de déploiement"""
    
    print("\n" + "="*70)
    print("🚀 DÉMONSTRATION DU SYSTÈME DE DÉPLOIEMENT HIÉRARCHIQUE")
    print("="*70)
    
    # 1. Trouver ou créer un projet
    print("\n📋 ÉTAPE 1: Préparation du projet")
    print("-" * 70)
    
    projet = Projet.objects.first()
    if not projet:
        print("❌ Aucun projet trouvé. Créez d'abord un projet.")
        return
    
    print(f"✅ Projet: {projet.nom}")
    
    # 2. Trouver l'étape DEPLOIEMENT
    try:
        type_deploiement = TypeEtape.objects.get(nom='DEPLOIEMENT')
        etape_deploiement = projet.etapes.get(type_etape=type_deploiement)
        print(f"✅ Étape DEPLOIEMENT trouvée: {etape_deploiement.nom}")
    except:
        print("❌ Étape DEPLOIEMENT introuvable")
        return
    
    # 3. Trouver un utilisateur
    admin = Utilisateur.objects.filter(est_admin=True).first()
    if not admin:
        admin = Utilisateur.objects.first()
    
    if not admin:
        print("❌ Aucun utilisateur trouvé")
        return
    
    print(f"✅ Utilisateur: {admin.get_full_name()}")
    
    # 4. Créer une tâche de déploiement
    print("\n📋 ÉTAPE 2: Création d'une tâche de déploiement")
    print("-" * 70)
    
    tache_deploiement = TacheEtape.objects.create(
        etape=etape_deploiement,
        nom="Release 2.0 - Démonstration",
        description="Déploiement de la version 2.0 sur tous les environnements",
        responsable=admin,
        statut='EN_COURS',
        priorite='HAUTE'
    )
    
    print(f"✅ Tâche créée: {tache_deploiement.nom}")
    print(f"   ID: {tache_deploiement.id}")
    
    # 5. Créer plusieurs déploiements
    print("\n📋 ÉTAPE 3: Création des déploiements")
    print("-" * 70)
    
    deploiements_config = [
        {
            'version': 'v2.0.0',
            'environnement': 'DEV',
            'description': 'Déploiement sur l\'environnement de développement',
            'priorite': 'NORMALE'
        },
        {
            'version': 'v2.0.0',
            'environnement': 'TEST',
            'description': 'Déploiement sur l\'environnement de test',
            'priorite': 'NORMALE'
        },
        {
            'version': 'v2.0.0',
            'environnement': 'PREPROD',
            'description': 'Déploiement sur l\'environnement de pré-production',
            'priorite': 'HAUTE'
        },
        {
            'version': 'v2.0.0',
            'environnement': 'PROD',
            'description': 'Déploiement sur l\'environnement de production',
            'priorite': 'CRITIQUE'
        }
    ]
    
    deploiements_crees = []
    
    for config in deploiements_config:
        deploiement = Deploiement.objects.create(
            tache_deploiement=tache_deploiement,
            version=config['version'],
            environnement=config['environnement'],
            description=config['description'],
            responsable=admin,
            priorite=config['priorite'],
            statut='PREVU',
            createur=admin
        )
        deploiements_crees.append(deploiement)
        print(f"✅ Déploiement créé: {config['version']} sur {config['environnement']}")
        print(f"   Priorité: {config['priorite']}, Statut: PREVU")
    
    # 6. Simuler le workflow d'autorisation et d'exécution
    print("\n📋 ÉTAPE 4: Workflow d'autorisation et d'exécution")
    print("-" * 70)
    
    for i, deploiement in enumerate(deploiements_crees):
        print(f"\n🔹 Déploiement {i+1}: {deploiement.version} sur {deploiement.environnement}")
        
        # Autoriser
        if deploiement.peut_etre_autorise():
            deploiement.autoriser(admin)
            print(f"   ✅ Autorisé par {admin.get_full_name()}")
        
        # Exécuter (simuler succès pour DEV et TEST, échec pour PREPROD)
        if deploiement.peut_etre_execute():
            deploiement.demarrer(admin)
            print(f"   ▶️  Démarré par {admin.get_full_name()}")
            
            if deploiement.environnement in ['DEV', 'TEST']:
                deploiement.marquer_reussi(f"Déploiement réussi sur {deploiement.environnement}\nAucune erreur détectée.")
                print(f"   ✅ Marqué comme RÉUSSI")
            elif deploiement.environnement == 'PREPROD':
                incident = deploiement.marquer_echec(
                    f"Erreur lors du déploiement sur {deploiement.environnement}\nErreur de connexion à la base de données.",
                    creer_incident=True
                )
                print(f"   ❌ Marqué comme ÉCHEC")
                if incident:
                    print(f"   🚨 Incident créé automatiquement: {incident.nom}")
            else:
                # PROD reste en attente
                print(f"   ⏸️  En attente (PROD nécessite validation supplémentaire)")
    
    # 7. Afficher le résumé
    print("\n📋 ÉTAPE 5: Résumé des déploiements")
    print("-" * 70)
    
    deploiements = tache_deploiement.deploiements.all()
    
    print(f"\n📊 Statistiques:")
    print(f"   Total: {deploiements.count()}")
    print(f"   Réussis: {deploiements.filter(statut='REUSSI').count()}")
    print(f"   Échecs: {deploiements.filter(statut='ECHEC').count()}")
    print(f"   Prévus: {deploiements.filter(statut='PREVU').count()}")
    print(f"   En cours: {deploiements.filter(statut='EN_COURS').count()}")
    
    print(f"\n📋 Liste détaillée:")
    for deploiement in deploiements:
        statut_emoji = {
            'PREVU': '⏸️',
            'EN_COURS': '▶️',
            'REUSSI': '✅',
            'ECHEC': '❌',
            'ANNULE': '🚫'
        }.get(deploiement.statut, '❓')
        
        print(f"   {statut_emoji} {deploiement.version} sur {deploiement.environnement}: {deploiement.statut}")
    
    # 8. Afficher l'URL pour accéder à l'interface
    print("\n📋 ÉTAPE 6: Accès à l'interface web")
    print("-" * 70)
    
    url = f"/projets/{projet.id}/etapes/{etape_deploiement.id}/taches/{tache_deploiement.id}/deploiements/"
    print(f"\n🌐 URL de gestion des déploiements:")
    print(f"   {url}")
    print(f"\n💡 Pour accéder à cette page:")
    print(f"   1. Démarrez le serveur: python manage.py runserver")
    print(f"   2. Ouvrez: http://localhost:8000{url}")
    print(f"   3. Cliquez sur le bouton 🚀 dans la liste des tâches")
    
    print("\n" + "="*70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("="*70)
    
    # Nettoyer (optionnel)
    print("\n🧹 Nettoyage des données de démonstration...")
    reponse = input("Voulez-vous supprimer les données créées? (o/n): ")
    if reponse.lower() == 'o':
        # Supprimer les incidents créés
        incidents = TacheEtape.objects.filter(nom__startswith="INCIDENT - Échec déploiement")
        incidents_count = incidents.count()
        incidents.delete()
        
        # Supprimer les déploiements
        deploiements.delete()
        
        # Supprimer la tâche
        tache_deploiement.delete()
        
        print(f"✅ Nettoyage terminé:")
        print(f"   - {deploiements.count()} déploiements supprimés")
        print(f"   - {incidents_count} incidents supprimés")
        print(f"   - 1 tâche supprimée")
    else:
        print("ℹ️  Données conservées pour exploration")


if __name__ == '__main__':
    try:
        demo_deploiement()
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
