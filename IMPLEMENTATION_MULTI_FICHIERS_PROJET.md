# Implémentation Multi-Fichiers pour les Projets

## Statut: EN COURS

## Objectif
Permettre l'ajout de plusieurs fichiers lors de la création d'un projet et dans les détails du projet, avec possibilité de supprimer des fichiers.

## Ce qui a été fait

### 1. Modèle de données ✅
- Créé `core/models_fichiers.py` avec le modèle `FichierProjet`
- Champs: projet, fichier, nom_original, taille, type_mime, date_ajout, ajoute_par
- Méthodes utilitaires: get_extension(), get_taille_formatee(), get_icone()
- Relation: Un projet peut avoir plusieurs fichiers (ForeignKey avec related_name='fichiers')

### 2. Migration ✅
- Créé `core/migrations/0050_add_fichier_projet.py`
- Crée la table `core_fichierprojet`

### 3. Import dans models.py ✅
- Ajouté l'import de FichierProjet dans core/models.py

### 4. Vues ✅
- Créé `core/views_fichiers.py` avec 3 vues:
  - `ajouter_fichiers_projet`: Ajoute plusieurs fichiers (max 10MB chacun)
  - `supprimer_fichier_projet`: Supprime un fichier (JSON response)
  - `telecharger_fichier_projet`: Télécharge un fichier

### 5. URLs ✅
- Ajouté les routes dans `core/urls.py`:
  - `/projets/<uuid>/fichiers/ajouter/`
  - `/fichiers/<int>/supprimer/`
  - `/fichiers/<int>/telecharger/`

## Ce qui reste à faire

### 6. Formulaire de création de projet ⏳
Modifier `templates/core/creer_projet.html`:
```html
<!-- Remplacer le champ fichier_description par -->
<input 
    type="file" 
    id="fichiers" 
    name="fichiers" 
    multiple
    accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar,.jpg,.jpeg,.png"
    class="..."
>
<p class="text-xs text-gray-500 mt-1">
    <i class="fas fa-info-circle mr-1"></i>
    Vous pouvez sélectionner plusieurs fichiers (max 10MB chacun)
</p>
```

### 7. Vue de création de projet ⏳
Modifier `core/views.py` - fonction `creer_projet_view`:
```python
# Après la création du projet
fichiers = request.FILES.getlist('fichiers')
for fichier in fichiers:
    if fichier.size <= 10 * 1024 * 1024:  # Max 10MB
        type_mime, _ = mimetypes.guess_type(fichier.name)
        FichierProjet.objects.create(
            projet=projet,
            fichier=fichier,
            nom_original=fichier.name,
            taille=fichier.size,
            type_mime=type_mime or 'application/octet-stream',
            ajoute_par=request.user
        )
```

### 8. Affichage dans projet_detail.html ⏳
Ajouter une section pour afficher les fichiers:
```html
<!-- Section Fichiers du Projet -->
<div class="bg-white rounded-lg p-4 shadow-sm border border-slate-200">
    <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold text-slate-900">
            <i class="fas fa-paperclip text-purple-600 mr-2"></i>
            Fichiers Attachés
        </h3>
        {% if can_manage %}
        <button onclick="document.getElementById('ajouterFichiersModal').classList.remove('hidden')"
                class="text-sm bg-purple-600 hover:bg-purple-700 text-white px-3 py-1.5 rounded-lg">
            <i class="fas fa-plus mr-1"></i>Ajouter
        </button>
        {% endif %}
    </div>
    
    {% if projet.fichiers.all %}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
        {% for fichier in projet.fichiers.all %}
        <div class="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between">
                <div class="flex items-start space-x-2 flex-1 min-w-0">
                    <i class="fas {{ fichier.get_icone }} text-lg mt-0.5"></i>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-gray-900 truncate">
                            {{ fichier.nom_original }}
                        </p>
                        <p class="text-xs text-gray-500">
                            {{ fichier.get_taille_formatee }} • {{ fichier.date_ajout|date:"d/m/Y" }}
                        </p>
                    </div>
                </div>
                <div class="flex items-center space-x-1 ml-2">
                    <a href="{% url 'telecharger_fichier_projet' fichier.id %}"
                       class="text-blue-600 hover:text-blue-800 p-1">
                        <i class="fas fa-download text-sm"></i>
                    </a>
                    {% if can_manage %}
                    <button onclick="supprimerFichier({{ fichier.id }}, '{{ fichier.nom_original }}')"
                            class="text-red-600 hover:text-red-800 p-1">
                        <i class="fas fa-trash text-sm"></i>
                    </button>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% else %}
    <p class="text-sm text-gray-500 text-center py-4">
        <i class="fas fa-inbox text-2xl text-gray-300 mb-2"></i><br>
        Aucun fichier attaché
    </p>
    {% endif %}
</div>

<!-- Modale Ajouter Fichiers -->
<div id="ajouterFichiersModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl max-w-md w-full p-6">
        <h3 class="text-lg font-bold mb-4">Ajouter des fichiers</h3>
        <form method="post" action="{% url 'ajouter_fichiers_projet' projet.id %}" enctype="multipart/form-data">
            {% csrf_token %}
            <input type="file" name="fichiers" multiple required
                   class="w-full px-3 py-2 border rounded-lg mb-4">
            <div class="flex gap-2">
                <button type="button" onclick="document.getElementById('ajouterFichiersModal').classList.add('hidden')"
                        class="flex-1 bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg">
                    Annuler
                </button>
                <button type="submit" class="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg">
                    Ajouter
                </button>
            </div>
        </form>
    </div>
</div>

<script>
function supprimerFichier(fichierId, nomFichier) {
    if (!confirm(`Supprimer le fichier "${nomFichier}" ?`)) return;
    
    fetch(`/fichiers/${fichierId}/supprimer/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.error);
        }
    });
}
</script>
```

### 9. Migration de la base de données ⏳
```bash
docker-compose exec web python manage.py migrate
```

## Notes importantes
- Limite de taille: 10MB par fichier
- Types acceptés: PDF, Word, Excel, PowerPoint, images, archives, texte
- Seuls les administrateurs peuvent ajouter/supprimer des fichiers
- Tous les membres du projet peuvent télécharger les fichiers
- Les fichiers sont stockés dans `media/projets/fichiers/YYYY/MM/`

## Prochaines étapes
1. Appliquer les modifications au formulaire de création
2. Modifier la vue de création
3. Ajouter la section fichiers dans projet_detail.html
4. Exécuter la migration
5. Tester l'ajout/suppression/téléchargement
