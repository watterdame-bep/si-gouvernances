# -*- coding: utf-8 -*-
"""
Template tags pour l'affichage des informations budgétaires
"""

from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def total_materiel(projet):
    """Retourne le total des dépenses en matériel"""
    try:
        total = sum(
            ligne.montant for ligne in projet.lignes_budget.filter(type_ligne='MATERIEL')
        )
        return int(total) if total else 0
    except:
        return 0


@register.filter
def total_services(projet):
    """Retourne le total des dépenses en services"""
    try:
        total = sum(
            ligne.montant for ligne in projet.lignes_budget.filter(type_ligne='SERVICE')
        )
        return int(total) if total else 0
    except:
        return 0


@register.filter
def total_depenses(projet):
    """Retourne le total de toutes les dépenses"""
    try:
        total = sum(ligne.montant for ligne in projet.lignes_budget.all())
        return int(total) if total else 0
    except:
        return 0


@register.filter
def budget_disponible(projet):
    """Retourne le budget disponible (budget total - dépenses)"""
    try:
        budget_total = projet.budget_previsionnel or Decimal('0')
        depenses = sum(ligne.montant for ligne in projet.lignes_budget.all()) or Decimal('0')
        disponible = budget_total - depenses
        return int(disponible)
    except:
        return int(projet.budget_previsionnel or 0)


@register.filter
def pourcentage_utilise(projet):
    """Retourne le pourcentage du budget utilisé"""
    try:
        budget_total = float(projet.budget_previsionnel or 0)
        if budget_total == 0:
            return 0
        depenses = float(sum(ligne.montant for ligne in projet.lignes_budget.all()) or 0)
        return round((depenses / budget_total) * 100, 1)
    except:
        return 0


@register.filter
def statut_budget(projet):
    """Retourne le statut du budget (OK, ATTENTION, CRITIQUE, DEPASSE)"""
    try:
        pourcentage = pourcentage_utilise(projet)
        disponible = budget_disponible(projet)
        
        if disponible < 0:
            return 'DEPASSE'
        elif pourcentage >= 90:
            return 'CRITIQUE'
        elif pourcentage >= 75:
            return 'ATTENTION'
        else:
            return 'OK'
    except:
        return 'OK'


@register.filter
def couleur_statut_budget(projet):
    """Retourne la couleur associée au statut du budget"""
    statut = statut_budget(projet)
    couleurs = {
        'OK': 'green',
        'ATTENTION': 'yellow',
        'CRITIQUE': 'orange',
        'DEPASSE': 'red'
    }
    return couleurs.get(statut, 'green')
