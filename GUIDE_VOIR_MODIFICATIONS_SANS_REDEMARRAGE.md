# Guide: Voir les Modifications Sans Redémarrer le PC

## 🎯 Problème

Vous devez redémarrer votre PC pour voir les modifications apportées au code Django.

## ✅ Solutions (par ordre de priorité)

### 1. **Forcer le Rechargement du Navigateur** ⭐ (Solution la plus courante)

Le navigateur met en cache les fichiers CSS, JavaScript et HTML pour accélérer le chargement.

#### Raccourcis Clavier

**Windows/Linux**:
- `Ctrl + Shift + R` (Chrome, Firefox, Edge)
- `Ctrl + F5` (Alternative)
- `Shift + F5` (Alternative)

**Mac**:
- `Cmd + Shift + R` (Chrome, Firefox, Safari)
- `Cmd + Option + R` (Alternative Safari)

#### Désactiver le Cache Pendant le Développement

**Chrome/Edge**:
1. Appuyez sur `F12` pour ouvrir les DevTools
2. Allez dans l'onglet **"Network"**
3. Cochez **"Disable cache"**
4. Gardez les DevTools ouverts pendant le développement

**Firefox**:
1. Appuyez sur `F12` pour ouvrir les DevTools
2. Allez dans l'onglet **"Network"**
3. Cochez **"Disable HTTP cache"**
4. Gardez les DevTools ouverts

**Safari**:
1. Menu **Develop** → **Disable Caches**
2. Si le menu Develop n'est pas visible: Preferences → Advanced → "Show Develop menu"

### 2. **Vérifier que le Serveur Django Tourne**

Le serveur Django doit être **en cours d'exécution** pour voir les modifications.

#### Vérifier si le Serveur Tourne

```bash
# Ouvrir un terminal et vérifier
netstat -ano | findstr :8000
```

Si rien ne s'affiche, le serveur n'est pas lancé.

#### Démarrer le Serveur Django

```bash
python manage.py runserver
```

**Sortie attendue**:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 06, 2026 - 15:30:00
Django version 5.2.5, using settings 'si_gouvernance.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

#### Signes que le Serveur Recharge Automatiquement

Quand vous modifiez un fichier, vous devriez voir dans le terminal:
```
[06/Feb/2026 15:31:23] "GET /projets/ HTTP/1.1" 200 12345
Watching for file changes with StatReloader
```

### 3. **Vider Complètement le Cache du Navigateur**

Si le rechargement forcé ne suffit pas:

**Chrome/Edge**:
1. `Ctrl + Shift + Delete`
2. Sélectionner **"Cached images and files"**
3. Période: **"All time"**
4. Cliquer sur **"Clear data"**

**Firefox**:
1. `Ctrl + Shift + Delete`
2. Cocher **"Cache"**
3. Période: **"Everything"**
4. Cliquer sur **"Clear Now"**

### 4. **Mode Navigation Privée** (Test Rapide)

Pour tester rapidement sans cache:
- **Chrome/Edge**: `Ctrl + Shift + N`
- **Firefox**: `Ctrl + Shift + P`
- **Safari**: `Cmd + Shift + N`

Ouvrez votre application dans cette fenêtre. Si ça fonctionne, c'est un problème de cache.

### 5. **Redémarrer le Serveur Django** (Si nécessaire)

Parfois, pour certaines modifications (models, settings), il faut redémarrer le serveur:

1. Dans le terminal où tourne le serveur: `Ctrl + C`
2. Relancer: `python manage.py runserver`

**Quand redémarrer le serveur**:
- ✅ Modifications de `models.py`
- ✅ Modifications de `settings.py`
- ✅ Ajout de nouveaux fichiers Python
- ✅ Installation de nouveaux packages
- ❌ Modifications de templates (`.html`)
- ❌ Modifications de views (`.py`)
- ❌ Modifications de CSS/JavaScript

### 6. **Vérifier les Fichiers Statiques** (CSS/JS)

Si les modifications CSS/JavaScript ne s'affichent pas:

#### Collecter les Fichiers Statiques

```bash
python manage.py collectstatic --noinput
```

#### Vérifier STATIC_URL dans settings.py

Le fichier `settings.py` devrait avoir:
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### 7. **Utiliser django-browser-reload** (Recommandé)

Cette extension recharge automatiquement le navigateur quand vous modifiez un fichier.

#### Installation

```bash
pip install django-browser-reload
```

#### Configuration

Dans `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'django_browser_reload',
]

MIDDLEWARE = [
    # ...
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]
```

Dans `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('__reload__/', include('django_browser_reload.urls')),
]
```

Maintenant, le navigateur se recharge automatiquement à chaque modification!

## 🔍 Diagnostic: Pourquoi Ça Ne Marche Pas?

### Vérifier DEBUG = True

Dans `si_gouvernance/settings.py`:
```python
DEBUG = True  # Doit être True en développement
```

### Vérifier que le Serveur Détecte les Changements

Modifiez un fichier et regardez le terminal. Vous devriez voir:
```
Watching for file changes with StatReloader
```

Si vous ne voyez pas ce message, le serveur ne surveille pas les fichiers.

### Vérifier les Permissions de Fichiers

Sur Windows, parfois les fichiers sont verrouillés. Fermez tous les éditeurs de texte et IDEs qui pourraient bloquer les fichiers.

## 📋 Checklist de Dépannage

Quand une modification ne s'affiche pas:

- [ ] 1. Forcer le rechargement: `Ctrl + Shift + R`
- [ ] 2. Vérifier que le serveur Django tourne
- [ ] 3. Regarder le terminal pour les erreurs
- [ ] 4. Vider le cache du navigateur
- [ ] 5. Essayer en navigation privée
- [ ] 6. Redémarrer le serveur Django
- [ ] 7. Vérifier que le fichier est bien sauvegardé
- [ ] 8. Vérifier qu'il n'y a pas d'erreurs de syntaxe

## 🎓 Bonnes Pratiques

### Pendant le Développement

1. **Gardez les DevTools ouverts** avec "Disable cache" activé
2. **Utilisez un terminal dédié** pour le serveur Django
3. **Surveillez les messages du serveur** pour détecter les erreurs
4. **Sauvegardez toujours** avant de tester (`Ctrl + S`)
5. **Utilisez django-browser-reload** pour le rechargement automatique

### Workflow Recommandé

```
1. Modifier le code
2. Sauvegarder (Ctrl + S)
3. Regarder le terminal (erreurs?)
4. Recharger le navigateur (Ctrl + Shift + R)
5. Tester la modification
```

## 🚫 Ce Qu'il NE FAUT PAS Faire

- ❌ **Redémarrer le PC** pour voir les modifications
- ❌ **Fermer/Rouvrir le navigateur** à chaque fois
- ❌ **Arrêter/Relancer le serveur** pour les templates
- ❌ **Modifier les fichiers sans sauvegarder**
- ❌ **Ignorer les erreurs dans le terminal**

## 💡 Astuces Supplémentaires

### Raccourci pour Tout Rafraîchir

Créez un script batch `refresh.bat`:
```batch
@echo off
echo Rechargement du serveur Django...
taskkill /F /IM python.exe
timeout /t 2
start cmd /k python manage.py runserver
echo Serveur redémarré!
```

### Extension Chrome Recommandée

**LiveReload**: Recharge automatiquement la page quand les fichiers changent.

### Configuration VS Code

Si vous utilisez VS Code, installez:
- **Python** (extension officielle)
- **Django** (extension pour templates)
- **Auto Save**: File → Auto Save (pour sauvegarder automatiquement)

## 📊 Résumé

| Type de Modification | Action Requise |
|---------------------|----------------|
| Templates HTML | Ctrl + Shift + R |
| CSS/JavaScript | Ctrl + Shift + R + Vider cache |
| Views Python | Ctrl + Shift + R |
| Models Python | Redémarrer serveur |
| Settings Python | Redémarrer serveur |
| URLs Python | Ctrl + Shift + R |

## ✅ Conclusion

**Vous ne devriez JAMAIS avoir besoin de redémarrer votre PC** pour voir les modifications Django. Dans 99% des cas, un simple `Ctrl + Shift + R` suffit. Si ça ne marche pas, c'est probablement un problème de cache du navigateur ou le serveur Django n'est pas lancé.

**Solution la plus simple**: Gardez les DevTools ouverts avec "Disable cache" activé pendant le développement!
