"""
Fix duplicate creer_cas_test_view functions and update to use tache_etape
"""

with open('core/views_tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first occurrence
first_start = content.find('@login_required\n@require_http_methods(["POST"])\ndef creer_cas_test_view(request, projet_id, etape_id, test_id):')
print(f"First occurrence at position: {first_start}")

# Find the second occurrence
second_start = content.find('@login_required\n@require_http_methods(["POST"])\ndef creer_cas_test_view(request, projet_id, etape_id, test_id):', first_start + 100)
print(f"Second occurrence at position: {second_start}")

if second_start > 0:
    # Find the end of the second function (next @login_required or end of file)
    second_end = content.find('\n\n@login_required', second_start + 100)
    if second_end == -1:
        second_end = content.find('\n\ndef ', second_start + 100)
    
    print(f"Second function ends at position: {second_end}")
    
    # Remove the duplicate
    new_content = content[:second_start] + content[second_end:]
    
    # Now update the first occurrence to use tache_id and tache_etape
    new_content = new_content.replace(
        'def creer_cas_test_view(request, projet_id, etape_id, test_id):',
        'def creer_cas_test_view(request, projet_id, etape_id, tache_id):'
    )
    
    new_content = new_content.replace(
        'tache_test = get_object_or_404(TacheTest, id=test_id, etape=etape)',
        '''from .models import TacheEtape, CasTest
    tache_etape = get_object_or_404(TacheEtape, id=tache_id, etape=etape)'''
    )
    
    new_content = new_content.replace(
        '''# Créer le cas de test
        from .models import CasTest
        cas_test = CasTest.objects.create(
            tache_test=tache_test,''',
        '''# Créer le cas de test
        cas_test = CasTest.objects.create(
            tache_etape=tache_etape,'''
    )
    
    # Write the fixed content
    with open('core/views_tests.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Duplicate removed and function updated")
else:
    print("No duplicate found")
