#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lire le fichier
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Corriger ligne par ligne
corrected = []
count = 0

for i, line in enumerate(lines):
    # Si la ligne contient le pattern problématique
    if 'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet' in line:
        # Lire aussi la ligne suivante si nécessaire
        full_line = line
        j = i + 1
        while j < len(lines) and '{% endif %}' not in full_line:
            full_line += lines[j]
            j += 1
        
        # Remplacer dans la ligne complète
        if '{% if compte.membre %}{{ compte.membre.get_nom_complet %}{% else %}{{ compte.get_full_name }}{% endif %}' in full_line:
            full_line = full_line.replace(
                '{% if compte.membre %}{{ compte.membre.get_nom_complet %}{% else %}{{ compte.get_full_name }}{% endif %}',
                '{{ compte.membre.get_nom_complet|default:compte.get_full_name }}'
            )
            count += 1
            print(f"✓ Ligne {i+1} corrigée")
            
            # Ajouter la ligne corrigée
            corrected.append(full_line)
            # Sauter les lignes suivantes qui ont été fusionnées
            for _ in range(j - i - 1):
                lines.pop(i + 1)
        else:
            corrected.append(line)
    else:
        corrected.append(line)

# Écrire le fichier
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.writelines(corrected)

print(f"\n{count} lignes corrigées!")
