#!/usr/bin/env python3
"""
Diagnostic complet du système pour identifier tous les problèmes
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Projet, ModuleProjet

def diagnostic_complet():
    """Diagnostic complet du système"""
    
    print("🔍 DIAGNOSTIC COMPLET DU SYSTÈME")
    print("=" * 80)
    
    # Créer un client de test
    client = Client()
    
    # Récupérer un utilisateur admin
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        print("❌ Aucun utilisateur admin trouvé")
        return
    
    # Se connecter
    client.force_login(admin_user)
    print(f"👤 Utilisateur: {admin_user.get_full_name()} (Admin: {admin_user.est_super_admin()})")
    
    # Récupérer le projet GESTION STOCK
    projet = Projet.objects.filter(nom__icontains='GESTION STOCK').first()
    
    if not projet:
        print("❌ Projet GESTION STOCK non trouvé")
        return
    
    print(f"📁 Projet: {projet.nom} (ID: {projet.id})")
    
    # 1. TEST DE LA PAGE DE GESTION DES MODULES
    print(f"\n{'='*20} 1. PAGE GESTION MODULES {'='*20}")
    url_modules = f'/projets/{projet.id}/modules/'
    
    try:
        response = client.get(url_modules)
        print(f"🌐 URL: {url_modules}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Vérifications essentielles
            checks = [
                ('Modules du Projet', 'Titre principal'),
                ('Nouveau Module', 'Bouton créer module'),
                ('ouvrirModalCreerModule', 'Fonction JS créer module'),
                ('gererTachesModule', 'Fonction JS tâches'),
                ('Gérer les tâches', 'Bouton tâches'),
                ('bg-green-600', 'Style bouton tâches'),
                ('voirDetailsModule', 'Fonction détails'),
                ('ouvrirModalAffecterModuleNouveau', 'Fonction affecter'),
            ]
            
            for check, desc in checks:
                status = "✅" if check in content else "❌"
                print(f"   {status} {desc}")
            
            # Compter les modules
            modules = projet.modules.all()
            print(f"📊 Modules dans le projet: {modules.count()}")
            
            for module in modules:
                print(f"   - {module.nom} (ID: {module.id})")
                affectations = module.affectations.filter(date_fin_affectation__isnull=True)
                print(f"     Équipe: {affectations.count()} membre(s)")
                for aff in affectations:
                    print(f"       • {aff.utilisateur.get_full_name()} ({aff.role_module})")
        
    except Exception as e:
        print(f"💥 Erreur: {str(e)}")
    
    # 2. TEST DE LA CRÉATION DE MODULE
    print(f"\n{'='*20} 2. CRÉATION DE MODULE {'='*20}")
    url_creer = f'/projets/{projet.id}/modules/creer/'
    
    try:
        response = client.get(url_creer)
        print(f"🌐 URL: {url_creer}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Page de création accessible")
        elif response.status_code == 302:
            print(f"🔄 Redirection vers: {response.url}")
        elif response.status_code == 405:
            print("❌ Erreur 405 - Method Not Allowed")
        else:
            print(f"❌ Erreur {response.status_code}")
            
    except Exception as e:
        print(f"💥 Erreur: {str(e)}")
    
    # 3. TEST DES TÂCHES DE MODULE
    print(f"\n{'='*20} 3. TÂCHES DE MODULE {'='*20}")
    
    if modules.exists():
        module = modules.first()
        url_taches = f'/projets/{projet.id}/modules/{module.id}/taches/'
        
        try:
            response = client.get(url_taches)
            print(f"🌐 URL: {url_taches}")
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Page tâches accessible")
                content = response.content.decode('utf-8')
                
                if 'Tâches du Module' in content:
                    print("✅ Interface tâches correcte")
                
                taches = module.taches.all()
                print(f"📊 Tâches dans le module: {taches.count()}")
                
            else:
                print(f"❌ Erreur {response.status_code}")
                
        except Exception as e:
            print(f"💥 Erreur: {str(e)}")
    
    # 4. VÉRIFICATION DES FICHIERS CRITIQUES
    print(f"\n{'='*20} 4. FICHIERS CRITIQUES {'='*20}")
    
    fichiers_critiques = [
        'core/views.py',
        'core/views_affectation.py', 
        'core/views_taches_module.py',
        'core/urls.py',
        'templates/core/gestion_modules.html',
        'templates/core/creer_module.html',
        'templates/core/gestion_taches_module.html',
    ]
    
    for fichier in fichiers_critiques:
        if os.path.exists(fichier):
            print(f"✅ {fichier}")
        else:
            print(f"❌ {fichier} - MANQUANT")
    
    # 5. VÉRIFICATION DES URLS
    print(f"\n{'='*20} 5. CONFIGURATION URLS {'='*20}")
    
    from django.urls import reverse
    from django.urls.exceptions import NoReverseMatch
    
    urls_test = [
        ('gestion_modules', [projet.id]),
        ('creer_module', [projet.id]),
        ('gestion_taches_module', [projet.id, modules.first().id] if modules.exists() else None),
    ]
    
    for url_name, args in urls_test:
        if args:
            try:
                url = reverse(url_name, args=args)
                print(f"✅ {url_name}: {url}")
            except NoReverseMatch as e:
                print(f"❌ {url_name}: {str(e)}")
        else:
            print(f"⚠️ {url_name}: Pas de module pour tester")
    
    print(f"\n{'='*20} RÉSUMÉ {'='*20}")
    print("Si des éléments sont marqués ❌, ils nécessitent une correction.")
    print("Les problèmes les plus critiques sont généralement:")
    print("1. Erreurs 405 sur la création de module")
    print("2. Boutons manquants dans l'interface")
    print("3. URLs mal configurées")

if __name__ == '__main__':
    diagnostic_complet()