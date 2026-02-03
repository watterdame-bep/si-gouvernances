from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Utilisateur, Projet, Affectation, ActionAudit, RoleSysteme, RoleProjet, StatutProjet, Membre, TypeEtape, EtapeProjet, ModuleProjet, TacheModule, TacheEtape
from .utils import enregistrer_audit, envoyer_notification_changement_mot_de_passe
import json

def login_view(request):
    """Vue de connexion avec audit automatique"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            try:
                # Récupérer l'utilisateur par email
                utilisateur = Utilisateur.objects.get(email=email)
                
                # Vérifier si le compte est bloqué
                if utilisateur.est_compte_bloque():
                    messages.error(request, 'Compte temporairement bloqué. Réessayez plus tard.')
                    enregistrer_audit(
                        utilisateur=utilisateur,
                        type_action='TENTATIVE_CONNEXION_ECHOUEE',
                        description=f'Tentative de connexion sur compte bloqué',
                        request=request
                    )
                    return render(request, 'core/login.html')
                
                # Authentifier l'utilisateur
                user = authenticate(request, username=utilisateur.username, password=password)
                
                if user is not None and user.statut_actif:
                    # Connexion réussie
                    login(request, user)
                    user.reinitialiser_tentatives()
                    user.derniere_connexion = timezone.now()
                    user.save()
                    
                    # Audit de connexion
                    enregistrer_audit(
                        utilisateur=user,
                        type_action='CONNEXION',
                        description=f'Connexion réussie',
                        request=request
                    )
                    
                    messages.success(request, f'Bienvenue {user.get_full_name()} !')
                    return redirect('dashboard')
                else:
                    # Échec de connexion
                    utilisateur.tentatives_connexion_echouees += 1
                    
                    if utilisateur.tentatives_connexion_echouees >= 5:
                        utilisateur.bloquer_compte()
                        messages.error(request, 'Trop de tentatives échouées. Compte bloqué temporairement.')
                    else:
                        messages.error(request, 'Email ou mot de passe incorrect.')
                    
                    utilisateur.save()
                    
                    # Audit de tentative échouée
                    enregistrer_audit(
                        utilisateur=utilisateur,
                        type_action='TENTATIVE_CONNEXION_ECHOUEE',
                        description=f'Tentative {utilisateur.tentatives_connexion_echouees}/5',
                        request=request
                    )
                    
            except Utilisateur.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')
    
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    """Vue de déconnexion avec audit"""
    # Audit de déconnexion
    enregistrer_audit(
        utilisateur=request.user,
        type_action='DECONNEXION',
        description='Déconnexion utilisateur',
        request=request
    )
    
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def dashboard_view(request):
    """Tableau de bord principal pour tous les utilisateurs avec contrôles d'accès"""
    user = request.user
    
    # Context de base pour tous les utilisateurs
    context = {
        'user': user,
        'is_super_admin': user.est_super_admin(),
    }
    
    if user.est_super_admin():
        # Données pour Super Admin
        context.update({
            'projets': Projet.objects.all()[:10],
            'total_projets': Projet.objects.count(),
            'projets_actifs': Projet.objects.exclude(statut__nom__in=['TERMINE', 'ARCHIVE']).count(),
            'utilisateurs_actifs': Utilisateur.objects.filter(statut_actif=True).count(),
            'total_utilisateurs': Utilisateur.objects.count(),
            'super_admins': Utilisateur.objects.filter(is_superuser=True).count(),
        })
    else:
        # Données pour utilisateur normal
        mes_projets = Projet.objects.filter(
            affectations__utilisateur=user, 
            affectations__date_fin__isnull=True
        ).distinct()
        
        context.update({
            'mes_projets': mes_projets,
            'projets_en_cours': mes_projets.filter(statut__nom='EN_COURS').count(),
            'mes_roles': user.get_roles_par_projet(),
        })
    
    return render(request, 'core/dashboard.html', context)



@login_required
def projets_list_view(request):
    """Liste des projets selon les permissions"""
    user = request.user
    
    # Filtrage selon les permissions
    if user.est_super_admin():
        projets = Projet.objects.all()
    else:
        # Utilisateur normal voit ses projets affectés
        projets = Projet.objects.filter(affectations__utilisateur=user, affectations__date_fin__isnull=True).distinct()
    
    # Recherche
    search = request.GET.get('search', '')
    if search:
        projets = projets.filter(
            Q(nom__icontains=search) |
            Q(client__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Filtrage par statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        projets = projets.filter(statut__nom=statut_filter)
    
    # Pagination
    paginator = Paginator(projets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Utiliser le même template pour tous, avec conditions dans le template
    template_name = 'core/projets_list.html'
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'statut_filter': statut_filter,
        'statuts': StatutProjet.objects.all(),
        'can_create': user.est_super_admin(),
        'is_super_admin': user.est_super_admin(),
    }
    
    return render(request, template_name, context)

@login_required
def projet_detail_view(request, projet_id):
    """Détail d'un projet avec permissions"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer l'équipe (avec gestion des erreurs pour les références invalides)
    try:
        affectations = projet.affectations.filter(date_fin__isnull=True).select_related('utilisateur', 'role_projet', 'role_sur_projet')
    except Exception as e:
        # En cas d'erreur (références invalides), récupérer sans select_related
        affectations = projet.affectations.filter(date_fin__isnull=True)
        # Filtrer les affectations avec des utilisateurs valides
        valid_affectations = []
        for aff in affectations:
            try:
                # Tester l'accès à l'utilisateur
                _ = aff.utilisateur
                valid_affectations.append(aff)
            except:
                # Supprimer l'affectation invalide
                aff.delete()
        affectations = valid_affectations
    
    # Déterminer les permissions d'édition (Admin + Chef de projet système uniquement)
    can_edit = user.est_super_admin()
    if not can_edit:
        # Vérifier si l'utilisateur a le rôle système "CHEF_PROJET"
        can_edit = user.role_systeme and user.role_systeme.nom == 'CHEF_PROJET'
    
    # Permissions pour voir les paramètres (Admin + Chef de projet système + Responsable principal)
    can_manage = can_edit
    if not can_manage:
        # Vérifier si l'utilisateur est responsable principal du projet
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    # Récupérer le rôle de l'utilisateur sur ce projet
    user_role_on_project = None
    user_affectation = None
    if not user.est_super_admin():
        user_affectation = projet.affectations.filter(
            utilisateur=user,
            date_fin__isnull=True
        ).first()
        if user_affectation:
            user_role_on_project = user_affectation.role_sur_projet
    
    # Utiliser le même template pour tous, avec conditions dans le template
    template_name = 'core/projet_detail.html'
    
    context = {
        'projet': projet,
        'affectations': affectations,
        'responsable': projet.get_responsable_principal(),
        'can_edit': can_edit,
        'can_manage': can_manage,
        'user_role_on_project': user_role_on_project,
        'user_affectation': user_affectation,
        'is_super_admin': user.est_super_admin(),
        'historique_audit': ActionAudit.objects.filter(projet=projet)[:10] if user.est_super_admin() else None,
    }
    
    return render(request, template_name, context)

@login_required
def audit_view(request):
    """Consultation du journal d'audit (Super Admins uniquement)"""
    user = request.user
    
    if not user.est_super_admin():
        messages.error(request, 'Accès non autorisé. Seuls les Super Admins peuvent consulter l\'audit.')
        enregistrer_audit(
            utilisateur=user,
            type_action='ACCES_REFUSE',
            description='Tentative d\'accès non autorisé à l\'audit',
            request=request
        )
        return redirect('dashboard')
    
    # Enregistrer la consultation d'audit
    enregistrer_audit(
        utilisateur=user,
        type_action='CONSULTATION_AUDIT',
        description='Consultation du journal d\'audit',
        request=request
    )
    
    # Récupérer les actions d'audit
    actions = ActionAudit.objects.all().select_related('utilisateur', 'projet').order_by('-timestamp')
    
    # Filtres
    utilisateur_filter = request.GET.get('user', '')
    if utilisateur_filter:
        actions = actions.filter(utilisateur_id=utilisateur_filter)
    
    type_action_filter = request.GET.get('action_type', '')
    if type_action_filter:
        actions = actions.filter(type_action=type_action_filter)
    
    date_debut = request.GET.get('date_from', '')
    date_fin = request.GET.get('date_to', '')
    if date_debut:
        try:
            actions = actions.filter(timestamp__date__gte=date_debut)
        except:
            pass
    if date_fin:
        try:
            actions = actions.filter(timestamp__date__lte=date_fin)
        except:
            pass
    
    search = request.GET.get('search', '')
    if search:
        actions = actions.filter(
            Q(description__icontains=search) |
            Q(utilisateur__first_name__icontains=search) |
            Q(utilisateur__last_name__icontains=search) |
            Q(utilisateur__email__icontains=search)
        )
    
    # Statistiques pour le dashboard
    today = timezone.now().date()
    stats = {
        'connexions_today': ActionAudit.objects.filter(
            type_action='CONNEXION',
            timestamp__date=today
        ).count(),
        'failed_attempts': ActionAudit.objects.filter(
            type_action='TENTATIVE_CONNEXION_ECHOUEE',
            timestamp__date=today
        ).count(),
        'blocked_actions': ActionAudit.objects.filter(
            type_action='ACCES_REFUSE',
            timestamp__date=today
        ).count(),
    }
    
    # Pagination
    paginator = Paginator(actions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Liste des utilisateurs pour le filtre
    users = Utilisateur.objects.filter(statut_actif=True).order_by('first_name', 'last_name')
    
    # Alertes de sécurité récentes
    security_alerts = []
    recent_failed_attempts = ActionAudit.objects.filter(
        type_action='TENTATIVE_CONNEXION_ECHOUEE',
        timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
    ).count()
    
    if recent_failed_attempts > 10:
        security_alerts.append({
            'severity': 'warning',
            'title': 'Tentatives de connexion suspectes',
            'description': f'{recent_failed_attempts} tentatives échouées dans les dernières 24h',
            'timestamp': timezone.now()
        })
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'stats': stats,
        'security_alerts': security_alerts,
        'types_actions': ActionAudit.TYPE_ACTIONS,
    }
    
    return render(request, 'core/audit_new.html', context)
    
    return render(request, 'core/audit.html', context)

@login_required
@require_http_methods(["POST"])
def modifier_budget_projet(request, projet_id):
    """Modification du budget avec validation hiérarchique"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        # Vérifier si l'utilisateur est responsable principal du projet
        if not projet.affectations.filter(utilisateur=user, est_responsable_principal=True, date_fin__isnull=True).exists():
            return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        nouveau_budget = float(request.POST.get('budget', 0))
        ancien_budget = float(projet.budget_previsionnel)
        
        if nouveau_budget <= 0:
            return JsonResponse({'success': False, 'error': 'Le budget doit être supérieur à 0'})
        
        # Calculer l'écart
        ecart_pourcent = abs(nouveau_budget - ancien_budget) / ancien_budget * 100
        
        # Si écart > 20% et utilisateur n'est pas Super Admin, demander validation
        if ecart_pourcent > 20 and not user.est_super_admin():
            # TODO: Implémenter le système de validation hiérarchique
            return JsonResponse({
                'success': False, 
                'error': f'Modification de {ecart_pourcent:.1f}% nécessite une validation Super Admin'
            })
        
        # Enregistrer l'audit avant modification
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_BUDGET',
            description=f'Budget modifié: {ancien_budget}€ → {nouveau_budget}€',
            projet=projet,
            donnees_avant={'budget': ancien_budget},
            donnees_apres={'budget': nouveau_budget},
            request=request
        )
        
        # Appliquer la modification
        projet.budget_previsionnel = nouveau_budget
        projet.save()
        
        messages.success(request, f'Budget modifié avec succès: {nouveau_budget}€')
        return JsonResponse({'success': True})
        
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Budget invalide'})

# Vue pour tester la robustesse du système
@login_required
def test_robustesse_view(request):
    """Vue de test pour vérifier la robustesse du noyau central"""
    if not request.user.est_super_admin():
        messages.error(request, 'Accès réservé aux Super Admins.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        test_type = request.POST.get('test_type')
        
        if test_type == 'coherence_donnees':
            # Test de cohérence des données
            resultats = []
            
            # Vérifier les projets sans responsable
            projets_sans_responsable = Projet.objects.exclude(
                affectations__est_responsable_principal=True,
                affectations__date_fin__isnull=True
            )
            resultats.append(f"Projets sans responsable: {projets_sans_responsable.count()}")
            
            # Vérifier les utilisateurs inactifs avec affectations
            utilisateurs_inactifs_affectes = Utilisateur.objects.filter(
                statut_actif=False,
                affectations__date_fin__isnull=True
            ).distinct()
            resultats.append(f"Utilisateurs inactifs avec affectations: {utilisateurs_inactifs_affectes.count()}")
            
            messages.info(request, ' | '.join(resultats))
        
        elif test_type == 'audit_integrite':
            # Vérifier l'intégrité de l'audit
            total_actions = ActionAudit.objects.count()
            actions_sans_hash = ActionAudit.objects.filter(hash_integrite='').count()
            
            messages.info(request, f"Actions d'audit: {total_actions} | Sans hash: {actions_sans_hash}")
    
    return render(request, 'core/test_robustesse.html')

from .utils import enregistrer_audit, require_super_admin, generer_mot_de_passe_temporaire, generer_username
from django.contrib.auth.hashers import make_password
from decimal import Decimal

@require_super_admin
def creer_projet_view(request):
    """Vue de création d'un nouveau projet (Super Admins uniquement) - Interface simplifiée"""
    
    if request.method == 'POST':
        # Récupérer les données essentielles uniquement
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        client = request.POST.get('client', '').strip()
        statut_nom = request.POST.get('statut')
        priorite = request.POST.get('priorite', 'MOYENNE')
        
        # Validation minimale
        errors = []
        
        if not nom:
            errors.append('Le nom du projet est obligatoire.')
        elif Projet.objects.filter(nom=nom).exists():
            errors.append('Ce nom de projet existe déjà.')
            
        if not description:
            errors.append('La description du projet est obligatoire.')
            
        # Vérifier que le statut existe
        try:
            statut = StatutProjet.objects.get(nom=statut_nom) if statut_nom else None
            if not statut:
                errors.append('Veuillez sélectionner un statut pour le projet.')
        except StatutProjet.DoesNotExist:
            errors.append('Le statut sélectionné n\'existe pas.')
            
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Créer le projet avec valeurs par défaut
                projet = Projet.objects.create(
                    nom=nom,
                    description=description,
                    client=client if client else 'À définir',  # Valeur par défaut si vide
                    budget_previsionnel=Decimal('0'),  # Budget par défaut à 0
                    devise='EUR',
                    statut=statut,
                    priorite=priorite,
                    createur=request.user
                )
                
                # Initialiser automatiquement les étapes standard
                projet.initialiser_etapes_standard(request.user)
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='CREATION_PROJET',
                    description=f'Création du projet {projet.nom}',
                    projet=projet,
                    request=request,
                    donnees_apres={
                        'nom': nom,
                        'client': client if client else 'À définir',
                        'statut': statut.nom,
                        'priorite': priorite,
                        'etapes_initialisees': True
                    }
                )
                
                messages.success(request, f'Projet "{projet.nom}" créé avec succès !')
                
                # Stocker temporairement les informations du projet pour l'affichage
                request.session['nouveau_projet'] = {
                    'id': str(projet.id),
                    'nom': projet.nom,
                    'client': projet.client,
                    'statut': projet.statut.get_nom_display(),
                    'priorite': projet.get_priorite_display(),
                    'description': projet.description,
                    'date_creation': projet.date_creation.strftime('%d/%m/%Y %H:%M')
                }
                
                return redirect('projet_cree_success')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Récupérer les données pour le formulaire (seulement Idée et Planifié)
    context = {
        'statuts': StatutProjet.objects.filter(nom__in=['IDEE', 'PLANIFIE']).order_by('ordre_affichage'),
        'priorites': Projet._meta.get_field('priorite').choices,
    }
    
    return render(request, 'core/creer_projet.html', context)

@require_super_admin
def projet_cree_success_view(request):
    """Page de confirmation après création de projet avec informations complètes"""
    
    # Récupérer les informations du nouveau projet depuis la session
    nouveau_projet = request.session.get('nouveau_projet')
    
    if not nouveau_projet:
        messages.error(request, 'Aucune information de projet trouvée.')
        return redirect('projets_list')
    
    # Nettoyer la session après récupération
    del request.session['nouveau_projet']
    
    context = {
        'projet_info': nouveau_projet,
        'date_creation': timezone.now()
    }
    
    return render(request, 'core/projet_cree_success.html', context)

@require_super_admin
def gestion_utilisateurs_view(request):
    """Vue de gestion des utilisateurs (Super Admins uniquement)"""
    
    # Nettoyer la notification de la session après affichage
    if 'nouveau_utilisateur' in request.session:
        del request.session['nouveau_utilisateur']
    
    # Récupérer tous les utilisateurs
    utilisateurs = Utilisateur.objects.all().order_by('first_name', 'last_name')
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    if statut_filter == 'actif':
        utilisateurs = utilisateurs.filter(statut_actif=True)
    elif statut_filter == 'inactif':
        utilisateurs = utilisateurs.filter(statut_actif=False)
    elif statut_filter == 'super_admin':
        utilisateurs = utilisateurs.filter(is_superuser=True)
    
    search = request.GET.get('search', '')
    if search:
        utilisateurs = utilisateurs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(utilisateurs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    stats = {
        'total': Utilisateur.objects.count(),
        'actifs': Utilisateur.objects.filter(statut_actif=True).count(),
        'inactifs': Utilisateur.objects.filter(statut_actif=False).count(),
        'super_admins': Utilisateur.objects.filter(is_superuser=True).count(),
        'bloques': Utilisateur.objects.filter(compte_bloque_jusqu__gt=timezone.now()).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'statut_filter': statut_filter,
        'search': search,
    }
    
    return render(request, 'core/gestion_utilisateurs.html', context)

@require_super_admin
def creer_utilisateur_moderne_view(request):
    """Vue moderne de création d'un nouvel utilisateur (sans affectations)"""
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telephone = request.POST.get('telephone', '').strip()
        role_systeme_nom = request.POST.get('role_systeme')
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append('Le prénom est obligatoire.')
        if not last_name:
            errors.append('Le nom est obligatoire.')
        if not email:
            errors.append('L\'email est obligatoire.')
        elif Utilisateur.objects.filter(email=email).exists():
            errors.append('Cet email est déjà utilisé.')
        
        if not role_systeme_nom:
            errors.append('Le rôle système est obligatoire.')
        
        try:
            role_systeme = RoleSysteme.objects.get(nom=role_systeme_nom)
        except RoleSysteme.DoesNotExist:
            errors.append('Le rôle système sélectionné n\'existe pas.')
            role_systeme = None
        
        try:
            taux_horaire = Decimal('0')  # Valeur par défaut
        except:
            errors.append('Erreur lors de l\'initialisation du taux horaire.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Générer username et mot de passe
                username = generer_username(first_name, last_name)
                mot_de_passe_temporaire = generer_mot_de_passe_temporaire()
                
                # Créer l'utilisateur
                utilisateur = Utilisateur.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    telephone=telephone,
                    taux_horaire=taux_horaire,
                    role_systeme=role_systeme,
                    password=make_password(mot_de_passe_temporaire),
                    statut_actif=True
                )
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='CREATION_UTILISATEUR',
                    description=f'Création de l\'utilisateur {utilisateur.get_full_name()} ({utilisateur.email})',
                    request=request,
                    donnees_apres={
                        'username': username,
                        'email': email,
                        'role_systeme': role_systeme.nom if role_systeme else None
                    }
                )
                
                messages.success(request, f'Utilisateur créé avec succès !')
                
                # Stocker temporairement le mot de passe pour l'affichage
                request.session['nouveau_utilisateur'] = {
                    'id': str(utilisateur.id),
                    'nom_complet': utilisateur.get_full_name(),
                    'username': username,
                    'email': email,
                    'telephone': telephone,
                    'mot_de_passe': mot_de_passe_temporaire
                }
                
                return redirect('utilisateur_cree_success')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {}
    
    return render(request, 'core/creer_utilisateur_moderne.html', context)

@require_super_admin
def utilisateur_cree_success_view(request):
    """Page de confirmation après création d'utilisateur avec informations complètes"""
    
    # Récupérer les informations du nouvel utilisateur depuis la session
    nouveau_utilisateur = request.session.get('nouveau_utilisateur')
    
    if not nouveau_utilisateur:
        messages.error(request, 'Aucune information d\'utilisateur trouvée.')
        return redirect('gestion_utilisateurs')
    
    # Générer les initiales pour l'affichage
    nom_complet = nouveau_utilisateur.get('nom_complet', '')
    mots = nom_complet.split()
    initiales = ''.join([mot[0].upper() for mot in mots[:2]]) if mots else 'U'
    
    # Construire l'URL de connexion complète
    url_connexion = request.build_absolute_uri('/login/')
    
    # Nettoyer la session après récupération
    del request.session['nouveau_utilisateur']
    
    context = {
        'utilisateur_info': nouveau_utilisateur,
        'initiales': initiales,
        'url_connexion': url_connexion,
        'date_creation': timezone.now()
    }
    
    return render(request, 'core/utilisateur_cree_success.html', context)

@require_super_admin
def modifier_utilisateur_view(request, user_id):
    """Vue de modification d'un utilisateur"""
    
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        # Sauvegarder l'état avant modification
        donnees_avant = {
            'first_name': utilisateur.first_name,
            'last_name': utilisateur.last_name,
            'telephone': utilisateur.telephone,
            'taux_horaire': str(utilisateur.taux_horaire),
            'statut_actif': utilisateur.statut_actif,
            'is_superuser': utilisateur.is_superuser
        }
        
        # Récupérer les nouvelles données
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        taux_horaire = request.POST.get('taux_horaire', '0')
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append('Le prénom est obligatoire.')
        if not last_name:
            errors.append('Le nom est obligatoire.')
        
        try:
            taux_horaire = Decimal(taux_horaire) if taux_horaire else Decimal('0')
            if taux_horaire < 0:
                errors.append('Le taux horaire ne peut pas être négatif.')
        except:
            errors.append('Le taux horaire doit être un nombre valide.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Mettre à jour l'utilisateur
                utilisateur.first_name = first_name
                utilisateur.last_name = last_name
                utilisateur.telephone = telephone
                utilisateur.taux_horaire = taux_horaire
                utilisateur.is_superuser = is_superuser
                utilisateur.is_staff = is_superuser  # Staff si super admin
                utilisateur.save()
                
                # Données après modification
                donnees_apres = {
                    'first_name': utilisateur.first_name,
                    'last_name': utilisateur.last_name,
                    'telephone': utilisateur.telephone,
                    'taux_horaire': str(utilisateur.taux_horaire),
                    'statut_actif': utilisateur.statut_actif,
                    'is_superuser': utilisateur.is_superuser
                }
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='MODIFICATION_UTILISATEUR',
                    description=f'Modification de l\'utilisateur {utilisateur.get_full_name()}',
                    request=request,
                    donnees_avant=donnees_avant,
                    donnees_apres=donnees_apres
                )
                
                messages.success(request, f'Utilisateur modifié avec succès !')
                return redirect('gestion_utilisateurs')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'utilisateur': utilisateur,
    }
    
    return render(request, 'core/modifier_utilisateur.html', context)

@require_super_admin
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Active/désactive un utilisateur"""
    
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    # Ne pas permettre de se désactiver soi-même
    if utilisateur == request.user:
        return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas modifier votre propre statut.'})
    
    ancien_statut = utilisateur.statut_actif
    utilisateur.statut_actif = not ancien_statut
    utilisateur.save()
    
    # Audit
    action = 'REACTIVATION_UTILISATEUR' if utilisateur.statut_actif else 'DESACTIVATION_UTILISATEUR'
    description = f'{"Réactivation" if utilisateur.statut_actif else "Désactivation"} de l\'utilisateur {utilisateur.get_full_name()}'
    
    enregistrer_audit(
        utilisateur=request.user,
        type_action=action,
        description=description,
        request=request,
        donnees_avant={'statut_actif': ancien_statut},
        donnees_apres={'statut_actif': utilisateur.statut_actif}
    )
    
    messages.success(request, f'Utilisateur {"réactivé" if utilisateur.statut_actif else "désactivé"} avec succès.')
    
    return JsonResponse({
        'success': True,
        'nouveau_statut': utilisateur.statut_actif,
        'message': f'Utilisateur {"réactivé" if utilisateur.statut_actif else "désactivé"} avec succès.'
    })

@require_super_admin
@require_http_methods(["POST"])
def reset_user_password(request, user_id):
    """Réinitialise le mot de passe d'un utilisateur"""
    
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    # Générer un nouveau mot de passe temporaire
    nouveau_mot_de_passe = generer_mot_de_passe_temporaire()
    utilisateur.password = make_password(nouveau_mot_de_passe)
    
    # Débloquer le compte et réinitialiser les tentatives
    utilisateur.reinitialiser_tentatives()
    utilisateur.save()
    
    # Audit
    enregistrer_audit(
        utilisateur=request.user,
        type_action='REINITIALISATION_MOT_PASSE',
        description=f'Réinitialisation du mot de passe pour {utilisateur.get_full_name()}',
        request=request
    )
    
    messages.success(request, 'Mot de passe réinitialisé avec succès !')
    
    return JsonResponse({
        'success': True,
        'nouveau_mot_de_passe': nouveau_mot_de_passe,
        'message': 'Mot de passe réinitialisé avec succès !'
    })

@require_super_admin
@require_http_methods(["GET"])
def audit_log_detail(request, log_id):
    """Récupère les détails complets d'un log d'audit"""
    
    try:
        log = get_object_or_404(ActionAudit, id=log_id)
        
        # Préparer les données pour le JSON
        data = {
            'id': str(log.id),
            'timestamp': log.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            'utilisateur': {
                'nom_complet': log.utilisateur.get_full_name(),
                'username': log.utilisateur.username,
                'email': log.utilisateur.email,
                'role': 'Super Admin' if log.utilisateur.is_superuser else 'Utilisateur',
            },
            'type_action': {
                'code': log.type_action,
                'nom': log.get_type_action_display(),
            },
            'description': log.description,
            'adresse_ip': log.adresse_ip,
            'user_agent': log.user_agent,
            'hash_integrite': log.hash_integrite,
            'projet': None,
            'donnees_avant': log.donnees_avant,
            'donnees_apres': log.donnees_apres,
        }
        
        # Ajouter les informations du projet si disponible
        if log.projet:
            data['projet'] = {
                'nom': log.projet.nom,
                'client': log.projet.client,
                'statut': log.projet.statut.get_nom_display(),
                'budget': f"{log.projet.budget_previsionnel:,.2f} €",
            }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def parametres_projet_view(request, projet_id):
    """Vue principale des paramètres de projet - Gestion d'équipe V1"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions (Admin + Chef de projet uniquement)
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        # Vérifier si l'utilisateur est responsable principal (chef de projet)
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage and not user.a_acces_projet(projet):
        messages.error(request, 'Vous n\'avez pas accès aux paramètres de ce projet.')
        return redirect('projet_detail', projet_id=projet.id)
    
    # Récupérer l'équipe actuelle
    affectations = projet.affectations.filter(date_fin__isnull=True).select_related('utilisateur', 'role_projet', 'role_sur_projet').order_by('-est_responsable_principal', 'utilisateur__first_name')
    
    # Récupérer les utilisateurs disponibles (actifs, pas déjà dans l'équipe, et pas administrateurs)
    utilisateurs_dans_equipe = [aff.utilisateur.id for aff in affectations]
    utilisateurs_disponibles = Utilisateur.objects.filter(
        statut_actif=True,
        is_superuser=False  # Exclure les administrateurs
    ).exclude(id__in=utilisateurs_dans_equipe).order_by('first_name', 'last_name')
    
    # Récupérer tous les rôles projet disponibles
    roles_disponibles = RoleProjet.objects.all()
    
    context = {
        'projet': projet,
        'affectations': affectations,
        'utilisateurs_disponibles': utilisateurs_disponibles,
        'roles_disponibles': roles_disponibles,
        'can_manage': can_manage,
        'responsable': projet.get_responsable_principal(),
        'is_creator': projet.createur == user,
    }
    
    return render(request, 'core/parametres_projet.html', context)

@login_required
@require_http_methods(["POST"])
def ajouter_membre_projet(request, projet_id):
    """Ajouter un membre à l'équipe du projet"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        utilisateur_id = request.POST.get('utilisateur_id')
        
        # Validation - Plus besoin de rôle
        if not utilisateur_id:
            return JsonResponse({'success': False, 'error': 'Utilisateur requis'})
        
        utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id, statut_actif=True)
        
        # Empêcher l'ajout d'administrateurs dans les équipes
        if utilisateur.est_super_admin():
            return JsonResponse({'success': False, 'error': 'Les administrateurs ne peuvent pas être membres d\'une équipe'})
        
        # Vérifier que l'utilisateur n'est pas déjà dans l'équipe
        if projet.affectations.filter(utilisateur=utilisateur, date_fin__isnull=True).exists():
            return JsonResponse({'success': False, 'error': 'Cet utilisateur fait déjà partie de l\'équipe'})
        
        # Obtenir le rôle par défaut "MEMBRE" ou créer une affectation sans rôle spécifique
        role_par_defaut = None
        try:
            role_par_defaut = RoleProjet.objects.filter(nom='MEMBRE').first()
        except:
            pass
        
        # Créer l'affectation comme membre normal (sans responsabilité)
        affectation = Affectation(
            utilisateur=utilisateur,
            projet=projet,
            role_projet=role_par_defaut,  # Peut être None si pas de rôle MEMBRE
            est_responsable_principal=False  # Toujours False lors de l'ajout
        )
        
        # Valider avant de sauvegarder
        try:
            affectation.full_clean()
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
        # Sauvegarder
        affectation.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='AFFECTATION_UTILISATEUR',
            description=f'Ajout de {utilisateur.get_full_name()} au projet {projet.nom} comme membre normal',
            projet=projet,
            request=request,
            donnees_apres={
                'utilisateur': utilisateur.get_full_name(),
                'role': role_par_defaut.nom if role_par_defaut else 'Membre',
                'est_responsable': False
            }
        )
        
        messages.success(request, f'{utilisateur.get_full_name()} ajouté à l\'équipe comme membre normal !')
        return JsonResponse({'success': True, 'message': 'Membre ajouté avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def retirer_membre_projet(request, projet_id):
    """Retirer un membre de l'équipe du projet"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        affectation_id = request.POST.get('affectation_id')
        
        if not affectation_id:
            return JsonResponse({'success': False, 'error': 'Affectation requise'})
        
        affectation = get_object_or_404(Affectation, id=affectation_id, projet=projet, date_fin__isnull=True)
        
        # Ne pas permettre de retirer le créateur du projet
        if affectation.utilisateur == projet.createur:
            return JsonResponse({'success': False, 'error': 'Le créateur du projet ne peut pas être retiré'})
        
        # Ne pas permettre de se retirer soi-même si on est le seul responsable
        if affectation.utilisateur == user and affectation.est_responsable_principal:
            autres_responsables = projet.affectations.filter(
                est_responsable_principal=True,
                date_fin__isnull=True
            ).exclude(id=affectation.id).exists()
            
            if not autres_responsables and not user.est_super_admin():
                return JsonResponse({'success': False, 'error': 'Vous ne pouvez pas vous retirer en tant que seul responsable'})
        
        # Terminer l'affectation
        utilisateur_nom = affectation.utilisateur.get_full_name()
        role_nom = (affectation.role_projet.get_nom_display() if affectation.role_projet 
                   else affectation.role_sur_projet.get_nom_display() if affectation.role_sur_projet 
                   else "Aucun rôle")
        etait_responsable = affectation.est_responsable_principal
        
        affectation.terminer_affectation()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='RETRAIT_UTILISATEUR',
            description=f'Retrait de {utilisateur_nom} du projet {projet.nom}' + (' (était responsable principal)' if etait_responsable else ''),
            projet=projet,
            request=request,
            donnees_avant={
                'utilisateur': utilisateur_nom,
                'role': role_nom,
                'est_responsable': etait_responsable
            }
        )
        
        messages.success(request, f'{utilisateur_nom} retiré de l\'équipe avec succès !')
        return JsonResponse({'success': True, 'message': 'Membre retiré avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def modifier_role_membre(request, projet_id):
    """Modifier le rôle d'un membre de l'équipe"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        affectation_id = request.POST.get('affectation_id')
        nouveau_role_id = request.POST.get('role_id')
        
        if not affectation_id or not nouveau_role_id:
            return JsonResponse({'success': False, 'error': 'Affectation et rôle requis'})
        
        affectation = get_object_or_404(Affectation, id=affectation_id, projet=projet, date_fin__isnull=True)
        nouveau_role = get_object_or_404(RoleProjet, id=nouveau_role_id)
        
        # Sauvegarder l'ancien rôle pour l'audit
        ancien_role = affectation.role_projet or affectation.role_sur_projet
        
        if ancien_role.id == nouveau_role.id:
            return JsonResponse({'success': False, 'error': 'Le rôle est déjà celui-ci'})
        
        # Mettre à jour le rôle
        affectation.role_projet = nouveau_role
        affectation.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_ROLE',
            description=f'Changement de rôle pour {affectation.utilisateur.get_full_name()} sur le projet {projet.nom}: {ancien_role.get_nom_display()} → {nouveau_role.get_nom_display()}',
            projet=projet,
            request=request,
            donnees_avant={'role': ancien_role.nom},
            donnees_apres={'role': nouveau_role.nom}
        )
        
        messages.success(request, f'Rôle modifié avec succès pour {affectation.utilisateur.get_full_name()} !')
        return JsonResponse({'success': True, 'message': 'Rôle modifié avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def definir_responsable(request, projet_id):
    """Définir un membre comme responsable principal"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions 
    can_change_responsable = user.est_super_admin() or projet.createur == user
    
    # Permettre aussi au responsable principal actuel de transférer sa responsabilité
    if not can_change_responsable:
        responsable_actuel = projet.affectations.filter(
            utilisateur=user,
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_change_responsable = responsable_actuel is not None
    
    if not can_change_responsable:
        return JsonResponse({'success': False, 'error': 'Vous n\'avez pas les permissions pour changer le responsable principal'})
    
    try:
        # Gérer les deux types de formulaires
        affectation_id = request.POST.get('affectation_id')  # Formulaire définir responsable
        nouveau_responsable_id = request.POST.get('nouveau_responsable_id')  # Formulaire transfert
        
        if nouveau_responsable_id:
            # Mode transfert : nouveau_responsable_id contient l'ID de l'affectation du nouveau responsable
            nouvelle_affectation = get_object_or_404(Affectation, id=nouveau_responsable_id, projet=projet, date_fin__isnull=True)
        elif affectation_id:
            # Mode définir : affectation_id contient l'ID de l'affectation à promouvoir
            nouvelle_affectation = get_object_or_404(Affectation, id=affectation_id, projet=projet, date_fin__isnull=True)
        else:
            return JsonResponse({'success': False, 'error': 'Affectation requise'})
        
        if nouvelle_affectation.est_responsable_principal:
            return JsonResponse({'success': False, 'error': 'Cet utilisateur est déjà responsable principal'})
        
        # Retirer le statut de responsable principal à l'ancien responsable
        ancien_responsable = None
        ancienne_affectation = projet.affectations.filter(
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        
        if ancienne_affectation:
            ancien_responsable = ancienne_affectation.utilisateur.get_full_name()
            ancienne_affectation.est_responsable_principal = False
            ancienne_affectation.save()
        
        # Définir le nouveau responsable principal
        nouvelle_affectation.est_responsable_principal = True
        nouvelle_affectation.save()
        
        nouveau_responsable = nouvelle_affectation.utilisateur.get_full_name()
        
        # Audit
        if ancien_responsable:
            description = f'Transfert de responsabilité sur le projet {projet.nom}: {ancien_responsable} → {nouveau_responsable}'
            message_success = f'Responsabilité transférée de {ancien_responsable} à {nouveau_responsable} !'
        else:
            description = f'Définition du responsable principal sur le projet {projet.nom}: {nouveau_responsable}'
            message_success = f'{nouveau_responsable} est maintenant responsable principal !'
        
        enregistrer_audit(
            utilisateur=user,
            type_action='CHANGEMENT_RESPONSABLE',
            description=description,
            projet=projet,
            request=request,
            donnees_avant={'ancien_responsable': ancien_responsable},
            donnees_apres={'nouveau_responsable': nouveau_responsable}
        )
        
        messages.success(request, message_success)
        return JsonResponse({'success': True, 'message': message_success, 'transfert': ancien_responsable is not None})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_super_admin
def modifier_projet_view(request, projet_id):
    """Vue de modification d'un projet (Super Admins uniquement)"""
    
    projet = get_object_or_404(Projet, id=projet_id)
    
    if request.method == 'POST':
        # Sauvegarder l'état avant modification
        donnees_avant = {
            'nom': projet.nom,
            'description': projet.description,
            'client': projet.client,
            'budget_previsionnel': str(projet.budget_previsionnel),
            'statut': projet.statut.nom,
            'priorite': projet.priorite
        }
        
        # Récupérer les nouvelles données
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        client = request.POST.get('client', '').strip()
        budget_previsionnel = request.POST.get('budget_previsionnel', '0')
        statut_nom = request.POST.get('statut')
        priorite = request.POST.get('priorite', 'MOYENNE')
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom du projet est obligatoire.')
        elif nom != projet.nom and Projet.objects.filter(nom=nom).exists():
            errors.append('Ce nom de projet existe déjà.')
            
        if not description:
            errors.append('La description du projet est obligatoire.')
        
        # Validation du budget
        try:
            budget_previsionnel = Decimal(budget_previsionnel) if budget_previsionnel else Decimal('0')
            if budget_previsionnel < 0:
                errors.append('Le budget ne peut pas être négatif.')
        except:
            errors.append('Le budget doit être un nombre valide.')
        
        # Vérifier que le statut existe
        try:
            statut = StatutProjet.objects.get(nom=statut_nom) if statut_nom else None
            if not statut:
                errors.append('Veuillez sélectionner un statut pour le projet.')
        except StatutProjet.DoesNotExist:
            errors.append('Le statut sélectionné n\'existe pas.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Mettre à jour le projet
                projet.nom = nom
                projet.description = description
                projet.client = client if client else 'À définir'
                projet.budget_previsionnel = budget_previsionnel
                projet.statut = statut
                projet.priorite = priorite
                projet.save()
                
                # Données après modification
                donnees_apres = {
                    'nom': projet.nom,
                    'description': projet.description,
                    'client': projet.client,
                    'budget_previsionnel': str(projet.budget_previsionnel),
                    'statut': projet.statut.nom,
                    'priorite': projet.priorite
                }
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='MODIFICATION_PROJET',
                    description=f'Modification du projet {projet.nom}',
                    projet=projet,
                    request=request,
                    donnees_avant=donnees_avant,
                    donnees_apres=donnees_apres
                )
                
                messages.success(request, f'Projet "{projet.nom}" modifié avec succès !')
                return redirect('projet_detail', projet_id=projet.id)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    # Récupérer les données pour le formulaire
    context = {
        'projet': projet,
        'statuts': StatutProjet.objects.all().order_by('ordre_affichage'),
        'priorites': Projet._meta.get_field('priorite').choices,
    }
    
    return render(request, 'core/modifier_projet.html', context)

@login_required
@require_http_methods(["POST"])
def transferer_responsabilite_projet(request, projet_id):
    """Transférer la responsabilité principale d'un projet à un autre membre"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions (seul le créateur peut transférer la responsabilité)
    if not user.est_super_admin() and projet.createur != user:
        return JsonResponse({'success': False, 'error': 'Seul le créateur du projet peut transférer la responsabilité principale'})
    
    try:
        ancien_responsable_id = request.POST.get('ancien_responsable_id')
        nouveau_responsable_id = request.POST.get('nouveau_responsable_id')
        
        if not ancien_responsable_id or not nouveau_responsable_id:
            return JsonResponse({'success': False, 'error': 'Ancien et nouveau responsable requis'})
        
        # Récupérer les affectations
        ancienne_affectation = get_object_or_404(Affectation, id=ancien_responsable_id, projet=projet, date_fin__isnull=True)
        nouvelle_affectation = get_object_or_404(Affectation, id=nouveau_responsable_id, projet=projet, date_fin__isnull=True)
        
        # Vérifier que l'ancien est bien responsable
        if not ancienne_affectation.est_responsable_principal:
            return JsonResponse({'success': False, 'error': 'L\'utilisateur sélectionné n\'est pas responsable principal'})
        
        # Vérifier que le nouveau n'est pas déjà responsable
        if nouvelle_affectation.est_responsable_principal:
            return JsonResponse({'success': False, 'error': 'L\'utilisateur sélectionné est déjà responsable principal'})
        
        # Effectuer le transfert
        ancien_nom = ancienne_affectation.utilisateur.get_full_name()
        nouveau_nom = nouvelle_affectation.utilisateur.get_full_name()
        
        # Retirer la responsabilité à l'ancien
        ancienne_affectation.est_responsable_principal = False
        ancienne_affectation.save()
        
        # Donner la responsabilité au nouveau
        nouvelle_affectation.est_responsable_principal = True
        nouvelle_affectation.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='CHANGEMENT_RESPONSABLE',
            description=f'Transfert de responsabilité sur le projet {projet.nom}: {ancien_nom} → {nouveau_nom}',
            projet=projet,
            request=request,
            donnees_avant={'responsable': ancien_nom},
            donnees_apres={'responsable': nouveau_nom}
        )
        
        messages.success(request, f'Responsabilité transférée avec succès de {ancien_nom} à {nouveau_nom} !')
        return JsonResponse({'success': True, 'message': f'Responsabilité transférée à {nouveau_nom} avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
@login_required
@require_http_methods(["POST"])
def transferer_responsabilite_automatique(request, projet_id):
    """Transférer automatiquement la responsabilité lors de la définition d'un nouveau responsable"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions (seul le créateur peut transférer la responsabilité)
    if not user.est_super_admin() and projet.createur != user:
        return JsonResponse({'success': False, 'error': 'Seul le créateur du projet peut transférer la responsabilité principale'})
    
    try:
        nouveau_responsable_id = request.POST.get('nouveau_responsable_id')
        
        if not nouveau_responsable_id:
            return JsonResponse({'success': False, 'error': 'Nouveau responsable requis'})
        
        # Récupérer l'affectation du nouveau responsable
        nouvelle_affectation = get_object_or_404(Affectation, id=nouveau_responsable_id, projet=projet, date_fin__isnull=True)
        
        # Trouver l'ancien responsable
        ancienne_affectation = projet.affectations.filter(
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        
        if not ancienne_affectation:
            return JsonResponse({'success': False, 'error': 'Aucun responsable principal trouvé'})
        
        # Vérifier que le nouveau n'est pas déjà responsable
        if nouvelle_affectation.est_responsable_principal:
            return JsonResponse({'success': False, 'error': 'L\'utilisateur sélectionné est déjà responsable principal'})
        
        # Effectuer le transfert automatique
        ancien_nom = ancienne_affectation.utilisateur.get_full_name()
        nouveau_nom = nouvelle_affectation.utilisateur.get_full_name()
        
        # Retirer la responsabilité à l'ancien
        ancienne_affectation.est_responsable_principal = False
        ancienne_affectation.save()
        
        # Donner la responsabilité au nouveau
        nouvelle_affectation.est_responsable_principal = True
        nouvelle_affectation.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='CHANGEMENT_RESPONSABLE',
            description=f'Transfert automatique de responsabilité sur le projet {projet.nom}: {ancien_nom} → {nouveau_nom}',
            projet=projet,
            request=request,
            donnees_avant={'responsable': ancien_nom},
            donnees_apres={'responsable': nouveau_nom}
        )
        
        messages.success(request, f'Responsabilité transférée automatiquement de {ancien_nom} à {nouveau_nom} !')
        return JsonResponse({'success': True, 'message': f'Responsabilité transférée à {nouveau_nom} avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ============================================================================
# NOUVELLES VUES - GESTION SÉPARÉE MEMBRES (RH) ET COMPTES UTILISATEUR
# ============================================================================

# ===== GESTION DES MEMBRES (PROFILS RH) =====

@require_super_admin
def gestion_membres_view(request):
    """Vue de gestion des membres (profils RH)"""
    
    # Filtres
    search = request.GET.get('search', '').strip()
    statut_filter = request.GET.get('statut', '')
    
    # Base queryset
    membres = Membre.objects.all()
    
    # Appliquer les filtres
    if search:
        membres = membres.filter(
            Q(nom__icontains=search) |
            Q(prenom__icontains=search) |
            Q(email_personnel__icontains=search) |
            Q(poste__icontains=search) |
            Q(departement__icontains=search)
        )
    
    if statut_filter:
        membres = membres.filter(statut=statut_filter)
    
    # Statistiques
    stats = {
        'total': Membre.objects.count(),
        'actifs': Membre.objects.filter(statut='ACTIF').count(),
        'inactifs': Membre.objects.filter(statut='INACTIF').count(),
        'avec_compte': Membre.objects.filter(compte_utilisateur__isnull=False).count(),
        'sans_compte': Membre.objects.filter(compte_utilisateur__isnull=True).count(),
    }
    
    # Pagination
    paginator = Paginator(membres.order_by('nom', 'prenom'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'statut_filter': statut_filter,
        'stats': stats,
        'statut_choices': Membre.STATUT_CHOICES,
    }
    
    return render(request, 'core/gestion_membres.html', context)

@require_super_admin
def creer_membre_view(request):
    """Vue de création d'un nouveau membre (profil RH)"""
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email_personnel = request.POST.get('email_personnel', '').strip().lower()
        telephone = request.POST.get('telephone', '').strip()
        telephone_urgence = request.POST.get('telephone_urgence', '').strip()
        
        # Adresse (simplifiée et obligatoire)
        adresse = request.POST.get('adresse', '').strip()
        
        # Informations professionnelles
        poste = request.POST.get('poste', '').strip()
        departement = request.POST.get('departement', '').strip()
        niveau_experience = request.POST.get('niveau_experience', '')
        
        # Compétences
        competences_techniques = request.POST.get('competences_techniques', '').strip()
        specialites = request.POST.get('specialites', '').strip()
        
        # Autres
        date_embauche = request.POST.get('date_embauche', '')
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom est obligatoire.')
        if not prenom:
            errors.append('Le prénom est obligatoire.')
        if not email_personnel:
            errors.append('L\'email personnel est obligatoire.')
        elif Membre.objects.filter(email_personnel=email_personnel).exists():
            errors.append('Cet email est déjà utilisé.')
        if not adresse:
            errors.append('L\'adresse est obligatoire.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Créer le membre
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
                    date_embauche=date_embauche if date_embauche else None,
                    createur=request.user
                )
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='CREATION_MEMBRE',
                    description=f'Création du profil membre {membre.get_nom_complet()} ({membre.email_personnel})',
                    request=request,
                    donnees_apres={
                        'nom': nom,
                        'prenom': prenom,
                        'email_personnel': email_personnel,
                        'poste': poste,
                        'departement': departement
                    }
                )
                
                messages.success(request, f'Profil membre créé avec succès !')
                
                # Stocker temporairement les informations pour l'affichage
                request.session['nouveau_membre'] = {
                    'id': str(membre.id),
                    'nom_complet': membre.get_nom_complet(),
                    'email_personnel': email_personnel,
                    'poste': poste,
                    'departement': departement
                }
                
                return redirect('membre_cree_success')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'niveau_experience_choices': Membre.NIVEAU_EXPERIENCE_CHOICES,
    }
    
    return render(request, 'core/creer_membre.html', context)

@require_super_admin
def membre_cree_success_view(request):
    """Page de confirmation après création d'un membre"""
    
    # Récupérer les informations du nouveau membre depuis la session
    nouveau_membre = request.session.get('nouveau_membre')
    
    if not nouveau_membre:
        messages.error(request, 'Aucune information de membre trouvée.')
        return redirect('gestion_membres')
    
    # Générer les initiales pour l'affichage
    nom_complet = nouveau_membre.get('nom_complet', '')
    mots = nom_complet.split()
    initiales = ''.join([mot[0].upper() for mot in mots[:2]]) if mots else 'M'
    
    # Nettoyer la session après récupération
    del request.session['nouveau_membre']
    
    context = {
        'membre_info': nouveau_membre,
        'initiales': initiales,
        'date_creation': timezone.now(),
    }
    
    return render(request, 'core/membre_cree_success.html', context)

@require_super_admin
def detail_membre_view(request, membre_id):
    """Vue de détail d'un membre"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    context = {
        'membre': membre,
    }
    
    return render(request, 'core/detail_membre.html', context)

@require_super_admin
def modifier_membre_view(request, membre_id):
    """Vue de modification d'un membre"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email_personnel = request.POST.get('email_personnel', '').strip().lower()
        telephone = request.POST.get('telephone', '').strip()
        telephone_urgence = request.POST.get('telephone_urgence', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        poste = request.POST.get('poste', '').strip()
        departement = request.POST.get('departement', '').strip()
        niveau_experience = request.POST.get('niveau_experience', '')
        date_embauche = request.POST.get('date_embauche', '')
        statut = request.POST.get('statut', 'ACTIF')
        competences_techniques = request.POST.get('competences_techniques', '').strip()
        specialites = request.POST.get('specialites', '').strip()
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom est obligatoire.')
        if not prenom:
            errors.append('Le prénom est obligatoire.')
        if not email_personnel:
            errors.append('L\'email personnel est obligatoire.')
        elif Membre.objects.filter(email_personnel=email_personnel).exclude(pk=membre.pk).exists():
            errors.append('Cet email est déjà utilisé par un autre membre.')
        if not adresse:
            errors.append('L\'adresse est obligatoire.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Sauvegarder les anciennes valeurs pour l'audit
                anciennes_donnees = {
                    'nom': membre.nom,
                    'prenom': membre.prenom,
                    'email_personnel': membre.email_personnel,
                    'telephone': membre.telephone,
                    'adresse': membre.adresse,
                    'poste': membre.poste,
                    'statut': membre.statut
                }
                
                # Mettre à jour le membre
                membre.nom = nom
                membre.prenom = prenom
                membre.email_personnel = email_personnel
                membre.telephone = telephone
                membre.telephone_urgence = telephone_urgence
                membre.adresse = adresse
                membre.poste = poste
                membre.departement = departement
                membre.niveau_experience = niveau_experience
                membre.date_embauche = date_embauche if date_embauche else None
                membre.statut = statut
                membre.competences_techniques = competences_techniques
                membre.specialites = specialites
                membre.save()
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='MODIFICATION_MEMBRE',
                    description=f'Modification du membre {membre.get_nom_complet()}',
                    request=request,
                    donnees_avant=anciennes_donnees,
                    donnees_apres={
                        'nom': nom,
                        'prenom': prenom,
                        'email_personnel': email_personnel,
                        'telephone': telephone,
                        'adresse': adresse,
                        'poste': poste,
                        'statut': statut
                    }
                )
                
                messages.success(request, f'Membre modifié avec succès !')
                return redirect('detail_membre', membre_id=membre.id)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'membre': membre,
        'niveau_experience_choices': Membre.NIVEAU_EXPERIENCE_CHOICES,
        'statut_choices': Membre.STATUT_CHOICES,
    }
    
    return render(request, 'core/modifier_membre.html', context)

# ===== GESTION DES COMPTES UTILISATEUR (ACCÈS SYSTÈME) =====

@require_super_admin
def gestion_comptes_view(request):
    """Vue de gestion des comptes utilisateur (accès système)"""
    
    # Filtres
    search = request.GET.get('search', '').strip()
    statut_filter = request.GET.get('statut', '')
    role_filter = request.GET.get('role', '')
    
    # Base queryset avec les membres associés
    comptes = Utilisateur.objects.select_related('membre', 'role_systeme').all()
    
    # Appliquer les filtres
    if search:
        comptes = comptes.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(membre__nom__icontains=search) |
            Q(membre__prenom__icontains=search)
        )
    
    if statut_filter == 'actif':
        comptes = comptes.filter(statut_actif=True)
    elif statut_filter == 'inactif':
        comptes = comptes.filter(statut_actif=False)
    elif statut_filter == 'super_admin':
        comptes = comptes.filter(is_superuser=True)
    
    if role_filter:
        comptes = comptes.filter(role_systeme__nom=role_filter)
    
    # Statistiques
    stats = {
        'total': Utilisateur.objects.count(),
        'actifs': Utilisateur.objects.filter(statut_actif=True).count(),
        'inactifs': Utilisateur.objects.filter(statut_actif=False).count(),
        'super_admins': Utilisateur.objects.filter(is_superuser=True).count(),
        'avec_membre': Utilisateur.objects.filter(membre__isnull=False).count(),
    }
    
    # Pagination
    paginator = Paginator(comptes.order_by('-date_creation'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'statut_filter': statut_filter,
        'role_filter': role_filter,
        'stats': stats,
        'roles_systeme': RoleSysteme.objects.all(),
    }
    
    return render(request, 'core/gestion_comptes.html', context)

@require_super_admin
def creer_compte_utilisateur_view(request, membre_id):
    """Vue de création d'un compte utilisateur pour un membre existant"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    # Vérifier que le membre n'a pas déjà un compte
    if membre.a_compte_utilisateur():
        messages.error(request, 'Ce membre a déjà un compte utilisateur.')
        return redirect('detail_membre', membre_id=membre.id)
    
    # Vérifier que le membre peut avoir un compte
    if not membre.peut_avoir_compte():
        messages.error(request, 'Ce membre ne peut pas avoir de compte utilisateur (statut ou email manquant).')
        return redirect('detail_membre', membre_id=membre.id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username', '').strip()
        role_systeme_nom = request.POST.get('role_systeme')
        mot_de_passe_personnalise = request.POST.get('mot_de_passe_personnalise', '').strip()
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Le nom d\'utilisateur est obligatoire.')
        elif Utilisateur.objects.filter(username=username).exists():
            errors.append('Ce nom d\'utilisateur est déjà utilisé.')
        
        if not role_systeme_nom:
            errors.append('Le rôle système est obligatoire.')
        
        try:
            role_systeme = RoleSysteme.objects.get(nom=role_systeme_nom)
        except RoleSysteme.DoesNotExist:
            errors.append('Le rôle système sélectionné n\'existe pas.')
            role_systeme = None
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Générer ou utiliser le mot de passe
                if mot_de_passe_personnalise:
                    mot_de_passe_temporaire = mot_de_passe_personnalise
                else:
                    mot_de_passe_temporaire = generer_mot_de_passe_temporaire()
                
                # Créer le compte utilisateur
                utilisateur = Utilisateur.objects.create(
                    username=username,
                    email=membre.email_personnel,
                    first_name=membre.prenom,
                    last_name=membre.nom,
                    membre=membre,
                    role_systeme=role_systeme,
                    password=make_password(mot_de_passe_temporaire),
                    statut_actif=True
                )
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='CREATION_COMPTE_UTILISATEUR',
                    description=f'Création du compte utilisateur {username} pour le membre {membre.get_nom_complet()}',
                    request=request,
                    donnees_apres={
                        'username': username,
                        'membre_id': str(membre.id),
                        'role_systeme': role_systeme.nom if role_systeme else None
                    }
                )
                
                messages.success(request, f'Compte utilisateur créé avec succès !')
                
                # Stocker temporairement le mot de passe pour l'affichage
                request.session['nouveau_compte'] = {
                    'id': str(utilisateur.id),
                    'username': username,
                    'membre_nom_complet': membre.get_nom_complet(),
                    'email': membre.email_personnel,
                    'mot_de_passe': mot_de_passe_temporaire,
                    'role_systeme': role_systeme.get_nom_display() if role_systeme else None
                }
                
                return redirect('compte_cree_success')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    # Générer un nom d'utilisateur suggéré
    username_suggere = generer_username(membre.prenom, membre.nom)
    
    context = {
        'membre': membre,
        'username_suggere': username_suggere,
        'roles_systeme': RoleSysteme.objects.all(),
    }
    
    return render(request, 'core/creer_compte_utilisateur.html', context)

@require_super_admin
def compte_cree_success_view(request):
    """Page de confirmation après création d'un compte utilisateur"""
    
    # Récupérer les informations du nouveau compte depuis la session
    nouveau_compte = request.session.get('nouveau_compte')
    
    if not nouveau_compte:
        messages.error(request, 'Aucune information de compte trouvée.')
        return redirect('gestion_comptes')
    
    # Générer les initiales pour l'affichage
    nom_complet = nouveau_compte.get('membre_nom_complet', '')
    mots = nom_complet.split()
    initiales = ''.join([mot[0].upper() for mot in mots[:2]]) if mots else 'U'
    
    # Construire l'URL de connexion complète
    url_connexion = request.build_absolute_uri('/login/')
    
    # Nettoyer la session après récupération
    del request.session['nouveau_compte']
    
    context = {
        'compte_info': nouveau_compte,
        'initiales': initiales,
        'url_connexion': url_connexion,
        'date_creation': timezone.now(),
    }
    
    return render(request, 'core/compte_cree_success.html', context)

@require_super_admin
def modifier_compte_view(request, user_id):
    """Vue de modification d'un compte utilisateur"""
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if request.method == 'POST':
        # Récupérer les données du formulaire
        username = request.POST.get('username', '').strip()
        role_systeme_nom = request.POST.get('role_systeme')
        statut_actif = request.POST.get('statut_actif') == 'true'
        is_superuser = request.POST.get('is_superuser') == 'true'
        
        # Validation
        errors = []
        
        if not username:
            errors.append('Le nom d\'utilisateur est obligatoire.')
        elif Utilisateur.objects.filter(username=username).exclude(pk=utilisateur.pk).exists():
            errors.append('Ce nom d\'utilisateur est déjà utilisé.')
        
        if not role_systeme_nom:
            errors.append('Le rôle système est obligatoire.')
        
        try:
            role_systeme = RoleSysteme.objects.get(nom=role_systeme_nom)
        except RoleSysteme.DoesNotExist:
            errors.append('Le rôle système sélectionné n\'existe pas.')
            role_systeme = None
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Sauvegarder les anciennes valeurs pour l'audit
                anciennes_donnees = {
                    'username': utilisateur.username,
                    'role_systeme': utilisateur.role_systeme.nom if utilisateur.role_systeme else None,
                    'statut_actif': utilisateur.statut_actif,
                    'is_superuser': utilisateur.is_superuser
                }
                
                # Mettre à jour le compte
                utilisateur.username = username
                utilisateur.role_systeme = role_systeme
                utilisateur.statut_actif = statut_actif
                utilisateur.is_superuser = is_superuser
                utilisateur.save()
                
                # Audit
                enregistrer_audit(
                    utilisateur=request.user,
                    type_action='MODIFICATION_COMPTE_UTILISATEUR',
                    description=f'Modification du compte {username}',
                    request=request,
                    donnees_avant=anciennes_donnees,
                    donnees_apres={
                        'username': username,
                        'role_systeme': role_systeme.nom if role_systeme else None,
                        'statut_actif': statut_actif,
                        'is_superuser': is_superuser
                    }
                )
                
                messages.success(request, f'Compte modifié avec succès !')
                return redirect('gestion_comptes')
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'utilisateur': utilisateur,
        'roles_systeme': RoleSysteme.objects.all(),
    }
    
    return render(request, 'core/modifier_compte.html', context)

@require_super_admin
@require_http_methods(["POST"])
def toggle_compte_status(request, user_id):
    """Active/désactive un compte utilisateur"""
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if utilisateur == request.user:
        return JsonResponse({'success': False, 'error': 'Impossible de modifier votre propre compte.'})
    
    nouveau_statut = not utilisateur.statut_actif
    ancien_statut = utilisateur.statut_actif
    
    utilisateur.statut_actif = nouveau_statut
    utilisateur.save()
    
    # Audit
    enregistrer_audit(
        utilisateur=request.user,
        type_action='MODIFICATION_STATUT_COMPTE',
        description=f'Changement de statut du compte {utilisateur.username}: {"Actif" if ancien_statut else "Inactif"} → {"Actif" if nouveau_statut else "Inactif"}',
        request=request,
        donnees_avant={'statut_actif': ancien_statut},
        donnees_apres={'statut_actif': nouveau_statut}
    )
    
    action = 'activé' if nouveau_statut else 'désactivé'
    messages.success(request, f'Compte {action} avec succès.')
    
    return JsonResponse({'success': True, 'nouveau_statut': nouveau_statut})

@require_super_admin
@require_http_methods(["POST"])
def reset_compte_password(request, user_id):
    """Réinitialise le mot de passe d'un compte utilisateur"""
    utilisateur = get_object_or_404(Utilisateur, id=user_id)
    
    if utilisateur == request.user:
        return JsonResponse({'success': False, 'error': 'Impossible de réinitialiser votre propre mot de passe.'})
    
    # Générer un nouveau mot de passe temporaire
    nouveau_mot_de_passe = generer_mot_de_passe_temporaire()
    utilisateur.set_password(nouveau_mot_de_passe)
    utilisateur.save()
    
    # Audit
    enregistrer_audit(
        utilisateur=request.user,
        type_action='REINITIALISATION_MOT_PASSE_COMPTE',
        description=f'Réinitialisation du mot de passe du compte {utilisateur.username}',
        request=request
    )
    
    messages.success(request, f'Mot de passe réinitialisé avec succès.')
    
    return JsonResponse({
        'success': True, 
        'nouveau_mot_de_passe': nouveau_mot_de_passe,
        'username': utilisateur.username
    })

# ============================================================================
# NOUVELLES VUES - ARCHITECTURE ÉTAPES/MODULES/TÂCHES
# ============================================================================

from .models import TypeEtape, EtapeProjet, ModuleProjet, TacheModule

# ===== GESTION DES ÉTAPES =====

@login_required
def gestion_etapes_view(request, projet_id):
    """Vue de gestion des étapes d'un projet"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les étapes avec timeline
    timeline = projet.get_timeline_etapes()
    
    # Permissions d'édition
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        # Vérifier si l'utilisateur est responsable principal
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    context = {
        'projet': projet,
        'timeline': timeline,
        'can_manage': can_manage,
        'etapes_passees': timeline['passees'],
        'etape_courante': timeline['courante'],
        'etapes_futures': timeline['futures'],
    }
    
    return render(request, 'core/gestion_etapes.html', context)

@login_required
@require_http_methods(["POST"])
def activer_etape(request, projet_id, etape_id):
    """Active une étape (passe à l'étape suivante)"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        etape.activer_etape(user)
        messages.success(request, f'Étape "{etape.type_etape.get_nom_display()}" activée avec succès !')
        return JsonResponse({'success': True, 'message': 'Étape activée avec succès'})
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def terminer_etape(request, projet_id, etape_id):
    """Termine une étape et active automatiquement la suivante"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        # Terminer l'étape (qui active automatiquement la suivante et envoie les notifications)
        etape_suivante = etape.terminer_etape(user)
        
        # Message de succès avec information sur l'étape suivante
        if etape_suivante:
            if etape_suivante.type_etape.nom == 'DEVELOPPEMENT':
                message = f'Étape "{etape.type_etape.get_nom_display()}" terminée avec succès ! L\'étape "{etape_suivante.type_etape.get_nom_display()}" a été automatiquement activée. Vous pouvez maintenant créer des modules pour ce projet.'
            else:
                message = f'Étape "{etape.type_etape.get_nom_display()}" terminée avec succès ! L\'étape "{etape_suivante.type_etape.get_nom_display()}" a été automatiquement activée.'
        else:
            message = f'Étape "{etape.type_etape.get_nom_display()}" terminée avec succès ! C\'était la dernière étape du projet.'
        
        messages.success(request, message)
        return JsonResponse({
            'success': True, 
            'message': message,
            'etape_suivante': {
                'nom': etape_suivante.type_etape.get_nom_display(),
                'id': str(etape_suivante.id),
                'permet_modules': etape_suivante.type_etape.nom == 'DEVELOPPEMENT'
            } if etape_suivante else None,
            'notifications_envoyees': True
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ===== GESTION DES MODULES =====

@login_required
def detail_etape_view(request, projet_id, etape_id):
    """Vue de consultation détaillée d'une étape avec ses tâches et historique"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les tâches de cette étape
    taches_etape = etape.taches_etape.all().order_by('priorite', 'date_creation')
    
    # Récupérer les modules créés dans cette étape
    modules_crees = etape.modules_crees.all().order_by('date_creation')
    
    # Récupérer l'historique d'audit pour cette étape
    historique_audit = ActionAudit.objects.filter(
        projet=projet,
        type_action__in=[
            'ACTIVATION_ETAPE', 
            'ACTIVATION_ETAPE_AUTOMATIQUE',
            'CLOTURE_ETAPE',
            'CREATION_TACHE',
            'ASSIGNATION_TACHE',
            'CREATION_MODULE'
        ],
        description__icontains=etape.type_etape.get_nom_display()
    ).order_by('-timestamp')[:20]
    
    # Statistiques de l'étape
    stats = {
        'total_taches': taches_etape.count(),
        'taches_terminees': taches_etape.filter(statut='TERMINEE').count(),
        'taches_en_cours': taches_etape.filter(statut='EN_COURS').count(),
        'taches_bloquees': taches_etape.filter(statut='BLOQUEE').count(),
        'modules_crees': modules_crees.count(),
        'duree_etape': None
    }
    
    # Calculer la durée de l'étape si elle est terminée
    if etape.statut == 'TERMINEE' and etape.date_debut_reelle and etape.date_fin_reelle:
        duree = etape.date_fin_reelle - etape.date_debut_reelle
        stats['duree_etape'] = duree.days
    
    # Progression des tâches
    if stats['total_taches'] > 0:
        stats['progression'] = round((stats['taches_terminees'] / stats['total_taches']) * 100)
    else:
        stats['progression'] = 0
    
    # Permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    context = {
        'projet': projet,
        'etape': etape,
        'taches_etape': taches_etape,
        'modules_crees': modules_crees,
        'historique_audit': historique_audit,
        'stats': stats,
        'can_manage': can_manage,
        'equipe': projet.get_equipe(),
    }
    
    return render(request, 'core/detail_etape.html', context)

@login_required
def gestion_modules_view(request, projet_id):
    """Vue de gestion des modules d'un projet"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les modules
    modules = projet.modules.all().order_by('date_creation')
    
    # Étape courante
    etape_courante = projet.get_etape_courante()
    
    # Permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    # Vérifier si on peut créer des modules librement
    peut_creer_librement = etape_courante and etape_courante.peut_creer_modules_librement() if etape_courante else False
    
    context = {
        'projet': projet,
        'modules': modules,
        'etape_courante': etape_courante,
        'can_manage': can_manage,
        'peut_creer_librement': peut_creer_librement,
    }
    
    return render(request, 'core/gestion_modules.html', context)

@login_required
def creer_module_view(request, projet_id):
    """Vue de création d'un module"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        messages.error(request, 'Permission refusée.')
        return redirect('gestion_modules', projet_id=projet.id)
    
    # Étape courante
    etape_courante = projet.get_etape_courante()
    if not etape_courante:
        messages.error(request, 'Aucune étape active pour ce projet.')
        return redirect('gestion_modules', projet_id=projet.id)
    
    peut_creer_librement = etape_courante.peut_creer_modules_librement()
    
    # Vérifier que nous sommes en phase de développement
    if etape_courante.type_etape.nom != 'DEVELOPPEMENT':
        messages.error(request, 'La création de modules n\'est autorisée qu\'en phase de développement.')
        return redirect('gestion_modules', projet_id=projet.id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        justification = request.POST.get('justification', '').strip()
        couleur = request.POST.get('couleur', '#10B981')
        icone_emoji = request.POST.get('icone_emoji', '🧩')
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom du module est obligatoire.')
        elif ModuleProjet.objects.filter(projet=projet, nom=nom).exists():
            errors.append('Ce nom de module existe déjà pour ce projet.')
        
        if not description:
            errors.append('La description du module est obligatoire.')
        
        # Si création tardive, justification obligatoire
        if not peut_creer_librement and not justification:
            errors.append('Une justification est obligatoire pour créer un module après la phase de conception.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Créer le module
                module = ModuleProjet.objects.create(
                    projet=projet,
                    nom=nom,
                    description=description,
                    etape_creation=etape_courante,
                    createur=user,
                    couleur=couleur,
                    icone_emoji=icone_emoji,
                    justification_creation_tardive=justification if not peut_creer_librement else ''
                )
                
                # Audit
                type_audit = 'CREATION_MODULE_TARDIVE' if not peut_creer_librement else 'CREATION_MODULE'
                enregistrer_audit(
                    utilisateur=user,
                    type_action=type_audit,
                    description=f'Création du module "{nom}" dans l\'étape {etape_courante.type_etape.get_nom_display()}',
                    projet=projet,
                    request=request,
                    donnees_apres={
                        'module': nom,
                        'etape_creation': etape_courante.type_etape.nom,
                        'creation_tardive': not peut_creer_librement,
                        'justification': justification if not peut_creer_librement else None
                    }
                )
                
                messages.success(request, f'Module "{nom}" créé avec succès !')
                return redirect('detail_module', projet_id=projet.id, module_id=module.id)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'projet': projet,
        'etape_courante': etape_courante,
        'peut_creer_librement': peut_creer_librement,
    }
    
    return render(request, 'core/creer_module.html', context)

@login_required
def detail_module_view(request, projet_id, module_id):
    """Vue de détail d'un module avec ses tâches"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    module = get_object_or_404(ModuleProjet, id=module_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les tâches
    taches = module.taches.all().order_by('priorite', 'date_creation')
    
    # Permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    # Statistiques
    stats = {
        'total_taches': taches.count(),
        'taches_terminees': taches.filter(statut='TERMINEE').count(),
        'taches_en_cours': taches.filter(statut='EN_COURS').count(),
        'taches_bloquees': taches.filter(statut='BLOQUEE').count(),
        'progression': module.get_progression_taches()
    }
    
    context = {
        'projet': projet,
        'module': module,
        'taches': taches,
        'can_manage': can_manage,
        'stats': stats,
        'equipe': projet.get_equipe(),
    }
    
    return render(request, 'core/detail_module.html', context)

# ===== GESTION DES TÂCHES =====

@login_required
def gestion_taches_view(request, module_id):
    """Vue de gestion des tâches d'un module"""
    module = get_object_or_404(ModuleProjet, id=module_id)
    projet = module.projet
    user = request.user
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les tâches
    taches = module.taches.all().order_by('statut', 'priorite', 'date_creation')
    
    # Permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    context = {
        'projet': projet,
        'module': module,
        'taches': taches,
        'can_manage': can_manage,
        'equipe': projet.get_equipe(),
        'etapes': projet.etapes.all().order_by('ordre'),
    }
    
    return render(request, 'core/gestion_taches.html', context)

@login_required
def creer_tache_view(request, module_id):
    """Vue de création d'une tâche"""
    from .utils import peut_creer_taches
    
    module = get_object_or_404(ModuleProjet, id=module_id)
    projet = module.projet
    user = request.user
    
    # Vérifier les permissions avec la nouvelle fonction
    if not peut_creer_taches(user, projet):
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des tâches sur ce projet.')
        return redirect('detail_module', projet_id=projet.id, module_id=module.id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        responsable_id = request.POST.get('responsable_id')
        priorite = request.POST.get('priorite', 'MOYENNE')
        etape_execution_id = request.POST.get('etape_execution_id')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom de la tâche est obligatoire.')
        
        if not description:
            errors.append('La description de la tâche est obligatoire.')
        
        responsable = None
        if responsable_id:
            try:
                responsable = Utilisateur.objects.get(id=responsable_id)
                # Vérifier que le responsable fait partie de l'équipe
                if not projet.affectations.filter(utilisateur=responsable, date_fin__isnull=True).exists():
                    errors.append('Le responsable doit faire partie de l\'équipe du projet.')
            except Utilisateur.DoesNotExist:
                errors.append('Responsable invalide.')
        
        etape_execution = None
        if etape_execution_id:
            try:
                etape_execution = EtapeProjet.objects.get(id=etape_execution_id, projet=projet)
            except EtapeProjet.DoesNotExist:
                errors.append('Étape d\'exécution invalide.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Créer la tâche
                tache = TacheModule.objects.create(
                    module=module,
                    nom=nom,
                    description=description,
                    responsable=responsable,
                    priorite=priorite,
                    etape_execution=etape_execution,
                    date_debut=date_debut if date_debut else None,
                    date_fin=date_fin if date_fin else None,
                    createur=user
                )
                
                # Audit
                enregistrer_audit(
                    utilisateur=user,
                    type_action='CREATION_TACHE',
                    description=f'Création de la tâche "{nom}" dans le module {module.nom}',
                    projet=projet,
                    request=request,
                    donnees_apres={
                        'tache': nom,
                        'module': module.nom,
                        'responsable': responsable.get_full_name() if responsable else None,
                        'priorite': priorite
                    }
                )
                
                messages.success(request, f'Tâche "{nom}" créée avec succès !')
                return redirect('detail_module', projet_id=projet.id, module_id=module.id)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la création : {str(e)}')
    
    context = {
        'projet': projet,
        'module': module,
        'equipe': projet.get_equipe(),
        'etapes': projet.etapes.all().order_by('ordre'),
        'priorites': TacheModule.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/creer_tache.html', context)

@login_required
@require_http_methods(["POST"])
def assigner_tache(request, module_id, tache_id):
    """Assigne une tâche à un responsable"""
    module = get_object_or_404(ModuleProjet, id=module_id)
    tache = get_object_or_404(TacheModule, id=tache_id, module=module)
    projet = module.projet
    user = request.user
    
    # Vérifier les permissions
    can_manage = user.est_super_admin() or projet.createur == user
    if not can_manage:
        affectation_user = projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).first()
        can_manage = affectation_user is not None
    
    if not can_manage:
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        responsable_id = request.POST.get('responsable_id')
        
        if not responsable_id:
            return JsonResponse({'success': False, 'error': 'Responsable requis'})
        
        responsable = get_object_or_404(Utilisateur, id=responsable_id)
        
        # Vérifier que le responsable fait partie de l'équipe
        if not projet.affectations.filter(utilisateur=responsable, date_fin__isnull=True).exists():
            return JsonResponse({'success': False, 'error': 'Le responsable doit faire partie de l\'équipe du projet'})
        
        # Assigner la tâche
        tache.assigner_responsable(responsable, user)
        
        messages.success(request, f'Tâche assignée à {responsable.get_full_name()} avec succès !')
        return JsonResponse({'success': True, 'message': 'Tâche assignée avec succès'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Vues de détail et modification (à implémenter selon les besoins)
@login_required
def detail_tache_view(request, module_id, tache_id):
    """Vue de détail d'une tâche"""
    # TODO: Implémenter selon les besoins
    pass

@login_required
def modifier_module_view(request, projet_id, module_id):
    """Vue de modification d'un module"""
    # TODO: Implémenter selon les besoins
    pass

@login_required
def modifier_tache_view(request, module_id, tache_id):
    """Vue de modification d'une tâche"""
    # TODO: Implémenter selon les besoins
    pass

# ===== GESTION DES TÂCHES D'ÉTAPES =====

@login_required
def gestion_taches_etape_view(request, projet_id, etape_id):
    """Vue de gestion des tâches d'une étape"""
    from .utils import peut_creer_taches
    
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Récupérer les tâches
    taches = etape.taches_etape.all().order_by('statut', 'priorite', 'date_creation')
    
    # Permissions de création
    can_create = peut_creer_taches(user, projet)
    
    context = {
        'projet': projet,
        'etape': etape,
        'taches': taches,
        'can_create': can_create,
        'equipe': projet.get_equipe(),
    }
    
    return render(request, 'core/gestion_taches_etape.html', context)

@login_required
def creer_tache_etape_view(request, projet_id, etape_id):
    """Vue de création d'une tâche d'étape (supporte AJAX)"""
    from .utils import peut_creer_taches
    
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    
    # Vérifier les permissions
    if not peut_creer_taches(user, projet):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Vous n\'avez pas les permissions pour créer des tâches sur ce projet.'})
        messages.error(request, 'Vous n\'avez pas les permissions pour créer des tâches sur ce projet.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Vérifier que l'étape n'est pas terminée
    if etape.statut == 'TERMINEE':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Impossible de créer une tâche dans une étape terminée.'})
        messages.error(request, 'Impossible de créer une tâche dans une étape terminée.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        responsable_id = request.POST.get('responsable_id')
        priorite = request.POST.get('priorite', 'MOYENNE')
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom de la tâche est obligatoire.')
        
        if not description:
            errors.append('La description de la tâche est obligatoire.')
        
        responsable = None
        if responsable_id:
            try:
                responsable = Utilisateur.objects.get(id=responsable_id)
                # Vérifier que le responsable fait partie de l'équipe (sauf pour les super admins)
                if not responsable.est_super_admin():
                    if not projet.affectations.filter(utilisateur=responsable, date_fin__isnull=True).exists():
                        errors.append('Le responsable doit faire partie de l\'équipe du projet.')
            except Utilisateur.DoesNotExist:
                errors.append('Responsable invalide.')
        
        if errors:
            # Gestion des erreurs pour AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': ' '.join(errors)})
            
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Créer la tâche
                tache = TacheEtape.objects.create(
                    etape=etape,
                    nom=nom,
                    description=description,
                    responsable=responsable,
                    priorite=priorite,
                    date_debut=date_debut if date_debut else None,
                    date_fin=date_fin if date_fin else None,
                    createur=user
                )
                
                # Audit
                enregistrer_audit(
                    utilisateur=user,
                    type_action='CREATION_TACHE',
                    description=f'Création de la tâche d\'étape "{nom}" dans l\'étape {etape.type_etape.get_nom_display()}',
                    projet=projet,
                    request=request,
                    donnees_apres={
                        'tache': nom,
                        'etape': etape.type_etape.nom,
                        'responsable': responsable.get_full_name() if responsable else None,
                        'priorite': priorite
                    }
                )
                
                # Réponse pour AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True, 
                        'message': f'Tâche d\'étape "{nom}" créée avec succès !',
                        'tache': {
                            'id': str(tache.id),
                            'nom': tache.nom,
                            'description': tache.description,
                            'priorite': tache.get_priorite_display(),
                            'statut': tache.get_statut_display(),
                            'responsable': responsable.get_full_name() if responsable else None
                        }
                    })
                
                messages.success(request, f'Tâche d\'étape "{nom}" créée avec succès !')
                return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
                
            except Exception as e:
                error_msg = f'Erreur lors de la création : {str(e)}'
                
                # Gestion des erreurs pour AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': error_msg})
                
                messages.error(request, error_msg)
    
    context = {
        'projet': projet,
        'etape': etape,
        'equipe': projet.get_equipe(),
        'priorites': TacheEtape.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/creer_tache_etape.html', context)

@login_required
def modifier_tache_etape_view(request, projet_id, etape_id, tache_id):
    """Vue de modification d'une tâche d'étape avec fonctionnalités avancées"""
    from .utils import peut_creer_taches
    
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not tache.peut_etre_modifiee_par(user):
        messages.error(request, 'Vous n\'avez pas les permissions pour modifier cette tâche.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Vérifier que l'étape n'est pas terminée
    if etape.statut == 'TERMINEE':
        messages.error(request, 'Impossible de modifier une tâche dans une étape terminée.')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        responsable_id = request.POST.get('responsable_id')
        priorite = request.POST.get('priorite', tache.priorite)
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        pourcentage_completion = request.POST.get('pourcentage_completion', tache.pourcentage_completion)
        etiquettes = request.POST.get('etiquettes', tache.etiquettes)
        
        # Validation
        errors = []
        
        if not nom:
            errors.append('Le nom de la tâche est obligatoire.')
        
        if not description:
            errors.append('La description de la tâche est obligatoire.')
        
        responsable = None
        if responsable_id:
            try:
                responsable = Utilisateur.objects.get(id=responsable_id)
                # Vérifier que le responsable fait partie de l'équipe (sauf pour les super admins)
                if not responsable.est_super_admin():
                    if not projet.affectations.filter(utilisateur=responsable, date_fin__isnull=True).exists():
                        errors.append('Le responsable doit faire partie de l\'équipe du projet.')
            except Utilisateur.DoesNotExist:
                errors.append('Responsable invalide.')
        
        # Validation du pourcentage
        try:
            pourcentage_completion = int(pourcentage_completion)
            if pourcentage_completion < 0 or pourcentage_completion > 100:
                errors.append('Le pourcentage de completion doit être entre 0 et 100.')
        except (ValueError, TypeError):
            errors.append('Pourcentage de completion invalide.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Sauvegarder les anciennes valeurs pour l'historique
                donnees_avant = {
                    'nom': tache.nom,
                    'description': tache.description,
                    'responsable': tache.responsable.get_full_name() if tache.responsable else None,
                    'priorite': tache.priorite,
                    'date_debut': str(tache.date_debut) if tache.date_debut else None,
                    'date_fin': str(tache.date_fin) if tache.date_fin else None,
                    'pourcentage_completion': tache.pourcentage_completion,
                    'etiquettes': tache.etiquettes
                }
                
                # Mettre à jour la tâche
                tache.nom = nom
                tache.description = description
                tache.responsable = responsable
                tache.priorite = priorite
                tache.date_debut = date_debut if date_debut else None
                tache.date_fin = date_fin if date_fin else None
                tache.etiquettes = etiquettes
                
                # Mettre à jour la progression (avec logique automatique de statut)
                if pourcentage_completion != tache.pourcentage_completion:
                    tache.mettre_a_jour_progression(pourcentage_completion, user, "Modification manuelle")
                else:
                    tache.save()
                
                # Enregistrer dans l'historique
                from .models import HistoriqueTache
                HistoriqueTache.objects.create(
                    tache=tache,
                    utilisateur=user,
                    type_action='MODIFICATION',
                    description=f'Modification de la tâche "{nom}"',
                    donnees_avant=donnees_avant,
                    donnees_apres={
                        'nom': nom,
                        'description': description,
                        'responsable': responsable.get_full_name() if responsable else None,
                        'priorite': priorite,
                        'date_debut': str(date_debut) if date_debut else None,
                        'date_fin': str(date_fin) if date_fin else None,
                        'pourcentage_completion': pourcentage_completion,
                        'etiquettes': etiquettes
                    }
                )
                
                messages.success(request, f'Tâche "{nom}" modifiée avec succès !')
                return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
                
            except Exception as e:
                messages.error(request, f'Erreur lors de la modification : {str(e)}')
    
    context = {
        'projet': projet,
        'etape': etape,
        'tache': tache,
        'equipe': projet.get_equipe(),
        'priorites': TacheEtape.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/modifier_tache_etape.html', context)

@login_required
@require_http_methods(["POST"])
def changer_statut_tache_etape(request, projet_id, etape_id, tache_id):
    """Change le statut d'une tâche d'étape avec historique"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not tache.peut_etre_modifiee_par(user):
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        nouveau_statut = request.POST.get('statut')
        commentaire = request.POST.get('commentaire', '').strip()
        
        if not nouveau_statut:
            return JsonResponse({'success': False, 'error': 'Statut requis'})
        
        # Valider le statut
        statuts_valides = [choice[0] for choice in TacheEtape.STATUT_CHOICES]
        if nouveau_statut not in statuts_valides:
            return JsonResponse({'success': False, 'error': 'Statut invalide'})
        
        # Changer le statut avec la méthode du modèle
        tache.changer_statut(nouveau_statut, user, commentaire)
        
        return JsonResponse({
            'success': True,
            'message': f'Statut changé vers "{tache.get_statut_display()}" avec succès',
            'nouveau_statut': nouveau_statut,
            'nouveau_statut_display': tache.get_statut_display(),
            'pourcentage_completion': tache.pourcentage_completion
        })
        
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def mettre_a_jour_progression_tache(request, projet_id, etape_id, tache_id):
    """Met à jour la progression d'une tâche"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)

@login_required
@require_http_methods(["POST"])
def terminer_tache_etape(request, projet_id, etape_id, tache_id):
    """Marquer une tâche comme terminée avec notifications complètes"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not (user.est_super_admin() or 
            projet.get_responsable_principal() == user or
            tache.responsable == user or
            projet.affectations.filter(utilisateur=user, date_fin__isnull=True).exists()):
        return JsonResponse({
            'success': False, 
            'error': 'Vous n\'avez pas les permissions pour marquer cette tâche comme terminée'
        })
    
    # Vérifier que la tâche n'est pas déjà terminée
    if tache.statut == 'TERMINEE':
        return JsonResponse({
            'success': False,
            'error': 'Cette tâche est déjà terminée'
        })
    
    try:
        # Marquer la tâche comme terminée
        ancien_statut = tache.statut
        ancienne_progression = tache.pourcentage_completion
        
        tache.statut = 'TERMINEE'
        tache.pourcentage_completion = 100
        tache.date_fin_reelle = timezone.now()
        tache.save()
        
        # Créer les notifications
        from .models import NotificationTache
        
        # 1. Notification pour le responsable principal du projet (si différent)
        responsable_principal = projet.get_responsable_principal()
        if responsable_principal and responsable_principal != user:
            NotificationTache.objects.create(
                destinataire=responsable_principal,
                tache=tache,
                type_notification='COMPLETION',
                message=f'La tâche "{tache.nom}" a été marquée comme terminée par {user.get_full_name() or user.username}'
            )
        
        # 2. Notification pour le responsable de la tâche (si différent)
        if tache.responsable and tache.responsable != user and tache.responsable != responsable_principal:
            NotificationTache.objects.create(
                destinataire=tache.responsable,
                tache=tache,
                type_notification='COMPLETION',
                message=f'Votre tâche "{tache.nom}" a été marquée comme terminée'
            )
        
        # 3. NOUVEAU: Notifications pour TOUS les administrateurs (sauf celui qui termine)
        administrateurs = Utilisateur.objects.filter(
            is_superuser=True,
            statut_actif=True
        ).exclude(id=user.id)
        
        for admin in administrateurs:
            NotificationTache.objects.create(
                destinataire=admin,
                tache=tache,
                type_notification='COMPLETION',
                message=f'Tâche "{tache.nom}" terminée par {user.get_full_name() or user.username} dans le projet {projet.nom}'
            )
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='COMPLETION_TACHE',
            description=f'Tâche d\'étape "{tache.nom}" marquée comme terminée',
            projet=projet,
            request=request,
            donnees_avant={'statut': ancien_statut, 'pourcentage_completion': ancienne_progression},
            donnees_apres={'statut': 'TERMINEE', 'pourcentage_completion': 100}
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Tâche "{tache.nom}" marquée comme terminée avec succès !',
            'nouveau_statut': tache.statut,
            'pourcentage': tache.pourcentage_completion
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la finalisation de la tâche : {str(e)}'
        })
@login_required
@require_http_methods(["POST"])
def assigner_tache_etape(request, projet_id, etape_id, tache_id):
    """Assigne une tâche d'étape à un responsable"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not tache.peut_etre_modifiee_par(user):
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        responsable_id = request.POST.get('responsable_id')
        
        if not responsable_id:
            return JsonResponse({'success': False, 'error': 'Responsable requis'})
        
        responsable = get_object_or_404(Utilisateur, id=responsable_id)
        
        # Vérifier que le responsable fait partie de l'équipe (sauf pour les super admins)
        if not responsable.est_super_admin():
            if not projet.affectations.filter(utilisateur=responsable, date_fin__isnull=True).exists():
                return JsonResponse({'success': False, 'error': 'Le responsable doit faire partie de l\'équipe du projet'})
        
        # Assigner la tâche
        tache.assigner_responsable(responsable, user)
        
        return JsonResponse({
            'success': True, 
            'message': f'Tâche assignée à {responsable.get_full_name()} avec succès',
            'responsable': {
                'id': responsable.id,
                'nom': responsable.get_full_name()
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def ajouter_commentaire_tache(request, projet_id, etape_id, tache_id):
    """Ajoute un commentaire à une tâche"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions (tous les membres de l'équipe peuvent commenter)
    if not user.est_super_admin() and not user.a_acces_projet(projet):
        return JsonResponse({'success': False, 'error': 'Permission refusée'})
    
    try:
        contenu = request.POST.get('contenu', '').strip()
        
        if not contenu:
            return JsonResponse({'success': False, 'error': 'Le contenu du commentaire est requis'})
        
        # Créer le commentaire
        from .models import CommentaireTache
        commentaire = CommentaireTache.objects.create(
            tache=tache,
            auteur=user,
            contenu=contenu
        )
        
        # Traiter les mentions
        commentaire.notifier_mentions()
        
        # Enregistrer dans l'historique
        from .models import HistoriqueTache
        HistoriqueTache.objects.create(
            tache=tache,
            utilisateur=user,
            type_action='COMMENTAIRE',
            description=f'Ajout d\'un commentaire sur la tâche "{tache.nom}"',
            donnees_apres={'contenu': contenu}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Commentaire ajouté avec succès',
            'commentaire': {
                'id': commentaire.id,
                'auteur': user.get_full_name(),
                'contenu': contenu,
                'date_creation': commentaire.date_creation.strftime('%d/%m/%Y %H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def historique_tache_view(request, projet_id, etape_id, tache_id):
    """Vue de l'historique complet d'une tâche"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    etape = get_object_or_404(EtapeProjet, id=etape_id, projet=projet)
    tache = get_object_or_404(TacheEtape, id=tache_id, etape=etape)
    
    # Vérifier les permissions
    if not user.est_super_admin() and not user.a_acces_projet(projet):
        messages.error(request, 'Permission refusée')
        return redirect('detail_etape', projet_id=projet.id, etape_id=etape.id)
    
    # Récupérer l'historique
    historique = tache.historique.all().order_by('-timestamp')
    
    # Récupérer les commentaires
    commentaires = tache.commentaires_tache.all().order_by('-date_creation')
    
    context = {
        'projet': projet,
        'etape': etape,
        'tache': tache,
        'historique': historique,
        'commentaires': commentaires,
    }
    
    return render(request, 'core/historique_tache.html', context)

@login_required
def notifications_taches_view(request):
    """Vue des notifications de tâches pour l'utilisateur connecté"""
    user = request.user
    
    # Récupérer les notifications non lues
    from .models import NotificationTache
    notifications_non_lues = NotificationTache.objects.filter(
        destinataire=user,
        lue=False
    ).order_by('-date_creation')
    
    # Récupérer les notifications récentes (7 derniers jours)
    from datetime import timedelta
    date_limite = timezone.now() - timedelta(days=7)
    notifications_recentes = NotificationTache.objects.filter(
        destinataire=user,
        date_creation__gte=date_limite
    ).order_by('-date_creation')
    
    context = {
        'notifications_non_lues': notifications_non_lues,
        'notifications_recentes': notifications_recentes,
        'total_non_lues': notifications_non_lues.count(),
    }
    
    return render(request, 'core/notifications_taches.html', context)

@login_required
@require_http_methods(["POST"])
def marquer_notification_lue(request, notification_id):
    """Marque une notification comme lue"""
    user = request.user
    
    try:
        from .models import NotificationTache
        notification = get_object_or_404(NotificationTache, id=notification_id, destinataire=user)
        
        if not notification.lue:
            notification.marquer_comme_lue()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# API Endpoints pour les notifications
@login_required
def api_notifications(request):
    """API pour récupérer les notifications de l'utilisateur connecté"""
    user = request.user
    
    try:
        from .models import NotificationTache
        
        # Récupérer les notifications non lues
        notifications_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        ).order_by('-date_creation')
        
        # Récupérer les notifications récentes (dernières 10)
        notifications_recentes = NotificationTache.objects.filter(
            destinataire=user
        ).order_by('-date_creation')[:10]
        
        # Préparer les données pour JSON
        notifications_data = []
        for notif in notifications_recentes:
            notifications_data.append({
                'id': notif.id,
                'message': notif.message,
                'date_creation': notif.date_creation.isoformat(),
                'lue': notif.lue,
                'type_notification': notif.type_notification,
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'total_non_lues': notifications_non_lues.count(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications': [],
            'total_non_lues': 0,
        })

@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """API pour marquer une notification comme lue"""
    user = request.user
    
    try:
        from .models import NotificationTache
        notification = get_object_or_404(NotificationTache, id=notification_id, destinataire=user)
        
        if not notification.lue:
            notification.marquer_comme_lue()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """API pour marquer toutes les notifications comme lues"""
    user = request.user
    
    try:
        from .models import NotificationTache
        
        # Marquer toutes les notifications non lues comme lues
        notifications_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        )
        
        count = 0
        for notification in notifications_non_lues:
            notification.marquer_comme_lue()
            count += 1
        
        return JsonResponse({
            'success': True,
            'marked_count': count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ============================================================================
# API NOTIFICATIONS - FONCTIONS COMPLÈTES
# ============================================================================

@login_required
def notifications_taches_view(request):
    """Vue des notifications de tâches pour l'utilisateur connecté"""
    user = request.user
    
    context = {
        'user': user,
    }
    
    return render(request, 'core/notifications_taches.html', context)

@login_required
def api_notifications(request):
    """API pour récupérer les notifications de l'utilisateur connecté (icône navbar)"""
    user = request.user
    
    try:
        from .models import NotificationTache
        
        # Pour l'icône : seulement les notifications NON LUES (dernières 10)
        notifications_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        ).order_by('-date_creation')[:10]
        
        # Compter le total des non lues pour le badge
        total_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        ).count()
        
        # Préparer les données pour JSON
        notifications_data = []
        for notif in notifications_non_lues:
            notifications_data.append({
                'id': notif.id,
                'message': notif.message,
                'date_creation': notif.date_creation.isoformat(),
                'lue': False,
                'type_notification': notif.type_notification,
                'tache_id': notif.tache.id if notif.tache else None,
                'projet_nom': notif.tache.etape.projet.nom if notif.tache and notif.tache.etape else None,
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'total_non_lues': total_non_lues,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications': [],
            'total_non_lues': 0,
        })

@login_required
def api_notifications_detailed(request):
    """API pour la page complète des notifications avec séparation lues/non lues"""
    user = request.user
    
    try:
        from .models import NotificationTache
        
        # Récupérer les notifications non lues
        notifications_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        ).order_by('-date_creation')
        
        # Récupérer les notifications lues récentes (dernières 50)
        notifications_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=True
        ).order_by('-date_creation')[:50]
        
        # Préparer les données pour JSON - Non lues
        notifications_non_lues_data = []
        for notif in notifications_non_lues:
            notifications_non_lues_data.append({
                'id': notif.id,
                'message': notif.message,
                'date_creation': notif.date_creation.isoformat(),
                'lue': False,
                'type_notification': notif.type_notification,
                'tache_id': notif.tache.id if notif.tache else None,
                'projet_nom': notif.tache.etape.projet.nom if notif.tache and notif.tache.etape else None,
            })
        
        # Préparer les données pour JSON - Lues
        notifications_lues_data = []
        for notif in notifications_lues:
            notifications_lues_data.append({
                'id': notif.id,
                'message': notif.message,
                'date_creation': notif.date_creation.isoformat(),
                'lue': True,
                'type_notification': notif.type_notification,
                'tache_id': notif.tache.id if notif.tache else None,
                'projet_nom': notif.tache.etape.projet.nom if notif.tache and notif.tache.etape else None,
            })
        
        return JsonResponse({
            'success': True,
            'notifications_non_lues': notifications_non_lues_data,
            'notifications_lues': notifications_lues_data,
            'total_non_lues': notifications_non_lues.count(),
            'total_lues': notifications_lues.count(),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'notifications_non_lues': [],
            'notifications_lues': [],
            'total_non_lues': 0,
            'total_lues': 0,
        })

@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """API pour marquer une notification comme lue"""
    user = request.user
    
    try:
        from .models import NotificationTache
        notification = get_object_or_404(NotificationTache, id=notification_id, destinataire=user)
        
        if not notification.lue:
            notification.marquer_comme_lue()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """API pour marquer toutes les notifications comme lues"""
    user = request.user
    
    try:
        from .models import NotificationTache
        
        # Marquer toutes les notifications non lues comme lues
        notifications_non_lues = NotificationTache.objects.filter(
            destinataire=user,
            lue=False
        )
        
        count = 0
        for notification in notifications_non_lues:
            notification.marquer_comme_lue()
            count += 1
        
        return JsonResponse({
            'success': True,
            'marked_count': count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def mes_taches_view(request, projet_id):
    """Vue pour qu'un membre voie ses tâches dans un projet"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier que l'utilisateur a accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            messages.error(request, 'Vous n\'avez pas accès à ce projet.')
            return redirect('projets_list')
    
    # Filtres
    statut_filter = request.GET.get('statut', '')
    priorite_filter = request.GET.get('priorite', '')
    
    # Récupérer toutes les tâches dont l'utilisateur est responsable dans ce projet
    mes_taches_etape = TacheEtape.objects.filter(
        responsable=user,
        etape__projet=projet
    ).select_related('etape', 'etape__type_etape').order_by('statut', 'priorite', 'date_creation')
    
    # Appliquer les filtres
    if statut_filter:
        mes_taches_etape = mes_taches_etape.filter(statut=statut_filter)
    
    if priorite_filter:
        mes_taches_etape = mes_taches_etape.filter(priorite=priorite_filter)
    
    # Récupérer aussi les tâches de modules si elles existent
    mes_taches_module = []
    try:
        mes_taches_module = TacheModule.objects.filter(
            responsable=user,
            module__projet=projet
        ).select_related('module').order_by('statut', 'priorite', 'date_creation')
        
        # Appliquer les filtres aux tâches de modules aussi
        if statut_filter:
            mes_taches_module = mes_taches_module.filter(statut=statut_filter)
        
        if priorite_filter:
            mes_taches_module = mes_taches_module.filter(priorite=priorite_filter)
            
    except:
        pass  # TacheModule peut ne pas exister
    
    # Statistiques (sur toutes les tâches, pas seulement filtrées)
    all_taches_etape = TacheEtape.objects.filter(responsable=user, etape__projet=projet)
    all_taches_module = []
    try:
        all_taches_module = TacheModule.objects.filter(responsable=user, module__projet=projet)
    except:
        pass
    
    stats = {
        'total': all_taches_etape.count() + len(all_taches_module),
        'en_cours': all_taches_etape.filter(statut='EN_COURS').count() + len([t for t in all_taches_module if t.statut == 'EN_COURS']),
        'terminees': all_taches_etape.filter(statut='TERMINEE').count() + len([t for t in all_taches_module if t.statut == 'TERMINEE']),
        'bloquees': all_taches_etape.filter(statut='BLOQUEE').count() + len([t for t in all_taches_module if t.statut == 'BLOQUEE']),
        'a_faire': all_taches_etape.filter(statut='A_FAIRE').count() + len([t for t in all_taches_module if t.statut == 'A_FAIRE']),
    }
    
    # Enregistrer l'audit de consultation
    enregistrer_audit(
        utilisateur=user,
        type_action='CONSULTATION_TACHES',
        description=f'Consultation des tâches personnelles dans le projet {projet.nom}',
        projet=projet,
        request=request,
        donnees_apres={
            'nombre_taches_etape': mes_taches_etape.count(),
            'nombre_taches_module': len(mes_taches_module),
            'filtres': {
                'statut': statut_filter,
                'priorite': priorite_filter
            }
        }
    )
    
    context = {
        'projet': projet,
        'mes_taches_etape': mes_taches_etape,
        'mes_taches_module': mes_taches_module,
        'stats': stats,
        'user': user,
        'statut_filter': statut_filter,
        'priorite_filter': priorite_filter,
        'statuts_disponibles': TacheEtape.STATUT_CHOICES,
        'priorites_disponibles': TacheEtape.PRIORITE_CHOICES,
    }
    
    return render(request, 'core/mes_taches_optimisee.html', context)

@login_required
@require_http_methods(["POST"])
def terminer_tache_view(request, projet_id, tache_id, type_tache):
    """Marquer une tâche comme terminée"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        if type_tache == 'etape':
            tache = get_object_or_404(TacheEtape, id=tache_id, etape__projet=projet)
        elif type_tache == 'module':
            tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
        else:
            return JsonResponse({'success': False, 'error': 'Type de tâche invalide'})
        
        # Vérifier que l'utilisateur est le responsable de la tâche
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Vous n\'êtes pas responsable de cette tâche'})
        
        # Vérifier que la tâche n'est pas déjà terminée
        if tache.statut == 'TERMINEE':
            return JsonResponse({'success': False, 'error': 'Cette tâche est déjà terminée'})
        
        # Sauvegarder l'état avant modification pour l'audit
        donnees_avant = {
            'statut': tache.statut,
            'pourcentage_completion': getattr(tache, 'pourcentage_completion', 0),
            'date_fin_reelle': tache.date_fin_reelle.isoformat() if tache.date_fin_reelle else None
        }
        
        # Marquer comme terminée
        tache.statut = 'TERMINEE'
        tache.date_fin_reelle = timezone.now()
        
        # Mettre à jour le pourcentage de completion à 100% si le champ existe
        if hasattr(tache, 'pourcentage_completion'):
            tache.pourcentage_completion = 100
        
        # Si la tâche n'avait pas de date de début réelle, la définir maintenant
        if not tache.date_debut_reelle:
            tache.date_debut_reelle = tache.date_fin_reelle
        
        tache.save()
        
        # Données après modification pour l'audit
        donnees_apres = {
            'statut': 'TERMINEE',
            'pourcentage_completion': getattr(tache, 'pourcentage_completion', 100),
            'date_fin_reelle': tache.date_fin_reelle.isoformat()
        }
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='COMPLETION_TACHE',
            description=f'Tâche terminée: {tache.nom} ({type_tache})',
            projet=projet,
            request=request,
            donnees_avant=donnees_avant,
            donnees_apres=donnees_apres
        )
        
        # Calculer les statistiques mises à jour pour la réponse
        if type_tache == 'etape':
            total_taches = TacheEtape.objects.filter(responsable=user, etape__projet=projet).count()
            taches_terminees = TacheEtape.objects.filter(responsable=user, etape__projet=projet, statut='TERMINEE').count()
        else:
            try:
                total_taches = TacheModule.objects.filter(responsable=user, module__projet=projet).count()
                taches_terminees = TacheModule.objects.filter(responsable=user, module__projet=projet, statut='TERMINEE').count()
            except:
                total_taches = 0
                taches_terminees = 0
        
        pourcentage_completion_projet = (taches_terminees / total_taches * 100) if total_taches > 0 else 0
        
        return JsonResponse({
            'success': True, 
            'message': f'Tâche "{tache.nom}" marquée comme terminée !',
            'date_completion': tache.date_fin_reelle.strftime('%d/%m/%Y %H:%M'),
            'stats': {
                'total_taches': total_taches,
                'taches_terminees': taches_terminees,
                'pourcentage_completion': round(pourcentage_completion_projet, 1)
            }
        })
        
    except Exception as e:
        # Log de l'erreur pour le débogage
        enregistrer_audit(
            utilisateur=user,
            type_action='ERREUR_COMPLETION_TACHE',
            description=f'Erreur lors de la completion de tâche {tache_id}: {str(e)}',
            projet=projet,
            request=request,
            donnees_apres={'erreur': str(e)}
        )
@login_required
@require_http_methods(["POST"])
def changer_statut_ma_tache_view(request, projet_id, tache_id, type_tache):
    """Permettre à un membre de changer le statut de sa tâche"""
    user = request.user
    projet = get_object_or_404(Projet, id=projet_id)
    
    # Vérifier l'accès au projet
    if not user.est_super_admin():
        if not user.a_acces_projet(projet) and projet.createur != user:
            return JsonResponse({'success': False, 'error': 'Accès refusé au projet'})
    
    try:
        if type_tache == 'etape':
            tache = get_object_or_404(TacheEtape, id=tache_id, etape__projet=projet)
        elif type_tache == 'module':
            tache = get_object_or_404(TacheModule, id=tache_id, module__projet=projet)
        else:
            return JsonResponse({'success': False, 'error': 'Type de tâche invalide'})
        
        # Vérifier que l'utilisateur est le responsable de la tâche
        if tache.responsable != user:
            return JsonResponse({'success': False, 'error': 'Vous n\'êtes pas responsable de cette tâche'})
        
        # Récupérer le nouveau statut
        nouveau_statut = request.POST.get('statut')
        if not nouveau_statut:
            return JsonResponse({'success': False, 'error': 'Statut manquant'})
        
        # Valider le statut
        statuts_valides = [choice[0] for choice in TacheEtape.STATUT_CHOICES]
        if nouveau_statut not in statuts_valides:
            return JsonResponse({'success': False, 'error': 'Statut invalide'})
        
        # Sauvegarder l'état avant modification
        ancien_statut = tache.statut
        
        # Appliquer le changement
        tache.statut = nouveau_statut
        
        # Gérer les dates selon le statut
        if nouveau_statut == 'EN_COURS' and not tache.date_debut_reelle:
            tache.date_debut_reelle = timezone.now()
        elif nouveau_statut == 'TERMINEE':
            tache.date_fin_reelle = timezone.now()
            if hasattr(tache, 'pourcentage_completion'):
                tache.pourcentage_completion = 100
        
        tache.save()
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='CHANGEMENT_STATUT_TACHE',
            description=f'Changement de statut de tâche: {tache.nom} ({ancien_statut} → {nouveau_statut})',
            projet=projet,
            request=request,
            donnees_avant={'statut': ancien_statut},
            donnees_apres={'statut': nouveau_statut}
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Statut de la tâche "{tache.nom}" mis à jour !',
            'nouveau_statut': nouveau_statut,
            'ancien_statut': ancien_statut
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Erreur lors du changement de statut: {str(e)}'})

# ============================================================================
# VUES DE PROFIL UTILISATEUR
# ============================================================================

@login_required
def profil_view(request):
    """Vue du profil utilisateur - permet de voir et modifier ses informations personnelles"""
    user = request.user
    
    # Les administrateurs ne peuvent pas accéder à cette vue (ils ont leur propre interface)
    if user.est_super_admin():
        messages.info(request, 'Les administrateurs gèrent leurs informations via l\'interface d\'administration.')
        return redirect('dashboard')
    
    # Enregistrer la consultation du profil
    enregistrer_audit(
        utilisateur=user,
        type_action='CONSULTATION_PROFIL',
        description='Consultation du profil personnel',
        request=request
    )
    
    # Récupérer les projets de l'utilisateur pour affichage
    mes_projets = Projet.objects.filter(
        affectations__utilisateur=user, 
        affectations__date_fin__isnull=True
    ).distinct()[:5]  # Limiter à 5 projets récents
    
    # Récupérer les informations du membre associé (profil RH)
    membre = None
    if hasattr(user, 'membre') and user.membre:
        membre = user.membre
    
    # Statistiques personnelles
    stats = {
        'projets_actifs': mes_projets.count(),
        'taches_en_cours': 0,
        'taches_terminees': 0,
        'derniere_connexion': user.derniere_connexion,
        'membre_depuis': user.date_joined,
    }
    
    # Calculer les statistiques de tâches
    try:
        taches_etape = TacheEtape.objects.filter(responsable=user)
        stats['taches_en_cours'] += taches_etape.filter(statut='EN_COURS').count()
        stats['taches_terminees'] += taches_etape.filter(statut='TERMINEE').count()
        
        # Ajouter les tâches de modules si elles existent
        try:
            taches_module = TacheModule.objects.filter(responsable=user)
            stats['taches_en_cours'] += taches_module.filter(statut='EN_COURS').count()
            stats['taches_terminees'] += taches_module.filter(statut='TERMINEE').count()
        except:
            pass
    except:
        pass
    
    context = {
        'user': user,
        'membre': membre,  # Ajouter les informations du membre
        'mes_projets': mes_projets,
        'stats': stats,
        'peut_modifier': True,  # L'utilisateur peut toujours modifier son propre profil
    }
    
    return render(request, 'core/profil.html', context)

@login_required
@require_http_methods(["POST"])
def modifier_profil_view(request):
    """Modification des informations personnelles du profil"""
    user = request.user
    
    # Les administrateurs ne peuvent pas utiliser cette vue
    if user.est_super_admin():
        return JsonResponse({'success': False, 'error': 'Accès non autorisé pour les administrateurs'})
    
    try:
        # Sauvegarder l'état avant modification pour l'audit
        donnees_avant = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'telephone': user.telephone,
        }
        
        # Récupérer les nouvelles données
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        
        # Validation
        errors = []
        
        if not first_name:
            errors.append('Le prénom est obligatoire.')
        if not last_name:
            errors.append('Le nom est obligatoire.')
        
        if errors:
            return JsonResponse({'success': False, 'error': ' '.join(errors)})
        
        # Appliquer les modifications
        user.first_name = first_name
        user.last_name = last_name
        user.telephone = telephone
        user.save()
        
        # Données après modification pour l'audit
        donnees_apres = {
            'first_name': first_name,
            'last_name': last_name,
            'telephone': telephone,
        }
        
        # Audit
        enregistrer_audit(
            utilisateur=user,
            type_action='MODIFICATION_PROFIL',
            description='Modification des informations personnelles',
            request=request,
            donnees_avant=donnees_avant,
            donnees_apres=donnees_apres
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Profil mis à jour avec succès !',
            'nom_complet': user.get_full_name()
        })
        
    except Exception as e:
        # Audit de l'erreur
        enregistrer_audit(
            utilisateur=user,
            type_action='ERREUR_MODIFICATION_PROFIL',
            description=f'Erreur lors de la modification du profil: {str(e)}',
            request=request
        )
        return JsonResponse({'success': False, 'error': 'Une erreur est survenue lors de la modification'})

@login_required
@require_http_methods(["POST"])
def changer_mot_de_passe_view(request):
    """Changement du mot de passe utilisateur avec notification par email"""
    user = request.user
    
    # Les administrateurs ne peuvent pas utiliser cette vue
    if user.est_super_admin():
        return JsonResponse({'success': False, 'error': 'Accès non autorisé pour les administrateurs'})
    
    try:
        # Récupérer les données
        ancien_mot_de_passe = request.POST.get('ancien_mot_de_passe', '')
        nouveau_mot_de_passe = request.POST.get('nouveau_mot_de_passe', '')
        confirmer_mot_de_passe = request.POST.get('confirmer_mot_de_passe', '')
        
        # Validation
        errors = []
        
        if not ancien_mot_de_passe:
            errors.append('L\'ancien mot de passe est requis.')
        
        if not nouveau_mot_de_passe:
            errors.append('Le nouveau mot de passe est requis.')
        elif len(nouveau_mot_de_passe) < 8:
            errors.append('Le nouveau mot de passe doit contenir au moins 8 caractères.')
        
        if nouveau_mot_de_passe != confirmer_mot_de_passe:
            errors.append('La confirmation du mot de passe ne correspond pas.')
        
        # Vérifier l'ancien mot de passe
        if not user.check_password(ancien_mot_de_passe):
            errors.append('L\'ancien mot de passe est incorrect.')
        
        if errors:
            # Audit de tentative échouée
            enregistrer_audit(
                utilisateur=user,
                type_action='TENTATIVE_CHANGEMENT_MOT_DE_PASSE_ECHOUEE',
                description=f'Tentative de changement de mot de passe échouée: {", ".join(errors)}',
                request=request
            )
            return JsonResponse({'success': False, 'error': ' '.join(errors)})
        
        # Changer le mot de passe
        user.set_password(nouveau_mot_de_passe)
        user.save()
        
        # Audit de succès
        enregistrer_audit(
            utilisateur=user,
            type_action='CHANGEMENT_MOT_DE_PASSE',
            description='Changement de mot de passe réussi',
            request=request
        )
        
        # Envoyer la notification par email
        try:
            email_envoye = envoyer_notification_changement_mot_de_passe(user, request)
        except Exception as email_error:
            email_envoye = False
            # Audit de l'erreur d'email
            enregistrer_audit(
                utilisateur=user,
                type_action='ERREUR_NOTIFICATION_EMAIL',
                description=f'Erreur lors de l\'envoi de l\'email de notification: {str(email_error)}',
                request=request
            )
        
        # Message de succès avec information sur l'email
        message_succes = 'Mot de passe modifié avec succès ! Vous devrez vous reconnecter.'
        if email_envoye:
            message_succes += ' Un email de confirmation a été envoyé à votre adresse.'
        else:
            message_succes += ' Attention : l\'email de confirmation n\'a pas pu être envoyé.'
            # Audit de l'échec d'envoi d'email
            enregistrer_audit(
                utilisateur=user,
                type_action='ERREUR_NOTIFICATION_EMAIL',
                description='Échec de l\'envoi de l\'email de notification de changement de mot de passe',
                request=request
            )
        
        return JsonResponse({
            'success': True, 
            'message': message_succes,
            'email_envoye': email_envoye,
            'redirect_to_login': True
        })
        
    except Exception as e:
        # Audit de l'erreur
        enregistrer_audit(
            utilisateur=user,
            type_action='ERREUR_CHANGEMENT_MOT_DE_PASSE',
            description=f'Erreur lors du changement de mot de passe: {str(e)}',
            request=request
        )
        return JsonResponse({'success': False, 'error': 'Une erreur est survenue lors du changement de mot de passe'})