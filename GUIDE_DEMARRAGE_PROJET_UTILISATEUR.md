# 📘 Guide Utilisateur - Démarrage et Suivi des Projets

## 🎯 Vue d'ensemble

Le système permet maintenant de gérer le temps des projets de manière professionnelle :
- Le projet ne démarre que lorsque le responsable le décide
- Les dates sont calculées automatiquement
- Des alertes sont envoyées à J-7 de la fin

## 👥 Pour l'Administrateur

### Créer un Projet

1. **Aller sur "Nouveau Projet"**
2. **Remplir le formulaire** :
   - Nom du projet
   - Description
   - Client
   - **Durée estimée** : Choisir la durée et l'unité (jours, semaines, mois)
   - Statut
   - Priorité
3. **Créer le projet**
4. **Assigner un responsable** dans les paramètres du projet

### Résultat
- Le projet est créé avec une durée définie
- Le responsable reçoit une notification
- Le projet n'est pas encore démarré (pas de dates)

## 👤 Pour le Responsable du Projet

### Démarrer le Projet

1. **Ouvrir le projet** (cliquer sur le nom)
2. **Dans la sidebar droite**, voir le bloc "Échéances"
3. **Voir le message** : "Projet non démarré - Durée prévue : X jours"
4. **Cliquer sur le bouton vert** "Commencer le projet"
5. **Confirmer** le démarrage

### Résultat
- ✅ Date de début = Aujourd'hui
- ✅ Date de fin = Aujourd'hui + Durée
- ✅ Statut = EN_COURS
- ✅ L'équipe reçoit une notification
- ✅ Affichage des informations temporelles

## 📊 Affichage Temporel

### Informations Visibles

**Dates** :
- 🟢 Date de début
- 🔴 Date de fin prévue

**Indicateurs** :
- Badge coloré avec jours restants :
  - 🟢 Vert : Plus de 14 jours
  - 🔵 Bleu : 8-14 jours
  - 🟡 Jaune : 4-7 jours
  - 🔴 Rouge : 0-3 jours ou retard

**Barre de progression** :
- Affiche le pourcentage d'avancement temporel
- Couleur change selon l'avancement :
  - 🟢 Vert : 0-50%
  - 🟡 Jaune : 50-75%
  - 🟠 Orange : 75-90%
  - 🔴 Rouge : 90-100%

## 🔔 Notifications Automatiques

### Notification de Démarrage

**Qui reçoit** : Tous les membres de l'équipe (sauf celui qui démarre)

**Contenu** :
```
Titre : "Le projet X a démarré"
Message : "Le projet a été démarré par [Nom]. 
          Date de fin prévue : DD/MM/YYYY"
```

### Alerte J-7 (7 jours avant la fin)

**Qui reçoit** :
- Administrateur (créateur du projet)
- Responsable du projet
- Tous les membres de l'équipe

**Contenu** :
```
Titre : "⚠️ Projet X - Fin dans 7 jours"
Message : "Le projet se termine dans 7 jours (DD/MM/YYYY).
          [Message personnalisé selon le rôle]"
```

**Quand** : Automatiquement chaque jour à 8h00 (via planificateur)

## 📱 Exemples d'Utilisation

### Exemple 1 : Projet de 30 jours

```
1. Admin crée le projet avec durée = 30 jours
2. Admin assigne Bob comme responsable
3. Bob reçoit une notification
4. Bob ouvre le projet et clique "Commencer le projet"
5. Système calcule :
   - Date début : 09/02/2026
   - Date fin : 11/03/2026
6. L'équipe reçoit une notification
7. Le 04/03/2026 (J-7), tout le monde reçoit une alerte
```

### Exemple 2 : Projet de 2 semaines

```
1. Admin crée le projet avec durée = 2 semaines
2. Système convertit : 2 semaines = 14 jours
3. Responsable démarre le projet
4. Dates calculées :
   - Début : 09/02/2026
   - Fin : 23/02/2026
5. Alerte J-7 le 16/02/2026
```

## ⚠️ Points Importants

### Qui Peut Démarrer un Projet ?

**Uniquement le responsable du projet**

Si vous n'êtes pas le responsable, vous ne verrez pas le bouton "Commencer le projet".

### Quand Démarrer un Projet ?

**Démarrez le projet quand vous commencez réellement à travailler dessus**

Ne démarrez pas trop tôt car les dates seront calculées à partir du moment du démarrage.

### Peut-on Modifier les Dates ?

**Actuellement, non**

Une fois le projet démarré, les dates sont fixées. Si vous devez les modifier, contactez l'administrateur.

### Que se Passe-t-il si le Projet est en Retard ?

**Le badge devient rouge** et affiche "X jours de retard"

L'équipe continue de recevoir des alertes.

## 🎨 Codes Couleur

### Badges Jours Restants

| Couleur | Signification | Jours Restants |
|---------|---------------|----------------|
| 🟢 Vert | Tout va bien | > 14 jours |
| 🔵 Bleu | À surveiller | 8-14 jours |
| 🟡 Jaune | Attention | 4-7 jours |
| 🔴 Rouge | Urgent | 0-3 jours |
| 🔴 Rouge | Retard | < 0 jours |

### Barre de Progression

| Couleur | Avancement |
|---------|------------|
| 🟢 Vert | 0-50% |
| 🟡 Jaune | 50-75% |
| 🟠 Orange | 75-90% |
| 🔴 Rouge | 90-100% |

## ❓ FAQ

### Q : Je ne vois pas le bouton "Commencer le projet"

**R** : Vérifiez que :
- Vous êtes le responsable du projet
- Le projet a une durée définie
- Le projet n'est pas déjà démarré

### Q : Puis-je démarrer un projet plus tard ?

**R** : Oui ! Le projet reste en attente jusqu'à ce que vous cliquiez sur "Commencer le projet".

### Q : Les alertes J-7 sont-elles automatiques ?

**R** : Oui, elles sont envoyées automatiquement chaque jour à 8h00 par le système.

### Q : Puis-je changer la durée après création ?

**R** : Actuellement, vous devez contacter l'administrateur pour modifier la durée.

### Q : Que se passe-t-il si je démarre par erreur ?

**R** : Contactez l'administrateur pour réinitialiser les dates.

## 📞 Support

Pour toute question ou problème, contactez l'administrateur système.

---

**Date** : 09/02/2026  
**Version** : 1.0  
**Système** : SI-Gouvernance JCM
