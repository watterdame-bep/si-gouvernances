#!/usr/bin/env python
"""
Script pour ajouter la logique de justification dans creer_tache_etape_view
"""

def add_justification_logic():
    print("🔧 Ajout de la logique de justification")
    
    # Lire le fichier
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher et remplacer la section de récupération des données POST
    old_section = '''        date_fin = request.POST.get('date_fin')

        # Validation'''
    
    new_section = '''        date_fin = request.POST.get('date_fin')
        justification_etape_terminee = request.POST.get('justification_etape_terminee', '').strip()

        # Validation'''
    
    if old_section in content:
        content = content.replace(old_section, new_section)
        print("✅ Ajout du champ justification_etape_terminee")
    else:
        print("⚠ Section de récupération des données POST non trouvée")
    
    # Ajouter la validation de la justification
    old_validation = '''        if not description:
            errors.append('La description de la tâche est obligatoire.')

        responsable = None'''
    
    new_validation = '''        if not description:
            errors.append('La description de la tâche est obligatoire.')
        
        # Si l'étape est terminée, une justification est requise
        if etape_terminee and not justification_etape_terminee:
            errors.append('Une justification est requise pour ajouter une tâche à une étape terminée.')

        responsable = None'''
    
    if old_validation in content:
        content = content.replace(old_validation, new_validation)
        print("✅ Ajout de la validation de justification")
    else:
        print("⚠ Section de validation non trouvée")
    
    # Rechercher et modifier la section d'audit
    # Chercher la section d'audit existante
    audit_pattern = '''                # Audit
                enregistrer_audit(
                    utilisateur=user,
                    type_action='CREATION_TACHE',
                    description=f'Création de la tâche d\'étape "{nom}" dans l\'étape {etape.type_etape.get_nom_display()}','''
    
    new_audit = '''                # Audit avec justification si étape terminée
                audit_description = f'Création de la tâche d\'étape "{nom}" dans l\'étape {etape.type_etape.get_nom_display()}'
                if etape_terminee:
                    audit_description += f' (étape terminée - justification: {justification_etape_terminee})'
                
                enregistrer_audit(
                    utilisateur=user,
                    type_action='CREATION_TACHE',
                    description=audit_description,'''
    
    if audit_pattern in content:
        content = content.replace(audit_pattern, new_audit)
        print("✅ Modification de l'audit avec justification")
    else:
        print("⚠ Section d'audit non trouvée")
    
    # Ajouter etape_terminee et justification aux données d'audit
    audit_data_pattern = '''                    donnees_apres={
                        'tache': nom,
                        'etape': etape.type_etape.nom,
                        'responsable': responsable.get_full_name() if responsable else None,
                        'priorite': priorite
                    }'''
    
    new_audit_data = '''                    donnees_apres={
                        'tache': nom,
                        'etape': etape.type_etape.nom,
                        'etape_terminee': etape_terminee,
                        'justification': justification_etape_terminee if etape_terminee else None,
                        'responsable': responsable.get_full_name() if responsable else None,
                        'priorite': priorite
                    }'''
    
    if audit_data_pattern in content:
        content = content.replace(audit_data_pattern, new_audit_data)
        print("✅ Ajout des données de justification à l'audit")
    else:
        print("⚠ Section des données d'audit non trouvée")
    
    # Ajouter etape_terminee au contexte
    context_pattern = '''    context = {
        'projet': projet,
        'etape': etape,
        'equipe': projet.get_equipe(),
        'priorites': TacheEtape.PRIORITE_CHOICES,
    }'''
    
    new_context = '''    context = {
        'projet': projet,
        'etape': etape,
        'equipe': projet.get_equipe(),
        'priorites': TacheEtape.PRIORITE_CHOICES,
        'etape_terminee': etape_terminee,
    }'''
    
    if context_pattern in content:
        content = content.replace(context_pattern, new_context)
        print("✅ Ajout de etape_terminee au contexte")
    else:
        print("⚠ Section du contexte non trouvée")
    
    # Sauvegarder le fichier
    with open('core/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fichier sauvegardé")

def verify_changes():
    print("\n🔍 Vérification des modifications")
    
    with open('core/views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('justification_etape_terminee', 'Champ justification présent'),
        ('Une justification est requise', 'Validation de justification présente'),
        ('audit_description', 'Audit avec justification présent'),
        ('etape_terminee.*etape_terminee', 'Variable etape_terminee dans contexte')
    ]
    
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")

if __name__ == '__main__':
    print("🚀 Ajout de la logique de justification pour les étapes terminées")
    print("=" * 70)
    
    add_justification_logic()
    verify_changes()
    
    print("\n" + "=" * 70)
    print("✅ Modifications terminées !")
    print("\n📋 Fonctionnalités ajoutées :")
    print("   • Récupération du champ justification_etape_terminee")
    print("   • Validation obligatoire pour les étapes terminées")
    print("   • Audit enrichi avec justification")
    print("   • Variable etape_terminee dans le contexte")
    print("\n🔄 Redémarrez le serveur Django pour appliquer les changements")