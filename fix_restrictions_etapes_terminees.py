#!/usr/bin/env python
"""
Script pour supprimer toutes les restrictions sur les étapes terminées
"""

def fix_restrictions():
    print("🔧 Suppression des restrictions sur les étapes terminées")
    
    # Lire le fichier views.py
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher et remplacer les restrictions
    restrictions_found = 0
    
    # Pattern 1: Restriction avec message d'erreur
    old_pattern1 = '''    # Vérifier que l'étape n'est pas terminée
    if etape.statut == 'TERMINEE':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Impossible de créer une tâche dans une étape terminée.'})
        messages.error(request, 'Impossible de créer une tâche dans une étape terminée.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)'''
    
    new_pattern1 = '''    # Permettre l'ajout de tâches aux étapes terminées (avec justification)
    etape_terminee = etape.statut == 'TERMINEE' '''
    
    if old_pattern1 in content:
        content = content.replace(old_pattern1, new_pattern1)
        restrictions_found += 1
        print("✅ Restriction 1 supprimée (création de tâche)")
    
    # Pattern 2: Autre variante possible
    old_pattern2 = '''    if etape.statut == 'TERMINEE':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Impossible de créer une tâche dans une étape terminée.'})
        messages.error(request, 'Impossible de créer une tâche dans une étape terminée.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)'''
    
    new_pattern2 = '''    # Permettre l'ajout de tâches aux étapes terminées (avec justification)
    etape_terminee = etape.statut == 'TERMINEE' '''
    
    if old_pattern2 in content:
        content = content.replace(old_pattern2, new_pattern2)
        restrictions_found += 1
        print("✅ Restriction 2 supprimée (création de tâche)")
    
    # Vérifier s'il y a d'autres restrictions
    if 'Impossible de créer une tâche dans une étape terminée' in content:
        print("⚠ Il reste encore des restrictions à corriger manuellement")
        
        # Trouver les lignes contenant cette restriction
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'Impossible de créer une tâche dans une étape terminée' in line:
                print(f"   Ligne {i+1}: {line.strip()}")
    
    # Sauvegarder le fichier modifié
    if restrictions_found > 0:
        with open('core/views.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {restrictions_found} restriction(s) supprimée(s)")
    else:
        print("ℹ Aucune restriction trouvée à supprimer")
    
    return restrictions_found > 0

def verify_fix():
    print("\n🔍 Vérification des corrections")
    
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier qu'il n'y a plus de restrictions
    if 'Impossible de créer une tâche dans une étape terminée' in content:
        print("❌ Il reste encore des restrictions")
        return False
    
    # Vérifier que la logique de justification est présente
    if 'justification_etape_terminee' in content:
        print("✅ Logique de justification présente")
    else:
        print("⚠ Logique de justification manquante")
    
    if 'etape_terminee = etape.statut' in content:
        print("✅ Variable etape_terminee présente")
    else:
        print("⚠ Variable etape_terminee manquante")
    
    return True

if __name__ == '__main__':
    print("🚀 Correction des restrictions sur les étapes terminées")
    print("=" * 60)
    
    success = fix_restrictions()
    verify_fix()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Corrections appliquées avec succès !")
        print("\n📋 Actions effectuées :")
        print("   • Suppression des restrictions de création de tâches")
        print("   • Ajout de la logique d'étapes terminées")
        print("\n🔄 Redémarrez le serveur Django pour appliquer les changements")
    else:
        print("ℹ Aucune correction nécessaire ou déjà appliquée")