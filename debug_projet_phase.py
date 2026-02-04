#!/usr/bin/env python3
"""
Debug de la phase du projet pour comprendre pourquoi creer_module ne s'affiche pas
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import Projet, EtapeProjet, TypeEtape

def debug_projet_phase():
    """Debug de la phase du projet"""
    
    print("🔍 Debug de la phase du projet")
    print("=" * 50)
    
    # Récupérer le projet
    projet = Projet.objects.first()
    if not projet:
        print("❌ Aucun projet trouvé")
        return
    
    print(f"📁 Projet: {projet.nom}")
    print(f"🆔 ID: {projet.id}")
    
    # Vérifier l'étape courante
    etape_courante = projet.get_etape_courante()
    
    if not etape_courante:
        print("❌ Aucune étape courante trouvée")
        
        # Lister toutes les étapes du projet
        etapes = projet.etapes.all().order_by('ordre')
        print(f"\n📋 Étapes du projet ({etapes.count()}):")
        for etape in etapes:
            statut = "🟢 ACTIVE" if etape.est_active else "⚪ INACTIVE"
            terminee = "✅ TERMINÉE" if etape.date_fin else "⏳ EN COURS"
            print(f"  {etape.ordre}. {etape.type_etape.get_nom_display()} - {statut} - {terminee}")
            print(f"     Dates: {etape.date_debut_prevue} → {etape.date_fin_prevue or 'En cours'}")
        
        return
    
    print(f"📍 Étape courante: {etape_courante.type_etape.get_nom_display()}")
    print(f"🔧 Type étape nom: {etape_courante.type_etape.nom}")
    print(f"📅 Date début: {etape_courante.date_debut_prevue}")
    print(f"📅 Date fin: {etape_courante.date_fin_prevue or 'En cours'}")
    print(f"🟢 Est active: {etape_courante.est_active}")
    
    # Vérifier si on peut créer des modules
    peut_creer = etape_courante.peut_creer_modules_librement()
    print(f"🏗️ Peut créer modules librement: {peut_creer}")
    
    # Vérifier la condition spécifique
    est_developpement = etape_courante.type_etape.nom == 'DEVELOPPEMENT'
    print(f"💻 Est en phase DEVELOPPEMENT: {est_developpement}")
    
    if not est_developpement:
        print(f"⚠️ PROBLÈME IDENTIFIÉ: Le projet n'est pas en phase DEVELOPPEMENT")
        print(f"   Phase actuelle: {etape_courante.type_etape.nom}")
        print(f"   Phase requise: DEVELOPPEMENT")
        
        # Chercher l'étape de développement
        etape_dev = projet.etapes.filter(type_etape__nom='DEVELOPPEMENT').first()
        if etape_dev:
            print(f"📋 Étape DEVELOPPEMENT trouvée:")
            print(f"   Active: {etape_dev.est_active}")
            print(f"   Dates: {etape_dev.date_debut_prevue} → {etape_dev.date_fin_prevue or 'En cours'}")
            
            if not etape_dev.est_active:
                print("💡 SOLUTION: Activer l'étape DEVELOPPEMENT")
        else:
            print("❌ Aucune étape DEVELOPPEMENT trouvée dans le projet")
    
    print("\n" + "=" * 30)
    print("🔍 Toutes les étapes du projet:")
    
    etapes = projet.etapes.all().order_by('ordre')
    for etape in etapes:
        statut = "🟢 ACTIVE" if etape.est_active else "⚪ INACTIVE"
        terminee = "✅ TERMINÉE" if etape.date_fin else "⏳ EN COURS"
        current = "👈 COURANTE" if etape == etape_courante else ""
        print(f"  {etape.ordre}. {etape.type_etape.get_nom_display()} ({etape.type_etape.nom}) - {statut} - {terminee} {current}")

if __name__ == '__main__':
    debug_projet_phase()