from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    # path('dashboard-utilisateur/', views.dashboard_utilisateur_view, name='dashboard_utilisateur'), # Supprimé - utilise dashboard principal
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('projets/', views.projets_list_view, name='projets_list'),
    path('projets/creer/', views.creer_projet_view, name='creer_projet'),
    path('projets/cree-success/', views.projet_cree_success_view, name='projet_cree_success'),
    path('projets/<uuid:projet_id>/', views.projet_detail_view, name='projet_detail'),
    path('projets/<uuid:projet_id>/modifier-budget/', views.modifier_budget_projet, name='modifier_budget_projet'),
    path('projets/<uuid:projet_id>/modifier/', views.modifier_projet_view, name='modifier_projet'),
    path('projets/<uuid:projet_id>/parametres/', views.parametres_projet_view, name='parametres_projet'),
    path('projets/<uuid:projet_id>/ajouter-membre/', views.ajouter_membre_projet, name='ajouter_membre_projet'),
    path('projets/<uuid:projet_id>/retirer-membre/', views.retirer_membre_projet, name='retirer_membre_projet'),
    path('projets/<uuid:projet_id>/modifier-role/', views.modifier_role_membre, name='modifier_role_membre'),
    path('projets/<uuid:projet_id>/definir-responsable/', views.definir_responsable, name='definir_responsable'),
    path('projets/<uuid:projet_id>/transferer-responsabilite/', views.transferer_responsabilite_projet, name='transferer_responsabilite_projet'),
    path('projets/<uuid:projet_id>/transferer-responsabilite-automatique/', views.transferer_responsabilite_automatique, name='transferer_responsabilite_automatique'),
    path('audit/', views.audit_view, name='audit'),
    path('audit/log/<uuid:log_id>/', views.audit_log_detail, name='audit_log_detail'),
    
    # Gestion des membres (Profils RH)
    path('membres/', views.gestion_membres_view, name='gestion_membres'),
    path('membres/creer/', views.creer_membre_view, name='creer_membre'),
    path('membres/cree-success/', views.membre_cree_success_view, name='membre_cree_success'),
    path('membres/<uuid:membre_id>/', views.detail_membre_view, name='detail_membre'),
    path('membres/<uuid:membre_id>/modifier/', views.modifier_membre_view, name='modifier_membre'),
    
    # Gestion des comptes utilisateur (Accès système)
    path('comptes/', views.gestion_comptes_view, name='gestion_comptes'),
    path('membres/<uuid:membre_id>/creer-compte/', views.creer_compte_utilisateur_view, name='creer_compte_utilisateur'),
    path('comptes/cree-success/', views.compte_cree_success_view, name='compte_cree_success'),
    path('comptes/<uuid:user_id>/modifier/', views.modifier_compte_view, name='modifier_compte'),
    path('comptes/<uuid:user_id>/toggle-status/', views.toggle_compte_status, name='toggle_compte_status'),
    path('comptes/<uuid:user_id>/reset-password/', views.reset_compte_password, name='reset_compte_password'),
    
    # Anciennes URLs pour compatibilité (à supprimer progressivement)
    path('utilisateurs/', views.gestion_utilisateurs_view, name='gestion_utilisateurs'),
    path('utilisateurs/creer/', views.creer_utilisateur_moderne_view, name='creer_utilisateur'),
    path('utilisateurs/cree-success/', views.utilisateur_cree_success_view, name='utilisateur_cree_success'),
    path('utilisateurs/<uuid:user_id>/modifier/', views.modifier_utilisateur_view, name='modifier_utilisateur'),
    path('utilisateurs/<uuid:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('utilisateurs/<uuid:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    
    path('test-robustesse/', views.test_robustesse_view, name='test_robustesse'),
    
    # ============================================================================
    # NOUVELLES URLs - ARCHITECTURE ÉTAPES/MODULES/TÂCHES
    # ============================================================================
    
    # Gestion des étapes
    path('projets/<uuid:projet_id>/etapes/', views.gestion_etapes_view, name='gestion_etapes'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/', views.detail_etape_view, name='detail_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/activer/', views.activer_etape, name='activer_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/terminer/', views.terminer_etape, name='terminer_etape'),
    
    # Gestion des tâches d'étapes
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/', views.gestion_taches_etape_view, name='gestion_taches_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/creer/', views.creer_tache_etape_view, name='creer_tache_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/assigner/', views.assigner_tache_etape, name='assigner_tache_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/terminer/', views.terminer_tache_etape, name='terminer_tache_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/modifier/', views.modifier_tache_etape_view, name='modifier_tache_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/changer-statut/', views.changer_statut_tache_etape, name='changer_statut_tache_etape'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/progression/', views.mettre_a_jour_progression_tache, name='mettre_a_jour_progression_tache'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/commentaire/', views.ajouter_commentaire_tache, name='ajouter_commentaire_tache'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/historique/', views.historique_tache_view, name='historique_tache'),
    
    # Gestion des tâches pour les membres
    path('projets/<uuid:projet_id>/mes-taches/', views.mes_taches_view, name='mes_taches'),
    path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/terminer/<str:type_tache>/', views.terminer_tache_view, name='terminer_tache'),
    path('projets/<uuid:projet_id>/taches/<uuid:tache_id>/changer-statut/<str:type_tache>/', views.changer_statut_ma_tache_view, name='changer_statut_ma_tache'),
    
    # Notifications
    path('notifications/taches/', views.notifications_taches_view, name='notifications_taches'),
    # path('notifications/utilisateur/', views.notifications_utilisateur_view, name='notifications_utilisateur'),
    path('notifications/<int:notification_id>/lue/', views.marquer_notification_lue, name='marquer_notification_lue'),
    
    # Gestion des modules
    path('projets/<uuid:projet_id>/modules/', views.gestion_modules_view, name='gestion_modules'),
    path('projets/<uuid:projet_id>/modules/creer/', views.creer_module_view, name='creer_module'),
    path('projets/<uuid:projet_id>/modules/<uuid:module_id>/', views.detail_module_view, name='detail_module'),
    path('projets/<uuid:projet_id>/modules/<uuid:module_id>/modifier/', views.modifier_module_view, name='modifier_module'),
    
    # Gestion des tâches
    path('modules/<uuid:module_id>/taches/', views.gestion_taches_view, name='gestion_taches'),
    path('modules/<uuid:module_id>/taches/creer/', views.creer_tache_view, name='creer_tache'),
    path('modules/<uuid:module_id>/taches/<uuid:tache_id>/', views.detail_tache_view, name='detail_tache'),
    path('modules/<uuid:module_id>/taches/<uuid:tache_id>/modifier/', views.modifier_tache_view, name='modifier_tache'),
    path('modules/<uuid:module_id>/taches/<uuid:tache_id>/assigner/', views.assigner_tache, name='assigner_tache'),
    
    # API Endpoints pour les notifications
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/detailed/', views.api_notifications_detailed, name='api_notifications_detailed'),
    path('api/notifications/<int:notification_id>/mark-read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    
    # ============================================================================
    # PROFIL UTILISATEUR
    # ============================================================================
    path('profil/', views.profil_view, name='profil'),
    path('profil/modifier/', views.modifier_profil_view, name='modifier_profil'),
    path('profil/changer-mot-de-passe/', views.changer_mot_de_passe_view, name='changer_mot_de_passe'),
]