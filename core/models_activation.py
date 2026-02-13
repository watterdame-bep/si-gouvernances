# -*- coding: utf-8 -*-
"""
Modèle pour la gestion sécurisée de l'activation des comptes utilisateurs.

Ce système remplace l'ancien mécanisme d'envoi de mot de passe par email
par un système d'activation sécurisé professionnel.

Principes de sécurité :
- Le token n'est JAMAIS stocké en clair
- Expiration stricte de 24 heures
- Limitation des tentatives (5 max)
- Invalidation automatique des anciens tokens
- Audit complet de toutes les actions
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
import hashlib
import secrets


class AccountActivationToken(models.Model):
    """
    Token sécurisé pour l'activation de compte utilisateur.
    
    Sécurité :
    - token_hash : Hash SHA256 du token (jamais le token en clair)
    - expires_at : Expiration stricte côté serveur (24h)
    - attempts : Compteur de tentatives (max 5)
    - is_used : Marqueur d'utilisation unique
    """
    
    user = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.CASCADE,
        related_name='activation_tokens',
        verbose_name="Utilisateur"
    )
    
    # Token hashé (SHA256) - JAMAIS le token en clair
    token_hash = models.CharField(
        max_length=64,  # SHA256 = 64 caractères hex
        unique=True,
        db_index=True,
        verbose_name="Hash du token"
    )
    
    # Dates et expiration
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    expires_at = models.DateTimeField(
        db_index=True,
        verbose_name="Date d'expiration"
    )
    
    # Statut et utilisation
    is_used = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Token utilisé"
    )
    
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'utilisation"
    )
    
    invalidated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'invalidation"
    )
    
    # Sécurité anti-brute force
    attempts = models.IntegerField(
        default=0,
        verbose_name="Nombre de tentatives"
    )
    
    # Traçabilité
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP de création"
    )
    
    last_attempt_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dernière IP de tentative"
    )
    
    last_attempt_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière tentative"
    )
    
    class Meta:
        verbose_name = "Token d'activation"
        verbose_name_plural = "Tokens d'activation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used', 'expires_at']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        status = "Utilisé" if self.is_used else ("Expiré" if self.is_expired() else "Actif")
        return f"Token {status} pour {self.user.username}"
    
    def save(self, *args, **kwargs):
        """
        Définit automatiquement la date d'expiration à 24h si non définie.
        """
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """
        Vérifie si le token a expiré (vérification côté serveur).
        
        Returns:
            bool: True si expiré, False sinon
        """
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """
        Vérifie si le token est valide pour utilisation.
        
        Un token est valide si :
        - Il n'a pas été utilisé
        - Il n'a pas expiré
        - Il n'a pas dépassé le nombre de tentatives
        - Il n'a pas été invalidé manuellement
        
        Returns:
            bool: True si valide, False sinon
        """
        if self.is_used:
            return False
        if self.is_expired():
            return False
        if self.attempts >= 5:  # Max 5 tentatives
            return False
        if self.invalidated_at:
            return False
        return True
    
    def increment_attempts(self, ip_address=None):
        """
        Incrémente le compteur de tentatives (protection anti-brute force).
        
        Args:
            ip_address: Adresse IP de la tentative
        """
        self.attempts += 1
        self.last_attempt_at = timezone.now()
        if ip_address:
            self.last_attempt_ip = ip_address
        self.save(update_fields=['attempts', 'last_attempt_at', 'last_attempt_ip'])
    
    def mark_as_used(self):
        """
        Marque le token comme utilisé (invalidation définitive).
        """
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    def invalidate(self):
        """
        Invalide manuellement le token (par exemple si un nouveau est généré).
        """
        self.invalidated_at = timezone.now()
        self.save(update_fields=['invalidated_at'])
    
    @staticmethod
    def generate_token():
        """
        Génère un token cryptographiquement sécurisé.
        
        Utilise secrets.token_urlsafe() qui génère un token :
        - Aléatoire cryptographiquement
        - URL-safe (peut être utilisé dans une URL)
        - De 32 bytes = 43 caractères base64
        
        Returns:
            str: Token sécurisé
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_token(token):
        """
        Hash un token avec SHA256.
        
        Le token n'est JAMAIS stocké en clair en base de données.
        Seul le hash est stocké.
        
        Args:
            token: Token en clair
            
        Returns:
            str: Hash SHA256 du token (64 caractères hex)
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    @classmethod
    def create_for_user(cls, user, ip_address=None):
        """
        Crée un nouveau token d'activation pour un utilisateur.
        
        Sécurité :
        1. Invalide tous les tokens actifs existants
        2. Génère un nouveau token cryptographiquement sécurisé
        3. Stocke uniquement le hash du token
        4. Définit l'expiration à 24h
        
        Args:
            user: Instance de Utilisateur
            ip_address: Adresse IP de la demande
            
        Returns:
            tuple: (token_instance, token_en_clair)
        """
        # 1. Invalider tous les tokens actifs existants pour cet utilisateur
        cls.objects.filter(
            user=user,
            is_used=False,
            invalidated_at__isnull=True
        ).update(invalidated_at=timezone.now())
        
        # 2. Générer un nouveau token sécurisé
        token_plain = cls.generate_token()
        token_hash = cls.hash_token(token_plain)
        
        # 3. Créer l'instance en base (avec le hash uniquement)
        token_instance = cls.objects.create(
            user=user,
            token_hash=token_hash,
            ip_address=ip_address,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # 4. Retourner l'instance ET le token en clair (pour l'email)
        # Le token en clair ne sera JAMAIS stocké
        return token_instance, token_plain
    
    @classmethod
    def verify_token(cls, user, token_plain, ip_address=None):
        """
        Vérifie un token pour un utilisateur.
        
        Processus de vérification :
        1. Hash le token fourni
        2. Cherche le token en base
        3. Vérifie la validité
        4. Incrémente les tentatives
        
        Args:
            user: Instance de Utilisateur
            token_plain: Token en clair à vérifier
            ip_address: Adresse IP de la tentative
            
        Returns:
            AccountActivationToken ou None: Instance si valide, None sinon
        """
        # 1. Hash le token fourni
        token_hash = cls.hash_token(token_plain)
        
        # 2. Chercher le token en base
        try:
            token_instance = cls.objects.get(
                user=user,
                token_hash=token_hash
            )
        except cls.DoesNotExist:
            return None
        
        # 3. Incrémenter les tentatives (même si invalide)
        token_instance.increment_attempts(ip_address)
        
        # 4. Vérifier la validité
        if not token_instance.is_valid():
            return None
        
        return token_instance


class AccountActivationLog(models.Model):
    """
    Journal d'audit pour les activations de compte.
    
    Trace toutes les actions liées à l'activation :
    - Création de token
    - Tentatives d'activation
    - Succès/échecs
    - Renvois de lien
    """
    
    ACTION_CHOICES = [
        ('TOKEN_CREATED', 'Token créé'),
        ('TOKEN_SENT', 'Email envoyé'),
        ('ACTIVATION_ATTEMPT', 'Tentative d\'activation'),
        ('ACTIVATION_SUCCESS', 'Activation réussie'),
        ('ACTIVATION_FAILED', 'Activation échouée'),
        ('TOKEN_EXPIRED', 'Token expiré'),
        ('TOKEN_RESENT', 'Token renvoyé'),
        ('TOO_MANY_ATTEMPTS', 'Trop de tentatives'),
    ]
    
    user = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name='activation_logs'
    )
    
    token = models.ForeignKey(
        AccountActivationToken,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        blank=True,
        default=''
    )
    
    details = models.TextField(
        blank=True,
        default=''
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log d'activation"
        verbose_name_plural = "Logs d'activation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user.username} - {self.created_at}"
