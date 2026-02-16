from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from .models import Membre, Utilisateur
from .utils import enregistrer_audit

@login_required
def creer_profil_membre_admin_view(request):
    """Permet à un administrateur de créer son propre profil membre"""
    user = request.user
    
    # Vérifier que l'utilisateur est admin et n'a pas déjà un profil membre
    if not user.is_superuser:
        messages.error(request, 'Seuls les administrateurs peuvent accéder à cette page.')
        return redirect('dashboard')
    
    if hasattr(user, 'membre') and user.membre:
        messages.info(request, 'Vous avez déjà un profil membre.')
        return redirect('profil')
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            nom = request.POST.get('nom', '').strip()
            prenom = request.POST.get('prenom', '').strip()
            email_personnel = request.POST.get('email_personnel', '').strip()
            telephone = request.POST.get('telephone', '').strip()
            telephone_urgence = request.POST.get('telephone_urgence', '').strip()
            adresse = request.POST.get('adresse', '').strip()
            poste = request.POST.get('poste', '').strip()
            departement = request.POST.get('departement', '').strip()
            niveau_experience = request.POST.get('niveau_experience', '')
            competences_techniques = request.POST.get('competences_techniques', '').strip()
            specialites = request.POST.get('specialites', '').strip()
            
            # Validation
            if not nom or not prenom:
                messages.error(request, 'Le nom et le prénom sont obligatoires.')
                return render(request, 'core/creer_profil_membre_admin.html', {
                    'user': user,
                    'niveaux_experience': Membre.NIVEAU_EXPERIENCE_CHOICES,
                })
            
            if not email_personnel:
                messages.error(request, 'L\'email personnel est obligatoire.')
                return render(request, 'core/creer_profil_membre_admin.html', {
                    'user': user,
                    'niveaux_experience': Membre.NIVEAU_EXPERIENCE_CHOICES,
                })
            
            if not adresse:
                messages.error(request, 'L\'adresse est obligatoire.')
                return render(request, 'core/creer_profil_membre_admin.html', {
                    'user': user,
                    'niveaux_experience': Membre.NIVEAU_EXPERIENCE_CHOICES,
                })
            
            # Vérifier que l'email personnel n'existe pas déjà
            if Membre.objects.filter(email_personnel=email_personnel).exists():
                messages.error(request, 'Cet email personnel est déjà utilisé par un autre membre.')
                return render(request, 'core/creer_profil_membre_admin.html', {
                    'user': user,
                    'niveaux_experience': Membre.NIVEAU_EXPERIENCE_CHOICES,
                })
            
            # Créer le profil membre
            membre = Membre.objects.create(
                nom=nom,
                prenom=prenom,
                email_personnel=email_personnel,
                telephone=telephone,
                telephone_urgence=telephone_urgence,
                adresse=adresse,
                poste=poste,
                departement=departement,
                niveau_experience=niveau_experience,
                competences_techniques=competences_techniques,
                specialites=specialites,
                statut='ACTIF',
                createur=user
            )
            
            # Lier le profil membre au compte utilisateur
            user.membre = membre
            user.save()
            
            # Mettre à jour les informations du compte utilisateur si nécessaire
            if not user.first_name:
                user.first_name = prenom
            if not user.last_name:
                user.last_name = nom
            user.save()
            
            # Audit
            enregistrer_audit(
                utilisateur=user,
                type_action='CREATION_PROFIL_MEMBRE_ADMIN',
                description=f'Création du profil membre pour l\'administrateur {user.get_full_name()}',
                request=request,
                donnees_apres={
                    'membre_id': str(membre.id),
                    'nom_complet': f'{prenom} {nom}',
                    'email_personnel': email_personnel,
                    'poste': poste,
                    'departement': departement
                }
            )
            
            messages.success(request, 'Votre profil membre a été créé avec succès !')
            return redirect('profil')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du profil : {str(e)}')
    
    context = {
        'user': user,
        'niveaux_experience': Membre.NIVEAU_EXPERIENCE_CHOICES,
    }
    
    return render(request, 'core/creer_profil_membre_admin.html', context)


@login_required
@require_http_methods(["POST"])
def modifier_email_admin_view(request):
    """
    Permet à un administrateur de modifier son email personnel
    et synchronise automatiquement avec son compte utilisateur
    """
    user = request.user
    
    # Vérifier que l'utilisateur est admin
    if not user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Seuls les administrateurs peuvent modifier leur email.'
        }, status=403)
    
    # Vérifier que l'utilisateur a un profil membre
    if not hasattr(user, 'membre') or not user.membre:
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas de profil membre associé.'
        }, status=400)
    
    try:
        # Récupérer les données
        data = json.loads(request.body)
        nouvel_email = data.get('email_personnel', '').strip()
        
        # Validation
        if not nouvel_email:
            return JsonResponse({
                'success': False,
                'error': 'L\'email ne peut pas être vide.'
            }, status=400)
        
        # Vérifier le format email
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, nouvel_email):
            return JsonResponse({
                'success': False,
                'error': 'Format d\'email invalide.'
            }, status=400)
        
        # Vérifier que l'email n'est pas déjà utilisé par un autre membre
        if Membre.objects.filter(email_personnel=nouvel_email).exclude(id=user.membre.id).exists():
            return JsonResponse({
                'success': False,
                'error': 'Cet email est déjà utilisé par un autre membre.'
            }, status=400)
        
        # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
        if Utilisateur.objects.filter(email=nouvel_email).exclude(id=user.id).exists():
            return JsonResponse({
                'success': False,
                'error': 'Cet email est déjà utilisé par un autre compte utilisateur.'
            }, status=400)
        
        # Sauvegarder l'ancien email pour l'audit
        ancien_email_membre = user.membre.email_personnel
        ancien_email_user = user.email
        
        # Transaction atomique pour garantir la cohérence
        with transaction.atomic():
            # Mettre à jour le profil membre
            user.membre.email_personnel = nouvel_email
            user.membre.save()
            
            # Synchroniser avec le compte utilisateur
            user.email = nouvel_email
            user.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_EMAIL_ADMIN',
            description=f'Modification de l\'email par l\'administrateur {user.get_full_name()}',
            request=request,
            donnees_avant={
                'email_membre': ancien_email_membre,
                'email_user': ancien_email_user
            },
            donnees_apres={
                'email_membre': nouvel_email,
                'email_user': nouvel_email
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Email modifié avec succès !',
            'nouvel_email': nouvel_email
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données JSON invalides.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la modification : {str(e)}'
        }, status=500)