#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lire tout le contenu
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern à chercher (avec possibilité de retours à la ligne)
import re

# Chercher le pattern avec espaces/retours à la ligne flexibles
pattern = r'data-compte-name="\{%\s*if\s+compte\.membre\s*%\}\{\{\s*compte\.membre\.get_nom_complet\s*%\}\{%\s*else\s*%\}\{\{\s*compte\.get_full_name\s*%\}\{%\s*endif\s*%\}"'

# Compter les occurrences
matches = re.findall(pattern, content)
print(f"Nombre d'occurrences trouvées: {len(matches)}")

# Remplacer
replacement = 'data-compte-name="{{ compte.membre.get_nom_complet|default:compte.get_full_name }}"'
content_fixed = re.sub(pattern, replacement, content)

# Écrire le fichier
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print(f"Remplacement effectué! {len(matches)} occurrences corrigées.")
