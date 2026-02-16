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
    DIRECTION = 'DIRECTION'
    
    ROLE_CHOICES = [
        (DEVELOPPEUR, 'Développeur'),
        (CHEF_PROJET, 'Chef de Projet'),
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
    
    def est_chef_projet_de(self, projet):
        """Vérifie si l'utilisateur est chef de projet sur un projet"""
        if self.est_super_admin():
            return True
        affectation = self.affectations.filter(
            projet=projet, 
            date_fin__isnull=True,
            est_responsable_principal=True
        ).first()
        return affectation is not None
    
    def est_developpeur(self):
        """Vérifie si l'utilisateur a le rôle système développeur"""
        if self.role_systeme:
            return self.role_systeme.nom == 'DEVELOPPEUR'
        return False

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
    fichier_description = models.FileField(
        upload_to='projets/descriptions/',
        null=True,
        blank=True,
        help_text="Fichier de description du projet (PDF, Word)",
        verbose_name="Fichier de description"
    )
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
    
    # Paramètres de notifications
    notifications_admin_activees = models.BooleanField(
        default=False,
        help_text="Si activé, l'administrateur recevra les notifications liées à ce projet (étapes terminées, tâches importantes, etc.)"
    )
    
    # Gestion temporelle du projet
    duree_projet = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée prévue du projet en jours",
        verbose_name="Durée du projet (jours)"
    )
    date_debut = models.DateField(
        null=True,
        blank=True,
        help_text="Date de démarrage effectif du projet",
        verbose_name="Date de début"
    )
    date_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Date de fin prévue du projet (calculée automatiquement)",
        verbose_name="Date de fin prévue"
    )
    
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
    
    # ========================================================================
    # MÉTHODES DE GESTION DU DÉMARRAGE ET SUIVI TEMPOREL
    # ========================================================================
    
    def peut_etre_demarre(self):
        """
        Vérifie si le projet peut être démarré
        
        Returns:
            bool: True si le projet peut être démarré
        """
        # Statuts depuis lesquels un projet peut être démarré
        statuts_demarrables = ['CREE', 'IDEE', 'AFFECTE', 'PLANIFIE']
        
        return (
            self.date_debut is None and
            self.duree_projet is not None and
            self.duree_projet > 0 and
            self.statut.nom in statuts_demarrables
        )
    
    def demarrer_projet(self, utilisateur):
        """
        Démarre le projet : calcule les dates et change le statut
        
        Args:
            utilisateur: L'utilisateur qui démarre le projet (doit être le responsable)
        
        Returns:
            dict: Résultat de l'opération avec succès et message
        
        Raises:
            ValidationError: Si le projet ne peut pas être démarré
        """
        from datetime import timedelta
        from .utils import enregistrer_audit
        
        # Vérifications
        if not self.peut_etre_demarre():
            return {
                'success': False,
                'message': 'Le projet ne peut pas être démarré (déjà démarré ou durée non définie)'
            }
        
        # Vérifier que l'utilisateur est le responsable
        responsable = self.get_responsable_principal()
        if not responsable or responsable.id != utilisateur.id:
            return {
                'success': False,
                'message': 'Seul le responsable du projet peut le démarrer'
            }
        
        # Calculer les dates
        self.date_debut = timezone.now().date()
        self.date_fin = self.date_debut + timedelta(days=self.duree_projet)
        
        # Changer le statut vers EN_COURS
        try:
            statut_en_cours = StatutProjet.objects.get(nom='EN_COURS')
            self.statut = statut_en_cours
        except StatutProjet.DoesNotExist:
            return {
                'success': False,
                'message': 'Statut EN_COURS non trouvé dans le système'
            }
        
        self.save()
        
        # Enregistrer l'audit
        enregistrer_audit(
            utilisateur=utilisateur,
            type_action='DEMARRAGE_PROJET',
            description=f'Démarrage du projet {self.nom}',
            projet=self,
            donnees_apres={
                'date_debut': self.date_debut.isoformat(),
                'date_fin': self.date_fin.isoformat(),
                'duree_jours': self.duree_projet,
                'responsable': responsable.get_full_name()
            }
        )
        
        # Créer des notifications pour l'équipe
        self._notifier_demarrage_projet(utilisateur)
        
        return {
            'success': True,
            'message': f'Projet démarré avec succès. Date de fin prévue : {self.date_fin.strftime("%d/%m/%Y")}',
            'date_debut': self.date_debut,
            'date_fin': self.date_fin
        }
    
    def _notifier_demarrage_projet(self, utilisateur_demarreur):
        """
        Crée des notifications pour l'équipe lors du démarrage du projet
        
        Args:
            utilisateur_demarreur: L'utilisateur qui a démarré le projet
        """
        equipe = self.get_equipe()
        
        for membre in equipe:
            if membre.id != utilisateur_demarreur.id:  # Pas de notification pour celui qui démarre
                NotificationProjet.objects.create(
                    destinataire=membre,
                    projet=self,
                    type_notification='PROJET_DEMARRE',
                    titre=f"Le projet {self.nom} a démarré",
                    message=f"Le projet a été démarré par {utilisateur_demarreur.get_full_name()}. Date de fin prévue : {self.date_fin.strftime('%d/%m/%Y')}",
                    lue=False
                )
    
    def jours_restants(self):
        """
        Calcule le nombre de jours restants jusqu'à la fin du projet
        
        Returns:
            int or None: Nombre de jours restants, None si pas démarré
        """
        if not self.date_fin:
            return None
        
        aujourd_hui = timezone.now().date()
        delta = self.date_fin - aujourd_hui
        return delta.days
    
    def est_proche_fin(self, jours=7):
        """
        Vérifie si le projet est proche de sa fin
        
        Args:
            jours: Nombre de jours avant la fin pour considérer "proche" (défaut: 7)
        
        Returns:
            bool: True si le projet se termine dans X jours ou moins
        """
        jours_rest = self.jours_restants()
        if jours_rest is None:
            return False
        
        return 0 <= jours_rest <= jours
    
    def pourcentage_avancement_temps(self):
        """
        Calcule le pourcentage d'avancement basé sur le temps écoulé
        
        Returns:
            float or None: Pourcentage (0-100), None si pas démarré
        """
        if not self.date_debut or not self.date_fin:
            return None
        
        aujourd_hui = timezone.now().date()
        
        # Si pas encore commencé
        if aujourd_hui < self.date_debut:
            return 0.0
        
        # Si déjà terminé
        if aujourd_hui > self.date_fin:
            return 100.0
        
        # Calcul du pourcentage
        duree_totale = (self.date_fin - self.date_debut).days
        duree_ecoulee = (aujourd_hui - self.date_debut).days
        
        if duree_totale == 0:
            return 100.0
        
        return round((duree_ecoulee / duree_totale) * 100, 1)
    
    def get_badge_jours_restants(self):
        """
        Retourne un badge coloré selon les jours restants
        
        Returns:
            dict: {'classe': 'badge-success', 'texte': 'X jours restants'}
        """
        jours = self.jours_restants()
        
        if jours is None:
            return {'classe': 'badge-secondary', 'texte': 'Non démarré'}
        
        if jours < 0:
            return {'classe': 'badge-danger', 'texte': f'{abs(jours)} jours de retard'}
        elif jours == 0:
            return {'classe': 'badge-danger', 'texte': 'Dernier jour'}
        elif jours <= 3:
            return {'classe': 'badge-danger', 'texte': f'{jours} jours restants'}
        elif jours <= 7:
            return {'classe': 'badge-warning', 'texte': f'{jours} jours restants'}
        elif jours <= 14:
            return {'classe': 'badge-info', 'texte': f'{jours} jours restants'}
        else:
            return {'classe': 'badge-success', 'texte': f'{jours} jours restants'}

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
    
    def save(self, *args, **kwargs):
        """
        Synchronise automatiquement role_projet avec est_responsable_principal
        pour maintenir la cohérence
        """
        # Synchroniser le rôle avec le flag responsable
        if self.est_responsable_principal:
            # Si responsable, forcer le rôle RESPONSABLE_PRINCIPAL
            try:
                self.role_projet = RoleProjet.objects.get(nom='RESPONSABLE_PRINCIPAL')
            except RoleProjet.DoesNotExist:
                # Créer le rôle s'il n'existe pas
                self.role_projet = RoleProjet.objects.create(
                    nom='RESPONSABLE_PRINCIPAL',
                    description='Responsable Principal du Projet'
                )
        else:
            # Si pas responsable, forcer le rôle MEMBRE
            try:
                self.role_projet = RoleProjet.objects.get(nom='MEMBRE')
            except RoleProjet.DoesNotExist:
                # Créer le rôle s'il n'existe pas
                self.role_projet = RoleProjet.objects.create(
                    nom='MEMBRE',
                    description='Membre de l\'équipe projet'
                )
        
        super().save(*args, **kwargs)
    
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
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True, related_name='actions_audit')
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
        ancien_statut = self.statut
        self.statut = 'EN_COURS'
        self.date_debut_reelle = timezone.now()
        self.save()
        
        # Notification CHANGEMENT_STATUT pour l'étape
        from .models import NotificationEtape
        responsable = self.projet.get_responsable_principal()
        if responsable:
            NotificationEtape.objects.create(
                destinataire=responsable,
                etape=self,
                type_notification='CHANGEMENT_STATUT',
                titre=f"Étape activée: {self.type_etape.get_nom_display()}",
                message=f"L'étape '{self.type_etape.get_nom_display()}' du projet '{self.projet.nom}' a été activée manuellement.",
                emetteur=utilisateur,
                donnees_contexte={
                    'ancien_statut': ancien_statut,
                    'nouveau_statut': self.statut,
                    'date_activation': self.date_debut_reelle.isoformat()
                }
            )
        
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
            nombre_taches = taches_non_terminees.count()
            raise ValidationError(
                f'Impossible de terminer l\'étape. Il reste {nombre_taches} tâche{"s" if nombre_taches > 1 else ""} non terminée{"s" if nombre_taches > 1 else ""}. Veuillez terminer toutes les tâches avant de clôturer l\'étape.'
            )
        
        # Récupérer l'étape suivante avant de terminer celle-ci
        etape_suivante = self.get_etape_suivante()
        
        self.statut = 'TERMINEE'
        self.date_fin_reelle = timezone.now()
        self.save()
        
        # Créer une notification pour l'administrateur
        from .models import NotificationEtape
        admins = Utilisateur.objects.filter(is_superuser=True, statut_actif=True)
        for admin in admins:
            # Ne pas notifier si l'admin est celui qui termine l'étape
            if admin != utilisateur:
                NotificationEtape.objects.create(
                    destinataire=admin,
                    etape=self,
                    type_notification='ETAPE_TERMINEE',
                    titre=f"✅ Étape terminée: {self.type_etape.get_nom_display()}",
                    message=f"{utilisateur.get_full_name()} a terminé l'étape '{self.type_etape.get_nom_display()}' du projet '{self.projet.nom}'",
                    emetteur=utilisateur,
                    donnees_contexte={
                        'etape_id': str(self.id),
                        'projet_id': str(self.projet.id),
                        'type_etape': self.type_etape.nom,
                        'date_cloture': self.date_fin_reelle.isoformat()
                    }
                )
        
        # Audit de clôture
        from .utils import enregistrer_audit
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
        
        # Activer automatiquement l'étape suivante si elle existe
        if etape_suivante and etape_suivante.statut == 'A_VENIR':
            etape_suivante.statut = 'EN_COURS'
            etape_suivante.date_debut_reelle = timezone.now()
            etape_suivante.save()
            
            # Notifier l'équipe de l'activation de la nouvelle étape
            from .models import NotificationEtape
            equipe = self.projet.get_equipe()
            for membre in equipe:
                NotificationEtape.objects.create(
                    destinataire=membre,
                    etape=etape_suivante,
                    type_notification='ETAPE_ACTIVEE',
                    titre=f"Nouvelle étape activée: {etape_suivante.type_etape.get_nom_display()}",
                    message=f"L'étape '{etape_suivante.type_etape.get_nom_display()}' du projet '{self.projet.nom}' a été activée.",
                    emetteur=utilisateur,
                    donnees_contexte={
                        'etape_precedente': self.type_etape.nom,
                        'date_activation': etape_suivante.date_debut_reelle.isoformat()
                    }
                )
            
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
            
            # Si l'étape suivante est DEVELOPPEMENT, notifier les développeurs
            if etape_suivante.type_etape.nom == 'DEVELOPPEMENT':
                # Notifier les développeurs que les modules sont disponibles
                developpeurs = Utilisateur.objects.filter(
                    role_systeme__nom='DEVELOPPEUR',
                    statut_actif=True,
                    affectations__projet=self.projet,
                    affectations__date_fin__isnull=True
                ).distinct()
                
                for dev in developpeurs:
                    NotificationEtape.objects.create(
                        destinataire=dev,
                        etape=etape_suivante,
                        type_notification='MODULES_DISPONIBLES',
                        titre=f"Modules disponibles: {self.projet.nom}",
                        message=f"L'étape de développement est activée. Vous pouvez maintenant créer et vous affecter des modules pour le projet '{self.projet.nom}'.",
                        emetteur=utilisateur,
                        donnees_contexte={
                            'projet_id': str(self.projet.id),
                            'etape_id': str(etape_suivante.id)
                        }
                    )
                
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
        
        # Si c'était la dernière étape, notifier que le projet est terminé
        else:
            # Notifier l'équipe que le projet est terminé
            from .models import NotificationProjet
            equipe = self.projet.get_equipe()
            for membre in equipe:
                NotificationProjet.objects.create(
                    destinataire=membre,
                    projet=self.projet,
                    type_notification='PROJET_TERMINE',
                    titre=f"🎉 Projet terminé: {self.projet.nom}",
                    message=f"Toutes les étapes du projet '{self.projet.nom}' sont terminées. Félicitations à toute l'équipe!",
                    emetteur=utilisateur,
                    donnees_contexte={
                        'derniere_etape': self.type_etape.nom,
                        'date_fin': timezone.now().isoformat()
                    }
                )
        
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
    
    # Clôture du module
    est_cloture = models.BooleanField(default=False, help_text="Indique si le module est clôturé")
    date_cloture = models.DateTimeField(blank=True, null=True, help_text="Date de clôture du module")
    cloture_par = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='modules_clotures',
        help_text="Utilisateur ayant clôturé le module"
    )
    
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
    
    def get_responsable(self):
        """Retourne le responsable du module"""
        affectation = self.affectations.filter(
            role_module='RESPONSABLE',
            date_fin_affectation__isnull=True
        ).first()
        return affectation.utilisateur if affectation else None

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
    
    def get_role_module_display_from_value(self, role_value):
        """Retourne le libellé d'un rôle à partir de sa valeur"""
        role_dict = dict(self.ROLE_MODULE_CHOICES)
        return role_dict.get(role_value, role_value)

class TacheModule(models.Model):
    """Tâches d'un module"""
    STATUT_CHOICES = [
        ('A_FAIRE', 'À faire'),
        ('EN_COURS', 'En cours'),
        ('EN_PAUSE', 'En pause'),
        ('TERMINEE', 'Terminée'),
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
    
    # Progression
    pourcentage_completion = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Pourcentage de completion de la tâche (0-100)"
    )
    
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
    
    def get_statut_display_from_value(self, statut_value):
        """Retourne le libellé d'un statut à partir de sa valeur"""
        statut_dict = dict(self.STATUT_CHOICES)
        return statut_dict.get(statut_value, statut_value)
    
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
        """Assigne un responsable à la tâche avec audit et notification"""
        ancien_responsable = self.responsable
        self.responsable = responsable
        self.save()
        
        # Créer une notification pour le nouveau responsable
        if responsable and responsable != utilisateur_assigneur:
            from .models import NotificationTache
            NotificationTache.objects.create(
                destinataire=responsable,
                tache=self,
                type_notification='ASSIGNATION',
                message=f'La tâche "{self.nom}" du module "{self.module.nom}" vous a été assignée par {utilisateur_assigneur.get_full_name()}.'
            )
        
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
        ('ECHEC', 'Échec'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('MOYENNE', 'Moyenne'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    etape = models.ForeignKey(EtapeProjet, on_delete=models.CASCADE, related_name='taches_etape')

    # Relation avec le cas de test (nouveau)
    cas_test = models.ForeignKey(
        'CasTest', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='rolesysteme_cas_tests',
        help_text="Cas de test qui a généré ce bug"
    )
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
        """Assigne un responsable à la tâche avec audit et notification"""
        ancien_responsable = self.responsable
        self.responsable = responsable
        self.save()
        
        # Créer une notification pour le nouveau responsable
        if responsable and responsable != utilisateur_assigneur:
            from .models import NotificationTache
            NotificationTache.objects.create(
                destinataire=responsable,
                tache=self,
                type_notification='ASSIGNATION',
                message=f'La tâche "{self.nom}" de l\'étape "{self.etape.type_etape.get_nom_display()}" vous a été assignée par {utilisateur_assigneur.get_full_name()}.'
            )
        
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
    
    def mettre_a_jour_statut_avec_sous_taches(self):
        """Met à jour le statut de la tâche en fonction de ses sous-tâches (CasTest)"""
        # Cette méthode ne s'applique que pour les étapes de TEST
        if self.etape.type_etape.nom != 'TESTS':
            return
        
        cas_tests = self.cas_tests.all()
        if not cas_tests.exists():
            return
        
        # Calculer les statistiques des cas de test
        total_cas = cas_tests.count()
        cas_passes = cas_tests.filter(statut='PASSE').count()
        cas_echecs = cas_tests.filter(statut='ECHEC').count()
        cas_en_cours = cas_tests.filter(statut='EN_COURS').count()
        
        # Déterminer le nouveau statut
        if cas_passes == total_cas:
            # Tous les cas sont passés
            nouveau_statut = 'TERMINEE'
            self.pourcentage_completion = 100
        elif cas_echecs > 0:
            # Il y a des échecs
            nouveau_statut = 'BLOQUEE'
            self.pourcentage_completion = int((cas_passes / total_cas) * 100)
        elif cas_en_cours > 0:
            # Des cas sont en cours
            nouveau_statut = 'EN_COURS'
            self.pourcentage_completion = int((cas_passes / total_cas) * 100)
        else:
            # Tous les cas sont en attente
            nouveau_statut = 'A_FAIRE'
            self.pourcentage_completion = 0
        
        # Mettre à jour si nécessaire
        if self.statut != nouveau_statut:
            self.statut = nouveau_statut
            if nouveau_statut == 'TERMINEE':
                self.date_fin_reelle = timezone.now()
            self.save()
    
    def mettre_a_jour_progression_depuis_cas_tests(self):
        """Alias pour mettre_a_jour_statut_avec_sous_taches - utilisé par CasTest"""
        self.mettre_a_jour_statut_avec_sous_taches()
    
    def get_statistiques_cas_tests(self):
        """Retourne les statistiques des cas de test pour cette tâche"""
        if self.etape.type_etape.nom != 'TESTS':
            return None
        
        cas_tests = self.cas_tests.all()
        if not cas_tests.exists():
            return None
        
        total = cas_tests.count()
        passes = cas_tests.filter(statut='PASSE').count()
        echecs = cas_tests.filter(statut='ECHEC').count()
        en_cours = cas_tests.filter(statut='EN_COURS').count()
        en_attente = cas_tests.filter(statut='EN_ATTENTE').count()
        bloques = cas_tests.filter(statut='BLOQUE').count()
        
        return {
            'total': total,
            'passes': passes,
            'echecs': echecs,
            'en_cours': en_cours,
            'en_attente': en_attente,
            'bloques': bloques,
            'pourcentage_reussite': int((passes / total) * 100) if total > 0 else 0,
        }
    
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
        ('ALERTE_ECHEANCE', 'Alerte échéance (2j ou 1j)'),
        ('ALERTE_CRITIQUE', 'Alerte critique (jour J)'),
        ('ALERTE_RETARD', 'Alerte retard'),
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
        ('CAS_TEST_PASSE', 'Cas de test passé'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_etapes')
    etape = models.ForeignKey(EtapeProjet, on_delete=models.CASCADE, related_name='notifications')

    # Relation avec le cas de test (nouveau)
    cas_test = models.ForeignKey(
        'CasTest', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='commentairetache_cas_tests',
        help_text="Cas de test qui a généré ce bug"
    )
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
        ('CHANGEMENT_STATUT', 'Changement de statut de tâche'),
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


class NotificationProjet(models.Model):
    """Notifications liées aux projets (démarrage, alertes fin, etc.)"""
    
    TYPE_NOTIFICATION_CHOICES = [
        ('AFFECTATION_RESPONSABLE', 'Affectation comme responsable'),
        ('AJOUT_EQUIPE', 'Ajout à l\'équipe du projet'),
        ('PROJET_DEMARRE', 'Projet démarré'),
        ('ALERTE_FIN_PROJET', 'Alerte fin de projet (J-7)'),
        ('PROJET_TERMINE', 'Projet terminé'),
        ('PROJET_SUSPENDU', 'Projet suspendu'),
        ('CHANGEMENT_ECHEANCE', 'Changement d\'échéance'),
        ('ASSIGNATION_TICKET_MAINTENANCE', 'Assignation ticket de maintenance'),
        ('TICKET_RESOLU', 'Ticket de maintenance résolu'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications_projets')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=30, choices=TYPE_NOTIFICATION_CHOICES)
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
        related_name='notifications_projets_emises',
        null=True, 
        blank=True
    )
    donnees_contexte = models.JSONField(null=True, blank=True, help_text="Données contextuelles")
    
    class Meta:
        verbose_name = "Notification de Projet"
        verbose_name_plural = "Notifications de Projets"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['destinataire', 'lue', '-date_creation']),
            models.Index(fields=['projet', '-date_creation']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.destinataire.get_full_name()}"
    
    def marquer_comme_lue(self):
        """Marque la notification comme lue"""
        if not self.lue:
            self.lue = True
            self.date_lecture = timezone.now()
            self.save()


class AlerteProjet(models.Model):
    """Alertes système liées aux projets (échéances, dépassements, etc.) - Séparées des notifications"""
    
    TYPE_ALERTE_CHOICES = [
        ('ECHEANCE_J7', 'Échéance dans 7 jours'),
        ('ECHEANCE_J3', 'Échéance dans 3 jours'),
        ('ECHEANCE_J1', 'Échéance dans 1 jour'),
        ('ECHEANCE_DEPASSEE', 'Échéance dépassée'),
        ('BUDGET_DEPASSE', 'Budget dépassé'),
        ('TACHES_EN_RETARD', 'Tâches en retard'),
        ('CONTRAT_EXPIRATION', 'Contrat proche expiration'),
        ('CONTRAT_EXPIRE', 'Contrat expiré'),
    ]
    
    NIVEAU_CHOICES = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('DANGER', 'Critique'),
    ]
    
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='alertes_projets')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='alertes')
    type_alerte = models.CharField(max_length=30, choices=TYPE_ALERTE_CHOICES)
    niveau = models.CharField(max_length=10, choices=NIVEAU_CHOICES, default='WARNING')
    titre = models.CharField(max_length=200, help_text="Titre de l'alerte")
    message = models.TextField(help_text="Contenu de l'alerte")
    
    # État
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    donnees_contexte = models.JSONField(null=True, blank=True, help_text="Données contextuelles (jours restants, etc.)")
    
    class Meta:
        verbose_name = "Alerte de Projet"
        verbose_name_plural = "Alertes de Projets"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['destinataire', 'lue', '-date_creation']),
            models.Index(fields=['projet', '-date_creation']),
            models.Index(fields=['type_alerte', '-date_creation']),
        ]
    
    def __str__(self):
        return f"[{self.get_niveau_display()}] {self.titre} - {self.destinataire.get_full_name()}"
    
    def marquer_comme_lue(self):
        """Marque l'alerte comme lue"""
        if not self.lue:
            self.lue = True
            self.date_lecture = timezone.now()
            self.save()
    
    def get_couleur_badge(self):
        """Retourne la couleur du badge selon le niveau"""
        couleurs = {
            'INFO': 'blue',
            'WARNING': 'yellow',
            'DANGER': 'red',
        }
        return couleurs.get(self.niveau, 'gray')
    
    def get_icone(self):
        """Retourne l'icône FontAwesome selon le type d'alerte"""
        icones = {
            'ECHEANCE_J7': 'fa-clock',
            'ECHEANCE_J3': 'fa-exclamation-circle',
            'ECHEANCE_J1': 'fa-exclamation-triangle',
            'ECHEANCE_DEPASSEE': 'fa-times-circle',
            'BUDGET_DEPASSE': 'fa-dollar-sign',
            'TACHES_EN_RETARD': 'fa-tasks',
            'CONTRAT_EXPIRATION': 'fa-file-contract',
            'CONTRAT_EXPIRE': 'fa-ban',
        }
        return icones.get(self.type_alerte, 'fa-bell')


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


@receiver(post_save, sender=Affectation)
def notifier_responsable_projet(sender, instance, created, **kwargs):
    """
    Signal qui notifie automatiquement un utilisateur lorsqu'il est désigné
    comme responsable principal d'un projet
    """
    # Vérifier si c'est une nouvelle affectation ou une modification
    if instance.est_responsable_principal and instance.date_fin is None:
        # Vérifier si une notification n'existe pas déjà pour éviter les doublons
        notification_existante = NotificationProjet.objects.filter(
            destinataire=instance.utilisateur,
            projet=instance.projet,
            type_notification='AFFECTATION_RESPONSABLE',
            date_creation__gte=timezone.now() - timezone.timedelta(minutes=5)
        ).exists()
        
        if not notification_existante:
            # Déterminer le message selon l'état du projet
            if instance.projet.peut_etre_demarre():
                message_action = "Vous pouvez maintenant démarrer le projet en cliquant sur le bouton 'Commencer le projet'."
            elif instance.projet.date_debut:
                message_action = f"Le projet a déjà été démarré le {instance.projet.date_debut.strftime('%d/%m/%Y')}."
            else:
                message_action = "Définissez une durée pour le projet avant de pouvoir le démarrer."
            
            # Créer la notification
            NotificationProjet.objects.create(
                destinataire=instance.utilisateur,
                projet=instance.projet,
                type_notification='AFFECTATION_RESPONSABLE',
                titre=f"🎯 Vous êtes responsable du projet {instance.projet.nom}",
                message=f"Vous avez été désigné(e) comme responsable principal du projet '{instance.projet.nom}'. "
                        f"{message_action} "
                        f"Budget: {instance.projet.budget_previsionnel} {instance.projet.devise}. "
                        f"Client: {instance.projet.client}.",
                emetteur=None,  # Notification système
                lue=False,
                donnees_contexte={
                    'role': 'RESPONSABLE_PRINCIPAL',
                    'date_affectation': instance.date_debut.isoformat() if instance.date_debut else timezone.now().isoformat(),
                    'projet_id': str(instance.projet.id),
                    'peut_demarrer': instance.projet.peut_etre_demarre(),
                    'projet_demarre': instance.projet.date_debut is not None
                }
            )

# ============================================================================
# SYSTÈME DE TESTS V1 - GESTION QUALITÉ
# ============================================================================

class TacheTest(models.Model):
    """Tâches de test pour l'étape TEST - Version 1 simplifiée"""
    
    TYPE_TEST_CHOICES = [
        ('FONCTIONNEL', 'Test Fonctionnel'),
        ('SECURITE', 'Test de Sécurité'),
        ('INTEGRATION', 'Test d\'Intégration'),
    ]
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('PASSE', 'Passé'),
        ('ECHEC', 'Échec'),
        ('BLOQUE', 'Bloqué'),
    ]
    
    PRIORITE_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_test = models.CharField(max_length=20, unique=True, help_text="Auto-généré: TEST-PROJ-001")
    
    # Relations
    etape = models.ForeignKey(EtapeProjet, on_delete=models.CASCADE, related_name='taches_test')

    # Relation avec le cas de test (nouveau)
    cas_test = models.ForeignKey(
        'CasTest', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notificationmodule_cas_tests',
        help_text="Cas de test qui a généré ce bug"
    )
    module_concerne = models.ForeignKey(ModuleProjet, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Métadonnées test
    nom = models.CharField(max_length=200)
    description = models.TextField()
    type_test = models.CharField(max_length=20, choices=TYPE_TEST_CHOICES, default='FONCTIONNEL')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Scénario de test
    scenario_test = models.TextField(help_text="Étapes détaillées du test")
    resultats_attendus = models.TextField(help_text="Résultats attendus")
    resultats_obtenus = models.TextField(blank=True, help_text="Résultats obtenus lors de l'exécution")
    
    # Statut et exécution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_execution = models.DateTimeField(null=True, blank=True)
    
    # Assignation
    assignee_qa = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='taches_test_assignees',
        help_text="QA responsable du test"
    )
    executeur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tests_executes',
        help_text="Personne qui a exécuté le test"
    )
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='taches_test_creees')
    
    class Meta:
        verbose_name = "Tâche de Test"
        verbose_name_plural = "Tâches de Test"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.numero_test} - {self.nom}"
    
    def save(self, *args, **kwargs):
        # Auto-générer le numero_test si pas défini
        if not self.numero_test:
            # Générer un numéro unique basé sur l'étape et le projet
            projet_prefix = self.etape.projet.nom[:4].upper().replace(' ', '')
            existing_count = TacheTest.objects.filter(etape__projet=self.etape.projet).count()
            self.numero_test = f"TEST-{projet_prefix}-{existing_count + 1:03d}"
        
        super().save(*args, **kwargs)
    
    def mettre_a_jour_statut(self):
        """Mettre à jour le statut de la tâche basé sur ses cas de test - UNIQUEMENT pour étape TEST"""
        # Vérifier que c'est bien une étape TEST
        if self.etape.type_etape.nom != 'TESTS':
            return  # Ne pas traiter si ce n'est pas l'étape TEST
        
        cas_tests = self.cas_tests.all()
        
        if not cas_tests.exists():
            return
        
        total_cas = cas_tests.count()
        cas_passes = cas_tests.filter(statut='PASSE').count()
        cas_echecs = cas_tests.filter(statut='ECHEC').count()
        cas_en_cours = cas_tests.filter(statut='EN_COURS').count()
        
        if cas_echecs > 0:
            self.statut = 'ECHEC'
        elif cas_passes == total_cas:
            self.statut = 'PASSE'
        elif cas_en_cours > 0 or cas_passes > 0:
            self.statut = 'EN_COURS'
        else:
            self.statut = 'EN_ATTENTE'
        
        self.save()
    
    @property
    def statistiques_cas(self):
        """Retourne les statistiques des cas de test - UNIQUEMENT pour étape TEST"""
        if self.etape.type_etape.nom != 'TESTS':
            return {'total': 0, 'passes': 0, 'echecs': 0, 'en_cours': 0, 'en_attente': 0}
        
        cas_tests = self.cas_tests.all()
        return {
            'total': cas_tests.count(),
            'passes': cas_tests.filter(statut='PASSE').count(),
            'echecs': cas_tests.filter(statut='ECHEC').count(),
            'en_cours': cas_tests.filter(statut='EN_COURS').count(),
            'en_attente': cas_tests.filter(statut='EN_ATTENTE').count(),
        }
    
    @property
    def progression_pourcentage(self):
        """Calcule le pourcentage de progression - UNIQUEMENT pour étape TEST"""
        stats = self.statistiques_cas
        if stats['total'] == 0:
            return 0
        return round((stats['passes'] / stats['total']) * 100, 1)



class CasTest(models.Model):
    """Cas de test individuel dans une tâche d'étape"""
    
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('PASSE', 'Passé'),
        ('ECHEC', 'Échec'),
        ('BLOQUE', 'Bloqué'),
    ]
    
    PRIORITE_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('HAUTE', 'Haute'),
        ('MOYENNE', 'Moyenne'),
        ('BASSE', 'Basse'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_cas = models.CharField(max_length=30, help_text="Auto-généré: AUTH-001, AUTH-002, etc.")
    
    # Relations - Utilise TacheEtape directement (correspond à la base de données)
    tache_etape = models.ForeignKey('TacheEtape', on_delete=models.CASCADE, related_name='cas_tests', null=True, blank=True)
    
    # Informations du cas
    nom = models.CharField(max_length=200, help_text="Ex: Connexion avec email valide")
    description = models.TextField(help_text="Description détaillée du cas de test")
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='MOYENNE')
    
    # Données de test
    donnees_entree = models.TextField(blank=True, help_text="Données d'entrée du test")
    preconditions = models.TextField(blank=True, help_text="Conditions préalables à remplir")
    
    # Étapes d'exécution
    etapes_execution = models.TextField(help_text="Étapes détaillées pour exécuter ce cas")
    
    # Résultats
    resultats_attendus = models.TextField(help_text="Résultats attendus pour ce cas spécifique")
    resultats_obtenus = models.TextField(blank=True, help_text="Résultats obtenus lors de l'exécution")
    
    # Statut et exécution
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_execution = models.DateTimeField(null=True, blank=True)
    
    # Assignation et exécution
    executeur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cas_tests_executes',
        help_text="QA qui a exécuté ce cas"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cas_tests_crees'
    )
    
    # Ordre dans la tâche
    ordre = models.PositiveIntegerField(default=1)
    
    class Meta:
        ordering = ['ordre', 'date_creation']
        unique_together = ['tache_etape', 'numero_cas']
        verbose_name = "Cas de test"
        verbose_name_plural = "Cas de tests"
    
    def __str__(self):
        return f"{self.numero_cas} - {self.nom}"
    
    def save(self, *args, **kwargs):
        # Auto-générer le numéro de cas si pas défini
        if not self.numero_cas:
            # Prendre le préfixe de la tâche parent et ajouter un numéro séquentiel
            prefix = self.tache_etape.nom[:4].upper().replace(' ', '')
            existing_count = CasTest.objects.filter(tache_etape=self.tache_etape).count()
            self.numero_cas = f"{prefix}-{existing_count + 1:03d}"
        
        super().save(*args, **kwargs)
    
    @property
    def est_critique(self):
        """Vérifie si ce cas est critique"""
        return self.priorite == 'CRITIQUE'
    
    @property
    def peut_etre_execute(self):
        """Vérifie si ce cas peut être exécuté"""
        return self.statut in ['EN_ATTENTE', 'ECHEC']
    
    @property
    def est_termine(self):
        """Vérifie si ce cas est terminé (passé ou échoué)"""
        return self.statut in ['PASSE', 'ECHEC']
    
    def marquer_comme_passe(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme passé"""
        self.statut = 'PASSE'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour la progression de la tâche d'étape parente
        self.tache_etape.mettre_a_jour_progression_depuis_cas_tests()
        
        # Notifier le responsable du projet
        projet = self.tache_etape.etape.projet
        responsable_projet = projet.get_responsable_principal()
        
        if responsable_projet and responsable_projet != executeur:
            NotificationEtape.objects.create(
                destinataire=responsable_projet,
                etape=self.tache_etape.etape,
                cas_test=self,
                type_notification='CAS_TEST_PASSE',
                titre=f'Cas de test passé : {self.numero_cas}',
                message=f'Le cas de test "{self.nom}" de la tâche "{self.tache_etape.nom}" a été marqué comme passé par {executeur.get_full_name()}.'
            )
    
    def marquer_comme_echec(self, executeur, resultats_obtenus=""):
        """Marquer le cas comme échoué"""
        self.statut = 'ECHEC'
        self.executeur = executeur
        self.resultats_obtenus = resultats_obtenus
        self.date_execution = timezone.now()
        self.save()
        
        # Mettre à jour la progression de la tâche d'étape parente
        self.tache_etape.mettre_a_jour_progression_depuis_cas_tests()

class BugTest(models.Model):
    """Bugs découverts lors des tests - Version 1 simplifiée"""
    
    GRAVITE_CHOICES = [
        ('CRITIQUE', 'Critique'),
        ('MAJEUR', 'Majeur'),
        ('MINEUR', 'Mineur'),
    ]
    
    STATUT_CHOICES = [
        ('OUVERT', 'Ouvert'),
        ('ASSIGNE', 'Assigné'),
        ('EN_COURS', 'En cours'),
        ('RESOLU', 'Résolu'),
        ('FERME', 'Fermé'),
        ('REJETE', 'Rejeté'),
    ]
    
    TYPE_BUG_CHOICES = [
        ('FONCTIONNEL', 'Fonctionnel'),
        ('SECURITE', 'Sécurité'),
        ('UI_UX', 'Interface utilisateur'),
        ('DONNEES', 'Données'),
        ('AUTRE', 'Autre'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_bug = models.CharField(max_length=20, unique=True, help_text="Auto-généré: BUG-PROJ-001")
    titre = models.CharField(max_length=200)
    
    # Relations
    tache_test = models.ForeignKey(TacheTest, on_delete=models.CASCADE, related_name='bugs')
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='bugs_test')
    module_concerne = models.ForeignKey(ModuleProjet, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Classification
    gravite = models.CharField(max_length=20, choices=GRAVITE_CHOICES)
    type_bug = models.CharField(max_length=20, choices=TYPE_BUG_CHOICES, default='FONCTIONNEL')
    
    # Description
    description = models.TextField(help_text="Description détaillée du bug")
    etapes_reproduction = models.TextField(help_text="Étapes pour reproduire le bug")
    environnement = models.CharField(max_length=100, blank=True, help_text="Environnement de test")
    
    # Workflow
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='OUVERT')
    resolution = models.TextField(blank=True, help_text="Description de la résolution")
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    # Assignation
    rapporteur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.PROTECT, 
        related_name='bugs_rapportes',
        help_text="QA qui a rapporté le bug"
    )
    assignee_dev = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bugs_assignes',
        help_text="Développeur assigné pour la correction"
    )
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bug de Test"
        verbose_name_plural = "Bugs de Test"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.numero_bug} - {self.titre}"
    
    def save(self, *args, **kwargs):
        """Auto-génération du numéro de bug"""
        if not self.numero_bug:
            # Compter les bugs existants pour ce projet
            count = BugTest.objects.filter(projet=self.projet).count() + 1
            self.numero_bug = f"BUG-{str(self.projet.id)[:8].upper()}-{count:03d}"
        super().save(*args, **kwargs)
    
    def est_critique(self):
        """Vérifie si le bug est critique"""
        return self.gravite == 'CRITIQUE'
    
    def est_ouvert(self):
        """Vérifie si le bug est encore ouvert"""
        return self.statut in ['OUVERT', 'ASSIGNE', 'EN_COURS']
    
    def assigner_a_developpeur(self, developpeur):
        """Assigne le bug à un développeur"""
        self.assignee_dev = developpeur
        self.statut = 'ASSIGNE'
        self.save()
    
    def marquer_comme_resolu(self, resolution=""):
        """Marque le bug comme résolu"""
        self.statut = 'RESOLU'
        self.resolution = resolution
        self.date_resolution = timezone.now()
        self.save()
    
    def fermer_bug(self):
        """Ferme définitivement le bug"""
        self.statut = 'FERME'
        if not self.date_resolution:
            self.date_resolution = timezone.now()
        self.save()

class ValidationTest(models.Model):
    """Validation de l'étape TEST par le Chef de projet"""
    
    # Relations
    etape = models.OneToOneField(EtapeProjet, on_delete=models.CASCADE, related_name='validation_test')
    
    # Validation
    est_validee = models.BooleanField(default=False)
    validateur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Chef de projet qui a validé"
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Critères de validation (calculés automatiquement)
    tous_tests_passes = models.BooleanField(default=False)
    aucun_bug_critique = models.BooleanField(default=False)
    
    # Commentaires
    commentaires_validation = models.TextField(blank=True)
    conditions_specifiques = models.TextField(blank=True, help_text="Conditions spéciales pour cette validation")
    
    # Métriques simples
    nb_tests_total = models.IntegerField(default=0)
    nb_tests_passes = models.IntegerField(default=0)
    nb_bugs_critiques = models.IntegerField(default=0)
    nb_bugs_majeurs = models.IntegerField(default=0)
    nb_bugs_mineurs = models.IntegerField(default=0)
    
    # Audit
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Validation de Test"
        verbose_name_plural = "Validations de Test"
    
    def __str__(self):
        statut = "Validée" if self.est_validee else "En attente"
        return f"Validation TEST - {self.etape.projet.nom} - {statut}"
    
    def calculer_metriques(self):
        """Calcule automatiquement les métriques de validation"""
        # Tests
        tests = self.etape.taches_test.all()
        self.nb_tests_total = tests.count()
        self.nb_tests_passes = tests.filter(statut='PASSE').count()
        self.tous_tests_passes = self.nb_tests_total > 0 and self.nb_tests_passes == self.nb_tests_total
        
        # Bugs
        bugs = BugTest.objects.filter(projet=self.etape.projet, statut__in=['OUVERT', 'ASSIGNE', 'EN_COURS'])
        self.nb_bugs_critiques = bugs.filter(gravite='CRITIQUE').count()
        self.nb_bugs_majeurs = bugs.filter(gravite='MAJEUR').count()
        self.nb_bugs_mineurs = bugs.filter(gravite='MINEUR').count()
        self.aucun_bug_critique = self.nb_bugs_critiques == 0
        
        self.save()
    
    def peut_etre_validee(self):
        """Vérifie si l'étape peut être validée"""
        self.calculer_metriques()
        return self.tous_tests_passes and self.aucun_bug_critique
    
    def valider_etape(self, validateur, commentaires=""):
        """Valide l'étape TEST"""
        if not self.peut_etre_validee():
            raise ValidationError("L'étape ne peut pas être validée : tests non passés ou bugs critiques ouverts")
        
        self.est_validee = True
        self.validateur = validateur
        self.date_validation = timezone.now()
        self.commentaires_validation = commentaires
        self.save()
        
        # Marquer l'étape comme terminée
        self.etape.statut = 'TERMINEE'
        self.etape.date_fin_reelle = timezone.now()
        self.etape.save()
    
    def get_taux_reussite_tests(self):
        """Retourne le taux de réussite des tests en pourcentage"""
        if self.nb_tests_total == 0:
            return 0
        return round((self.nb_tests_passes / self.nb_tests_total) * 100, 1)

# ============================================================================
# SIGNAUX POUR LE SYSTÈME DE TESTS
# ============================================================================

@receiver(post_save, sender=EtapeProjet)
def creer_validation_test_automatiquement(sender, instance, created, **kwargs):
    """
    Crée automatiquement une ValidationTest quand une étape TEST est créée
    """
    if created and instance.type_etape.nom == 'TESTS':
        ValidationTest.objects.get_or_create(etape=instance)

@receiver(post_save, sender=TacheTest)
def mettre_a_jour_validation_test(sender, instance, **kwargs):
    """
    Met à jour les métriques de validation quand une tâche de test change
    """
    try:
        validation = instance.etape.validation_test
        validation.calculer_metriques()
    except ValidationTest.DoesNotExist:
        pass

@receiver(post_save, sender=BugTest)
def mettre_a_jour_validation_test_bug(sender, instance, **kwargs):
    """
    Met à jour les métriques de validation quand un bug change
    """
    try:
        validation = instance.projet.etapes.filter(type_etape__nom='TESTS').first().validation_test
        validation.calculer_metriques()
    except (AttributeError, ValidationTest.DoesNotExist):
        pass


# ============================================================================
# MODÈLE DEPLOIEMENT - Architecture hiérarchique
# ============================================================================

class Deploiement(models.Model):
    """
    Déploiement spécifique lié à une tâche de déploiement
    Architecture: TacheEtape (tâche de déploiement) → Deploiement (action technique)
    """
    STATUT_CHOICES = [
        ('PREVU', 'Prévu'),
        ('EN_COURS', 'En cours'),
        ('REUSSI', 'Réussi'),
        ('ECHEC', 'Échec'),
        ('ANNULE', 'Annulé'),
    ]
    
    ENVIRONNEMENT_CHOICES = [
        ('DEV', 'Développement'),
        ('TEST', 'Test'),
        ('PREPROD', 'Pré-production'),
        ('PROD', 'Production'),
    ]
    
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers la tâche de déploiement parente
    tache_deploiement = models.ForeignKey(
        TacheEtape,
        on_delete=models.CASCADE,
        related_name='deploiements',
        verbose_name='Tâche de déploiement'
    )
    
    # Informations du déploiement
    version = models.CharField(max_length=50, verbose_name='Version')
    environnement = models.CharField(max_length=20, choices=ENVIRONNEMENT_CHOICES, verbose_name='Environnement')
    description = models.TextField(verbose_name='Description')
    
    # Statut et priorité
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PREVU')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='NORMALE')
    
    # Responsables
    responsable = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='deploiements_responsable')
    executant = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='deploiements_executes')
    
    # Gouvernance
    autorise_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='deploiements_autorises')
    date_autorisation = models.DateTimeField(null=True, blank=True)
    
    # Dates
    date_prevue = models.DateTimeField(null=True, blank=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    
    # Logs et résultats
    logs_deploiement = models.TextField(blank=True)
    commentaires = models.TextField(blank=True)
    
    # Incident lié
    incident_cree = models.ForeignKey(TacheEtape, on_delete=models.SET_NULL, null=True, blank=True, related_name='deploiement_origine_incident')
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, related_name='deploiements_crees')
    
    class Meta:
        verbose_name = "Déploiement"
        verbose_name_plural = "Déploiements"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.version} sur {self.get_environnement_display()} - {self.get_statut_display()}"
    
    def peut_etre_autorise(self):
        return self.statut == 'PREVU' and not self.autorise_par
    
    def peut_etre_execute(self):
        return self.statut == 'PREVU' and self.autorise_par is not None
    
    def autoriser(self, utilisateur):
        if not self.peut_etre_autorise():
            raise ValidationError('Ce déploiement ne peut pas être autorisé.')
        self.autorise_par = utilisateur
        self.date_autorisation = timezone.now()
        self.save()
    
    def demarrer(self, executant):
        if not self.peut_etre_execute():
            raise ValidationError('Ce déploiement ne peut pas être exécuté.')
        self.statut = 'EN_COURS'
        self.executant = executant
        self.date_debut = timezone.now()
        self.save()
    
    def marquer_reussi(self, logs=''):
        self.statut = 'REUSSI'
        self.date_fin = timezone.now()
        if logs:
            self.logs_deploiement = logs
        self.save()
    
    def marquer_echec(self, logs='', creer_incident=True):
        self.statut = 'ECHEC'
        self.date_fin = timezone.now()
        if logs:
            self.logs_deploiement = logs
        self.save()
        
        if creer_incident and not self.incident_cree:
            incident = TacheEtape.objects.create(
                etape=self.tache_deploiement.etape,
                nom=f"INCIDENT - Échec déploiement {self.version}",
                description=f"Échec du déploiement {self.version} sur {self.get_environnement_display()}.\n\nLogs:\n{self.logs_deploiement}",
                responsable=self.responsable,
                statut='A_FAIRE',
                priorite='CRITIQUE',
                createur=self.executant or self.createur
            )
            self.incident_cree = incident
            self.save()
            return incident
        return None


# ============================================================================
# SYSTÈME DE MAINTENANCE
# ============================================================================

class ContratGarantie(models.Model):
    """
    Contrat de garantie lié à un projet
    Définit les conditions de maintenance gratuite
    """
    TYPE_GARANTIE_CHOICES = [
        ('CORRECTIVE', 'Maintenance Corrective'),
        ('EVOLUTIVE', 'Maintenance Évolutive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='contrats_garantie')
    
    # Type et période
    type_garantie = models.CharField(max_length=20, choices=TYPE_GARANTIE_CHOICES)
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    
    # SLA (Service Level Agreement)
    sla_heures = models.IntegerField(
        verbose_name="SLA en heures",
        help_text="Temps de réponse maximum en heures"
    )
    
    # Conditions
    description_couverture = models.TextField(
        verbose_name="Description de la couverture",
        help_text="Détails sur ce qui est couvert par la garantie"
    )
    exclusions = models.TextField(
        blank=True,
        verbose_name="Exclusions",
        help_text="Ce qui n'est PAS couvert par la garantie"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='contrats_crees')
    
    class Meta:
        verbose_name = "Contrat de Garantie"
        verbose_name_plural = "Contrats de Garantie"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"{self.get_type_garantie_display()} - {self.projet.nom} ({self.date_debut} → {self.date_fin})"
    
    @property
    def est_actif(self):
        """Vérifie si le contrat est actuellement actif"""
        aujourd_hui = timezone.now().date()
        return self.date_debut <= aujourd_hui <= self.date_fin
    
    @property
    def jours_restants(self):
        """Calcule le nombre de jours restants"""
        if not self.est_actif:
            return 0
        return (self.date_fin - timezone.now().date()).days
    
    def clean(self):
        """Validation métier"""
        from django.db.models import Q
        
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError("La date de fin doit être après la date de début")
        
        # Vérifier qu'il n'y a pas de chevauchement pour le même type
        if self.projet_id:
            chevauchements = ContratGarantie.objects.filter(
                projet=self.projet,
                type_garantie=self.type_garantie
            ).filter(
                Q(date_debut__lte=self.date_fin, date_fin__gte=self.date_debut)
            ).exclude(id=self.id)
            
            if chevauchements.exists():
                raise ValidationError(
                    f"Un contrat {self.get_type_garantie_display()} existe déjà pour cette période"
                )


class TicketMaintenance(models.Model):
    """
    Ticket de maintenance SIMPLIFIÉ - V2
    Unité unique de travail - Inspiré de Jira/GitHub Issues
    """
    
    # Types de demande
    TYPE_DEMANDE_CHOICES = [
        ('BUG', '🐛 Bug / Anomalie'),
        ('AMELIORATION', '✨ Amélioration'),
        ('QUESTION', '❓ Question / Support'),
        ('AUTRE', '📋 Autre'),
    ]
    
    # Priorités
    PRIORITE_CHOICES = [
        ('BASSE', 'Basse'),
        ('NORMALE', 'Normale'),
        ('HAUTE', 'Haute'),
        ('CRITIQUE', 'Critique'),
    ]
    
    # Gravité (impact)
    GRAVITE_CHOICES = [
        ('MINEUR', 'Mineur - Impact faible'),
        ('MAJEUR', 'Majeur - Impact modéré'),
        ('CRITIQUE', 'Critique - Impact sévère'),
        ('BLOQUANT', 'Bloquant - Système inutilisable'),
    ]
    
    # Origine
    ORIGINE_CHOICES = [
        ('CLIENT', 'Client'),
        ('MONITORING', 'Monitoring'),
        ('INTERNE', 'Interne'),
    ]
    
    # Statuts
    STATUT_CHOICES = [
        ('OUVERT', '🆕 Ouvert'),
        ('EN_COURS', '🔵 En cours'),
        ('RESOLU', '✅ Résolu'),
        ('FERME', '🔒 Fermé'),
        ('REJETE', '❌ Rejeté'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_ticket = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='tickets_maintenance')
    contrat_garantie = models.ForeignKey(
        ContratGarantie, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name="Contrat de garantie"
    )
    
    # Description
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description_probleme = models.TextField(verbose_name="Description détaillée")
    
    # Classification
    type_demande = models.CharField(
        max_length=20, 
        choices=TYPE_DEMANDE_CHOICES,
        default='BUG',
        verbose_name="Type de demande"
    )
    priorite = models.CharField(
        max_length=20, 
        choices=PRIORITE_CHOICES,
        default='NORMALE',
        verbose_name="Priorité"
    )
    gravite = models.CharField(
        max_length=20, 
        choices=GRAVITE_CHOICES,
        default='MAJEUR',
        verbose_name="Gravité"
    )
    origine = models.CharField(max_length=20, choices=ORIGINE_CHOICES, default='CLIENT')
    
    # Statut et workflow
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='OUVERT',
        verbose_name="Statut"
    )
    
    # Assignation (ManyToMany pour permettre plusieurs développeurs)
    assignes_a = models.ManyToManyField(
        Utilisateur,
        blank=True,
        related_name='tickets_assignes_v2',
        verbose_name="Assigné à"
    )
    
    # Ancien champ (conservé pour compatibilité)
    assigne_a = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_assignes',
        verbose_name="Assigné à (ancien)"
    )
    
    # Suivi temporel
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_debut_travail = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de début du travail"
    )
    date_resolution = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de résolution"
    )
    date_fermeture = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de fermeture"
    )
    
    # Estimation et suivi du temps
    temps_estime = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Temps estimé (heures)",
        help_text="Estimation initiale du temps nécessaire"
    )
    temps_passe = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Temps passé (heures)",
        help_text="Temps réel passé sur le ticket"
    )
    
    # Résolution
    solution = models.TextField(
        blank=True,
        default='',
        verbose_name="Solution apportée",
        help_text="Description de la solution et des actions effectuées"
    )
    fichiers_modifies = models.TextField(
        blank=True,
        default='',
        verbose_name="Fichiers modifiés",
        help_text="Liste des fichiers modifiés (un par ligne)"
    )
    
    # Garantie
    est_sous_garantie = models.BooleanField(
        default=True,
        verbose_name="Sous garantie",
        help_text="True si couvert par un contrat actif"
    )
    
    # Anciens champs (conservés pour compatibilité)
    est_payant = models.BooleanField(
        default=False,
        verbose_name="Intervention payante (ancien)",
        help_text="True si hors garantie ou garantie inactive"
    )
    raison_rejet = models.TextField(
        blank=True,
        verbose_name="Raison hors garantie",
        help_text="Pourquoi le ticket n'est pas couvert"
    )
    
    # Métadonnées
    cree_par = models.ForeignKey(
        Utilisateur, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='tickets_crees',
        verbose_name="Créé par"
    )
    modifie_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_modifies',
        verbose_name="Modifié par"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Ticket de Maintenance"
        verbose_name_plural = "Tickets de Maintenance"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['numero_ticket']),
            models.Index(fields=['statut']),
            models.Index(fields=['priorite']),
            models.Index(fields=['-date_creation']),
        ]
    
    def __str__(self):
        return f"{self.numero_ticket} - {self.titre}"
    
    def save(self, *args, **kwargs):
        # Générer le numéro de ticket
        if not self.numero_ticket:
            count = TicketMaintenance.objects.count() + 1
            self.numero_ticket = f"MAINT-{count:05d}"
        
        # Vérifier la garantie à la création
        if not self.pk:  # Nouveau ticket
            self._verifier_garantie()
        
        super().save(*args, **kwargs)
    
    def _verifier_garantie(self):
        """
        RÈGLE MÉTIER CRITIQUE:
        Vérifier si le ticket est couvert par la garantie
        """
        if not self.contrat_garantie:
            self.est_sous_garantie = False
            self.est_payant = True
            self.raison_rejet = "Aucun contrat de garantie associé"
            return
        
        if not self.contrat_garantie.est_actif:
            self.est_sous_garantie = False
            self.est_payant = True
            self.raison_rejet = f"Contrat de garantie expiré (fin: {self.contrat_garantie.date_fin})"
            return
        
        # Contrat actif → sous garantie
        self.est_sous_garantie = True
        self.est_payant = False
        self.raison_rejet = ""
    
    @property
    def peut_etre_traite(self):
        """Vérifie si le ticket peut être traité"""
        if self.statut == 'REJETE':
            return False
        
        if self.est_payant:
            # Logique future: vérifier si paiement accepté
            return False
        
        return True
    
    @property
    def temps_ecoule(self):
        """Temps écoulé depuis la création (en heures)"""
        delta = timezone.now() - self.date_creation
        return delta.total_seconds() / 3600
    
    @property
    def sla_depasse(self):
        """Vérifie si le SLA est dépassé"""
        if not self.contrat_garantie:
            return False
        
        if self.statut in ['RESOLU', 'FERME']:
            return False
        
        return self.temps_ecoule > self.contrat_garantie.sla_heures
    
    @property
    def temps_restant_estime(self):
        """Calcule le temps restant estimé"""
        if not self.temps_estime:
            return None
        return max(0, float(self.temps_estime) - float(self.temps_passe))
    
    @property
    def pourcentage_avancement(self):
        """Calcule le pourcentage d'avancement basé sur le temps"""
        if not self.temps_estime or self.temps_estime == 0:
            return 0
        return min(100, int((float(self.temps_passe) / float(self.temps_estime)) * 100))
    
    def demarrer_travail(self, utilisateur):
        """Démarrer le travail sur le ticket"""
        if self.statut == 'OUVERT':
            self.statut = 'EN_COURS'
            self.date_debut_travail = timezone.now()
            self.modifie_par = utilisateur
            self.save()
            
            # Créer un commentaire automatique
            CommentaireTicket.objects.create(
                ticket=self,
                auteur=utilisateur,
                contenu=f"🔵 Travail démarré sur le ticket",
                est_interne=False
            )
    
    def resoudre(self, utilisateur, solution, fichiers_modifies=""):
        """Marquer le ticket comme résolu"""
        if not solution:
            raise ValidationError("Une solution doit être fournie pour résoudre le ticket")
        
        self.statut = 'RESOLU'
        self.date_resolution = timezone.now()
        self.solution = solution
        self.fichiers_modifies = fichiers_modifies
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"✅ Ticket résolu\n\nSolution: {solution[:200]}...",
            est_interne=False
        )
    
    def fermer(self, utilisateur):
        """Fermer le ticket (après validation client)"""
        if self.statut != 'RESOLU':
            raise ValidationError("Le ticket doit être résolu avant d'être fermé")
        
        self.statut = 'FERME'
        self.date_fermeture = timezone.now()
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"🔒 Ticket fermé et validé",
            est_interne=False
        )
    
    def rejeter(self, utilisateur, raison):
        """Rejeter le ticket"""
        if not raison:
            raise ValidationError("Une raison doit être fournie pour rejeter le ticket")
        
        self.statut = 'REJETE'
        self.raison_rejet = raison
        self.modifie_par = utilisateur
        self.save()
        
        # Créer un commentaire automatique
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=utilisateur,
            contenu=f"❌ Ticket rejeté\n\nRaison: {raison}",
            est_interne=False
        )
    
    def assigner(self, utilisateurs, assigne_par):
        """Assigner le ticket à un ou plusieurs développeurs"""
        self.assignes_a.set(utilisateurs)
        self.modifie_par = assigne_par
        self.save()
        
        # Créer un commentaire automatique
        noms = ", ".join([u.get_full_name() for u in utilisateurs])
        CommentaireTicket.objects.create(
            ticket=self,
            auteur=assigne_par,
            contenu=f"👤 Ticket assigné à: {noms}",
            est_interne=False
        )
    
    def ajouter_temps(self, heures, utilisateur):
        """Ajouter du temps passé sur le ticket"""
        self.temps_passe += heures
        self.modifie_par = utilisateur
        self.save()
        if not self.contrat_garantie:
            return False
        
        if self.statut in ['RESOLU', 'FERME']:
            return False
        
        return self.temps_ecoule > self.contrat_garantie.sla_heures


class BilletIntervention(models.Model):
    """
    Billet de sortie - Autorisation d'intervention
    RÈGLE CRITIQUE: Aucune intervention sans billet validé
    """
    TYPE_INTERVENTION_CHOICES = [
        ('ANALYSE', 'Analyse du problème'),
        ('CORRECTION', 'Correction'),
        ('DEPLOIEMENT_CORRECTIF', 'Déploiement correctif'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero_billet = models.CharField(max_length=20, unique=True, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='billets_intervention'
    )
    developpeur_autorise = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='billets_autorises'
    )
    
    # Type et durée
    type_intervention = models.CharField(max_length=30, choices=TYPE_INTERVENTION_CHOICES)
    duree_estimee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Durée estimée (heures)"
    )
    
    # Autorisation
    autorise_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='billets_autorises_par'
    )
    date_autorisation = models.DateTimeField(auto_now_add=True)
    
    # Instructions
    instructions = models.TextField(
        blank=True,
        verbose_name="Instructions spécifiques",
        help_text="Consignes pour le développeur"
    )
    
    class Meta:
        verbose_name = "Billet d'Intervention"
        verbose_name_plural = "Billets d'Intervention"
        ordering = ['-date_autorisation']
    
    def __str__(self):
        return f"{self.numero_billet} - {self.ticket.numero_ticket}"
    
    def save(self, *args, **kwargs):
        if not self.numero_billet:
            count = BilletIntervention.objects.count() + 1
            self.numero_billet = f"BILLET-{count:05d}"
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validation métier"""
        # Vérifier que le ticket peut être traité
        if self.ticket and not self.ticket.peut_etre_traite:
            raise ValidationError("Ce ticket ne peut pas être traité (rejeté ou payant non accepté)")
        
        # Vérifier que le développeur a les permissions
        if self.developpeur_autorise:
            if not self.developpeur_autorise.role_systeme:
                raise ValidationError("Le développeur doit avoir un rôle système")
            
            if self.developpeur_autorise.role_systeme.nom not in ['DEVELOPPEUR', 'CHEF_PROJET']:
                raise ValidationError("Seuls les développeurs et chefs de projet peuvent intervenir")


class InterventionMaintenance(models.Model):
    """
    Intervention technique réelle
    Enregistre les actions effectuées
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation
    billet = models.ForeignKey(
        BilletIntervention,
        on_delete=models.CASCADE,
        related_name='interventions'
    )
    
    # Description des actions
    description_actions = models.TextField(
        verbose_name="Description des actions effectuées"
    )
    
    # Temps
    date_debut = models.DateTimeField(verbose_name="Date de début")
    date_fin = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    temps_passe = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Temps passé (heures)",
        help_text="Temps réel passé sur l'intervention"
    )
    
    # Résultats
    correctif_applique = models.TextField(
        blank=True,
        verbose_name="Correctif appliqué",
        help_text="Détails techniques du correctif"
    )
    fichiers_modifies = models.TextField(
        blank=True,
        verbose_name="Fichiers modifiés",
        help_text="Liste des fichiers modifiés"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Intervention de Maintenance"
        verbose_name_plural = "Interventions de Maintenance"
        ordering = ['-date_debut']
    
    def __str__(self):
        return f"Intervention {self.billet.numero_billet} - {self.date_debut.strftime('%d/%m/%Y')}"
    
    def clean(self):
        """Validation métier"""
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError("La date de fin doit être après la date de début")
        
        # Vérifier que le temps passé est cohérent
        if self.temps_passe and self.billet:
            if self.temps_passe > self.billet.duree_estimee * 2:
                # Avertissement si dépassement de 200%
                pass  # On pourrait lever un warning


class StatutTechnique(models.Model):
    """
    Rapport technique final (obligatoire)
    RÈGLE: Un ticket ne peut être clôturé sans statut technique
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation (OneToOne car un seul statut par intervention)
    intervention = models.OneToOneField(
        InterventionMaintenance,
        on_delete=models.CASCADE,
        related_name='statut_technique'
    )
    
    # Analyse
    probleme_initial = models.TextField(
        verbose_name="Problème initial",
        help_text="Description du problème tel que rapporté"
    )
    cause_reelle = models.TextField(
        verbose_name="Cause réelle (Root Cause)",
        help_text="Analyse de la cause racine du problème"
    )
    solution_apportee = models.TextField(
        verbose_name="Solution apportée",
        help_text="Description détaillée de la solution"
    )
    
    # Impact et risques
    impact_systeme = models.TextField(
        verbose_name="Impact sur le système",
        help_text="Quels composants sont affectés"
    )
    risques_futurs = models.TextField(
        blank=True,
        verbose_name="Risques futurs",
        help_text="Risques identifiés pour l'avenir"
    )
    recommandations = models.TextField(
        blank=True,
        verbose_name="Recommandations",
        help_text="Actions préventives recommandées"
    )
    
    # Validation
    valide_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='statuts_valides'
    )
    date_validation = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    redige_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='statuts_rediges'
    )
    
    class Meta:
        verbose_name = "Statut Technique"
        verbose_name_plural = "Statuts Techniques"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Statut - {self.intervention.billet.ticket.numero_ticket}"
    
    def valider(self, validateur):
        """Valider le statut technique"""
        self.valide_par = validateur
        self.date_validation = timezone.now()
        self.save()
        
        # Marquer le ticket comme résolu
        self.intervention.billet.ticket.resoudre()


# ============================================================================
# MODÈLES SIMPLIFIÉS POUR LA MAINTENANCE V2
# ============================================================================

class CommentaireTicket(models.Model):
    """
    Commentaires et historique du ticket
    Permet le suivi des échanges et des actions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='commentaires',
        verbose_name="Ticket"
    )
    auteur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='commentaires_tickets',
        verbose_name="Auteur"
    )
    
    # Contenu
    contenu = models.TextField(verbose_name="Commentaire")
    
    # Visibilité
    est_interne = models.BooleanField(
        default=False,
        verbose_name="Commentaire interne",
        help_text="Si True, visible seulement par l'équipe technique"
    )
    
    # Pièce jointe (optionnel)
    fichier = models.FileField(
        upload_to='tickets/commentaires/',
        null=True,
        blank=True,
        verbose_name="Pièce jointe"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    modifie = models.BooleanField(default=False, verbose_name="Modifié")
    date_modification = models.DateTimeField(null=True, blank=True, verbose_name="Date de modification")
    
    class Meta:
        verbose_name = "Commentaire de Ticket"
        verbose_name_plural = "Commentaires de Tickets"
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Commentaire sur {self.ticket.numero_ticket} par {self.auteur}"
    
    def modifier(self, nouveau_contenu):
        """Modifier le commentaire"""
        self.contenu = nouveau_contenu
        self.modifie = True
        self.date_modification = timezone.now()
        self.save()


class PieceJointeTicket(models.Model):
    """
    Pièces jointes liées à un ticket
    Captures d'écran, logs, fichiers de configuration, etc.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    ticket = models.ForeignKey(
        TicketMaintenance,
        on_delete=models.CASCADE,
        related_name='pieces_jointes',
        verbose_name="Ticket"
    )
    uploade_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pieces_jointes_uploadees',
        verbose_name="Uploadé par"
    )
    
    # Fichier
    fichier = models.FileField(
        upload_to='tickets/pieces_jointes/',
        verbose_name="Fichier"
    )
    nom_fichier = models.CharField(max_length=255, verbose_name="Nom du fichier")
    taille_fichier = models.IntegerField(verbose_name="Taille (octets)")
    type_mime = models.CharField(max_length=100, blank=True, verbose_name="Type MIME")
    
    # Description
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Description optionnelle de la pièce jointe"
    )
    
    # Métadonnées
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Date d'upload")
    
    class Meta:
        verbose_name = "Pièce Jointe"
        verbose_name_plural = "Pièces Jointes"
        ordering = ['-date_upload']
    
    def __str__(self):
        return f"{self.nom_fichier} - {self.ticket.numero_ticket}"
    
    def save(self, *args, **kwargs):
        if self.fichier:
            self.nom_fichier = self.fichier.name
            self.taille_fichier = self.fichier.size
        super().save(*args, **kwargs)


# ============================================================================
# SYSTÈME D'ACTIVATION SÉCURISÉ DES COMPTES
# ============================================================================
from .models_activation import AccountActivationToken, AccountActivationLog

# ============================================================================
# SYSTÈME DE GESTION BUDGÉTAIRE
# ============================================================================
from .models_budget import LigneBudget, ResumeBudget

# ============================================================================
# SYSTÈME DE GESTION DES FICHIERS
# ============================================================================
from .models_fichiers import FichierProjet
