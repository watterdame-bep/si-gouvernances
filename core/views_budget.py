# -*- coding: utf-8 -*-
"""
Vues pour la gestion budgétaire des projets
Permet d'ajouter, consulter et supprimer des lignes budgétaires
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from decimal import Decimal
import json

from .models import Projet, Utilisateur
from .models_budget import LigneBudget, ResumeBudget
from .utils import enregistrer_audit


def peut_gerer_budget(user, projet):
    """
    Vérifie si l'utilisateur peut gérer le budget du projet
    Seuls les admins et le chef de projet (responsable) peuvent gérer le budget
    """
    if user.is_superuser:
        return True
    
    # Vérifier si l'utilisateur est le responsable principal du projet
    affectation = projet.affectations.filter(
        utilisateur=user,
        est_responsable_principal=True,
        date_fin__isnull=True
    ).first()
    
    return affectation is not None


@login_required
@require_http_methods(["POST"])
def ajouter_lignes_budget(request, projet_id):
    """
    Ajoute une ou plusieurs lignes budgétaires au projet
    Accepte un tableau de lignes en JSON
    """
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not peut_gerer_budget(request.user, projet):
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas la permission de gérer le budget de ce projet.'
        }, status=403)
    
    try:
        # Parser les données JSON
        data = json.loads(request.body)
        lignes_data = data.get('lignes', [])
        
        if not lignes_data:
            return JsonResponse({
                'success': False,
                'error': 'Aucune ligne budgétaire fournie.'
            })
        
        lignes_creees = []
        
        with transaction.atomic():
            for ligne_data in lignes_data:
                type_ligne = ligne_data.get('type')
                montant = ligne_data.get('montant')
                description = ligne_data.get('description', '').strip()
                
                # Validation
                if not type_ligne or type_ligne not in ['MATERIEL', 'SERVICE']:
                    return JsonResponse({
                        'success': False,
                        'error': f'Type invalide: {type_ligne}'
                    })
                
                try:
                    montant = Decimal(str(montant))
                    if montant <= 0:
                        return JsonResponse({
                            'success': False,
                            'error': 'Le montant doit être supérieur à 0.'
                        })
                except (ValueError, TypeError, Decimal.InvalidOperation):
                    return JsonResponse({
                        'success': False,
                        'error': f'Montant invalide: {montant}'
                    })
                
                # Créer la ligne
                ligne = LigneBudget.objects.create(
                    projet=projet,
                    type_ligne=type_ligne,
                    montant=montant,
                    description=description,
                    ajoute_par=request.user
                )
                
                lignes_creees.append({
                    'id': str(ligne.id),
                    'type': ligne.get_type_ligne_display(),
                    'montant': float(ligne.montant),
                    'description': ligne.description,
                    'date_ajout': ligne.date_ajout.strftime('%d/%m/%Y %H:%M')
                })
            
            # Enregistrer l'audit
            enregistrer_audit(
                utilisateur=request.user,
                type_action='AJOUT_LIGNES_BUDGET',
                description=f'Ajout de {len(lignes_creees)} ligne(s) budgétaire(s) au projet {projet.nom}',
                projet=projet,
                request=request,
                donnees_apres={
                    'nombre_lignes': len(lignes_creees),
                    'total_ajoute': sum(l['montant'] for l in lignes_creees)
                }
            )
        
        # Calculer le nouveau résumé
        resume = ResumeBudget(projet)
        
        # Vérifier si le budget est dépassé et notifier l'administrateur
        if resume.budget_disponible < 0:
            from .models import AlerteProjet
            
            # Récupérer tous les super admins
            admins = Utilisateur.objects.filter(is_superuser=True, is_active=True)
            
            for admin in admins:
                # Vérifier si une alerte similaire n'existe pas déjà (non lue)
                alerte_existante = AlerteProjet.objects.filter(
                    destinataire=admin,
                    projet=projet,
                    type_alerte='BUDGET_DEPASSE',
                    lue=False
                ).exists()
                
                if not alerte_existante:
                    AlerteProjet.objects.create(
                        destinataire=admin,
                        projet=projet,
                        type_alerte='BUDGET_DEPASSE',
                        titre=f'⚠️ Budget dépassé - {projet.nom}',
                        message=f'Le budget du projet "{projet.nom}" a été dépassé. '
                                f'Budget total: ${resume.budget_total:,.2f} | '
                                f'Dépenses: ${resume.total_depenses:,.2f} | '
                                f'Dépassement: ${abs(resume.budget_disponible):,.2f}',
                        niveau='URGENT'
                    )
        
        return JsonResponse({
            'success': True,
            'message': f'{len(lignes_creees)} ligne(s) budgétaire(s) ajoutée(s) avec succès.',
            'lignes': lignes_creees,
            'resume': resume.to_dict()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Données JSON invalides.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de l\'ajout: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def liste_lignes_budget(request, projet_id):
    """
    Retourne la liste complète des lignes budgétaires du projet
    """
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur a accès au projet
    if not (request.user.is_superuser or 
            projet.affectations.filter(utilisateur=request.user, date_fin__isnull=True).exists()):
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas accès à ce projet.'
        }, status=403)
    
    lignes = projet.lignes_budget.all().select_related('ajoute_par')
    
    lignes_data = []
    for ligne in lignes:
        lignes_data.append({
            'id': str(ligne.id),
            'type': ligne.type_ligne,
            'type_display': ligne.get_type_ligne_display(),
            'montant': float(ligne.montant),
            'montant_formate': ligne.get_montant_formate(),
            'description': ligne.description,
            'description_courte': ligne.get_description_courte(),
            'date_ajout': ligne.date_ajout.strftime('%d/%m/%Y %H:%M'),
            'ajoute_par': ligne.ajoute_par.get_full_name(),
            'peut_supprimer': peut_gerer_budget(request.user, projet)
        })
    
    # Calculer le résumé
    resume = ResumeBudget(projet)
    
    return JsonResponse({
        'success': True,
        'lignes': lignes_data,
        'resume': resume.to_dict(),
        'peut_gerer': peut_gerer_budget(request.user, projet)
    })


@login_required
@require_http_methods(["POST"])
def supprimer_ligne_budget(request, ligne_id):
    """
    Supprime une ligne budgétaire
    """
    ligne = get_object_or_404(LigneBudget, id=ligne_id)
    projet = ligne.projet
    
    # Vérifier les permissions
    if not peut_gerer_budget(request.user, projet):
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas la permission de supprimer cette ligne.'
        }, status=403)
    
    try:
        # Sauvegarder les infos pour l'audit
        ligne_info = {
            'type': ligne.get_type_ligne_display(),
            'montant': float(ligne.montant),
            'description': ligne.description
        }
        
        # Supprimer
        ligne.delete()
        
        # Enregistrer l'audit
        enregistrer_audit(
            utilisateur=request.user,
            type_action='SUPPRESSION_LIGNE_BUDGET',
            description=f'Suppression d\'une ligne budgétaire du projet {projet.nom}',
            projet=projet,
            request=request,
            donnees_avant=ligne_info
        )
        
        # Calculer le nouveau résumé
        resume = ResumeBudget(projet)
        
        return JsonResponse({
            'success': True,
            'message': 'Ligne budgétaire supprimée avec succès.',
            'resume': resume.to_dict()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la suppression: {str(e)}'
        })


@login_required
@require_http_methods(["GET"])
def resume_budget(request, projet_id):
    """
    Retourne le résumé budgétaire du projet
    """
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur a accès au projet
    if not (request.user.is_superuser or 
            projet.affectations.filter(utilisateur=request.user, date_fin__isnull=True).exists()):
        return JsonResponse({
            'success': False,
            'error': 'Vous n\'avez pas accès à ce projet.'
        }, status=403)
    
    resume = ResumeBudget(projet)
    
    return JsonResponse({
        'success': True,
        'resume': resume.to_dict(),
        'peut_gerer': peut_gerer_budget(request.user, projet)
    })
