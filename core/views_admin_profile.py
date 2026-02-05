from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Membre
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