# Python FastAPI Starter Project

Un projet starter Python backend basé sur FastAPI avec PostgreSQL et OAuth2.

## Technologies

- FastAPI
- PostgreSQL (avec SQLAlchemy)
- OAuth2 & OpenID Connect
- Asyncio
- Tests avec Pytest

## Structure du projet

```
.
├── app                     # Application principale
│   ├── api                 # API endpoints
│   ├── core                # Configuration de base et utilitaires
│   ├── db                  # Configuration de la base de données
│   ├── models              # Modèles SQLAlchemy (DB models)
│   ├── schemas             # Schémas Pydantic (validations, APIs)
│   ├── services            # Logique métier
│   └── main.py             # Point d'entrée de l'application
├── alembic                 # Migrations de base de données
├── tests                   # Tests unitaires et d'intégration
├── .env                    # Variables d'environnement (non versionné)
├── .env.example            # Exemple de variables d'environnement
├── requirements.txt        # Dépendances Python
└── README.md               # Documentation du projet
```

## Installation et démarrage

### 1. Configurer l'environnement

```bash
# Cloner le dépôt
git clone <repo-url>
cd starter-python

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier .env.example vers .env et ajuster les variables
cp .env.example .env
```

### 2. Initialiser la base de données

```bash
# Lancer PostgreSQL (si non démarré)
# docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# Appliquer les migrations
alembic upgrade head
```

### 3. Démarrer l'application

```bash
uvicorn app.main:app --reload
```

L'API sera disponible à l'adresse http://localhost:8000

Documentation API: http://localhost:8000/docs 