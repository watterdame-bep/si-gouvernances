# -*- coding: utf-8 -*-
"""
Modèles pour la gestion budgétaire des projets
Permet de suivre les dépenses en matériel et services
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import uuid


class LigneBudget(models.Model):
    """
    Ligne budgétaire pour un projet
    Représente une dépense en matériel ou service
    """
    TYPE_CHOICES = [
        ('MATERIEL', 'Matériel'),
        ('SERVICE', 'Service'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='lignes_budget')
    
    # Type et montant
    type_ligne = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de dépense")
    montant = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant")
    description = models.CharField(max_length=255, verbose_name="Nom de la dépense")
    
    # Métadonnées
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    ajoute_par = models.ForeignKey('Utilisateur', on_delete=models.PROTECT, related_name='lignes_budget_ajoutees')
    
    class Meta:
        verbose_name = "Ligne Budgétaire"
        verbose_name_plural = "Lignes Budgétaires"
        ordering = ['-date_ajout']
        indexes = [
            models.Index(fields=['projet', 'type_ligne']),
            models.Index(fields=['date_ajout']),
        ]
    
    def clean(self):
        """Validation des données"""
        if self.montant <= 0:
            raise ValidationError({'montant': 'Le montant doit être supérieur à 0.'})
    
    def __str__(self):
        return f"{self.get_type_ligne_display()} - {self.montant}€ ({self.projet.nom})"
    
    def get_montant_formate(self):
        """Retourne le montant formaté"""
        return f"{self.montant:,.2f}€"
    
    def get_description_courte(self, max_length=50):
        """Retourne une description tronquée"""
        if not self.description:
            return "Sans nom"
        if len(self.description) <= max_length:
            return self.description
        return f"{self.description[:max_length]}..."


class ResumeBudget:
    """
    Classe utilitaire pour calculer le résumé budgétaire d'un projet
    Non persistée en base de données
    """
    def __init__(self, projet):
        self.projet = projet
        self._calculer()
    
    def _calculer(self):
        """Calcule tous les totaux"""
        lignes = self.projet.lignes_budget.all()
        
        self.total_materiel = sum(
            ligne.montant for ligne in lignes if ligne.type_ligne == 'MATERIEL'
        ) or Decimal('0')
        
        self.total_services = sum(
            ligne.montant for ligne in lignes if ligne.type_ligne == 'SERVICE'
        ) or Decimal('0')
        
        self.total_depenses = self.total_materiel + self.total_services
        self.budget_total = self.projet.budget_previsionnel or Decimal('0')
        self.budget_disponible = self.budget_total - self.total_depenses
        
        # Pourcentages
        if self.budget_total > 0:
            self.pourcentage_utilise = (self.total_depenses / self.budget_total) * 100
            self.pourcentage_disponible = (self.budget_disponible / self.budget_total) * 100
        else:
            self.pourcentage_utilise = 0
            self.pourcentage_disponible = 0
        
        # Statut
        if self.budget_disponible < 0:
            self.statut = 'DEPASSE'
            self.statut_couleur = 'red'
        elif self.pourcentage_utilise >= 90:
            self.statut = 'CRITIQUE'
            self.statut_couleur = 'orange'
        elif self.pourcentage_utilise >= 75:
            self.statut = 'ATTENTION'
            self.statut_couleur = 'yellow'
        else:
            self.statut = 'OK'
            self.statut_couleur = 'green'
    
    def to_dict(self):
        """Retourne un dictionnaire avec toutes les données"""
        return {
            'budget_total': float(self.budget_total),
            'total_materiel': float(self.total_materiel),
            'total_services': float(self.total_services),
            'total_depenses': float(self.total_depenses),
            'budget_disponible': float(self.budget_disponible),
            'pourcentage_utilise': round(self.pourcentage_utilise, 2),
            'pourcentage_disponible': round(self.pourcentage_disponible, 2),
            'statut': self.statut,
            'statut_couleur': self.statut_couleur,
        }
