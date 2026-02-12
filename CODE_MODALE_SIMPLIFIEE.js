// Fonction simplifiée pour afficher les détails d'un cas de test
// À remplacer dans templates/core/gestion_cas_tests_tache.html
// Chercher la fonction voirDetailsCas et la remplacer par celle-ci

function voirDetailsCas(casId) {
    const modal = document.getElementById('detailsCasModal');
    const content = document.getElementById('detailsCasContent');
    
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <i class="fas fa-spinner fa-spin text-blue-600 text-xl"></i>
            </div>
            <p class="text-gray-600">Chargement...</p>
        </div>
    `;
    
    modal.classList.remove('hidden');
    
    fetch(`{% url 'details_cas_test' projet.id etape.id '00000000-0000-0000-0000-000000000000' %}`.replace('00000000-0000-0000-0000-000000000000', casId), {
        method: 'GET',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const cas = data.cas;
            
            // Modale simple et épurée
            content.innerHTML = `
                <div class="space-y-3">
                    <!-- Titre et statut -->
                    <div class="flex items-center justify-between pb-3 border-b">
                        <div>
                            <h4 class="text-lg font-semibold text-gray-900">${cas.nom}</h4>
                            <p class="text-xs text-gray-500 mt-1">${cas.numero_cas}</p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-xs font-medium ${
                            cas.statut === 'PASSE' ? 'bg-green-100 text-green-800' :
                            cas.statut === 'ECHEC' ? 'bg-red-100 text-red-800' :
                            cas.statut === 'EN_COURS' ? 'bg-blue-100 text-blue-800' :
                            'bg-gray-100 text-gray-800'
                        }">
                            ${cas.statut_display}
                        </span>
                    </div>
                    
                    <!-- Description -->
                    <div>
                        <p class="text-sm font-medium text-gray-700 mb-1">Description</p>
                        <p class="text-sm text-gray-600">${cas.description}</p>
                    </div>
                    
                    <!-- Étapes -->
                    <div>
                        <p class="text-sm font-medium text-gray-700 mb-1">Étapes d'exécution</p>
                        <pre class="text-sm text-gray-600 whitespace-pre-wrap font-sans">${cas.etapes_execution}</pre>
                    </div>
                    
                    <!-- Résultats attendus -->
                    <div>
                        <p class="text-sm font-medium text-gray-700 mb-1">Résultats attendus</p>
                        <p class="text-sm text-gray-600">${cas.resultats_attendus}</p>
                    </div>
                    
                    ${cas.resultats_obtenus ? `
                    <!-- Résultats obtenus -->
                    <div class="bg-blue-50 p-3 rounded">
                        <p class="text-sm font-medium text-blue-900 mb-1">✓ Résultats obtenus</p>
                        <p class="text-sm text-blue-800">${cas.resultats_obtenus}</p>
                        ${cas.date_execution ? `<p class="text-xs text-blue-600 mt-2">Exécuté le ${cas.date_execution}${cas.executeur ? ' par ' + cas.executeur : ''}</p>` : ''}
                    </div>
                    ` : ''}
                </div>
            `;
        } else {
            content.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-3"></i>
                    <p class="text-gray-600">${data.error || 'Erreur lors du chargement'}</p>
                </div>
            `;
        }
    })
    .catch(error => {
        content.innerHTML = `
            <div class="text-center py-8">
                <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-3"></i>
                <p class="text-gray-600">Erreur de connexion</p>
            </div>
        `;
    });
}
