"""
Vues SIMPLIFIÉES pour la gestion de la MAINTENANCE V2
Architecture moderne inspirée de Jira/GitHub Issues
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import (
    Projet, Utilisateur, ContratGarantie, TicketMaintenance,
    CommentaireTicket, PieceJointeTicket
)


# ============================================================================
# GESTION DES CONTRATS DE GARANTIE (Conservée)
# ============================================================================

@login_required
def gestion_contrats_view(request, projet_id):
    """Vue principale de gestion des contrats de garantie"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions d'accès
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer tous les contrats
    contrats = projet.contrats_garantie.all().select_related('cree_par')
    
    # Statistiques
    contrats_actifs = [c for c in contrats if c.est_actif]
    contrats_expires = [c for c in contrats if not c.est_actif]
    
    # RÈGLE DE GOUVERNANCE : Seul l'Admin peut créer/modifier des contrats
    peut_creer_contrat = user.est_super_admin()
    
    context = {
        'projet': projet,
        'contrats': contrats,
        'contrats_actifs': contrats_actifs,
        'contrats_expires': contrats_expires,
        'peut_creer': peut_creer_contrat,
    }
    
    return render(request, 'core/gestion_contrats.html', context)


@login_required
def creer_contrat_view(request, projet_id):
    """Créer un nouveau contrat de garantie"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # RÈGLE DE GOUVERNANCE : Seul l'Administrateur peut créer un contrat
    if not user.est_super_admin():
        messages.error(request, 'Permissions insuffisantes. Seul l\'Administrateur peut créer un contrat de maintenance.')
        return redirect('gestion_contrats', projet_id=projet.id)
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        context = {
            'projet': projet,
        }
        return render(request, 'core/creer_contrat.html', context)
    
    # POST: Créer le contrat
    try:
        type_garantie = request.POST.get('type_garantie')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        sla_heures = request.POST.get('sla_heures')
        description_couverture = request.POST.get('description_couverture', '').strip()
        exclusions = request.POST.get('exclusions', '').strip()
        
        # Validation
        if not all([type_garantie, date_debut, date_fin, sla_heures, description_couverture]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('creer_contrat', projet_id=projet.id)
        
        # Créer le contrat
        contrat = ContratGarantie(
            projet=projet,
            type_garantie=type_garantie,
            date_debut=date_debut,
            date_fin=date_fin,
            sla_heures=int(sla_heures),
            description_couverture=description_couverture,
            exclusions=exclusions,
            cree_par=user
        )
        
        # Valider (vérifie les chevauchements)
        contrat.full_clean()
        contrat.save()
        
        messages.success(request, f'Contrat de garantie {contrat.get_type_garantie_display()} créé avec succès.')
        return redirect('gestion_contrats', projet_id=projet.id)
        
    except ValidationError as e:
        messages.error(request, f'Erreur de validation : {e.message}')
        return redirect('creer_contrat', projet_id=projet.id)
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('creer_contrat', projet_id=projet.id)


# ============================================================================
# GESTION DES TICKETS DE MAINTENANCE - VERSION SIMPLIFIÉE
# ============================================================================

@login_required
def gestion_tickets_view(request, projet_id):
    """Vue principale de gestion des tickets de maintenance"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions d'accès
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer tous les tickets avec les relations
    tickets = projet.tickets_maintenance.all().select_related(
        'contrat_garantie', 'cree_par', 'modifie_par'
    ).prefetch_related('assignes_a').order_by('-date_creation')
    
    # Filtres
    statut_filtre = request.GET.get('statut')
    priorite_filtre = request.GET.get('priorite')
    type_filtre = request.GET.get('type')
    
    if statut_filtre:
        tickets = tickets.filter(statut=statut_filtre)
    if priorite_filtre:
        tickets = tickets.filter(priorite=priorite_filtre)
    if type_filtre:
        tickets = tickets.filter(type_demande=type_filtre)
    
    # Statistiques
    stats = {
        'total': tickets.count(),
        'ouverts': tickets.filter(statut='OUVERT').count(),
        'en_cours': tickets.filter(statut='EN_COURS').count(),
        'resolus': tickets.filter(statut='RESOLU').count(),
        'fermes': tickets.filter(statut='FERME').count(),
        'rejetes': tickets.filter(statut='REJETE').count(),
        'critiques': tickets.filter(priorite='CRITIQUE').count(),
        'sla_depasses': len([t for t in tickets if t.sla_depasse]),
    }
    
    # Contrats actifs pour création
    contrats_actifs = [c for c in projet.contrats_garantie.all() if c.est_actif]
    
    # RÈGLE DE GOUVERNANCE : Seuls Admin et Responsable du projet peuvent créer un ticket
    responsable_projet = projet.get_responsable_principal()
    peut_creer_ticket = user.est_super_admin() or (responsable_projet and responsable_projet == user)
    
    context = {
        'projet': projet,
        'tickets': tickets,
        'stats': stats,
        'contrats_actifs': contrats_actifs,
        'peut_creer': peut_creer_ticket,
        'a_contrat_actif': len(contrats_actifs) > 0,
    }
    
    return render(request, 'core/gestion_tickets.html', context)


@login_required
def creer_ticket_view(request, projet_id):
    """Créer un nouveau ticket de maintenance - VERSION SIMPLIFIÉE"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # RÈGLE DE GOUVERNANCE 1 : Seuls Admin et Responsable du projet peuvent créer un ticket
    responsable_projet = projet.get_responsable_principal()
    peut_creer = user.est_super_admin() or (responsable_projet and responsable_projet == user)
    
    if not peut_creer:
        messages.error(request, 'Permissions insuffisantes. Seuls l\'Administrateur et le Responsable du projet peuvent créer un ticket de maintenance.')
        return redirect('gestion_tickets', projet_id=projet.id)
    
    # RÈGLE DE GOUVERNANCE 2 : Vérifier qu'il existe un contrat actif
    contrats_actifs = [c for c in projet.contrats_garantie.all() if c.est_actif]
    
    if not contrats_actifs:
        messages.error(request, 'Impossible de créer un ticket : aucun contrat de maintenance actif pour ce projet.')
        return redirect('gestion_tickets', projet_id=projet.id)
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        # Récupérer l'équipe pour l'assignation
        equipe = projet.get_equipe()
        developpeurs = [m for m in equipe if m.role_systeme and m.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']]
        
        context = {
            'projet': projet,
            'contrats_actifs': contrats_actifs,
            'developpeurs': developpeurs,
        }
        return render(request, 'core/creer_ticket.html', context)
    
    # POST: Créer le ticket
    try:
        titre = request.POST.get('titre', '').strip()
        description = request.POST.get('description_probleme', '').strip()
        type_demande = request.POST.get('type_demande', 'BUG')
        priorite = request.POST.get('priorite', 'NORMALE')
        gravite = request.POST.get('gravite', 'MAJEUR')
        origine = request.POST.get('origine', 'CLIENT')
        contrat_id = request.POST.get('contrat_garantie')
        temps_estime = request.POST.get('temps_estime', '')
        assignes_ids = request.POST.getlist('assignes_a')
        
        # Validation
        if not all([titre, description, gravite, origine]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('creer_ticket', projet_id=projet.id)
        
        # Récupérer le contrat si spécifié
        contrat = None
        if contrat_id:
            contrat = get_object_or_404(ContratGarantie, id=contrat_id, projet=projet)
            if not contrat.est_actif:
                messages.error(request, 'Le contrat sélectionné n\'est plus actif.')
                return redirect('creer_ticket', projet_id=projet.id)
        
        # Créer le ticket
        ticket = TicketMaintenance.objects.create(
            projet=projet,
            contrat_garantie=contrat,
            titre=titre,
            description_probleme=description,
            type_demande=type_demande,
            priorite=priorite,
            gravite=gravite,
            origine=origine,
            temps_estime=float(temps_estime) if temps_estime else None,
            cree_par=user
        )
        
        # Assigner les développeurs si spécifiés
        if assignes_ids:
            assignes = Utilisateur.objects.filter(id__in=assignes_ids)
            ticket.assigner(assignes, user)
            # Démarrer automatiquement le travail si assigné
            if ticket.statut == 'OUVERT':
                ticket.demarrer_travail(user)
            
            # Créer des notifications pour chaque développeur assigné
            from .models import NotificationProjet
            for dev in assignes:
                NotificationProjet.objects.create(
                    destinataire=dev,
                    projet=projet,
                    type_notification='ASSIGNATION_TICKET_MAINTENANCE',
                    titre=f'Ticket de maintenance {ticket.numero_ticket}',
                    message=f'Vous avez été assigné au ticket de maintenance {ticket.numero_ticket} : {ticket.titre}',
                    emetteur=user,
                    donnees_contexte={
                        'ticket_id': str(ticket.id),
                        'ticket_numero': ticket.numero_ticket,
                        'lien': f'/projets/{projet.id}/tickets/{ticket.id}/?from=notifications'
                    }
                )
        
        # Message selon le statut de garantie
        if not ticket.est_sous_garantie:
            messages.warning(
                request,
                f'Ticket {ticket.numero_ticket} créé. ⚠️ HORS GARANTIE : {ticket.raison_rejet}'
            )
        else:
            messages.success(request, f'Ticket {ticket.numero_ticket} créé avec succès sous garantie.')
        
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
        
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('creer_ticket', projet_id=projet.id)


@login_required
def detail_ticket_view(request, projet_id, ticket_id):
    """Vue détaillée d'un ticket - STYLE JIRA"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        role_projet = user.get_role_sur_projet(projet)
        if not role_projet and not user.a_acces_projet(projet):
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les commentaires
    commentaires = ticket.commentaires.all().select_related('auteur').order_by('date_creation')
    
    # Récupérer les pièces jointes
    pieces_jointes = ticket.pieces_jointes.all().select_related('uploade_par').order_by('-date_upload')
    
    # Permissions
    role_projet = user.get_role_sur_projet(projet)
    responsable_projet = projet.get_responsable_principal()
    
    peut_modifier = user.est_super_admin() or (responsable_projet and responsable_projet == user)
    peut_commenter = user.a_acces_projet(projet) or user.est_super_admin()
    est_assigne = user in ticket.assignes_a.all()
    peut_resoudre = est_assigne or peut_modifier
    
    # Équipe pour assignation
    equipe = projet.get_equipe()
    developpeurs = [m for m in equipe if m.role_systeme and m.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']]
    
    context = {
        'projet': projet,
        'ticket': ticket,
        'commentaires': commentaires,
        'pieces_jointes': pieces_jointes,
        'peut_modifier': peut_modifier,
        'peut_commenter': peut_commenter,
        'peut_resoudre': peut_resoudre,
        'est_assigne': est_assigne,
        'developpeurs': developpeurs,
    }
    
    return render(request, 'core/detail_ticket.html', context)


@login_required
@require_http_methods(["POST"])
def assigner_ticket_view(request, projet_id, ticket_id):
    """Assigner un ticket à un ou plusieurs développeurs"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    responsable_projet = projet.get_responsable_principal()
    if not user.est_super_admin() and not (responsable_projet and responsable_projet == user):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        assignes_ids = request.POST.getlist('assignes_a')
        
        if not assignes_ids:
            return JsonResponse({'success': False, 'error': 'Aucun développeur sélectionné'})
        
        assignes = Utilisateur.objects.filter(id__in=assignes_ids)
        ticket.assigner(assignes, user)
        
        # Démarrer le travail si le ticket est ouvert
        if ticket.statut == 'OUVERT':
            ticket.demarrer_travail(user)
        
        # Créer des notifications pour chaque développeur assigné
        from .models import NotificationProjet
        for dev in assignes:
            NotificationProjet.objects.create(
                destinataire=dev,
                projet=ticket.projet,
                type_notification='ASSIGNATION_TICKET_MAINTENANCE',
                titre=f'Ticket de maintenance {ticket.numero_ticket}',
                message=f'Vous avez été assigné au ticket de maintenance {ticket.numero_ticket} : {ticket.titre}',
                emetteur=user,
                donnees_contexte={
                    'ticket_id': str(ticket.id),
                    'ticket_numero': ticket.numero_ticket,
                    'lien': f'/projets/{ticket.projet.id}/tickets/{ticket.id}/?from=notifications'
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket assigné à {", ".join([a.get_full_name() for a in assignes])}'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def ajouter_commentaire_view(request, projet_id, ticket_id):
    """Ajouter un commentaire à un ticket"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    if not user.a_acces_projet(projet) and not user.est_super_admin():
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        contenu = request.POST.get('contenu', '').strip()
        est_interne = request.POST.get('est_interne') == 'true'
        
        if not contenu:
            return JsonResponse({'success': False, 'error': 'Le commentaire ne peut pas être vide'})
        
        commentaire = CommentaireTicket.objects.create(
            ticket=ticket,
            auteur=user,
            contenu=contenu,
            est_interne=est_interne
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Commentaire ajouté avec succès',
            'commentaire': {
                'id': str(commentaire.id),
                'auteur': user.get_full_name(),
                'contenu': contenu,
                'date': commentaire.date_creation.strftime('%d/%m/%Y %H:%M'),
                'est_interne': est_interne
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def resoudre_ticket_view(request, projet_id, ticket_id):
    """Marquer un ticket comme résolu"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    est_assigne = user in ticket.assignes_a.all()
    responsable_projet = projet.get_responsable_principal()
    peut_resoudre = est_assigne or user.est_super_admin() or (responsable_projet and responsable_projet == user)
    
    if not peut_resoudre:
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        solution = request.POST.get('solution', '').strip()
        fichiers_modifies = request.POST.get('fichiers_modifies', '').strip()
        temps_passe = request.POST.get('temps_passe', '')
        
        if not solution:
            return JsonResponse({'success': False, 'error': 'Une solution doit être fournie'})
        
        # Mettre à jour le temps passé si fourni
        if temps_passe:
            ticket.temps_passe = float(temps_passe)
            ticket.save()
        
        # Résoudre le ticket
        ticket.resoudre(user, solution, fichiers_modifies)
        
        # Créer une notification pour l'administrateur
        from .models import NotificationProjet
        # Chercher l'administrateur (rôle ADMIN ou DIRECTION)
        admin = Utilisateur.objects.filter(
            role_systeme__nom__in=['ADMIN', 'DIRECTION']
        ).first()
        
        if admin:
            NotificationProjet.objects.create(
                destinataire=admin,
                projet=projet,
                type_notification='TICKET_RESOLU',
                titre=f'Ticket {ticket.numero_ticket} résolu',
                message=f'Le ticket {ticket.numero_ticket} "{ticket.titre}" a été résolu par {user.get_full_name()}.',
                emetteur=user,
                donnees_contexte={
                    'ticket_id': str(ticket.id),
                    'ticket_numero': ticket.numero_ticket,
                    'lien': f'/projets/{projet.id}/tickets/{ticket.id}/?from=notifications'
                }
            )
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket {ticket.numero_ticket} marqué comme résolu'
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def fermer_ticket_view(request, projet_id, ticket_id):
    """Fermer un ticket (après validation client)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    responsable_projet = projet.get_responsable_principal()
    if not user.est_super_admin() and not (responsable_projet and responsable_projet == user):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        ticket.fermer(user)
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket {ticket.numero_ticket} fermé avec succès'
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def rejeter_ticket_view(request, projet_id, ticket_id):
    """Rejeter un ticket"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    responsable_projet = projet.get_responsable_principal()
    if not user.est_super_admin() and not (responsable_projet and responsable_projet == user):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        raison = request.POST.get('raison', '').strip()
        
        if not raison:
            return JsonResponse({'success': False, 'error': 'Une raison doit être fournie'})
        
        ticket.rejeter(user, raison)
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket {ticket.numero_ticket} rejeté'
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_http_methods(["POST"])
def ajouter_temps_view(request, projet_id, ticket_id):
    """Ajouter du temps passé sur un ticket"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier que l'utilisateur est assigné
    if user not in ticket.assignes_a.all() and not user.est_super_admin():
        return JsonResponse({'success': False, 'error': 'Vous devez être assigné au ticket'})
    
    try:
        heures = request.POST.get('heures', '')
        
        if not heures:
            return JsonResponse({'success': False, 'error': 'Le nombre d\'heures doit être fourni'})
        
        ticket.ajouter_temps(float(heures), user)
        
        return JsonResponse({
            'success': True,
            'message': f'{heures}h ajoutées au ticket',
            'temps_passe': float(ticket.temps_passe),
            'pourcentage': ticket.pourcentage_avancement
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================================================
# VUES GLOBALES POUR LA NAVIGATION TICKETS
# ============================================================================

@login_required
def mes_tickets_view(request):
    """Vue : Mes tickets assignés"""
    user = request.user
    
    # Récupérer uniquement les tickets assignés à l'utilisateur
    tickets = TicketMaintenance.objects.filter(
        assignes_a=user
    ).select_related('projet', 'cree_par').prefetch_related('assignes_a').order_by('-date_creation')
    
    # Filtres
    statut_filtre = request.GET.get('statut')
    priorite_filtre = request.GET.get('priorite')
    
    if statut_filtre:
        tickets = tickets.filter(statut=statut_filtre)
    if priorite_filtre:
        tickets = tickets.filter(priorite=priorite_filtre)
    
    # Statistiques
    stats = {
        'total': tickets.count(),
        'ouverts': tickets.filter(statut='OUVERT').count(),
        'en_cours': tickets.filter(statut='EN_COURS').count(),
        'resolus': tickets.filter(statut='RESOLU').count(),
    }
    
    context = {
        'tickets': tickets,
        'stats': stats,
        'page_title': 'Mes Tickets',
    }
    
    return render(request, 'core/mes_tickets.html', context)


@login_required
def tickets_projet_view(request, projet_id=None):
    """Vue : Tickets d'un projet (si membre ou responsable)"""
    user = request.user
    
    # Récupérer les projets accessibles
    if user.est_super_admin():
        projets_accessibles = Projet.objects.all()
    else:
        # Projets où l'utilisateur a une affectation active (membre ou responsable)
        projets_accessibles = Projet.objects.filter(
            affectations__utilisateur=user,
            affectations__date_fin__isnull=True  # Affectations actives uniquement
        ).distinct()
    
    # Si un projet spécifique est demandé
    if projet_id:
        projet = get_object_or_404(Projet, id=projet_id)
        
        # Vérifier l'accès
        if not user.est_super_admin() and projet not in projets_accessibles:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('tickets_projet')
        
        # Récupérer les tickets du projet
        tickets = TicketMaintenance.objects.filter(
            projet=projet
        ).select_related('projet', 'cree_par').prefetch_related('assignes_a').order_by('-date_creation')
        
        # Filtres
        statut_filtre = request.GET.get('statut')
        priorite_filtre = request.GET.get('priorite')
        
        if statut_filtre:
            tickets = tickets.filter(statut=statut_filtre)
        if priorite_filtre:
            tickets = tickets.filter(priorite=priorite_filtre)
        
        # Statistiques
        stats = {
            'total': tickets.count(),
            'ouverts': tickets.filter(statut='OUVERT').count(),
            'en_cours': tickets.filter(statut='EN_COURS').count(),
            'resolus': tickets.filter(statut='RESOLU').count(),
        }
        
        context = {
            'tickets': tickets,
            'stats': stats,
            'projet': projet,
            'projets_accessibles': projets_accessibles,
            'page_title': f'Tickets - {projet.nom}',
        }
        
        return render(request, 'core/tickets_projet.html', context)
    
    # Sinon, afficher la liste des projets
    context = {
        'projets': projets_accessibles,
        'page_title': 'Tickets par Projet',
    }
    
    return render(request, 'core/tickets_projet.html', context)


@login_required
def tous_tickets_view(request):
    """Vue : Tous les tickets (Admin uniquement)"""
    user = request.user
    
    # SÉCURITÉ : Vérifier que l'utilisateur est Admin
    if not user.est_super_admin():
        messages.error(request, 'Accès refusé. Cette page est réservée aux administrateurs.')
        return redirect('mes_tickets')
    
    # Récupérer tous les tickets
    tickets = TicketMaintenance.objects.all().select_related(
        'projet', 'cree_par'
    ).prefetch_related('assignes_a').order_by('-date_creation')
    
    # Filtres
    statut_filtre = request.GET.get('statut')
    priorite_filtre = request.GET.get('priorite')
    projet_filtre = request.GET.get('projet')
    
    if statut_filtre:
        tickets = tickets.filter(statut=statut_filtre)
    if priorite_filtre:
        tickets = tickets.filter(priorite=priorite_filtre)
    if projet_filtre:
        tickets = tickets.filter(projet_id=projet_filtre)
    
    # Statistiques globales
    stats = {
        'total': tickets.count(),
        'ouverts': tickets.filter(statut='OUVERT').count(),
        'en_cours': tickets.filter(statut='EN_COURS').count(),
        'resolus': tickets.filter(statut='RESOLU').count(),
        'critiques': tickets.filter(priorite='CRITIQUE').count(),
    }
    
    # Liste des projets pour le filtre
    projets = Projet.objects.all().order_by('nom')
    
    context = {
        'tickets': tickets,
        'stats': stats,
        'projets': projets,
        'page_title': 'Tous les Tickets',
    }
    
    return render(request, 'core/tous_tickets.html', context)
