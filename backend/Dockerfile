FROM python:3.11-slim

# Métadonnées
LABEL maintainer="IRMSIA Medical AI"
LABEL description="Backend FastAPI pour analyse d'imagerie médicale avec blockchain"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY backend/requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copier le code de l'application
COPY backend/ ./backend/
COPY config/ ./config/
COPY utils/ ./utils/
COPY core/ ./core/

# Créer les répertoires nécessaires
RUN mkdir -p /app/storage/uploads /app/storage/encrypted /app/storage/png /app/logs

# Exposer le port
EXPOSE 8000

# Commande par défaut
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

