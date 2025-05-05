#!/bin/bash

# Script de démarrage pour le projet FastAPI starter-python

set -e

# Créer un environnement virtuel si non existant
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python -m venv venv
fi

# Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate || source venv/Scripts/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Vérifier si .env existe, sinon copier de .env.example
if [ ! -f ".env" ]; then
    echo "Création du fichier .env à partir de .env.example..."
    cp .env.example .env
    echo "N'oubliez pas de modifier les valeurs dans le fichier .env"
fi

# Appliquer les migrations
echo "Application des migrations..."
alembic upgrade head

# Démarrer l'application
echo "Démarrage de l'application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 