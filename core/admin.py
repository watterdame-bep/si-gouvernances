from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Role, StatutProjet, Projet, Affectation, ActionAudit


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'niveau_hierarchique', 'date_creation']
    list_filter = ['niveau_hierarchique']
    search_fields = ['nom', 'description']


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_superuser', 'statut_actif', 'date_creation']
    list_filter = ['is_superuser', 'statut_actif', 'date_creation']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations JCONSULT MY', {
            'fields': ('telephone', 'taux_horaire', 'statut_actif', 
                      'tentatives_connexion_echouees', 'compte_bloque_jusqu')
        }),
    )
    
    def get_queryset(self, request):
        """Afficher les affectations de l'utilisateur dans l'admin"""
        return super().get_queryset(request).prefetch_related('affectations__projet', 'affectations__role_sur_projet')


@admin.register(StatutProjet)
class StatutProjetAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'couleur_affichage', 'ordre_affichage']
    list_editable = ['ordre_affichage']
    ordering = ['ordre_affichage']


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ['nom', 'client', 'budget_previsionnel', 'statut', 'priorite', 'get_responsable', 'date_creation']
    list_filter = ['statut', 'priorite', 'date_creation']
    search_fields = ['nom', 'client', 'description']
    readonly_fields = ['id', 'date_creation', 'date_modification']
    
    def get_responsable(self, obj):
        responsable = obj.get_responsable_principal()
        return responsable.get_full_name() if responsable else "Non affecté"
    get_responsable.short_description = "Responsable"


@admin.register(Affectation)
class AffectationAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'projet', 'role_sur_projet', 'est_responsable_principal', 'pourcentage_temps', 'date_debut']
    list_filter = ['role_sur_projet', 'est_responsable_principal', 'date_debut']
    search_fields = ['utilisateur__username', 'projet__nom']


@admin.register(ActionAudit)
class ActionAuditAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'utilisateur', 'type_action', 'projet', 'adresse_ip']
    list_filter = ['type_action', 'timestamp']
    search_fields = ['utilisateur__username', 'description', 'adresse_ip']
    readonly_fields = ['id', 'timestamp', 'hash_integrite']
    
    def has_add_permission(self, request):
        return False  # Empêche l'ajout manuel d'entrées d'audit
    
    def has_change_permission(self, request, obj=None):
        return False  # Empêche la modification des entrées d'audit
    
    def has_delete_permission(self, request, obj=None):
        return False  # Empêche la suppression des entrées d'audit