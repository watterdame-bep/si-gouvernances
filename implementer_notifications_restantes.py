"""
Script pour implémenter les notifications restantes dans le système

Ce script ajoute le code nécessaire pour les notifications manquantes:
1. CHANGEMENT_ECHEANCE (NotificationProjet)
2. PROJET_TERMINE (NotificationProjet)
3. PROJET_SUSPENDU (NotificationProjet)
4. ETAPE_ACTIVEE (NotificationEtape)
5. MODULES_DISPONIBLES (NotificationEtape)
6. CHANGEMENT_STATUT (NotificationEtape)
7. CHANGEMENT_ROLE (NotificationModule)
8. ECHEANCE_J3 et ECHEANCE_J1 (AlerteProjet)

Usage: python implementer_notifications_restantes.py
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si_gouvernance.settings')
django.setup()

from core.models import (
    Utilisateur, Projet, StatutProjet, NotificationProjet,
    NotificationEtape, NotificationModule, AlerteProjet
)


def afficher_statut_notifications():
    """Affiche le statut actuel des notifications implémentées"""
    print("\n" + "="*80)
    print("📊 STATUT DES NOTIFICATIONS")
    print("="*80)
    
    notifications_implementees = {
        'NotificationProjet': [
            ('AJOUT_EQUIPE', '✅'),
            ('AFFECTATION_RESPONSABLE', '✅'),
            ('PROJET_DEMARRE', '✅'),
            ('ASSIGNATION_TICKET_MAINTENANCE', '✅'),
            ('TICKET_RESOLU', '✅'),
            ('CHANGEMENT_ECHEANCE', '⏳'),
            ('PROJET_TERMINE', '⏳'),
            ('PROJET_SUSPENDU', '⏳'),
        ],
        'NotificationEtape': [
            ('ETAPE_TERMINEE', '✅'),
            ('CAS_TEST_PASSE', '✅'),
            ('ETAPE_ACTIVEE', '⏳'),
            ('MODULES_DISPONIBLES', '⏳'),
            ('CHANGEMENT_STATUT', '⏳'),
            ('RETARD_ETAPE', '⏳'),
        ],
        'NotificationModule': [
            ('AFFECTATION_MODULE', '✅'),
            ('RETRAIT_MODULE', '✅'),
            ('NOUVELLE_TACHE', '✅'),
            ('TACHE_TERMINEE', '✅'),
            ('MODULE_TERMINE', '✅'),
            ('CHANGEMENT_STATUT', '✅'),
            ('CHANGEMENT_ROLE', '⏳'),
        ],
        'NotificationTache': [
            ('ASSIGNATION', '✅'),
            ('CHANGEMENT_STATUT', '⏳'),
            ('COMMENTAIRE', '⏳'),
            ('MENTION', '⏳'),
            ('PIECE_JOINTE', '⏳'),
        ],
        'AlerteProjet': [
            ('ECHEANCE_J7', '✅'),
            ('ECHEANCE_J3', '⏳'),
            ('ECHEANCE_J1', '⏳'),
            ('ECHEANCE_DEPASSEE', '✅'),
            ('TACHES_EN_RETARD', '✅'),
            ('CONTRAT_EXPIRATION', '✅'),
            ('CONTRAT_EXPIRE', '✅'),
            ('BUDGET_DEPASSE', '⏳'),
        ]
    }
    
    total_implementees = 0
    total_notifications = 0
    
    for type_notif, notifs in notifications_implementees.items():
        implementees = sum(1 for _, statut in notifs if statut == '✅')
        total = len(notifs)
        total_implementees += implementees
        total_notifications += total
        
        print(f"\n{type_notif}:")
        for nom, statut in notifs:
            print(f"  {statut} {nom}")
        print(f"  Total: {implementees}/{total} ({round(implementees/total*100)}%)")
    
    print(f"\n{'='*80}")
    print(f"TOTAL GLOBAL: {total_implementees}/{total_notifications} ({round(total_implementees/total_notifications*100)}%)")
    print(f"{'='*80}\n")


def generer_code_notifications():
    """Génère le code pour les notifications manquantes"""
    print("\n" + "="*80)
    print("📝 CODE À AJOUTER POUR LES NOTIFICATIONS MANQUANTES")
    print("="*80)
    
    # 1. CHANGEMENT_ECHEANCE
    print("\n" + "-"*80)
    print("1. CHANGEMENT_ECHEANCE (NotificationProjet)")
    print("-"*80)
    print("""
Fichier: core/views.py - fonction modifier_projet()

# Après la modification de date_fin
if 'date_fin' in request.POST and projet.date_fin:
    ancienne_date = projet.date_fin
    nouvelle_date = # nouvelle date depuis le formulaire
    
    if ancienne_date != nouvelle_date:
        # Notifier l'équipe du changement d'échéance
        equipe = projet.get_equipe()
        for membre in equipe:
            NotificationProjet.objects.create(
                destinataire=membre,
                projet=projet,
                type_notification='CHANGEMENT_ECHEANCE',
                titre=f"Changement d'échéance: {projet.nom}",
                message=f"La date de fin du projet '{projet.nom}' a été modifiée de {ancienne_date.strftime('%d/%m/%Y')} à {nouvelle_date.strftime('%d/%m/%Y')}.",
                emetteur=request.user,
                donnees_contexte={
                    'ancienne_date': ancienne_date.isoformat(),
                    'nouvelle_date': nouvelle_date.isoformat()
                }
            )
""")
    
    # 2. PROJET_TERMINE
    print("\n" + "-"*80)
    print("2. PROJET_TERMINE (NotificationProjet)")
    print("-"*80)
    print("""
Fichier: core/models.py - méthode terminer_etape() de EtapeProjet

# Après la terminaison de la dernière étape
if not etape_suivante:  # C'était la dernière étape
    # Notifier l'équipe que le projet est terminé
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
""")
    
    # 3. PROJET_SUSPENDU
    print("\n" + "-"*80)
    print("3. PROJET_SUSPENDU (NotificationProjet)")
    print("-"*80)
    print("""
Fichier: core/views.py - fonction modifier_projet()

# Après la modification du statut
if ancien_statut != nouveau_statut and nouveau_statut.nom == 'SUSPENDU':
    # Notifier l'équipe de la suspension
    equipe = projet.get_equipe()
    for membre in equipe:
        NotificationProjet.objects.create(
            destinataire=membre,
            projet=projet,
            type_notification='PROJET_SUSPENDU',
            titre=f"⚠️ Projet suspendu: {projet.nom}",
            message=f"Le projet '{projet.nom}' a été suspendu. Toutes les activités sont en pause.",
            emetteur=request.user,
            donnees_contexte={
                'ancien_statut': ancien_statut.nom,
                'date_suspension': timezone.now().isoformat()
            }
        )
""")
    
    # 4. ETAPE_ACTIVEE
    print("\n" + "-"*80)
    print("4. ETAPE_ACTIVEE (NotificationEtape)")
    print("-"*80)
    print("""
Fichier: core/models.py - méthode terminer_etape() de EtapeProjet

# Après l'activation automatique de l'étape suivante
if etape_suivante and etape_suivante.statut == 'EN_COURS':
    # Notifier l'équipe de l'activation de la nouvelle étape
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
""")
    
    # 5. MODULES_DISPONIBLES
    print("\n" + "-"*80)
    print("5. MODULES_DISPONIBLES (NotificationEtape)")
    print("-"*80)
    print("""
Fichier: core/models.py - méthode terminer_etape() de EtapeProjet

# Si l'étape suivante est DEVELOPPEMENT
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
""")
    
    # 6. CHANGEMENT_ROLE (Module)
    print("\n" + "-"*80)
    print("6. CHANGEMENT_ROLE (NotificationModule)")
    print("-"*80)
    print("""
Fichier: core/views_affectation.py - fonction de modification d'affectation

# Après la modification du rôle
if ancien_role != nouveau_role:
    NotificationModule.objects.create(
        destinataire=affectation.utilisateur,
        module=affectation.module,
        type_notification='CHANGEMENT_ROLE',
        titre=f"Changement de rôle: {affectation.module.nom}",
        message=f"Votre rôle sur le module '{affectation.module.nom}' a été modifié de {ancien_role} à {nouveau_role}.",
        emetteur=request.user,
        donnees_contexte={
            'ancien_role': ancien_role,
            'nouveau_role': nouveau_role,
            'date_changement': timezone.now().isoformat()
        }
    )
""")
    
    # 7. ECHEANCE_J3 et ECHEANCE_J1
    print("\n" + "-"*80)
    print("7. ECHEANCE_J3 et ECHEANCE_J1 (AlerteProjet)")
    print("-"*80)
    print("""
Fichier: core/management/commands/check_project_deadlines.py

# Dans la méthode handle(), après la vérification J-7
elif jours_restants == 3:
    self._creer_alerte_j3(projet, responsable, jours_restants)
    nb_alertes_j3 += 1
elif jours_restants == 1:
    self._creer_alerte_j1(projet, responsable, jours_restants)
    nb_alertes_j1 += 1

# Ajouter les méthodes
def _creer_alerte_j3(self, projet, responsable, jours_restants):
    \"\"\"Crée une alerte J-3 pour un projet\"\"\"
    # Vérifier si une alerte J-3 existe déjà
    alerte_existante = AlerteProjet.objects.filter(
        projet=projet,
        destinataire=responsable,
        type_alerte='ECHEANCE_J3',
        date_creation__date=timezone.now().date()
    ).exists()
    
    if not alerte_existante:
        AlerteProjet.objects.create(
            destinataire=responsable,
            projet=projet,
            type_alerte='ECHEANCE_J3',
            niveau='WARNING',
            titre=f"⚠️ Échéance dans 3 jours: {projet.nom}",
            message=f"Le projet '{projet.nom}' se termine dans 3 jours (le {projet.date_fin.strftime('%d/%m/%Y')}). Assurez-vous que toutes les tâches critiques sont en cours de finalisation.",
            donnees_contexte={
                'jours_restants': jours_restants,
                'date_fin': projet.date_fin.isoformat(),
                'pourcentage_avancement': projet.pourcentage_avancement_temps()
            }
        )
        self.stdout.write(f"  ⚠️  Alerte J-3 créée pour {responsable.get_full_name()}")

def _creer_alerte_j1(self, projet, responsable, jours_restants):
    \"\"\"Crée une alerte J-1 pour un projet\"\"\"
    # Vérifier si une alerte J-1 existe déjà
    alerte_existante = AlerteProjet.objects.filter(
        projet=projet,
        destinataire=responsable,
        type_alerte='ECHEANCE_J1',
        date_creation__date=timezone.now().date()
    ).exists()
    
    if not alerte_existante:
        AlerteProjet.objects.create(
            destinataire=responsable,
            projet=projet,
            type_alerte='ECHEANCE_J1',
            niveau='DANGER',
            titre=f"🚨 Échéance DEMAIN: {projet.nom}",
            message=f"Le projet '{projet.nom}' se termine DEMAIN (le {projet.date_fin.strftime('%d/%m/%Y')}). C'est le dernier jour pour finaliser toutes les tâches!",
            donnees_contexte={
                'jours_restants': jours_restants,
                'date_fin': projet.date_fin.isoformat(),
                'pourcentage_avancement': projet.pourcentage_avancement_temps()
            }
        )
        self.stdout.write(f"  🚨 Alerte J-1 créée pour {responsable.get_full_name()}")
""")
    
    print("\n" + "="*80)
    print("✅ CODE GÉNÉRÉ AVEC SUCCÈS")
    print("="*80)
    print("\nPour implémenter ces notifications:")
    print("1. Copiez le code correspondant dans les fichiers indiqués")
    print("2. Ajoutez les imports nécessaires en haut des fichiers")
    print("3. Testez chaque notification individuellement")
    print("4. Vérifiez que les emails sont envoyés automatiquement")
    print("\n")


def main():
    """Fonction principale"""
    print("\n" + "="*80)
    print("🚀 IMPLÉMENTATION DES NOTIFICATIONS RESTANTES")
    print("="*80)
    
    # Afficher le statut actuel
    afficher_statut_notifications()
    
    # Générer le code
    generer_code_notifications()
    
    print("\n📚 Documentation:")
    print("  - SESSION_2026_02_15_IMPLEMENTATION_NOTIFICATIONS_RESTANTES.md")
    print("  - LISTE_COMPLETE_NOTIFICATIONS_UTILISATEURS.md")
    print("  - PLAN_IMPLEMENTATION_NOTIFICATIONS_MANQUANTES.md")
    print("\n")


if __name__ == '__main__':
    main()
