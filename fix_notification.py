#!/usr/bin/env python3
"""
Script pour corriger la notification dans terminer_tache_etape
"""

with open('core/views.py', 'r') as f:
    content = f.read()

# Remplacer seulement dans la fonction terminer_tache_etape (à la fin du fichier)
old_notification = """                NotificationTache.objects.create(
                    tache=tache,
                    utilisateur=membre,
                    type_notification='TACHE_TERMINEE',
                    message=f'La tâche "{tache.nom}" a été terminée par {user.get_full_name()}'
                )"""

new_notification = """                NotificationTache.objects.create(
                    destinataire=membre,
                    tache=tache,
                    type_notification='TACHE_TERMINEE',
                    titre=f'Tâche terminée: {tache.nom}',
                    message=f'La tâche "{tache.nom}" a été terminée par {user.get_full_name()}',
                    emetteur=user
                )"""

# Remplacer seulement la dernière occurrence (dans terminer_tache_etape)
last_pos = content.rfind(old_notification)
if last_pos != -1:
    content = content[:last_pos] + new_notification + content[last_pos + len(old_notification):]
    print(f"Notification corrigée à la position {last_pos}")
else:
    print("Notification non trouvée")

with open('core/views.py', 'w') as f:
    f.write(content)

print('Correction terminée')