#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Lire tout le contenu
with open('templates/core/gestion_comptes.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Patterns possibles (avec et sans retours à la ligne)
patterns = [
    'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet }}{% else %}{{ compte.get_full_name }}{% endif %}"',
    'data-compte-name="{% if compte.membre %}{{ compte.\nmembre.get_nom_complet %}{% else %}{{ compte.get_full_name }}{% endif %}"',
    'data-compte-name="{% if compte.membre %}{{ compte.membre.get_nom_complet\n %}{% else %}{{ compte.get_full_name }}{% endif %}"',
]

replacement = 'data-compte-name="{{ compte.membre.get_nom_complet|default:compte.get_full_name }}"'

total_replaced = 0
for pattern in patterns:
    count = content.count(pattern)
    if count > 0:
        print(f"Trouvé {count} occurrences du pattern")
        content = content.replace(pattern, replacement)
        total_replaced += count

# Essayer aussi avec des variations d'espaces
import re
# Remplacer toutes les variations possibles
pattern_regex = r'data-compte-name="{% if compte\.membre %}{{ compte\.membre\.get_nom_complet\s*%}{% else %}{{ compte\.get_full_name\s*%}{% endif %}"'
matches = len(re.findall(pattern_regex, content))
if matches > 0:
    print(f"Trouvé {matches} occurrences avec regex")
    content = re.sub(pattern_regex, replacement, content)
    total_replaced += matches

# Écrire le fichier
with open('templates/core/gestion_comptes.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nTotal: {total_replaced} occurrences corrigées.")

# Vérifier s'il reste des problèmes
if '{% if compte.membre %}{{ compte.membre.get_nom_complet' in content:
    print("\n⚠️ ATTENTION: Il reste encore des occurrences problématiques!")
    # Trouver les lignes
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if '{% if compte.membre %}{{ compte.membre.get_nom_complet' in line:
            print(f"  Ligne {i}: {line.strip()[:80]}...")
else:
    print("\n✓ Toutes les occurrences ont été corrigées!")
