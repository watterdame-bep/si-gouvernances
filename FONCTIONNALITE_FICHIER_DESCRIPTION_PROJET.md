# Fonctionnalité : Fichier de Description du Projet

**Date**: 12 février 2026  
**Statut**: ✅ Implémenté et testé

---

## Résumé

Remplacement du champ texte "description" par un champ fichier dans le formulaire de création de projet. Les utilisateurs peuvent maintenant joindre un fichier Word ou PDF pour décrire le projet, avec possibilité de téléchargement et visualisation.

---

## Modifications Apportées

### 1. Modèle de Données

**Fichier**: `core/models.py`

Ajout du champ `fichier_description` au modèle `Projet`:

```python
fichier_description = models.FileField(
    upload_to='projets/descriptions/',
    null=True,
    blank=True,
    help_text="Fichier de description du projet (PDF, Word)",
    verbose_name="Fichier de description"
)
```

**Migration**: `core/migrations/0039_add_fichier_description_projet.py`

---

### 2. Configuration Django

**Fichier**: `si_gouvernance/settings.py`

Ajout de la configuration pour les fichiers media:

```python
# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Fichier**: `si_gouvernance/urls.py`

Configuration pour servir les fichiers media en développement:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### 3. Formulaire de Création

**Fichier**: `templates/core/creer_projet.html`

**Modifications**:
- Ajout de `enctype="multipart/form-data"` au formulaire
- Remplacement du textarea "description" par un input file
- Validation côté client (taille max 10 MB, formats acceptés)
- Affichage des formats acceptés : PDF, Word (.doc, .docx)

**Validation JavaScript**:
```javascript
// Validation du fichier
const maxSize = 10 * 1024 * 1024; // 10 MB
const allowedTypes = ['application/pdf', 'application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
```

---

### 4. Vue de Création

**Fichier**: `core/views.py` - `creer_projet_view()`

**Modifications**:
- Récupération du fichier avec `request.FILES.get('fichier_description')`
- Validation côté serveur:
  - Taille maximale : 10 MB
  - Extensions autorisées : `.pdf`, `.doc`, `.docx`
  - Types MIME autorisés
- Description automatique : "Voir fichier joint"
- Enregistrement du fichier dans `media/projets/descriptions/`

**Validation serveur**:
```python
max_size = 10 * 1024 * 1024  # 10 MB
allowed_extensions = ['.pdf', '.doc', '.docx']
allowed_content_types = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
```

---

### 5. Vue de Téléchargement Sécurisée

**Fichier**: `core/views.py` - `telecharger_fichier_description_view()`

**Fonctionnalités**:
- Vérification des permissions d'accès au projet
- Vérification de l'existence du fichier
- Détermination automatique du type de contenu
- Téléchargement avec nom de fichier original
- Enregistrement dans l'audit

**Route**: `projets/<uuid:projet_id>/fichier-description/`

---

### 6. Affichage dans les Détails du Projet

**Fichier**: `templates/core/projet_detail.html`

**Section ajoutée dans la sidebar**:

```html
<!-- Fichier de description -->
{% if projet.fichier_description %}
<div class="bg-white rounded-lg p-3 md:p-4 shadow-md border border-white/20">
    <!-- Icône selon le type de fichier (PDF rouge, Word bleu) -->
    <!-- Nom du fichier et taille -->
    <!-- Bouton Télécharger -->
    <!-- Bouton Visualiser (seulement pour PDF) -->
</div>
{% endif %}
```

**Fonctionnalités**:
- Icône adaptée au type de fichier (PDF rouge, Word bleu)
- Affichage du nom et de la taille du fichier
- Bouton "Télécharger" pour tous les formats
- Bouton "Visualiser" uniquement pour les PDF
- Modal de visualisation PDF en plein écran

---

### 7. Modal de Visualisation PDF

**Fonctionnalités**:
- Affichage du PDF dans un iframe
- Modal plein écran (90% de la hauteur)
- Fermeture par clic en dehors ou touche Échap
- Design responsive

**JavaScript**:
```javascript
function visualiserPDF() {
    document.getElementById('visualiserPDFModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}
```

---

## Sécurité

### Validation des Fichiers

1. **Taille maximale**: 10 MB
2. **Extensions autorisées**: `.pdf`, `.doc`, `.docx`
3. **Types MIME vérifiés**: 
   - `application/pdf`
   - `application/msword`
   - `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

### Contrôle d'Accès

- Seuls les membres du projet peuvent télécharger le fichier
- Vérification des permissions avant chaque téléchargement
- Enregistrement dans l'audit pour traçabilité

---

## Structure des Fichiers

```
media/
└── projets/
    └── descriptions/
        ├── nom_fichier_1.pdf
        ├── nom_fichier_2.docx
        └── ...
```

---

## Utilisation

### Création d'un Projet

1. Accéder au formulaire de création de projet
2. Remplir les champs obligatoires (nom, statut, priorité, durée)
3. Sélectionner un fichier de description (PDF ou Word)
4. Cliquer sur "Créer le Projet"

### Consultation du Fichier

1. Accéder aux détails du projet
2. Dans la sidebar, section "Description"
3. Cliquer sur "Télécharger" pour obtenir le fichier
4. Cliquer sur "Visualiser" (PDF uniquement) pour voir le contenu

---

## Avantages

✅ Description plus détaillée et structurée  
✅ Possibilité d'inclure des images, tableaux, graphiques  
✅ Format professionnel (Word/PDF)  
✅ Visualisation directe des PDF  
✅ Téléchargement sécurisé  
✅ Traçabilité via l'audit  

---

## Limitations

- Taille maximale : 10 MB
- Formats acceptés : PDF, Word (.doc, .docx) uniquement
- Visualisation en ligne : PDF uniquement (Word nécessite téléchargement)
- Pas de modification du fichier après création (nécessite recréation du projet)

---

## Tests Recommandés

### Test 1 : Upload PDF
1. Créer un projet avec un fichier PDF
2. Vérifier l'upload réussi
3. Télécharger le fichier
4. Visualiser le PDF dans le modal

### Test 2 : Upload Word
1. Créer un projet avec un fichier .docx
2. Vérifier l'upload réussi
3. Télécharger le fichier
4. Vérifier que le bouton "Visualiser" n'apparaît pas

### Test 3 : Validation Taille
1. Tenter d'uploader un fichier > 10 MB
2. Vérifier le message d'erreur

### Test 4 : Validation Format
1. Tenter d'uploader un fichier .txt ou .jpg
2. Vérifier le message d'erreur

### Test 5 : Permissions
1. Se connecter en tant que membre non affecté au projet
2. Tenter d'accéder au fichier via l'URL directe
3. Vérifier le refus d'accès

---

## Fichiers Modifiés

1. `core/models.py` - Ajout du champ fichier_description
2. `core/migrations/0039_add_fichier_description_projet.py` - Migration
3. `si_gouvernance/settings.py` - Configuration MEDIA
4. `si_gouvernance/urls.py` - Configuration static files
5. `templates/core/creer_projet.html` - Formulaire avec input file
6. `core/views.py` - Vue de création et téléchargement
7. `core/urls.py` - Route de téléchargement
8. `templates/core/projet_detail.html` - Affichage et visualisation

---

## Notes Techniques

- Le champ `description` (TextField) est conservé pour compatibilité
- Valeur par défaut : "Voir fichier joint"
- Les fichiers sont stockés dans `media/projets/descriptions/`
- Le nom du fichier original est préservé
- L'audit enregistre chaque téléchargement

---

**Implémentation terminée avec succès** ✅
