from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class RoleSysteme(models.Model):
    """Rôles système pour la connexion et l'accès à l'interface"""
    DEVELOPPEUR = 'DEVELOPPEUR'
    CHEF_PROJET = 'CHEF_PROJET'
    QA = 'QA'
    DIRECTION = 'DIRECTION'
    
    ROLE_CHOICES = [
        (DEVELOPPEUR, 'Développeur'),
        (CHEF_PROJET, 'Chef de Projet'),
        (QA, 'Quality Assurance'),
        (DIRECTION, 'Direction'),
    ]
    
    nom = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    niveau_hierarchique = models.IntegerField(default=1)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rôle Système"
        verbose_name_plural = "Rôles Système"
        ordering = ['niveau_hierarchique']
    
    def __str__(self):
        return self.get_nom_display()


class RoleProjet(models.Model):
    """Rôles spécifiques aux projets pour les affectations"""
    RESPONSABLE_PRINCIPAL = 'RESPONSABLE_PRINCIPAL'
    MEMBRE = 'MEMBRE'
    
    ROLE_CHOICES = [
        (RESPONSABLE_PRINCIPAL, 'Responsable Principal'),
        (MEMBRE, 'Membre'),
    ]
    
    nom = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rôle Projet"
        verbose_name_plural = "Rôles Projet"
    
    def __str__(self):
        return self.get_nom_display()


class Membre(models.Model):
    """Profil RH - Informations personnelles et professionnelles indépendantes du compte système"""
    NIVEAU_EXPERIENCE_CHOICES = [
        ('JUNIOR', 'Junior (0-2 ans)'),
        ('INTERMEDIAIRE', 'Intermédiaire (2-5 ans)'),
        ('SENIOR', 'Senior (5-10 ans)'),
        ('EXPERT', 'Expert (10+ ans)'),
    ]
    
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('INACTIF', 'Inactif'),
        ('EN_CONGE', 'En congé'),
        ('SUSPENDU', 'Suspendu'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom de famille")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    email_personnel = models.EmailField(unique=True, verbose_name="Email personnel")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    telephone_urgence = models.CharField(max_length=20, blank=True, verbose_name="Téléphone d'urgence")
    
    # Adresse (simplifiée et obligatoire)
    adresse = models.CharField(max_length=300, verbose_name="Adresse complète", 
                              help_text="Adresse complète (rue, ville)")
    
    # Informations professionnelles
    poste = models.CharField(max_length=200, blank=True, verbose_name="Poste/Fonction")
    departement = models.CharField(max_length=100, blank=True, verbose_name="Département")
    niveau_experience = models.CharField(max_length=20, choices=NIVEAU_EXPERIENCE_CHOICES, blank=True, verbose_name="Niveau d'expérience")
    
    # Compétences et spécialités
    competences_techniques = models.TextField(blank=True, verbose_name="Compétences techniques", 
                                            help_text="Stack technique, langages, frameworks, outils...")
    specialites = models.TextField(blank=True, verbose_name="Spécialités", 
                                 help_text="Domaines d'expertise, certifications...")
    
    # Statut et dates
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF', verbose_name="Statut")
    date_embauche = models.DateField(null=True, blank=True, verbose_name="Date d'embauche")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création du profil")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    # Métadonnées
    createur = models.ForeignKey('Utilisateur', on_delete=models.PROTECT, related_name='membres_crees', 
                                null=True, blank=True, verbose_name="Créé par")
    
    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['nom', 'prenom']),
            models.Index(fields=['email_personnel']),
            models.Index(fields=['statut']),
        ]
    
    def clean(self):
        """Validation des données membre"""
        if self.email_personnel and Membre.objects.filter(email_personnel=self.email_personnel).exclude(pk=self.pk).exists():
            raise ValidationError({'email_personnel': 'Cet email est déjà utilisé.'})
        
        if not self.adresse:
            raise ValidationError({'adresse': 'L\'adresse est obligatoire.'})
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def get_nom_complet(self):
        """Retourne le nom complet"""
        return f"{self.prenom} {self.nom}"
    
    def get_initiales(self):
        """Retourne les initiales"""
        return f"{self.prenom[0].upper()}{self.nom[0].upper()}" if self.prenom and self.nom else "??"
    
    def get_adresse_complete(self):
        """Retourne l'adresse complète"""
        return self.adresse
    
    def a_compte_utilisateur(self):
        """Vérifie si le membre a un compte utilisateur associé"""
        return hasattr(self, 'compte_utilisateur') and self.compte_utilisateur is not None
    
    def get_compte_utilisateur(self):
        """Retourne le compte utilisateur associé s'il existe"""
        return getattr(self, 'compte_utilisateur', None)
    
    def peut_avoir_compte(self):
        """Vérifie si le membre peut avoir un compte utilisateur"""
        return self.statut in ['ACTIF', 'EN_CONGE'] and self.email_personnel


# Ancien modèle Role gardé pour compatibilité temporaire - sera supprimé après migration
class Role(models.Model):
    """Définition des rôles organisationnels - DEPRECATED"""
    DIRECTION = 'DIRECTION'
    CHEF_PROJET = 'CHEF_PROJET'
    DEVELOPPEUR = 'DEVELOPPEUR'
    QA = 'QA'
    FINANCE = 'FINANCE'
    SECURITE = 'SECURITE'
    
    ROLE_CHOICES = [
        (DIRECTION, 'Direction'),
        (CHEF_PROJET, 'Chef de Projet'),
        (DEVELOPPEUR, 'Développeur'),
        (QA, 'Quality Assurance'),
        (FINANCE, 'Finance'),
        (SECURITE, 'Sécurité'),
    ]
    
    nom = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField()
    niveau_hierarchique = models.IntegerField(default=1)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Rôle (Deprecated)"
        verbose_name_plural = "Rôles (Deprecated)"
    
    def __str__(self):
        return self.get_nom_display()


class Utilisateur(AbstractUser):
    """Compte utilisateur système lié à un profil membre"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers le profil membre (RH)
    membre = models.OneToOneField('Membre', on_delete=models.CASCADE, related_name='compte_utilisateur', 
                                 null=True, blank=True, verbose_name="Profil membre")
    
    # Informations système
    role_systeme = models.ForeignKey('RoleSysteme', on_delete=models.PROTECT, null=True, blank=True, 
                                   verbose_name="Rôle système")
    statut_actif = models.BooleanField(default=True, verbose_name="Compte actif")
    
    # Sécurité et connexion
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création du compte")
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    tentatives_connexion_echouees = models.IntegerField(default=0)
    compte_bloque_jusqu = models.DateTimeField(null=True, blank=True)
    
    # Champs hérités conservés pour compatibilité temporaire
    telephone = models.CharField(max_length=20, blank=True, help_text="DEPRECATED - Utiliser membre.telephone")
    taux_horaire = models.DecimalField(max_digits=8, decimal_places=2, default=0, 
                                     help_text="DEPRECATED - Utiliser membre.taux_horaire")
    
    class Meta:
        verbose_name = "Compte Utilisateur"
        verbose_name_plural = "Comptes Utilisateur"
    
    def clean(self):
        """Validation des données utilisateur"""
        if self.email and Utilisateur.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({'email': 'Cet email est déjà utilisé.'})
        
        # Si un membre est associé, synchroniser certaines informations
        if self.membre:
            if not self.email and self.membre.email_personnel:
                self.email = self.membre.email_personnel
            if not self.first_name and self.membre.prenom:
                self.first_name = self.membre.prenom
            if not self.last_name and self.membre.nom:
                self.last_name = self.membre.nom
    
    def save(self, *args, **kwargs):
        """Synchronisation automatique avec le profil membre"""
        # Vérifier si on empêche la synchronisation automatique
        skip_sync = kwargs.pop('sync_from_membre', False)
        
        # Ne pas synchroniser si explicitement demandé (cas de mise à jour manuelle)
        if not skip_sync and self.membre:
            # Synchroniser automatiquement depuis le membre vers l'utilisateur
            # Ceci se produit lors de la création ou modification du membre
            if self.membre.email_personnel:
                self.email = self.membre.email_personnel
            if self.membre.prenom:
                self.first_name = self.membre.prenom
            if self.membre.nom:
                self.last_name = self.membre.nom
        
        super().save(*args, **kwargs)
    
    def est_compte_bloque(self):
        """Vérifie si le compte est temporairement bloqué"""
        if self.compte_bloque_jusqu:
            return timezone.now() < self.compte_bloque_jusqu
        return False
    
    def bloquer_compte(self, duree_minutes=30):
        """Bloque le compte temporairement"""
        self.compte_bloque_jusqu = timezone.now() + timezone.timedelta(minutes=duree_minutes)
        self.save()
    
    def reinitialiser_tentatives(self):
        """Remet à zéro les tentatives de connexion"""
        self.tentatives_connexion_echouees = 0
        self.compte_bloque_jusqu = None
        self.save()
    
    def est_super_admin(self):
        """Vérifie si l'utilisateur est super admin système"""
        return self.is_superuser
    
    def get_roles_par_projet(self):
        """Retourne un dictionnaire des rôles par projet"""
        affectations = self.affectations.filter(date_fin__isnull=True).select_related('projet', 'role_projet')
        return {aff.projet: aff.role_projet for aff in affectations}
    
    def get_role_sur_projet(self, projet):
        """Retourne le rôle de l'utilisateur sur un projet spécifique"""
        affectation = self.affectations.filter(projet=projet, date_fin__isnull=True).first()
        return affectation.role_projet if affectation else None
    
    def a_acces_projet(self, projet):
        """Vérifie si l'utilisateur a accès à un projet"""
        return self.est_super_admin() or self.affectations.filter(projet=projet, date_fin__isnull=True).exists()
    
    def get_role_systeme_display(self):
        """Retourne le nom d'affichage du rôle système"""
        if self.is_superuser:
            return "Super Admin"
        elif self.role_systeme:
            return self.role_systeme.get_nom_display()
        else:
            return "Aucun rôle"
    
    def get_profil_membre(self):
        """Retourne le profil membre associé"""
        return self.membre
    
    def get_nom_complet_from_membre(self):
        """Retourne le nom complet depuis le profil membre"""
        if self.membre:
            return self.membre.get_nom_complet()
        return self.get_full_name()
    
    def get_telephone_from_membre(self):
        """Retourne le téléphone depuis le profil membre"""
        if self.membre and self.membre.telephone:
            return self.membre.telephone
        return self.telephone  # Fallback sur l'ancien champ
    
    def get_taux_horaire_from_membre(self):
        """Retourne le taux horaire depuis le profil membre"""
        if self.membre:
            return self.membre.taux_horaire
        return self.taux_horaire  # Fallback sur l'ancien champ


class StatutProjet(models.Model):
    """États possibles d'un projet dans son cycle de vie"""
    IDEE = 'IDEE'
    AFFECTE = 'AFFECTE'
    PLANIFIE = 'PLANIFIE'
    EN_COURS = 'EN_COURS'
    SUSPENDU = 'SUSPENDU'
    TERMINE = 'TERMINE'
    ARCHIVE = 'ARCHIVE'
    
    STATUT_CHOICES = [
        (IDEE, 'Idée'),
        (AFFECTE, 'Affecté'),
        (PLANIFIE, 'Planifié'),
        (EN_COURS, 'En cours'),
        (SUSPENDU, 'Suspendu'),
        (TERMINE, 'Terminé'),
        (ARCHIVE, 'Archivé'),
    ]
    
    nom = models.CharField(max_length=20, choices=STATUT_CHOICES, unique=True)
    description = models.TextField()
    couleur_affichage = models.CharField(max_length=7, default='#6B7280')  # Couleur hex
    ordre_affichage = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Statut de Projet"
        verbose_name_plural = "Statuts de Projet"
        ordering = ['ordre_affichage']
    
    def __str__(self):
        return self.get_nom_display()


class Projet(models.Model):
    """Entité centrale représentant un projet de JCONSULT MY"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    client = models.CharField(max_length=200)
    budget_previsionnel = models.DecimalField(max_digits=12, decimal_places=2)
    devise = models.CharField(max_length=3, default='EUR')
    statut = models.ForeignKey(StatutProjet, on_delete=models.PROTECT, related_name='projets')
    priorite = models.CharField(
        max_length=20,
        choices=[
            ('BASSE', 'Basse'),
            ('MOYENNE', 'Moyenne'),
            ('HAUTE', 'Haute'),
            ('CRITIQUE', 'Critique'),
        ],
        default='MOYENNE'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='projets_crees')
    commentaires = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']
    
    def clean(self):
        """Validation des données projet"""
        if self.budget_previsionnel <= 0:
            raise ValidationError({'budget_previsionnel': 'Le budget doit être supérieur à 0.'})
        
        if self.nom and Projet.objects.filter(nom=self.nom).exclude(pk=self.pk).exists():
            raise ValidationError({'nom': 'Ce nom de projet existe déjà.'})
    
    def __str__(self):
        return f"{self.nom} ({self.client})"
    
    def get_responsable_principal(self):
        """Retourne le responsable principal du projet"""
        affectation = self.affectations.filter(est_responsable_principal=True, date_fin__isnull=True).first()
        if affectation:
            try:
                return affectation.utilisateur
            except:
                # Si l'utilisateur n'existe plus, supprimer l'affectation invalide
                affectation.delete()
                return None
        return None
    
    def get_equipe(self):
        """Retourne tous les membres de l'équipe"""
        equipe = []
        for aff in self.affectations.filter(date_fin__isnull=True):
            try:
                equipe.append(aff.utilisateur)
            except:
                # Si l'utilisateur n'existe plus, supprimer l'affectation invalide
                aff.delete()
        return equipe
    
    def initialiser_etapes_standard(self, utilisateur):
        """Initialise les étapes standard du projet (évite les doublons)"""
        from .models import TypeEtape, EtapeProjet
        
        # Vérifier si le projet a déjà toutes les étapes standard
        types_etapes = TypeEtape.objects.all().order_by('ordre_standard')
        etapes_existantes = self.etapes.values_list('type_etape_id', flat=True)
        
        etapes_creees = 0
        for i, type_etape in enumerate(types_etapes, 1):
            # Créer seulement si l'étape n'existe pas déjà
            if type_etape.id not in etapes_existantes:
                EtapeProjet.objects.create(
                    projet=self,
                    type_etape=type_etape,
                    ordre=i,
                    statut='A_VENIR' if i > 1 else 'EN_COURS',  # Première étape active
                    createur=utilisateur
                )
                etapes_creees += 1
        
        # Audit seulement si des étapes ont été créées
        if etapes_creees > 0:
            from .utils import enregistrer_audit
            enregistrer_audit(
                utilisateur=utilisateur,
                type_action='CREATION_ETAPE',
                description=f'Initialisation de {etapes_creees} étapes standard pour le projet {self.nom}',
                projet=self,
                donnees_apres={
                    'etapes_creees': etapes_creees,
                    'total_etapes': self.etapes.count(),
                    'types_ajoutes': [t.nom for t in types_etapes if t.id not in etapes_existantes]
                }
            )
        
        return etapes_creees
    
    def get_etape_courante(self):
        """Retourne l'étape actuellement en cours"""
        return self.etapes.filter(statut='EN_COURS').first()
    
    def get_timeline_etapes(self):
        """Retourne les étapes organisées par statut pour la timeline"""
        etapes = self.etapes.all().order_by('ordre')
        return {
            'passees': etapes.filter(statut='TERMINEE'),
            'courante': etapes.filter(statut='EN_COURS').first(),
            'futures': etapes.filter(statut='A_VENIR')
        }


class Affectation(models.Model):
    """Relation entre un utilisateur et un projet avec un rôle spécifique au projet"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='affectations')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='affectations')
    role_projet = models.ForeignKey('RoleProjet', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Rôle sur le projet")
    est_responsable_principal = models.BooleanField(default=False)
    pourcentage_temps = models.IntegerField(default=100)  # Pourcentage de temps alloué
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notes sur l'affectation")
    
    # Champ temporaire pour compatibilité - sera supprimé après migration
    role_sur_projet = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True, verbose_name="Rôle sur le projet (deprecated)")
    
    class Meta:
        verbose_name = "Affectation"
        verbose_name_plural = "Affectations"
        unique_together = ['utilisateur', 'projet', 'date_fin']  # Un utilisateur ne peut avoir qu'une affectation active par projet
        indexes = [
            models.Index(fields=['utilisateur', 'projet', 'date_fin']),
            models.Index(fields=['projet', 'date_fin']),
        ]
    
    def clean(self):
        """Validation des règles d'affectation"""
        # Vérifier qu'il n'y a qu'un seul responsable principal par projet
        if self.est_responsable_principal:
            autres_responsables = Affectation.objects.filter(
                projet=self.projet,
                est_responsable_principal=True,
                date_fin__isnull=True
            ).exclude(pk=self.pk)
            
            if autres_responsables.exists():
                raise ValidationError('Un projet ne peut avoir qu\'un seul responsable principal.')
        
        # Vérifier que l'utilisateur est actif
        if not self.utilisateur.statut_actif:
            raise ValidationError('Impossible d\'affecter un utilisateur inactif.')
        
        # Vérifier qu'il n'y a pas déjà une affectation active pour ce couple utilisateur/projet
        if self.date_fin is None:
            affectation_existante = Affectation.objects.filter(
                utilisateur=self.utilisateur,
                projet=self.projet,
                date_fin__isnull=True
            ).exclude(pk=self.pk)
            
            if affectation_existante.exists():
                raise ValidationError('Cet utilisateur a déjà une affectation active sur ce projet.')
    
    def __str__(self):
        role_str = " (Responsable)" if self.est_responsable_principal else ""
        role_display = self.role_projet.get_nom_display() if self.role_projet else (self.role_sur_projet.get_nom_display() if self.role_sur_projet else "Aucun rôle")
        return f"{self.utilisateur.get_full_name()} → {self.projet.nom} ({role_display}){role_str}"
    
    def terminer_affectation(self):
        """Termine l'affectation en définissant la date de fin"""
        self.date_fin = timezone.now()
        self.save()


class ActionAudit(models.Model):
    """Journal d'audit pour la traçabilité complète des actions"""
    TYPE_ACTIONS = [
        ('CONNEXION', 'Connexion'),
        ('DECONNEXION', 'Déconnexion'),
        ('TENTATIVE_CONNEXION_ECHOUEE', 'Tentative de connexion échouée'),
        ('CREATION_PROJET', 'Création de projet'),
        ('MODIFICATION_PROJET', 'Modification de projet'),
        ('MODIFICATION_BUDGET', 'Modification de budget'),
        ('CHANGEMENT_STATUT', 'Changement de statut'),
        ('AFFECTATION_UTILISATEUR', 'Affectation d\'utilisateur'),
        ('RETRAIT_UTILISATEUR', 'Retrait d\'utilisateur'),
        ('MODIFICATION_ROLE', 'Modification de rôle'),
        ('CHANGEMENT_RESPONSABLE', 'Changement de responsable'),
        ('CONSULTATION_AUDIT', 'Consultation d\'audit'),
        ('CONSULTATION_PROFIL', 'Consultation de profil'),
        ('MODIFICATION_PROFIL', 'Modification de profil'),
        ('ACCES_REFUSE', 'Accès refusé'),
        ('ARCHIVAGE_PROJET', 'Archivage de projet'),
        ('CREATION_UTILISATEUR', 'Création d\'utilisateur'),
        ('MODIFICATION_UTILISATEUR', 'Modification d\'utilisateur'),
        ('DESACTIVATION_UTILISATEUR', 'Désactivation d\'utilisateur'),
        ('REACTIVATION_UTILISATEUR', 'Réactivation d\'utilisateur'),
        ('REINITIALISATION_MOT_PASSE', 'Réinitialisation de mot de passe'),
        ('CREATION_PROFIL_MEMBRE_ADMIN', 'Création de profil membre par admin'),
        # Nouveaux types pour l'architecture étapes/modules/tâches
        ('CREATION_ETAPE', 'Création d\'étape'),
        ('ACTIVATION_ETAPE', 'Activation d\'étape'),
        ('ACTIVATION_ETAPE_AUTOMATIQUE', 'Activation automatique d\'étape'),
        ('CLOTURE_ETAPE', 'Clôture d\'étape'),
        ('CREATION_MODULE', 'Création de module'),
        ('MODIFICATION_MODULE', 'Modification de module'),
        ('CREATION_TACHE', 'Création de tâche'),
        ('MODIFICATION_TACHE', 'Modification de tâche'),
        ('ASSIGNATION_TACHE', 'Assignation de tâche'),
        ('COMPLETION_TACHE', 'Completion de tâche'),
        ('CREATION_MODULE_TARDIVE', 'Création tardive de module'),
        ('ACTIVATION_MODULES_AUTOMATIQUE', 'Activation automatique des modules'),
        ('AFFECTATION_MODULE', 'Affectation de module'),
        ('RETRAIT_MODULE', 'Retrait de module'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='actions_audit')
    type_action = models.CharField(max_length=50, choices=TYPE_ACTIONS)
    projet = models.ForeignKey(Projet, on_delete=models.PROTECT, null=True, blank=True, related_name='actions_audit')
    description = models.TextField()
    donnees_avant = models.JSONField(null=True, blank=True)  # État avant modification
    donnees_apres = models.JSONField(null=True, blank=True)  # État après modification
    adresse_ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    hash_integrite = models.CharField(max_length=64)  # Hash SHA-256 pour l'intégrité
    
    class Meta:
        verbose_name = "Action d'Audit"
        verbose_name_plural = "Actions d'Audit"
        ordering = ['-timestamp']
    
    def save(self, *args, **kwargs):
        """Génère automatiquement le hash d'intégrité"""
        if not self.hash_integrite:
            import hashlib
            data_to_hash = f"{self.utilisateur.id}{self.type_action}{self.timestamp}{self.description}"
            self.hash_integrite = hashlib.sha256(data_to_hash.encode()).hexdigest()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.timestamp.strftime('%d/%m/%Y %H:%M')} - {self.utilisateur.get_full_name()} - {self.get_type_action_display()}"


# ============================================================================
# NOUVEAUX MODÈLES - ARCHITECTURE ÉTAPES/MODULES/TÂCHES
# ============================================================================

class TypeEtape(models.Model):
    """Types d'étapes standard pour les projets"""
    PLANIFICATION = 'PLANIFICATION'
    CONCEPTION = 'CONCEPTION'
    DEVELOPPEMENT = 'DEVELOPPEMENT'
    TESTS = 'TESTS'
    DEPLOIEMENT = 'DEPLOIEMENT'
    MAINTENANCE = 'MAINTENANCE'
    
    TYPE_CHOICES = [
        (PLANIFICATION, 'Planification'),
        (CONCEPTION, 'Conception'),
        (DEVELOPPEMENT, 'Développement'),
        (TESTS, 'Tests'),
        (DEPLOIEMENT, 'Déploiement'),
        (MAINTENANCE, 'Maintenance'),
    ]
    
    nom = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    description = models.TextField()
    ordre_standard = models.IntegerField(help_text="Ordre standard dans le cycle de vie")
    couleur = models.CharField(max_length=7, default="#3B82F6", help_text="Couleur hexadécimale pour l'affichage")
    icone_emoji = models.CharField(max_length=10, default="📋")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Type d'Étape"
        verbose_name_plural = "Types d'Étapes"
        ordering = ['ordre_standard']
    
    def __str__(self):
        return self.get_nom_display()


class EtapeProjet(models.Model):
    """Étapes temporelles d'un projet (logique de cycle de vie)"""
    STATUT_CHOICES = [
        ('A_VENIR', 'À venir'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='etapes')
    type_etape = models.ForeignKey(TypeEtape, on_delete=models.PROTECT)
    ordre = models.IntegerField(help_text="Ordre dans ce projet spécifique")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_VENIR')
    
    # Dates prévisionnelles
    date_debut_prevue = models.DateField(null=True, blank=True)
    date_fin_prevue = models.DateField(null=True, blank=True)
    
    # Dates réelles
    date_debut_reelle = models.DateTimeField(null=True, blank=True)
    date_fin_reelle = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='etapes_creees')
    
    # Commentaires et notes
    commentaires = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Étape de Projet"
        verbose_name_plural = "Étapes de Projet"
        ordering = ['projet', 'ordre']
        unique_together = [['projet', 'ordre'], ['projet', 'type_etape']]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_debut_prevue__lte=models.F('date_fin_prevue')),
                name='etape_dates_prevues_coherentes'
            ),
        ]
    
    def clean(self):
        """Validation métier"""
        # Une seule étape EN_COURS par projet
        if self.statut == 'EN_COURS':
            autres_en_cours = EtapeProjet.objects.filter(
                projet=self.projet, 
                statut='EN_COURS'
            ).exclude(pk=self.pk)
            
            if autres_en_cours.exists():
                raise ValidationError('Une seule étape peut être en cours à la fois pour un projet.')
        
        # Vérifier l'ordre logique des statuts
        if self.statut == 'TERMINEE':
            etapes_precedentes = EtapeProjet.objects.filter(
                projet=self.projet,
                ordre__lt=self.ordre
            ).exclude(statut='TERMINEE')
            
            if etapes_precedentes.exists():
                raise ValidationError('Impossible de terminer cette étape tant que les étapes précédentes ne sont pas terminées.')
    
    def __str__(self):
        return f"{self.projet.nom} - {self.type_etape.get_nom_display()} ({self.get_statut_display()})"
    
    def activer_etape(self, utilisateur):
        """Active cette étape (passe en EN_COURS)"""
        if self.statut != 'A_VENIR':
            raise ValidationError('Seules les étapes à venir peuvent être activées.')
        
        # Désactiver l'étape actuellement en cours
        etape_courante = EtapeProjet.objects.filter(
            projet=self.projet, 
            statut='EN_COURS'
        ).first()
        
        if etape_courante:
            etape_courante.statut = 'TERMINEE'
            etape_courante.date_fin_reelle = timezone.now()
            etape_courante.save()
        
        # Activer cette étape
        self.statut = 'EN_COURS'
        self.date_debut_reelle = timezone.now()
        self.save()
        
        # Audit
        from .utils import enregistrer_audit
        enregistrer_audit(
            utilisateur=utilisateur,
            type_action='ACTIVATION_ETAPE',
            description=f'Activation de l\'étape {self.type_etape.get_nom_display()}',
            projet=self.projet,
            donnees_apres={
                'etape': self.type_etape.nom,
                'ordre': self.ordre,
                'date_activation': self.date_debut_reelle.isoformat()
            }
        )
    
    def terminer_etape(self, utilisateur):
        """Termine cette étape et active automatiquement la suivante"""
        if self.statut != 'EN_COURS':
            raise ValidationError('Seules les étapes en cours peuvent être terminées.')
        
        # Vérifier que toutes les tâches de l'étape sont terminées
        taches_non_terminees = self.taches_etape.exclude(statut='TERMINEE')
        if taches_non_terminees.exists():
            noms_taches = list(taches_non_terminees.values_list('nom', flat=True))
            raise ValidationError(
                f'Impossible de terminer l\'étape. Les tâches suivantes ne sont pas terminées : {", ".join(noms_taches)}'
            )
        
        # Récupérer l'étape suivante avant de terminer celle-ci
        etape_suivante = self.get_etape_suivante()
        
        self.statut = 'TERMINEE'
        self.date_fin_reelle = timezone.now()
        self.save()
        
        # Audit de clôture
        from .utils import enregistrer_audit, envoyer_notification_etape_terminee
        enregistrer_audit(
            utilisateur=utilisateur,
            type_action='CLOTURE_ETAPE',
            description=f'Clôture de l\'étape {self.type_etape.get_nom_display()}',
            projet=self.projet,
            donnees_apres={
                'etape': self.type_etape.nom,
                'ordre': self.ordre,
                'date_cloture': self.date_fin_reelle.isoformat(),
                'etape_suivante': etape_suivante.type_etape.nom if etape_suivante else None
            }
        )
        
        # Envoyer les notifications par email aux administrateurs et chefs de projet
        try:
            resultat_notification = envoyer_notification_etape_terminee(self, utilisateur)
            if resultat_notification.get('success'):
                print(f"Notifications envoyées : {resultat_notification.get('emails_envoyes')}/{resultat_notification.get('total_destinataires')}")
        except Exception as e:
            print(f"Erreur lors de l'envoi des notifications : {e}")
        
        # Activer automatiquement l'étape suivante si elle existe
        if etape_suivante and etape_suivante.statut == 'A_VENIR':
            etape_suivante.statut = 'EN_COURS'
            etape_suivante.date_debut_reelle = timezone.now()
            etape_suivante.save()
            
            # Audit d'activation automatique
            enregistrer_audit(
                utilisateur=utilisateur,
                type_action='ACTIVATION_ETAPE_AUTOMATIQUE',
                description=f'Activation automatique de l\'étape {etape_suivante.type_etape.get_nom_display()} après clôture de {self.type_etape.get_nom_display()}',
                projet=self.projet,
                donnees_apres={
                    'etape_precedente': self.type_etape.nom,
                    'etape_activee': etape_suivante.type_etape.nom,
                    'ordre': etape_suivante.ordre,
                    'date_activation': etape_suivante.date_debut_reelle.isoformat()
                }
            )
            
            # Si l'étape suivante est DEVELOPPEMENT, activer automatiquement la création de modules
            if etape_suivante.type_etape.nom == 'DEVELOPPEMENT':
                # Audit spécial pour l'activation des modules
                enregistrer_audit(
                    utilisateur=utilisateur,
                    type_action='ACTIVATION_MODULES_AUTOMATIQUE',
                    description=f'Activation automatique de la création de modules pour l\'étape développement du projet {self.projet.nom}',
                    projet=self.projet,
                    donnees_apres={
                        'etape_developpement': etape_suivante.type_etape.nom,
                        'modules_actives': True,
                        'date_activation': etape_suivante.date_debut_reelle.isoformat()
                    }
                )
            
            return etape_suivante  # Retourner l'étape activée
        
        return None  # Aucune étape suivante
    
    def get_etape_suivante(self):
        """Retourne l'étape suivante dans l'ordre"""
        return EtapeProjet.objects.filter(
            projet=self.projet,
            ordre__gt=self.ordre
        ).first()
    
    def peut_creer_modules_librement(self):
        """Vérifie si on peut créer des modules librement dans cette étape"""
        return self.type_etape.nom == 'DEVELOPPEMENT'
    
    def a_taches_speciales(self):
        """Vérifie si cette étape a des tâches ajoutées après clôture"""
        return self.taches_etape.filter(ajoutee_apres_cloture=True).exists()
    
    def get_nombre_taches_speciales(self):
        """Retourne le nombre de tâches spéciales dans cette étape"""
        return self.taches_etape.filter(ajoutee_apres_cloture=True).count()


class ModuleProjet(models.Model):
    """Modules fonctionnels d'un projet (logique de structure produit)"""
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='modules')
    nom = models.CharField(max_length=100)
    description = models.TextField()
    
    # Traçabilité de création
    etape_creation = models.ForeignKey(EtapeProjet, on_delete=models.PROTECT, related_name='modules_crees')
    date_creation = models.DateTimeField(auto_now_add=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='modules_crees')
    
    # Métadonnées
    date_modification = models.DateTimeField(auto_now=True)
    couleur = models.CharField(max_length=7, default="#10B981", help_text="Couleur hexadécimale")
    icone_emoji = models.CharField(max_length=10, default="🧩")
    
    # Justification pour création tardive
    justification_creation_tardive = models.TextField(
        blank=True,
        help_text="Justification si créé après la phase de conception"
    )
    
    class Meta:
        verbose_name = "Module de Projet"
        verbose_name_plural = "Modules de Projet"
        ordering = ['projet', 'date_creation']
        unique_together = [['projet', 'nom']]
    
    def clean(self):
        """Validation métier"""
        if self.nom and ModuleProjet.objects.filter(
            projet=self.projet, 
            nom=self.nom
        ).exclude(pk=self.pk).exists():
            raise ValidationError({'nom': 'Ce nom de module existe déjà pour ce projet.'})
    
    def __str__(self):
        return f"{self.projet.nom} - {self.nom}"
    
    def est_creation_tardive(self):
        """Vérifie si le module a été créé après la phase de conception"""
        return not self.etape_creation.peut_creer_modules_librement()
    
    def get_progression_taches(self):
        """Calcule la progression des tâches du module"""
        taches = self.taches.all()
        if not taches:
            return 0
        
        taches_terminees = taches.filter(statut='TERMINEE').count()
        return round((taches_terminees / taches.count()) * 100)


class AffectationModule(models.Model):
    """Affectation d'un module à un ou plusieurs membres de l'équipe"""
    module = models.ForeignKey(ModuleProjet, on_delete=models.CASCADE, related_name='affectations')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='modules_affectes')
    
    # Rôle sur le module
    ROLE_MODULE_CHOICES = [
        ('RESPONSABLE', 'Responsable'),
        ('CONTRIBUTEUR', 'Contributeur'),
        ('CONSULTANT', 'Consultant'),
    ]
    role_module = models.CharField(max_length=20, choices=ROLE_MODULE_CHOICES, default='CONTRIBUTEUR')
    
    # Métadonnées
    date_affectation = models.DateTimeField(auto_now_add=True)
    date_fin_affectation = models.DateTimeField(null=True, blank=True)
    affecte_par = models.ForeignKey(
        Utilisateur, 
        on_delete=models.PROTECT, 
        related_name='affectations_modules_creees'
    )
    
    # Permissions spécifiques
    peut_creer_taches = models.BooleanField(default=True, help_text="Peut créer des tâches dans ce module")
    peut_voir_toutes_taches = models.BooleanField(default=False, help_text="Peut voir toutes les tâches du module")
    
    class Meta:
        verbose_name = "Affectation de Module"
        verbose_name_plural = "Affectations de Module"
        unique_together = [['module', 'utilisateur', 'date_fin_affectation']]
        ordering = ['module', 'role_module', 'date_affectation']
    
    def clean(self):
        """Validation métier"""
        # Vérifier que l'utilisateur fait partie de l'équipe du projet
        if not self.module.projet.affectations.filter(
            utilisateur=self.utilisateur,
            date_fin__isnull=True
        ).exists():
            raise ValidationError({
                'utilisateur': 'L\'utilisateur doit faire partie de l\'équipe du projet.'
            })
        
        # Vérifier qu'il n'y a pas déjà une affectation active
        if self.date_fin_affectation is None:
            affectation_existante = AffectationModule.objects.filter(
                module=self.module,
                utilisateur=self.utilisateur,
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk)
            
            if affectation_existante.exists():
                raise ValidationError('Cet utilisateur a déjà une affectation active sur ce module.')
        
        # Vérifier qu'il n'y a qu'un seul responsable par module
        if self.role_module == 'RESPONSABLE' and self.date_fin_affectation is None:
            responsable_existant = AffectationModule.objects.filter(
                module=self.module,
                role_module='RESPONSABLE',
                date_fin_affectation__isnull=True
            ).exclude(pk=self.pk)
            
            if responsable_existant.exists():
                responsable = responsable_existant.first()
                raise ValidationError({
                    'role_module': f'Le module a déjà un responsable : {responsable.utilisateur.get_full_name()}. Un seul responsable par module est autorisé.'
                })
    
    def __str__(self):
        return f"{self.utilisateur.get_full_name()} → {self.module.nom} ({self.get_role_module_display()})"
    
    def est_active(self):
        """Vérifie si l'affectation est active"""
        return self.date_fin_affectation is None
    
    def terminer_affectation(self):
        """Termine l'affectation"""
        self.date_fin_affectation = timezone.now()
        self.save()


class TacheModule(models.Model):
    """Tâches d'un module"""
    STATUT_CHOICES = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('BLOQUEE', 'Bloquée'),
    ]
    
    module = models.ForeignKey(ModuleProjet, on_delete=models.CASCADE, related_name='taches')
    nom = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignation
    responsable = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='taches_assignees'
    )
    
    # Visibilité des tâches
    est_privee = models.BooleanField(
        default=True, 
        help_text="Si True, seul le créateur peut voir cette tâche"
    )
    visible_par = models.ManyToManyField(
        Utilisateur,
        blank=True,
        related_name='taches_visibles',
        help_text="Utilisateurs autorisés à voir cette tâche (en plus du créateur)"
    )
    
    # Planification
    duree_estimee = models.DurationField(null=True, blank=True, help_text="Durée estimée en heures")
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    # Statut
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_FAIRE')
    
    # Étape d'exécution
    etape_execution = models.ForeignKey(
        EtapeProjet, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Étape du projet où cette tâche sera exécutée"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='taches_creees')
    
    # Suivi
    commentaires = models.TextField(blank=True)
    raison_blocage = models.TextField(blank=True, help_text="Raison du blocage si statut = BLOQUEE")
    
    class Meta:
        verbose_name = "Tâche de Module"
        verbose_name_plural = "Tâches de Module"
        ordering = ['module', 'date_creation']
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_debut__lte=models.F('date_fin')),
                name='tache_dates_coherentes'
            ),
        ]
    
    def clean(self):
        """Validation métier"""
        # Vérifier que le responsable fait partie de l'équipe du projet
        if self.responsable:
            if not self.module.projet.affectations.filter(
                utilisateur=self.responsable,
                date_fin__isnull=True
            ).exists():
                raise ValidationError({
                    'responsable': 'Le responsable doit faire partie de l\'équipe du projet.'
                })
        
        # Vérifier que l'étape d'exécution appartient au même projet
        if self.etape_execution:
            if self.etape_execution.projet != self.module.projet:
                raise ValidationError({
                    'etape_execution': 'L\'étape d\'exécution doit appartenir au même projet.'
                })
    
    def __str__(self):
        return f"{self.module.nom} - {self.nom}"
    
    def peut_etre_executee(self):
        """Vérifie si la tâche peut être exécutée selon l'étape actuelle du projet"""
        if not self.etape_execution:
            return True  # Pas de contrainte d'étape
        
        etape_courante = EtapeProjet.objects.filter(
            projet=self.module.projet,
            statut='EN_COURS'
        ).first()
        
        if not etape_courante:
            return False  # Aucune étape active
        
        return etape_courante.ordre >= self.etape_execution.ordre
    
    def peut_voir_tache(self, utilisateur):
        """Vérifie si un utilisateur peut voir cette tâche"""
        # Le créateur peut toujours voir sa tâche
        if self.createur == utilisateur:
            return True
        
        # Si la tâche n'est pas privée, tous les membres du projet peuvent la voir
        if not self.est_privee:
            return self.module.projet.affectations.filter(
                utilisateur=utilisateur,
                date_fin__isnull=True
            ).exists()
        
        # Pour les tâches privées, vérifier les permissions spéciales
        return self.visible_par.filter(id=utilisateur.id).exists()
    
    def peut_modifier_tache(self, utilisateur):
        """Vérifie si un utilisateur peut modifier cette tâche"""
        # Le créateur peut toujours modifier sa tâche
        if self.createur == utilisateur:
            return True
        
        # Les responsables du module peuvent modifier les tâches
        return self.module.affectations.filter(
            utilisateur=utilisateur,
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        ).exists()
    
    def assigner_responsable(self, responsable, utilisateur_assigneur):
        """Assigne un responsable à la tâche avec audit"""
        ancien_responsable = self.responsable
        self.responsable = responsable
        self.save()
        
        # Audit
        from .utils import enregistrer_audit
        enregistrer_audit(
            utilisateur=utilisateur_assigneur,
            type_action='ASSIGNATION_TACHE',
            description=f'Assignation de la tâche "{self.nom}" à {responsable.get_full_name()}',
            projet=self.module.projet,
            donnees_avant={
                'ancien_responsable': ancien_responsable.get_full_name() if ancien_responsable else None
            },
            donnees_apres={
                'nouveau_responsable': responsable.get_full_name(),
                'tache': self.nom,
                'module': self.module.nom
            }
        )


class TacheEtape(models.Model):
    """Tâches directement liées à une étape du projet"""
    STATUT_CHOICES = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('TERMINEE', 'Terminée'),
        ('BLOQUEE', 'Bloquée'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etape = models.ForeignKey(EtapeProjet, on_delete=models.CASCADE, related_name='taches_etape')
    nom = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignation
    responsable = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='taches_etape_assignees'
    )
    
    # Planification
    duree_estimee = models.DurationField(null=True, blank=True, help_text="Durée estimée en heures")
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    
    # Statut et priorité
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_FAIRE')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Gestion avancée
    pourcentage_completion = models.PositiveIntegerField(
        default=0, 
        validators=[MaxValueValidator(100)],
        help_text="Pourcentage de completion de la tâche (0-100)"
    )
    temps_passe = models.DurationField(
        null=True, 
        blank=True, 
        help_text="Temps réellement passé sur la tâche"
    )
    date_debut_reelle = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date et heure de début réel de la tâche"
    )
    date_fin_reelle = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date et heure de fin réelle de la tâche"
    )
    
    # Statut personnalisé (optionnel)
    statut_personnalise = models.ForeignKey(
        'StatutTachePersonnalise',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taches_avec_statut',
        help_text="Statut personnalisé selon le type d'étape"
    )
    
    # Dépendances
    taches_prerequises = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='taches_dependantes',
        help_text="Tâches qui doivent être terminées avant celle-ci"
    )
    
    # Étiquettes et catégorisation
    etiquettes = models.CharField(
        max_length=500,
        blank=True,
        help_text="Étiquettes séparées par des virgules (ex: urgent,backend,api)"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='taches_etape_creees')
    
    # Suivi
    commentaires = models.TextField(blank=True)
    raison_blocage = models.TextField(blank=True, help_text="Raison du blocage si statut = BLOQUEE")
    
    # Tâche ajoutée après clôture d'étape
    ajoutee_apres_cloture = models.BooleanField(
        default=False,
        help_text="Indique si cette tâche a été ajoutée après la clôture de l'étape"
    )
    justification_ajout_tardif = models.TextField(
        blank=True,
        help_text="Justification pour l'ajout de cette tâche après clôture de l'étape"
    )
    
    class Meta:
        verbose_name = "Tâche d'Étape"
        verbose_name_plural = "Tâches d'Étape"
        ordering = ['-date_creation']  # Tâches récentes en premier
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_debut__lte=models.F('date_fin')),
                name='tache_etape_dates_coherentes'
            ),
        ]
    
    def clean(self):
        """Validation métier"""
        # Vérifier que le responsable fait partie de l'équipe du projet
        if self.responsable:
            if not self.etape.projet.affectations.filter(
                utilisateur=self.responsable,
                date_fin__isnull=True
            ).exists():
                raise ValidationError({
                    'responsable': 'Le responsable doit faire partie de l\'équipe du projet.'
                })
    
    def __str__(self):
        return f"{self.etape.type_etape.get_nom_display()} - {self.nom}"
    
    def peut_etre_executee(self):
        """Vérifie si la tâche peut être exécutée selon l'étape actuelle du projet"""
        return self.etape.statut in ['EN_COURS', 'TERMINEE']
    
    def assigner_responsable(self, responsable, utilisateur_assigneur):
        """Assigne un responsable à la tâche avec audit"""
        ancien_responsable = self.responsable
        self.responsable = responsable
        self.save()
        
        # Audit
        from .utils import enregistrer_audit
        enregistrer_audit(
            utilisateur=utilisateur_assigneur,
            type_action='ASSIGNATION_TACHE',
            description=f'Assignation de la tâche d\'étape "{self.nom}" à {responsable.get_full_name()}',
            projet=self.etape.projet,
            donnees_avant={
                'ancien_responsable': ancien_responsable.get_full_name() if ancien_responsable else None
            },
            donnees_apres={
                'nouveau_responsable': responsable.get_full_name(),
                'tache': self.nom,
                'etape': self.etape.type_etape.nom
            }
        )
    
    def changer_statut(self, nouveau_statut, utilisateur, commentaire=None):
        """Change le statut de la tâche avec historique et notifications"""
        ancien_statut = self.statut
        
        # Vérifier si le changement est autorisé
        if self.statut_personnalise:
            if not self.statut_personnalise.peut_transitionner_vers(nouveau_statut):
                raise ValidationError(f"Transition de {ancien_statut} vers {nouveau_statut} non autorisée")
        
        self.statut = nouveau_statut
        
        # Mettre à jour les dates selon le statut
        if nouveau_statut == 'EN_COURS' and not self.date_debut_reelle:
            self.date_debut_reelle = timezone.now()
        elif nouveau_statut == 'TERMINEE':
            self.date_fin_reelle = timezone.now()
            self.pourcentage_completion = 100
        
        self.save()
        
        # Enregistrer dans l'historique
        HistoriqueTache.objects.create(
            tache=self,
            utilisateur=utilisateur,
            type_action='CHANGEMENT_STATUT',
            description=f'Changement de statut de {ancien_statut} vers {nouveau_statut}',
            donnees_avant={'statut': ancien_statut},
            donnees_apres={'statut': nouveau_statut, 'commentaire': commentaire}
        )
        
        # Créer des notifications pour les parties prenantes
        self._creer_notifications_changement_statut(ancien_statut, nouveau_statut, utilisateur)
    
    def mettre_a_jour_progression(self, pourcentage, utilisateur, commentaire=None):
        """Met à jour le pourcentage de progression de la tâche"""
        ancien_pourcentage = self.pourcentage_completion
        self.pourcentage_completion = min(100, max(0, pourcentage))
        
        # Mettre à jour le statut automatiquement selon la progression
        if self.pourcentage_completion == 100 and self.statut != 'TERMINEE':
            self.statut = 'TERMINEE'
            self.date_fin_reelle = timezone.now()
        elif self.pourcentage_completion > 0 and self.statut == 'A_FAIRE':
            self.statut = 'EN_COURS'
            if not self.date_debut_reelle:
                self.date_debut_reelle = timezone.now()
        
        self.save()
        
        # Enregistrer dans l'historique
        HistoriqueTache.objects.create(
            tache=self,
            utilisateur=utilisateur,
            type_action='MODIFICATION',
            description=f'Progression mise à jour: {ancien_pourcentage}% → {self.pourcentage_completion}%',
            donnees_avant={'pourcentage_completion': ancien_pourcentage},
            donnees_apres={'pourcentage_completion': self.pourcentage_completion, 'commentaire': commentaire}
        )
    
    def ajouter_temps_passe(self, duree, utilisateur, description=None):
        """Ajoute du temps passé sur la tâche"""
        if self.temps_passe:
            self.temps_passe += duree
        else:
            self.temps_passe = duree
        
        self.save()
        
        # Enregistrer dans l'historique
        HistoriqueTache.objects.create(
            tache=self,
            utilisateur=utilisateur,
            type_action='MODIFICATION',
            description=f'Temps ajouté: {duree} (Total: {self.temps_passe})',
            donnees_apres={'temps_ajoute': str(duree), 'temps_total': str(self.temps_passe), 'description': description}
        )
    
    def peut_etre_modifiee_par(self, utilisateur):
        """Vérifie si l'utilisateur peut modifier cette tâche"""
        # Les tâches terminées ne peuvent pas être modifiées
        if self.statut == 'TERMINEE':
            return False
        
        # Super admin peut tout modifier
        if utilisateur.est_super_admin():
            return True
        
        # Créateur peut modifier
        if self.createur == utilisateur:
            return True
        
        # Responsable peut modifier
        if self.responsable == utilisateur:
            return True
        
        # Responsable principal du projet peut modifier
        if self.etape.projet.affectations.filter(
            utilisateur=utilisateur,
            est_responsable_principal=True,
            date_fin__isnull=True
        ).exists():
            return True
        
        return False
    
    def est_en_retard(self):
        """Vérifie si la tâche est en retard"""
        if not self.date_fin or self.statut == 'TERMINEE':
            return False
        
        return timezone.now().date() > self.date_fin
    
    def jours_restants(self):
        """Calcule le nombre de jours restants avant l'échéance"""
        if not self.date_fin or self.statut == 'TERMINEE':
            return None
        
        delta = self.date_fin - timezone.now().date()
        return delta.days
    
    def get_etiquettes_list(self):
        """Retourne la liste des étiquettes"""
        if not self.etiquettes:
            return []
        return [tag.strip() for tag in self.etiquettes.split(',') if tag.strip()]
    
    def ajouter_etiquette(self, etiquette):
        """Ajoute une étiquette à la tâche"""
        etiquettes_actuelles = self.get_etiquettes_list()
        if etiquette not in etiquettes_actuelles:
            etiquettes_actuelles.append(etiquette)
            self.etiquettes = ', '.join(etiquettes_actuelles)
            self.save()
    
    def supprimer_etiquette(self, etiquette):
        """Supprime une étiquette de la tâche"""
        etiquettes_actuelles = self.get_etiquettes_list()
        if etiquette in etiquettes_actuelles:
            etiquettes_actuelles.remove(etiquette)
            self.etiquettes = ', '.join(etiquettes_actuelles)
            self.save()
    
    def peut_commencer(self):
        """Vérifie si la tâche peut commencer (toutes les dépendances sont terminées)"""
        return not self.taches_prerequises.exclude(statut='TERMINEE').exists()
    
    def can_complete(self, user):
        """Vérifie si l'utilisateur peut terminer cette tâche"""
        # 1. Super admin peut toujours terminer
        if user.est_super_admin():
            return True
        
        # 2. Responsable principal du projet
        if self.etape.projet.affectations.filter(
            utilisateur=user, 
            est_responsable_principal=True,
            date_fin__isnull=True
        ).exists():
            return True
        
        # 3. Chef de projet (rôle spécifique)
        if self.etape.projet.affectations.filter(
            utilisateur=user,
            role_projet__nom__icontains='chef',
            date_fin__isnull=True
        ).exists():
            return True
        
        # 4. Utilisateur assigné à cette tâche
        if self.responsable == user:
            return True
        
        return False
    
    def _creer_notifications_changement_statut(self, ancien_statut, nouveau_statut, utilisateur_emetteur):
        """Crée les notifications pour un changement de statut"""
        destinataires = set()
        
        # Notifier le responsable
        if self.responsable and self.responsable != utilisateur_emetteur:
            destinataires.add(self.responsable)
        
        # Notifier le créateur
        if self.createur != utilisateur_emetteur:
            destinataires.add(self.createur)
        
        # Notifier le responsable principal du projet
        responsable_projet = self.etape.projet.get_responsable_principal()
        if responsable_projet and responsable_projet != utilisateur_emetteur:
            destinataires.add(responsable_projet)
        
        # Créer les notifications
        for destinataire in destinataires:
            NotificationTache.objects.create(
                destinataire=destinataire,
                tache=self,
                type_notification='CHANGEMENT_STATUT',
                titre=f'Changement de statut: {self.nom}',
                message=f'La tâche "{self.nom}" est passée de {ancien_statut} à {nouveau_statut}',
                emetteur=utilisateur_emetteur,
                donnees_contexte={
                    'ancien_statut': ancien_statut,
                    'nouveau_statut': nouveau_statut,
                    'etape': self.etape.type_etape.nom
                }
            )

class CommentaireTache(models.Model):
    """Commentaires sur les tâches d'étape pour le suivi et la collaboration"""
    
    tache = models.ForeignKey(TacheEtape, on_delete=models.CASCADE, related_name='commentaires_tache')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='commentaires_taches')
    contenu = models.TextField(help_text="Contenu du commentaire")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    modifie = models.BooleanField(default=False)
    
    # Mentions et notifications
    mentions = models.ManyToManyField(
        Utilisateur, 
        blank=True, 
        related_name='mentions_commentaires',
        help_text="Utilisateurs mentionnés dans ce commentaire"
    )
    
    class Meta:
        verbose_name = "Commentaire de Tâche"
        verbose_name_plural = "Commentaires de Tâches"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commentaire de {self.auteur.get_full_name()} sur {self.tache.nom}"
    
    def extraire_mentions(self):
        """Extrait les mentions @utilisateur du contenu"""
        import re
        mentions = re.findall(r'@(\w+)', self.contenu)
        return mentions
    
    def notifier_mentions(self):
        """Notifie les utilisateurs mentionnés"""
        mentions_usernames = self.extraire_mentions()
        for username in mentions_usernames:
            try:
                utilisateur = Utilisateur.objects.get(username=username)
                self.mentions.add(utilisateur)
                # TODO: Envoyer notification
            except Utilisateur.DoesNotExist:
                pass


class HistoriqueTache(models.Model):
    """Historique des modifications et actions sur les tâches d'étape"""
    
    TYPE_ACTION_CHOICES = [
        ('CREATION', 'Création'),
        ('MODIFICATION', 'Modification'),
        ('CHANGEMENT_STATUT', 'Changement de statut'),
        ('ASSIGNATION', 'Assignation'),
        ('COMMENTAIRE', 'Ajout de commentaire'),
        ('SUPPRESSION', 'Suppression'),
    ]
    
    tache = models.ForeignKey(TacheEtape, on_delete=models.CASCADE, related_name='historique')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='actions_taches')
    type_action = models.CharField(max_length=20, choices=TYPE_ACTION_CHOICES)
    description = models.TextField(help_text="Description de l'action effectuée")
    
    # Données de changement
    donnees_avant = models.JSONField(null=True, blank=True, help_text="État avant modification")
    donnees_apres = models.JSONField(null=True, blank=True, help_text="État après modification")
    
    # Métadonnées
    timestamp = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Historique de Tâche"
        verbose_name_plural = "Historiques de Tâches"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.type_action} - {self.tache.nom} par {self.utilisateur.get_full_name()}"


class StatutTachePersonnalise(models.Model):
    """Statuts personnalisés pour les tâches selon le type d'étape"""
    
    type_etape = models.ForeignKey(TypeEtape, on_delete=models.CASCADE, related_name='statuts_taches_personnalises')
    nom = models.CharField(max_length=50, help_text="Nom du statut personnalisé")
    libelle = models.CharField(max_length=100, help_text="Libellé affiché")
    description = models.TextField(blank=True, help_text="Description du statut")
    couleur = models.CharField(max_length=7, default='#6B7280', help_text="Couleur hex pour l'affichage")
    icone_emoji = models.CharField(max_length=10, default='📋', help_text="Emoji représentant le statut")
    
    # Configuration
    ordre_affichage = models.IntegerField(default=1, help_text="Ordre d'affichage dans les listes")
    est_statut_final = models.BooleanField(default=False, help_text="Indique si c'est un statut de fin")
    permet_modification = models.BooleanField(default=True, help_text="Permet la modification de la tâche")
    
    # Transitions autorisées
    transitions_autorisees = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False,
        related_name='transitions_depuis',
        help_text="Statuts vers lesquels on peut transitionner"
    )
    
    class Meta:
        verbose_name = "Statut de Tâche Personnalisé"
        verbose_name_plural = "Statuts de Tâches Personnalisés"
        ordering = ['type_etape', 'ordre_affichage']
        unique_together = ['type_etape', 'nom']
    
    def __str__(self):
        return f"{self.type_etape.get_nom_display()} - {self.libelle}"
    
    def peut_transitionner_vers(self, nouveau_statut):
        """Vérifie si la transition vers un nouveau statut est autorisée"""
        return self.transitions_autorisees.filter(id=nouveau_statut.id).exists()


class PieceJointeTache(models.Model):
    """Pièces jointes attachées aux tâches d'étape"""
    
    tache = models.ForeignKey(TacheEtape, on_delete=models.CASCADE, related_name='pieces_jointes')
    nom_fichier = models.CharField(max_length=255, help_text="Nom original du fichier")
    fichier = models.FileField(upload_to='taches/pieces_jointes/%Y/%m/', help_text="Fichier attaché")
    taille_fichier = models.PositiveIntegerField(help_text="Taille du fichier en octets")
    type_mime = models.CharField(max_length=100, help_text="Type MIME du fichier")
    
    # Métadonnées
    date_upload = models.DateTimeField(auto_now_add=True)
    uploade_par = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='uploads_taches')
    description = models.TextField(blank=True, help_text="Description de la pièce jointe")
    
    # Versioning
    version = models.PositiveIntegerField(default=1, help_text="Version du fichier")
    fichier_precedent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='versions_suivantes',
        help_text="Version précédente de ce fichier"
    )
    
    class Meta:
        verbose_name = "Pièce Jointe de Tâche"
        verbose_name_plural = "Pièces Jointes de Tâches"
        ordering = ['-date_upload']
    
    def __str__(self):
        return f"{self.nom_fichier} (v{self.version}) - {self.tache.nom}"
    
    def save(self, *args, **kwargs):
        if self.fichier:
            self.taille_fichier = self.fichier.size
            # Déterminer le type MIME basé sur l'extension
            import mimetypes
            self.type_mime, _ = mimetypes.guess_type(self.nom_fichier)
            if not self.type_mime:
                self.type_mime = 'application/octet-stream'
        super().save(*args, **kwargs)
    
    def taille_lisible(self):
        """Retourne la taille du fichier dans un format lisible"""
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if self.taille_fichier < 1024.0:
                return f"{self.taille_fichier:.1f} {unit}"
            self.taille_fichier /= 1024.0
        return f"{self.taille_fichier:.1f} To"


class NotificationTache(models.Model):
    """Notifications liées aux tâches d'étape"""
    
    TYPE_NOTIFICATION_CHOICES = [
        ('ASSIGNATION', 'Assignation de tâche'),
        ('CHANGEMENT_STATUT', 'Changement de statut'),
        ('COMMENTAIRE', 'Nouveau commentaire'),
        ('MENTION', 'Mention dans un commentaire'),
        ('ECHEANCE', 'Échéance approchante'),
        ('RETARD', 'Tâche en retard'),
        ('PIECE_JOINTE', 'Nouvelle pièce jointe'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_taches')
    tache = models.ForeignKey(TacheEtape, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION_CHOICES)
    titre = models.CharField(max_length=200, help_text="Titre de la notification")
    message = models.TextField(help_text="Contenu de la notification")
    
    # État
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    emetteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.PROTECT, 
        related_name='notifications_emises',
        null=True, 
        blank=True
    )
    donnees_contexte = models.JSONField(null=True, blank=True, help_text="Données contextuelles")
    
    class Meta:
        verbose_name = "Notification de Tâche"
        verbose_name_plural = "Notifications de Tâches"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.get_full_name()}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.lue:
            self.lue = True
            self.date_lecture = timezone.now()
            self.save()


class NotificationEtape(models.Model):
    """Notifications liées aux étapes de projet"""
    
    TYPE_NOTIFICATION_CHOICES = [
        ('ETAPE_TERMINEE', 'Étape terminée'),
        ('ETAPE_ACTIVEE', 'Étape activée'),
        ('MODULES_DISPONIBLES', 'Modules disponibles'),
        ('RETARD_ETAPE', 'Retard d\'étape'),
        ('CHANGEMENT_STATUT', 'Changement de statut'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_etapes')
    etape = models.ForeignKey(EtapeProjet, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION_CHOICES)
    titre = models.CharField(max_length=200, help_text="Titre de la notification")
    message = models.TextField(help_text="Contenu de la notification")
    
    # État
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    emetteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.PROTECT, 
        related_name='notifications_etapes_emises',
        null=True, 
        blank=True
    )
    donnees_contexte = models.JSONField(null=True, blank=True, help_text="Données contextuelles")
    
    class Meta:
        verbose_name = "Notification d'Étape"
        verbose_name_plural = "Notifications d'Étapes"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.get_full_name()}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.lue:
            self.lue = True
            self.date_lecture = timezone.now()
            self.save()


class NotificationModule(models.Model):
    """Notifications liées aux modules de projet"""
    
    TYPE_NOTIFICATION_CHOICES = [
        ('AFFECTATION_MODULE', 'Affectation au module'),
        ('RETRAIT_MODULE', 'Retrait du module'),
        ('NOUVELLE_TACHE', 'Nouvelle tâche assignée'),
        ('TACHE_TERMINEE', 'Tâche terminée'),
        ('CHANGEMENT_ROLE', 'Changement de rôle'),
        ('MODULE_TERMINE', 'Module terminé'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_modules')
    module = models.ForeignKey(ModuleProjet, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION_CHOICES)
    titre = models.CharField(max_length=200, help_text="Titre de la notification")
    message = models.TextField(help_text="Contenu de la notification")
    
    # État
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    emetteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.PROTECT, 
        related_name='notifications_modules_emises',
        null=True, 
        blank=True
    )
    donnees_contexte = models.JSONField(null=True, blank=True, help_text="Données contextuelles")
    
    class Meta:
        verbose_name = "Notification de Module"
        verbose_name_plural = "Notifications de Modules"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.get_full_name()}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.lue:
            self.lue = True
            self.date_lecture = timezone.now()
            self.save()

# ============================================================================
# SIGNAUX DJANGO
# ============================================================================

@receiver(post_save, sender=TacheEtape)
def marquer_tache_speciale_automatiquement(sender, instance, created, **kwargs):
    """
    Signal qui marque automatiquement une tâche comme spéciale 
    si elle est créée sur une étape terminée
    """
    if created and instance.etape.statut == 'TERMINEE':
        # Marquer comme spéciale seulement si ce n'est pas déjà fait
        if not instance.ajoutee_apres_cloture:
            instance.ajoutee_apres_cloture = True
            if not instance.justification_ajout_tardif:
                instance.justification_ajout_tardif = "Tâche ajoutée automatiquement à une étape terminée"
            # Utiliser update_fields pour éviter une boucle infinie
            instance.save(update_fields=['ajoutee_apres_cloture', 'justification_ajout_tardif'])