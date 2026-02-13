#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lire le fichier
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacement simple
old_str = 'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet }}{% else %}{{ compte.get_full_name }}{% endif %}"'
new_str = 'data-compte-name="{{ compte.membre.get_nom_complet|default:compte.get_full_name }}"'

# Compter les occurrences
count = content.count(old_str)
print(f"Nombre d'occurrences trouvées: {count}")

# Remplacer
content = content.replace(old_str, new_str)

# Écrire le fichier
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Remplacement effectué avec succès! {count} occurrences remplacées.")
