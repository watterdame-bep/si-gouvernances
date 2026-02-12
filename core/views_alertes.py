"""
Vues pour la gestion des alertes projets
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from core.models import AlerteProjet, Projet


@login_required
def alertes_view(request):
    """Vue principale pour afficher les alertes de l'utilisateur"""
    
    # Récupérer toutes les alertes de l'utilisateur
    alertes = AlerteProjet.objects.filter(
        destinataire=request.user
    ).select_related('projet').order_by('-date_creation')
    
    # Statistiques
    total_alertes = alertes.count()
    alertes_non_lues = alertes.filter(lue=False).count()
    alertes_critiques = alertes.filter(niveau='DANGER', lue=False).count()
    alertes_avertissement = alertes.filter(niveau='WARNING', lue=False).count()
    
    context = {
        'alertes': alertes,
        'total_alertes': total_alertes,
        'alertes_non_lues': alertes_non_lues,
        'alertes_critiques': alertes_critiques,
        'alertes_avertissement': alertes_avertissement,
    }
    
    return render(request, 'core/alertes.html', context)


@login_required
def marquer_alerte_lue(request, alerte_id):
    """Marque une alerte comme lue"""
    
    alerte = get_object_or_404(AlerteProjet, id=alerte_id, destinataire=request.user)
    alerte.marquer_comme_lue()
    
    # Rediriger vers le projet concerné
    return redirect('projet_detail', projet_id=alerte.projet.id)


@login_required
def marquer_toutes_alertes_lues(request):
    """Marque toutes les alertes de l'utilisateur comme lues"""
    
    if request.method == 'POST':
        AlerteProjet.objects.filter(
            destinataire=request.user,
            lue=False
        ).update(lue=True, date_lecture=timezone.now())
    
    return redirect('alertes')


@login_required
def api_alertes_count(request):
    """API pour obtenir le nombre d'alertes non lues"""
    
    count = AlerteProjet.objects.filter(
        destinataire=request.user,
        lue=False
    ).count()
    
    return JsonResponse({'count': count})


@login_required
def api_alertes_list(request):
    """API pour obtenir la liste des alertes récentes"""
    
    alertes = AlerteProjet.objects.filter(
        destinataire=request.user
    ).select_related('projet').order_by('-date_creation')[:10]
    
    alertes_data = []
    for alerte in alertes:
        alertes_data.append({
            'id': alerte.id,
            'titre': alerte.titre,
            'message': alerte.message,
            'type_alerte': alerte.get_type_alerte_display(),
            'niveau': alerte.niveau,
            'couleur': alerte.get_couleur_badge(),
            'icone': alerte.get_icone(),
            'lue': alerte.lue,
            'date_creation': alerte.date_creation.isoformat(),
            'projet': {
                'id': str(alerte.projet.id),
                'nom': alerte.projet.nom,
            }
        })
    
    return JsonResponse({'alertes': alertes_data})
