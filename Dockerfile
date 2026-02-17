# ============================================================================
# DOCKERFILE MULTI-STAGE POUR SI-GOUVERNANCE
# ============================================================================
# Targets:
# - development: Image avec code monté en volume
# - production: Image standalone avec code copié et Tailwind CSS compilé
# ============================================================================

# ============================================================================
# STAGE 1: TAILWIND CSS BUILDER
# ============================================================================
FROM node:18-alpine as tailwind-builder

WORKDIR /app

# Copie des fichiers de configuration Tailwind
COPY package*.json ./
COPY tailwind.config.js ./
COPY theme/static/css/input.css ./theme/static/css/

# Copie des templates pour l'analyse Tailwind
COPY templates/ ./templates/
COPY core/ ./core/

# Installation et build de Tailwind CSS
RUN npm install && \
    npx tailwindcss -i ./theme/static/css/input.css -o ./theme/static/css/output.css --minify

# ============================================================================
# STAGE 2: BASE
# ============================================================================
FROM python:3.11-slim as base

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Répertoire de travail
WORKDIR /app

# ============================================================================
# STAGE 3: BUILDER (Installation des dépendances)
# ============================================================================
FROM base as builder

# Installation des dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des requirements Python
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 4: DEVELOPMENT (avec volume monté)
# ============================================================================
FROM base as development

# Installation des dépendances runtime + outils de dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    wget \
    vim \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copie des packages Python depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajout des binaires Python au PATH
ENV PATH=/root/.local/bin:$PATH

# Création des dossiers nécessaires
RUN mkdir -p /app/logs/celery \
    && mkdir -p /app/staticfiles \
    && mkdir -p /app/media \
    && chmod -R 755 /app/logs

# Exposition du port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Commande par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ============================================================================
# STAGE 5: PRODUCTION (image standalone)
# ============================================================================
FROM base as production

# Installation des dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    wget \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copie des packages Python depuis le builder
COPY --from=builder /root/.local /root/.local

# Ajout des binaires Python au PATH
ENV PATH=/root/.local/bin:$PATH

# Copie du code de l'application (PAS de volume en production)
COPY . .

# Copie du CSS Tailwind compilé depuis le builder
COPY --from=tailwind-builder /app/theme/static/css/output.css /app/theme/static/css/output.css

# Création des dossiers nécessaires
RUN mkdir -p /app/logs/celery \
    && mkdir -p /app/staticfiles \
    && mkdir -p /app/media \
    && chmod -R 755 /app/logs

# Collecte des fichiers statiques (peut être overridé au runtime)
RUN python manage.py collectstatic --noinput || true

# Création d'un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Exposition du port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Utiliser l'utilisateur non-root
USER appuser

# Commande par défaut (Gunicorn en production)
CMD ["gunicorn", "si_gouvernance.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
