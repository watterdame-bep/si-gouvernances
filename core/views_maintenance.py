"""
Vues pour la gestion de la MAINTENANCE
Conformes aux pratiques d'entreprise
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
    BilletIntervention, InterventionMaintenance, StatutTechnique
)


# ============================================================================
# GESTION DES CONTRATS DE GARANTIE
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
# GESTION DES TICKETS DE MAINTENANCE
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
    
    # Récupérer tous les tickets
    tickets = projet.tickets_maintenance.all().select_related(
        'contrat_garantie', 'cree_par', 'assigne_a'
    ).order_by('-date_creation')
    
    # Filtres
    statut_filtre = request.GET.get('statut')
    gravite_filtre = request.GET.get('gravite')
    
    if statut_filtre:
        tickets = tickets.filter(statut=statut_filtre)
    if gravite_filtre:
        tickets = tickets.filter(gravite=gravite_filtre)
    
    # Statistiques
    stats = {
        'total': tickets.count(),
        'ouverts': tickets.filter(statut='OUVERT').count(),
        'en_cours': tickets.filter(statut='EN_COURS').count(),
        'resolus': tickets.filter(statut='RESOLU').count(),
        'fermes': tickets.filter(statut='FERME').count(),
        'rejetes': tickets.filter(statut='REJETE').count(),
        'critiques': tickets.filter(gravite='CRITIQUE').count(),
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
    """Créer un nouveau ticket de maintenance"""
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
        context = {
            'projet': projet,
            'contrats_actifs': contrats_actifs,
        }
        return render(request, 'core/creer_ticket.html', context)
    
    # POST: Créer le ticket
    try:
        titre = request.POST.get('titre', '').strip()
        description_probleme = request.POST.get('description_probleme', '').strip()
        gravite = request.POST.get('gravite')
        origine = request.POST.get('origine')
        contrat_id = request.POST.get('contrat_garantie')
        
        # Validation
        if not all([titre, description_probleme, gravite, origine]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('creer_ticket', projet_id=projet.id)
        
        # Récupérer le contrat si spécifié
        contrat = None
        if contrat_id:
            contrat = get_object_or_404(ContratGarantie, id=contrat_id, projet=projet)
            # Vérifier que le contrat est actif
            if not contrat.est_actif:
                messages.error(request, 'Le contrat sélectionné n\'est plus actif.')
                return redirect('creer_ticket', projet_id=projet.id)
        
        # Créer le ticket
        ticket = TicketMaintenance.objects.create(
            projet=projet,
            contrat_garantie=contrat,
            titre=titre,
            description_probleme=description_probleme,
            gravite=gravite,
            origine=origine,
            cree_par=user
        )
        
        # Message selon le statut
        if ticket.est_payant:
            messages.warning(
                request,
                f'Ticket {ticket.numero_ticket} créé. ⚠️ INTERVENTION PAYANTE : {ticket.raison_rejet or "Pas de contrat de garantie actif"}'
            )
        else:
            messages.success(request, f'Ticket {ticket.numero_ticket} créé avec succès sous garantie.')
        
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
        
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('creer_ticket', projet_id=projet.id)


@login_required
def detail_ticket_view(request, projet_id, ticket_id):
    """Vue détaillée d'un ticket de maintenance"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        role_projet = user.get_role_sur_projet(projet)
        if not role_projet and not user.a_acces_projet(projet):
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les billets et interventions
    billets = ticket.billets_intervention.all().select_related(
        'developpeur_autorise', 'autorise_par'
    ).prefetch_related('interventions')
    
    # Permissions
    role_projet = user.get_role_sur_projet(projet)
    peut_emettre_billet = user.est_super_admin() or (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL')
    peut_intervenir = user.role_systeme and user.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']
    
    # Équipe pour assignation
    equipe = projet.get_equipe()
    developpeurs = [m for m in equipe if m.role_systeme and m.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']]
    
    context = {
        'projet': projet,
        'ticket': ticket,
        'billets': billets,
        'peut_emettre_billet': peut_emettre_billet,
        'peut_intervenir': peut_intervenir,
        'developpeurs': developpeurs,
    }
    
    return render(request, 'core/detail_ticket.html', context)


# ============================================================================
# GESTION DES BILLETS D'INTERVENTION
# ============================================================================

@login_required
def emettre_billet_view(request, projet_id, ticket_id):
    """Émettre un billet d'intervention"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    
    # Vérifier les permissions
    role_projet = user.get_role_sur_projet(projet)
    if not user.est_super_admin() and not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
        messages.error(request, 'Permissions insuffisantes.')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
    
    # Vérifier que le ticket peut être traité
    if not ticket.peut_etre_traite:
        messages.error(request, 'Ce ticket ne peut pas être traité (rejeté ou payant non accepté).')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        equipe = projet.get_equipe()
        developpeurs = [m for m in equipe if m.role_systeme and m.role_systeme.nom in ['DEVELOPPEUR', 'CHEF_PROJET']]
        
        context = {
            'projet': projet,
            'ticket': ticket,
            'developpeurs': developpeurs,
        }
        return render(request, 'core/emettre_billet.html', context)
    
    # POST: Créer le billet
    try:
        developpeur_id = request.POST.get('developpeur_autorise')
        type_intervention = request.POST.get('type_intervention')
        duree_estimee = request.POST.get('duree_estimee')
        instructions = request.POST.get('instructions', '').strip()
        
        # Validation
        if not all([developpeur_id, type_intervention, duree_estimee]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('emettre_billet', projet_id=projet.id, ticket_id=ticket.id)
        
        developpeur = get_object_or_404(Utilisateur, id=developpeur_id)
        
        # Créer le billet
        billet = BilletIntervention(
            ticket=ticket,
            developpeur_autorise=developpeur,
            type_intervention=type_intervention,
            duree_estimee=float(duree_estimee),
            autorise_par=user,
            instructions=instructions
        )
        
        # Valider
        billet.full_clean()
        billet.save()
        
        # Mettre à jour le ticket
        if ticket.statut == 'OUVERT':
            ticket.statut = 'EN_COURS'
            ticket.assigne_a = developpeur
            ticket.save()
        
        messages.success(request, f'Billet {billet.numero_billet} émis avec succès pour {developpeur.get_full_name()}.')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
        
    except ValidationError as e:
        messages.error(request, f'Erreur de validation : {e.message}')
        return redirect('emettre_billet', projet_id=projet.id, ticket_id=ticket.id)
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('emettre_billet', projet_id=projet.id, ticket_id=ticket.id)


# ============================================================================
# GESTION DES INTERVENTIONS
# ============================================================================

@login_required
def enregistrer_intervention_view(request, projet_id, ticket_id, billet_id):
    """Enregistrer une intervention technique"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    billet = get_object_or_404(BilletIntervention, id=billet_id, ticket=ticket)
    
    # Vérifier que l'utilisateur est le développeur autorisé
    if not user.est_super_admin() and user != billet.developpeur_autorise:
        messages.error(request, 'Vous n\'êtes pas autorisé à intervenir sur ce billet.')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        context = {
            'projet': projet,
            'ticket': ticket,
            'billet': billet,
        }
        return render(request, 'core/enregistrer_intervention.html', context)
    
    # POST: Créer l'intervention
    try:
        description_actions = request.POST.get('description_actions', '').strip()
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        temps_passe = request.POST.get('temps_passe')
        correctif_applique = request.POST.get('correctif_applique', '').strip()
        fichiers_modifies = request.POST.get('fichiers_modifies', '').strip()
        
        # Validation
        if not all([description_actions, date_debut, temps_passe]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('enregistrer_intervention', projet_id=projet.id, ticket_id=ticket.id, billet_id=billet.id)
        
        # Créer l'intervention
        intervention = InterventionMaintenance(
            billet=billet,
            description_actions=description_actions,
            date_debut=date_debut,
            date_fin=date_fin if date_fin else None,
            temps_passe=float(temps_passe),
            correctif_applique=correctif_applique,
            fichiers_modifies=fichiers_modifies
        )
        
        # Valider
        intervention.full_clean()
        intervention.save()
        
        messages.success(request, 'Intervention enregistrée avec succès. Vous devez maintenant rédiger le statut technique.')
        return redirect('rediger_statut_technique', projet_id=projet.id, ticket_id=ticket.id, intervention_id=intervention.id)
        
    except ValidationError as e:
        messages.error(request, f'Erreur de validation : {e.message}')
        return redirect('enregistrer_intervention', projet_id=projet.id, ticket_id=ticket.id, billet_id=billet.id)
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('enregistrer_intervention', projet_id=projet.id, ticket_id=ticket.id, billet_id=billet.id)


# ============================================================================
# GESTION DU STATUT TECHNIQUE
# ============================================================================

@login_required
def rediger_statut_technique_view(request, projet_id, ticket_id, intervention_id):
    """Rédiger le statut technique (rapport final)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    intervention = get_object_or_404(InterventionMaintenance, id=intervention_id, billet__ticket=ticket)
    
    # Vérifier que l'utilisateur peut rédiger
    if not user.est_super_admin():
        if user != intervention.billet.developpeur_autorise:
            role_projet = user.get_role_sur_projet(projet)
            if not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
                messages.error(request, 'Vous n\'êtes pas autorisé à rédiger ce statut technique.')
                return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
    
    # Vérifier si un statut existe déjà
    try:
        statut_existant = intervention.statut_technique
        messages.info(request, 'Un statut technique existe déjà pour cette intervention.')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
    except StatutTechnique.DoesNotExist:
        pass
    
    # GET: Afficher le formulaire
    if request.method == 'GET':
        context = {
            'projet': projet,
            'ticket': ticket,
            'intervention': intervention,
        }
        return render(request, 'core/rediger_statut_technique.html', context)
    
    # POST: Créer le statut technique
    try:
        probleme_initial = request.POST.get('probleme_initial', '').strip()
        cause_reelle = request.POST.get('cause_reelle', '').strip()
        solution_apportee = request.POST.get('solution_apportee', '').strip()
        impact_systeme = request.POST.get('impact_systeme', '').strip()
        risques_futurs = request.POST.get('risques_futurs', '').strip()
        recommandations = request.POST.get('recommandations', '').strip()
        
        # Validation
        if not all([probleme_initial, cause_reelle, solution_apportee, impact_systeme]):
            messages.error(request, 'Tous les champs obligatoires doivent être remplis.')
            return redirect('rediger_statut_technique', projet_id=projet.id, ticket_id=ticket.id, intervention_id=intervention.id)
        
        # Créer le statut technique
        statut = StatutTechnique.objects.create(
            intervention=intervention,
            probleme_initial=probleme_initial,
            cause_reelle=cause_reelle,
            solution_apportee=solution_apportee,
            impact_systeme=impact_systeme,
            risques_futurs=risques_futurs,
            recommandations=recommandations,
            redige_par=user
        )
        
        messages.success(request, 'Statut technique rédigé avec succès. En attente de validation.')
        return redirect('detail_ticket', projet_id=projet.id, ticket_id=ticket.id)
        
    except Exception as e:
        messages.error(request, f'Erreur : {str(e)}')
        return redirect('rediger_statut_technique', projet_id=projet.id, ticket_id=ticket.id, intervention_id=intervention.id)


@login_required
@require_http_methods(["POST"])
def valider_statut_technique_view(request, projet_id, ticket_id, statut_id):
    """Valider un statut technique (Chef de projet ou Admin)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    ticket = get_object_or_404(TicketMaintenance, id=ticket_id, projet=projet)
    statut = get_object_or_404(StatutTechnique, id=statut_id, intervention__billet__ticket=ticket)
    
    # Vérifier les permissions
    role_projet = user.get_role_sur_projet(projet)
    if not user.est_super_admin() and not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        # Valider le statut technique
        statut.valider(user)
        # → Ticket automatiquement marqué RESOLU
        
        return JsonResponse({
            'success': True,
            'message': f'Statut technique validé. Ticket {ticket.numero_ticket} marqué comme résolu.'
        })
        
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
    role_projet = user.get_role_sur_projet(projet)
    if not user.est_super_admin() and not (role_projet and role_projet.nom == 'RESPONSABLE_PRINCIPAL'):
        return JsonResponse({'success': False, 'error': 'Permissions insuffisantes'})
    
    try:
        ticket.fermer()
        
        return JsonResponse({
            'success': True,
            'message': f'Ticket {ticket.numero_ticket} fermé avec succès.'
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
