"""
Fix all references to tache_test to use tache_etape in views_tests.py
"""

with open('core/views_tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all tache_test references with tache_etape
replacements = [
    ('tache_test__etape=etape', 'tache_etape__etape=etape'),
    ('cas_test.tache_test.statut', 'cas_test.tache_etape.statut'),
]

for old, new in replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"✓ Replaced '{old}' with '{new}' ({count} occurrences)")

# Write the fixed content
with open('core/views_tests.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ All references updated")
