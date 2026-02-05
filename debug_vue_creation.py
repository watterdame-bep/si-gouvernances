#!/usr/bin/env python
"""
Debug de la vue de création de tâches
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from django.test import Client
from core.models import Utilisateur, Projet, EtapeProjet

def debug_vue_creation():
    print("🔍 DEBUG : Vue de création de tâches")
    print("=" * 50)
    
    try:
        # Récupérer les données
        admin = Utilisateur.objects.get(username='admin')
        projet = Projet.objects.first()
        etape_terminee = projet.etapes.filter(statut='TERMINEE').first()
        
        print(f"👤 Utilisateur: {admin.get_full_name()}")
        print(f"📁 Projet: {projet.nom}")
        print(f"🎯 Étape: {etape_terminee.type_etape.get_nom_display()}")
        print(f"📊 Statut étape: '{etape_terminee.statut}'")
        print(f"🔍 Étape terminée? {etape_terminee.statut == 'TERMINEE'}")
        
        # Test direct de la vue
        from core.views import creer_tache_etape_view
        from django.http import HttpRequest
        from django.contrib.auth.models import AnonymousUser
        
        # Créer une requête simulée
        request = HttpRequest()
        request.method = 'GET'
        request.user = admin
        
        print(f"\n🌐 Test direct de la vue...")
        try:
            response = creer_tache_etape_view(request, str(projet.id), str(etape_terminee.id))
            print(f"✅ Vue exécutée avec succès")
            print(f"📄 Type de réponse: {type(response)}")
            
            # Vérifier le contexte si c'est un render
            if hasattr(response, 'context_data'):
                context = response.context_data
                print(f"🔍 Contexte:")
                for key, value in context.items():
                    if key == 'etape_terminee':
                        print(f"  - {key}: {value}")
                    elif key in ['projet', 'etape']:
                        print(f"  - {key}: {value.nom if hasattr(value, 'nom') else value}")
            
        except Exception as e:
            print(f"❌ Erreur dans la vue: {e}")
            import traceback
            traceback.print_exc()
        
        # Test avec client HTTP
        print(f"\n🌐 Test avec client HTTP...")
        client = Client()
        client.force_login(admin)
        
        url = f'/projets/{projet.id}/etapes/{etape_terminee.id}/taches/creer/'
        response = client.get(url)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Vérifier les éléments clés
            checks = {
                'etape_terminee variable': 'etape_terminee' in content,
                'justification field': 'justification_etape_terminee' in content,
                'warning message': 'Étape terminée - Justification requise' in content,
                'yellow background': 'bg-yellow-50' in content,
                'exclamation icon': 'fa-exclamation-triangle' in content,
            }
            
            print(f"🔍 Vérifications du contenu:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"  {status} {check}: {result}")
            
            # Extraire un échantillon du contenu
            if 'justification' in content.lower():
                print(f"\n📝 Échantillon avec 'justification':")
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'justification' in line.lower():
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}{lines[j].strip()}")
                        break
        
        # Test POST avec justification
        print(f"\n📤 Test POST avec justification...")
        post_data = {
            'nom': 'Test Debug Tâche',
            'description': 'Test de debug avec justification',
            'priorite': 'HAUTE',
            'justification_etape_terminee': 'Test de debug du système'
        }
        
        response = client.post(url, post_data)
        print(f"📊 Status POST: {response.status_code}")
        
        if response.status_code == 302:
            # Vérifier la tâche créée
            from core.models import TacheEtape
            tache = TacheEtape.objects.filter(nom='Test Debug Tâche').first()
            if tache:
                print(f"✅ Tâche créée:")
                print(f"  - Nom: {tache.nom}")
                print(f"  - Ajoutée après clôture: {tache.ajoutee_apres_cloture}")
                print(f"  - Justification: '{tache.justification_ajout_tardif}'")
            else:
                print(f"❌ Tâche non trouvée")
        else:
            print(f"❌ Erreur POST: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"Contenu: {response.content.decode('utf-8')[:500]}...")
        
        print(f"\n🎉 Debug terminé!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_vue_creation()