#!/usr/bin/env python
"""
Script pour analyser le problème des responsables multiples et proposer une solution
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, Affectation, RoleProjet
from django.db.models import Count

def analyser_probleme():
    print("=" * 80)
    print("ANALYSE: Problème des Responsables Multiples")
    print("=" * 80)
    
    # 1. Trouver les projets avec plusieurs responsables
    print("\n1. PROJETS AVEC PLUSIEURS RESPONSABLES")
    print("-" * 80)
    
    projets_multi_resp = []
    
    for projet in Projet.objects.all():
        responsables = Affectation.objects.filter(
            projet=projet,
            est_responsable_principal=True,
            date_fin__isnull=True
        )
        
        if responsables.count() > 1:
            projets_multi_resp.append({
                'projet': projet,
                'responsables': list(responsables)
            })
    
    if not projets_multi_resp:
        print("✓ Aucun projet avec plusieurs responsables")
    else:
        print(f"⚠ {len(projets_multi_resp)} projet(s) avec plusieurs responsables:")
        for item in projets_multi_resp:
            print(f"\n  Projet: {item['projet'].nom}")
            print(f"  Responsables ({len(item['responsables'])}):")
            for aff in item['responsables']:
                print(f"    - {aff.utilisateur.get_full_name()} (ID: {aff.id})")
    
    # 2. Analyser l'utilisation de role_projet
    print("\n\n2. ANALYSE DE L'UTILISATION DES RÔLES")
    print("-" * 80)
    
    affectations_actives = Affectation.objects.filter(date_fin__isnull=True)
    
    # Compter par rôle
    roles_count = {}
    for aff in affectations_actives:
        role_nom = aff.role_projet.nom if aff.role_projet else "Aucun"
        flag = "Responsable" if aff.est_responsable_principal else "Membre"
        key = f"{role_nom} + flag={flag}"
        roles_count[key] = roles_count.get(key, 0) + 1
    
    print("Distribution des affectations:")
    for key, count in sorted(roles_count.items()):
        print(f"  {key}: {count}")
    
    # 3. Identifier les incohérences
    print("\n\n3. INCOHÉRENCES DÉTECTÉES")
    print("-" * 80)
    
    incoherences = []
    
    for aff in affectations_actives:
        role_nom = aff.role_projet.nom if aff.role_projet else None
        flag = aff.est_responsable_principal
        
        # Incohérence: RESPONSABLE_PRINCIPAL mais flag=False
        if role_nom == 'RESPONSABLE_PRINCIPAL' and not flag:
            incoherences.append({
                'type': 'ROLE_SANS_FLAG',
                'aff': aff,
                'desc': f"Rôle RESPONSABLE_PRINCIPAL mais flag=False"
            })
        
        # Incohérence: flag=True mais rôle différent
        if flag and role_nom != 'RESPONSABLE_PRINCIPAL':
            incoherences.append({
                'type': 'FLAG_SANS_ROLE',
                'aff': aff,
                'desc': f"Flag=True mais rôle={role_nom}"
            })
    
    if not incoherences:
        print("✓ Aucune incohérence détectée")
    else:
        print(f"⚠ {len(incoherences)} incohérence(s):")
        for inc in incoherences:
            aff = inc['aff']
            print(f"\n  {inc['desc']}")
            print(f"    Utilisateur: {aff.utilisateur.get_full_name()}")
            print(f"    Projet: {aff.projet.nom}")
    
    # 4. Proposition de solution
    print("\n\n4. PROPOSITION DE SOLUTION")
    print("=" * 80)
    
    print("""
PROBLÈME IDENTIFIÉ:
  La duplication entre 'role_projet' et 'est_responsable_principal' crée:
  - Des incohérences de données
  - De la complexité dans le code
  - Des bugs difficiles à détecter
  
SOLUTION RECOMMANDÉE:
  Supprimer le champ 'role_projet' et utiliser UNIQUEMENT 'est_responsable_principal'
  
  Avantages:
  ✓ Une seule source de vérité
  ✓ Pas d'incohérence possible
  ✓ Code plus simple et maintenable
  ✓ Moins de bugs
  
  Changements nécessaires:
  1. Supprimer le champ 'role_projet' du modèle Affectation
  2. Utiliser uniquement 'est_responsable_principal' partout
  3. Mettre à jour les vues et templates
  4. Créer une migration pour nettoyer les données
  
ALTERNATIVE (si vous voulez garder les rôles):
  Garder 'role_projet' mais le rendre automatique:
  - Si est_responsable_principal=True → role_projet=RESPONSABLE_PRINCIPAL (auto)
  - Si est_responsable_principal=False → role_projet=MEMBRE (auto)
  - Utiliser un signal ou une méthode save() pour maintenir la cohérence
    """)
    
    # 5. Statistiques
    print("\n5. STATISTIQUES")
    print("-" * 80)
    print(f"  Total affectations actives: {affectations_actives.count()}")
    print(f"  Responsables (flag=True): {affectations_actives.filter(est_responsable_principal=True).count()}")
    print(f"  Membres (flag=False): {affectations_actives.filter(est_responsable_principal=False).count()}")
    print(f"  Projets avec plusieurs responsables: {len(projets_multi_resp)}")
    print(f"  Incohérences: {len(incoherences)}")
    
    return projets_multi_resp, incoherences

if __name__ == '__main__':
    projets_multi, incoherences = analyser_probleme()
