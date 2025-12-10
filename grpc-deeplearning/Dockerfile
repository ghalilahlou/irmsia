# Dockerfile pour gRPC Deep Learning Service - IRMSIA
FROM python:3.11-slim

# Métadonnées
LABEL maintainer="IRMSIA Medical AI"
LABEL description="gRPC Server pour diagnostic DICOM avec Deep Learning"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système pour le traitement d'images
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Générer les fichiers proto (si nécessaire)
COPY proto/ ./proto/
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    ./proto/irmsia_dicom.proto || echo "Proto files may already exist"

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/models /app/logs /app/data

# Exposer le port gRPC
EXPOSE 50051

# Commande par défaut
CMD ["python", "server/diagnostic_server.py", "--port", "50051"]

