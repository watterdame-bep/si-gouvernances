#!/usr/bin/env python3
"""
Script pour corriger le template gestion_etapes.html
Remplace has_special_tasks par a_taches_speciales et special_tasks_count par get_nombre_taches_speciales
"""

def fix_template_badges():
    """Corrige le template pour utiliser les méthodes du modèle"""
    
    print("=" * 60)
    print("CORRECTION DU TEMPLATE GESTION_ETAPES.HTML")
    print("=" * 60)
    
    # Lire le fichier
    with open('templates/core/gestion_etapes.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Fichier lu: {len(content)} caractères")
    
    # Compter les occurrences avant correction
    count_has_special = content.count('has_special_tasks')
    count_special_count = content.count('special_tasks_count')
    
    print(f"🔍 Occurrences trouvées:")
    print(f"   - has_special_tasks: {count_has_special}")
    print(f"   - special_tasks_count: {count_special_count}")
    
    # Effectuer les remplacements
    print(f"\n🔧 Correction en cours...")
    
    # Remplacer has_special_tasks par a_taches_speciales
    new_content = content.replace('has_special_tasks', 'a_taches_speciales')
    
    # Remplacer special_tasks_count par get_nombre_taches_speciales
    new_content = new_content.replace('special_tasks_count', 'get_nombre_taches_speciales')
    
    # Vérifier les changements
    new_count_has_special = new_content.count('has_special_tasks')
    new_count_special_count = new_content.count('special_tasks_count')
    count_a_taches = new_content.count('a_taches_speciales')
    count_get_nombre = new_content.count('get_nombre_taches_speciales')
    
    print(f"✅ Après correction:")
    print(f"   - has_special_tasks: {new_count_has_special} (était {count_has_special})")
    print(f"   - special_tasks_count: {new_count_special_count} (était {count_special_count})")
    print(f"   - a_taches_speciales: {count_a_taches}")
    print(f"   - get_nombre_taches_speciales: {count_get_nombre}")
    
    # Écrire le fichier corrigé
    with open('templates/core/gestion_etapes.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"\n✅ Template corrigé avec succès!")
    
    if count_has_special > 0 or count_special_count > 0:
        print(f"🎉 {count_has_special + count_special_count} remplacements effectués")
    else:
        print(f"⚠️  Aucun remplacement nécessaire")

if __name__ == '__main__':
    fix_template_badges()