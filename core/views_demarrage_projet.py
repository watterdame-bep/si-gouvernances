"""
Vues pour la gestion du démarrage et suivi temporel des projets
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Projet, NotificationProjet
from .utils import enregistrer_audit


@login_required
@require_POST
def demarrer_projet_view(request, projet_id):
    """
    Vue pour démarrer un projet
    
    Règles :
    - Seul le responsable peut démarrer le projet
    - Le projet doit être en statut CREE
    - Une durée doit être définie
    """
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur est le responsable
    responsable = projet.get_responsable_principal()
    if not responsable or responsable.id != request.user.id:
        messages.error(request, "Seul le responsable du projet peut le démarrer.")
        return redirect('detail_projet', projet_id=projet.id)
    
    # Vérifier que le projet peut être démarré
    if not projet.peut_etre_demarre():
        messages.error(request, "Ce projet ne peut pas être démarré (déjà démarré ou durée non définie).")
        return redirect('detail_projet', projet_id=projet.id)
    
    # Démarrer le projet
    resultat = projet.demarrer_projet(request.user)
    
    if resultat['success']:
        messages.success(request, resultat['message'])
    else:
        messages.error(request, resultat['message'])
    
    return redirect('detail_projet', projet_id=projet.id)


@login_required
def ajax_demarrer_projet(request, projet_id):
    """
    Vue AJAX pour démarrer un projet
    
    Returns:
        JSON avec success, message, et données du projet
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur est le responsable
    responsable = projet.get_responsable_principal()
    if not responsable or responsable.id != request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Seul le responsable du projet peut le démarrer.'
        }, status=403)
    
    # Démarrer le projet
    resultat = projet.demarrer_projet(request.user)
    
    if resultat['success']:
        return JsonResponse({
            'success': True,
            'message': resultat['message'],
            'date_debut': resultat['date_debut'].strftime('%d/%m/%Y'),
            'date_fin': resultat['date_fin'].strftime('%d/%m/%Y'),
            'jours_restants': projet.jours_restants(),
            'pourcentage_avancement': projet.pourcentage_avancement_temps()
        })
    else:
        return JsonResponse({
            'success': False,
            'message': resultat['message']
        }, status=400)


@login_required
def info_temporelle_projet(request, projet_id):
    """
    Vue AJAX pour obtenir les informations temporelles d'un projet
    
    Returns:
        JSON avec les informations de timing du projet
    """
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur a accès au projet
    if not request.user.a_acces_projet(projet):
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas accès à ce projet.'
        }, status=403)
    
    data = {
        'success': True,
        'projet_id': str(projet.id),
        'nom': projet.nom,
        'duree_projet': projet.duree_projet,
        'date_debut': projet.date_debut.strftime('%d/%m/%Y') if projet.date_debut else None,
        'date_fin': projet.date_fin.strftime('%d/%m/%Y') if projet.date_fin else None,
        'jours_restants': projet.jours_restants(),
        'pourcentage_avancement': projet.pourcentage_avancement_temps(),
        'est_proche_fin': projet.est_proche_fin(),
        'badge': projet.get_badge_jours_restants(),
        'peut_etre_demarre': projet.peut_etre_demarre(),
        'est_responsable': projet.get_responsable_principal() == request.user if projet.get_responsable_principal() else False
    }
    
    return JsonResponse(data)
