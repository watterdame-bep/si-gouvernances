from django.urls import path
from . import views
from . import views_affectation
from . import views_taches_module
from . import views_admin_profile
from . import views_tests
from . import views_deploiement
from . import views_deploiement

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
    
    # ============================================================================
    # SYSTÈME DE TESTS V1
    # ============================================================================
    
    # Gestion des tests
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/', views.gestion_tests_view, name='gestion_tests'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/creer/', views.creer_test_view, name='creer_test'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/<uuid:test_id>/executer/', views.executer_test_view, name='executer_test'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/tests/<uuid:test_id>/modifier/', views.modifier_test_view, name='modifier_test'),
    
    # Gestion des cas de test (CasTest) - Hiérarchie
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/', views_tests.gestion_cas_tests_tache_view, name='gestion_cas_tests_tache'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/creer/', views_tests.creer_cas_test_view, name='creer_cas_test'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/cas-tests/api/', views_tests.api_cas_tests_tache_view, name='api_cas_tests_tache'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/cas-tests/<uuid:cas_test_id>/executer/', views_tests.executer_cas_test_view, name='executer_cas_test'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/cas-tests/<uuid:cas_test_id>/details/', views_tests.details_cas_test_view, name='details_cas_test'),
    
    # Gestion des bugs
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/bugs/', views.gestion_bugs_view, name='gestion_bugs'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/bugs/creer/', views.creer_bug_view, name='creer_bug'),
    path('projets/<uuid:projet_id>/bugs/<uuid:bug_id>/assigner/', views.assigner_bug_view, name='assigner_bug'),
    path('projets/<uuid:projet_id>/bugs/<uuid:bug_id>/resoudre/', views.resoudre_bug_view, name='resoudre_bug'),
    path('projets/<uuid:projet_id>/bugs/<uuid:bug_id>/fermer/', views.fermer_bug_view, name='fermer_bug'),
    
    # Validation des tests
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/validation/', views.validation_test_view, name='validation_test'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/valider/', views.valider_etape_test_view, name='valider_etape_test'),
    
    # ============================================================================
    # SYSTÈME DE DÉPLOIEMENT V2 - Architecture hiérarchique
    # ============================================================================
    
    # Gestion des déploiements d'une tâche
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/deploiements/', views_deploiement.gestion_deploiements_tache_view, name='gestion_deploiements_tache'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/deploiements/creer/', views_deploiement.creer_deploiement_view, name='creer_deploiement'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/deploiements/<uuid:deploiement_id>/autoriser/', views_deploiement.autoriser_deploiement_view, name='autoriser_deploiement'),
    path('projets/<uuid:projet_id>/etapes/<uuid:etape_id>/taches/<uuid:tache_id>/deploiements/<uuid:deploiement_id>/executer/', views_deploiement.executer_deploiement_view, name='executer_deploiement'),
    
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
    path('projets/<uuid:projet_id>/modules/<int:module_id>/', views.detail_module_view, name='detail_module'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/modifier/', views.modifier_module_view, name='modifier_module'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/affecter-nouveau/', views_affectation.affecter_module_nouveau, name='affecter_module_nouveau'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/equipe/', views_affectation.get_equipe_module_view, name='get_equipe_module'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/retirer-membre/', views_affectation.retirer_membre_module_view, name='retirer_membre_module'),
    
    # Gestion des tâches
    path('modules/<int:module_id>/taches/', views.gestion_taches_view, name='gestion_taches'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/taches/', views_taches_module.gestion_taches_module_view, name='gestion_taches_module'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/taches/creer/', views_taches_module.creer_tache_module_nouvelle_view, name='creer_tache_module_nouvelle'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/taches/<int:tache_id>/assigner/', views_taches_module.assigner_tache_module_view, name='assigner_tache_module'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/taches/<int:tache_id>/statut/', views_taches_module.modifier_statut_tache_module_view, name='modifier_statut_tache_module'),
    path('modules/<int:module_id>/taches/creer/', views.creer_tache_view, name='creer_tache'),
    path('modules/<int:module_id>/taches/<int:tache_id>/', views.detail_tache_view, name='detail_tache'),
    path('modules/<int:module_id>/taches/<int:tache_id>/modifier/', views.modifier_tache_view, name='modifier_tache'),
    path('modules/<int:module_id>/taches/<int:tache_id>/assigner/', views.assigner_tache, name='assigner_tache'),
    
    # API Endpoints pour les notifications
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/detailed/', views.api_notifications_detailed, name='api_notifications_detailed'),
    path('api/notifications/<int:notification_id>/mark-read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    
    # API Endpoints pour l'intégration CasTest
    path('api/tache-etape/<uuid:tache_etape_id>/tache-test/', views.api_tache_etape_to_tache_test, name='api_tache_etape_to_tache_test'),
    path('api/tache-test/<uuid:tache_test_id>/cas-tests/', views.api_tache_test_cas_tests, name='api_tache_test_cas_tests'),
    
    # ============================================================================
    # PROFIL UTILISATEUR
    # ============================================================================
    path('profil/', views.profil_view, name='profil'),
    path('profil/modifier/', views.modifier_profil_view, name='modifier_profil'),
    path('profil/changer-mot-de-passe/', views.changer_mot_de_passe_view, name='changer_mot_de_passe'),
    path('profil/creer-membre/', views_admin_profile.creer_profil_membre_admin_view, name='creer_profil_membre_admin'),
    
    # Gestion des modules (Phase développement)
    path('projets/<uuid:projet_id>/mes-modules/', views.mes_modules_view, name='mes_modules'),
    path('projets/<uuid:projet_id>/modules/<int:module_id>/taches/creer/', views.creer_tache_module_view, name='creer_tache_module'),
    path('projets/<uuid:projet_id>/taches-module/<int:tache_id>/statut/', views.modifier_statut_tache_module_view, name='modifier_statut_tache_module'),
]