#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# Lire le fichier
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern à rechercher et remplacer
old_pattern = r'data-compte-name="\{% if compte\.membre %\}\{\{ compte\.membre\.get_nom_complet %\}\{% else %\}\{\{ compte\.get_full_name %\}\{% endif %\}"'
new_value = 'data-compte-name="{{ compte.membre.get_nom_complet|default:compte.get_full_name }}"'

# Remplacer
content = re.sub(old_pattern, new_value, content)

# Écrire le fichier
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Remplacement effectué avec succès!")
