"""
Commande Django pour créer automatiquement le superadministrateur 'jovi'
Utilisé lors du déploiement initial
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée le superadministrateur jovi si il n\'existe pas déjà'

    def handle(self, *args, **options):
        username = 'jovi'
        email = 'jovi@si-gouvernance.local'
        password = 'jovi123'  # Mot de passe par défaut (à changer après première connexion)
        
        try:
            # Vérifier si l'utilisateur existe déjà
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'✓ L\'utilisateur "{username}" existe déjà')
                )
                user = User.objects.get(username=username)
                
                # S'assurer qu'il est superuser
                if not user.is_superuser:
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Droits superadmin ajoutés à "{username}"')
                    )
            else:
                # Créer le superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Superadministrateur "{username}" créé avec succès!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  Email: {email}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'  Mot de passe: {password}')
                )
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Changez le mot de passe après la première connexion!')
                )
                
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Erreur lors de la création: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Erreur inattendue: {e}')
            )
