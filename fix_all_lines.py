#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lire le fichier ligne par ligne
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Chercher et afficher les lignes problématiques
print("Lignes contenant le problème:")
for i, line in enumerate(lines, 1):
    if 'data-compte-name="{% if compte.membre %}' in line:
        print(f"Ligne {i}: {line.strip()[:100]}...")

# Corriger toutes les lignes
corrected_lines = []
for line in lines:
    if 'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet }}{% else %}{{ compte.get_full_name }}{% endif %}"' in line:
        line = line.replace(
            'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet }}{% else %}{{ compte.get_full_name }}{% endif %}"',
            'data-compte-name="{{ compte.membre.get_nom_complet|default:compte.get_full_name }}"'
        )
        print(f"✓ Ligne corrigée")
    corrected_lines.append(line)

# Écrire le fichier corrigé
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.writelines(corrected_lines)

print("\nFichier corrigé avec succès!")
