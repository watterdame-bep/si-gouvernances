"""
Vues pour la gestion des fichiers de projet
"""
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.db import transaction
import mimetypes
import os

from .models import Projet, FichierProjet
from .utils import enregistrer_audit


@login_required
@require_http_methods(["POST"])
def ajouter_fichiers_projet(request, projet_id):
    """Ajoute un ou plusieurs fichiers à un projet"""
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not request.user.est_super_admin():
        messages.error(request, "Vous n'avez pas la permission d'ajouter des fichiers.")
        return redirect('projet_detail', projet_id=projet_id)
    
    fichiers = request.FILES.getlist('fichiers')
    
    if not fichiers:
        messages.error(request, "Aucun fichier sélectionné.")
        return redirect('projet_detail', projet_id=projet_id)
    
    fichiers_ajoutes = []
    
    try:
        with transaction.atomic():
            for fichier in fichiers:
                # Vérifier la taille (max 10MB par fichier)
                if fichier.size > 10 * 1024 * 1024:
                    messages.warning(request, f"Le fichier '{fichier.name}' est trop volumineux (max 10MB).")
                    continue
                
                # Déterminer le type MIME
                type_mime, _ = mimetypes.guess_type(fichier.name)
                
                # Créer l'enregistrement
                fichier_projet = FichierProjet.objects.create(
                    projet=projet,
                    fichier=fichier,
                    nom_original=fichier.name,
                    taille=fichier.size,
                    type_mime=type_mime or 'application/octet-stream',
                    ajoute_par=request.user
                )
                
                fichiers_ajoutes.append(fichier.name)
            
            # Audit
            if fichiers_ajoutes:
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='AJOUT_FICHIERS_PROJET',
                    description=f"Ajout de {len(fichiers_ajoutes)} fichier(s) au projet {projet.nom}",
                    request=request,
                    donnees_apres={'fichiers': fichiers_ajoutes}
                )
                
                messages.success(request, f"{len(fichiers_ajoutes)} fichier(s) ajouté(s) avec succès.")
            
    except Exception as e:
        messages.error(request, f"Erreur lors de l'ajout des fichiers : {str(e)}")
    
    return redirect('projet_detail', projet_id=projet_id)


@login_required
@require_http_methods(["POST"])
def supprimer_fichier_projet(request, fichier_id):
    """Supprime un fichier d'un projet"""
    fichier = get_object_or_404(FichierProjet, id=fichier_id)
    projet_id = fichier.projet.id
    
    # Vérifier les permissions
    if not request.user.est_super_admin():
        return JsonResponse({
            'success': False,
            'error': "Vous n'avez pas la permission de supprimer des fichiers."
        })
    
    try:
        nom_fichier = fichier.nom_original
        
        # Supprimer le fichier physique
        if fichier.fichier:
            try:
                fichier.fichier.delete(save=False)
            except:
                pass
        
        # Supprimer l'enregistrement
        fichier.delete()
        
        # Audit
        enregistrer_audit(
            utilisateur=request.user,
            type_action='SUPPRESSION_FICHIER_PROJET',
            description=f"Suppression du fichier '{nom_fichier}' du projet {fichier.projet.nom}",
            request=request
        )
        
        return JsonResponse({
            'success': True,
            'message': f"Fichier '{nom_fichier}' supprimé avec succès."
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"Erreur lors de la suppression : {str(e)}"
        })


@login_required
def telecharger_fichier_projet(request, fichier_id):
    """Télécharge un fichier de projet"""
    fichier = get_object_or_404(FichierProjet, id=fichier_id)
    
    # Vérifier que l'utilisateur a accès au projet
    projet = fichier.projet
    if not request.user.est_super_admin():
        # Vérifier si l'utilisateur est membre du projet
        if not projet.affectations.filter(utilisateur=request.user, date_fin__isnull=True).exists():
            raise Http404("Fichier non trouvé")
    
    try:
        # Ouvrir le fichier
        response = FileResponse(fichier.fichier.open('rb'), content_type=fichier.type_mime)
        response['Content-Disposition'] = f'attachment; filename="{fichier.nom_original}"'
        response['Content-Length'] = fichier.taille
        
        return response
        
    except Exception as e:
        raise Http404("Fichier non trouvé")
