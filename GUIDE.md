# Guide d'utilisation - Starter Python

Ce guide explique comment utiliser, étendre et maintenir le projet Starter Python. Il détaille les étapes pour ajouter ou supprimer des fonctionnalités.

## Table des matières

1. [Structure du projet](#structure-du-projet)
2. [Ajouter une nouvelle fonctionnalité](#ajouter-une-nouvelle-fonctionnalité)
3. [Retirer une fonctionnalité](#retirer-une-fonctionnalité)
4. [Base de données et migrations](#base-de-données-et-migrations)
5. [Tests](#tests)
6. [Authentification et autorisation](#authentification-et-autorisation)

## Structure du projet

Le projet suit une architecture en couches:

- **Models**: Définition des tables de base de données (SQLAlchemy)
- **Schemas**: Validation des données d'entrée/sortie (Pydantic)
- **Services**: Logique métier et opérations CRUD
- **API**: Points d'accès REST

La structure des dossiers reflète cette architecture:

```
app/
├── api/              # Points d'accès de l'API
│   └── v1/           # Version 1 de l'API
│       ├── endpoints/  # Endpoints par ressource
│       ├── api.py      # Regroupement des routes
│       └── deps.py     # Dépendances partagées
├── core/             # Configuration et utilitaires
├── db/               # Configuration de la base de données
├── models/           # Modèles SQLAlchemy
├── schemas/          # Schémas Pydantic
├── services/         # Services pour la logique métier
└── main.py           # Point d'entrée de l'application
```

## Ajouter une nouvelle fonctionnalité

Pour ajouter une nouvelle fonctionnalité, suivez ces étapes:

### 1. Créer un nouveau modèle (si nécessaire)

Dans le dossier `app/models/`, créez un nouveau fichier pour votre entité:

```python
# app/models/product.py
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

N'oubliez pas d'ajouter l'import dans `app/db/base.py`:

```python
# app/db/base.py
from app.db.base_class import Base
from app.models.user import User
from app.models.item import Item
from app.models.product import Product  # Ajoutez cette ligne
```

### 2. Créer les schémas Pydantic

Dans le dossier `app/schemas/`, créez un nouveau fichier pour vos schémas:

```python
# app/schemas/product.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Schéma de base
class ProductBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

# Pour la création
class ProductCreate(ProductBase):
    name: str
    price: float

# Pour la mise à jour
class ProductUpdate(ProductBase):
    pass

# Pour la lecture (depuis la DB)
class ProductInDBBase(ProductBase):
    id: int
    name: str
    price: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Pour l'API
class Product(ProductInDBBase):
    pass
```

### 3. Créer le service

Dans le dossier `app/services/`, créez un fichier pour votre service:

```python
# app/services/product.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

def get_by_id(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
    return db.query(Product).offset(skip).limit(limit).all()

def create_product(db: Session, product_in: ProductCreate) -> Product:
    db_product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def update_product(db: Session, db_product: Product, product_in: ProductUpdate) -> Product:
    update_data = product_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_product, field, value)
        
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int) -> bool:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    db.delete(product)
    db.commit()
    return True
```

### 4. Créer les endpoints d'API

Dans le dossier `app/api/v1/endpoints/`, créez un fichier pour vos endpoints:

```python
# app/api/v1/endpoints/products.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.v1.deps import get_current_active_user, get_current_superuser, get_db
from app.models.user import User
from app.schemas.product import Product, ProductCreate, ProductUpdate
from app.services import product as product_service

router = APIRouter()

@router.get("/", response_model=List[Product])
async def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupérer tous les produits.
    """
    products = product_service.get_products(db, skip=skip, limit=limit)
    return products

@router.post("/", response_model=Product)
async def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Créer un nouveau produit (admin uniquement).
    """
    product = product_service.create_product(db, product_in=product_in)
    return product

@router.get("/{product_id}", response_model=Product)
async def read_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupérer un produit par son ID.
    """
    product = product_service.get_by_id(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

@router.put("/{product_id}", response_model=Product)
async def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Mettre à jour un produit (admin uniquement).
    """
    product = product_service.get_by_id(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    product = product_service.update_product(db, db_product=product, product_in=product_in)
    return product

@router.delete("/{product_id}", response_model=dict)
async def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Supprimer un produit (admin uniquement).
    """
    product = product_service.get_by_id(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    result = product_service.delete_product(db, product_id=product_id)
    return {"success": result}
```

### 5. Ajouter la route à l'API principale

Mettez à jour le fichier `app/api/v1/api.py`:

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, items, users, products  # Ajoutez "products"

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(products.router, prefix="/products", tags=["products"])  # Ajoutez cette ligne
```

### 6. Générer et appliquer les migrations

```bash
# Créer la migration
alembic revision --autogenerate -m "Add products table"

# Appliquer la migration
alembic upgrade head
```

## Retirer une fonctionnalité

Pour retirer une fonctionnalité existante, suivez ces étapes:

### 1. Supprimer les endpoints d'API

Supprimer le fichier d'endpoints correspondant, par exemple `app/api/v1/endpoints/items.py`.

### 2. Retirer la route de l'API principale

Modifiez le fichier `app/api/v1/api.py` pour supprimer l'import et la ligne incluant le routeur:

```python
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users  # Supprimez "items"

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# Supprimez la ligne incluant items.router
```

### 3. Retirer les services

Supprimez le fichier de service correspondant, par exemple `app/services/item.py`.

### 4. Retirer les schémas

Supprimez le fichier de schémas correspondant, par exemple `app/schemas/item.py`.

### 5. Retirer les modèles et leurs relations

1. Supprimez le fichier de modèle, par exemple `app/models/item.py`.
2. Mettez à jour les modèles qui font référence à celui-ci.

Par exemple, dans `app/models/user.py`, supprimez la relation:

```python
# Supprimez cette ligne
items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")
```

### 6. Mettre à jour l'import dans base.py

Modifiez le fichier `app/db/base.py` pour supprimer l'import:

```python
from app.db.base_class import Base
from app.models.user import User
# Supprimez la ligne important Item
```

### 7. Créer une migration pour supprimer la table

```bash
# Créer la migration
alembic revision --autogenerate -m "Remove items table"

# Appliquer la migration
alembic upgrade head
```

## Base de données et migrations

### Créer une nouvelle migration

Pour créer une nouvelle migration:

```bash
alembic revision --autogenerate -m "Description de la migration"
```

### Appliquer les migrations

Pour appliquer toutes les migrations jusqu'à la dernière:

```bash
alembic upgrade head
```

Pour appliquer jusqu'à une révision spécifique:

```bash
alembic upgrade <revision_id>
```

### Annuler des migrations

Pour revenir à une révision antérieure:

```bash
alembic downgrade <revision_id>
```

Pour annuler la dernière migration:

```bash
alembic downgrade -1
```

## Tests

Les tests se trouvent dans le dossier `tests/`. Vous pouvez exécuter les tests avec:

```bash
pytest
```

### Ajouter des tests

Pour ajouter des tests pour une nouvelle fonctionnalité:

1. Créez un nouveau fichier de test dans le dossier `tests/`, par exemple `tests/test_products.py`
2. Implémentez vos tests en utilisant pytest

Exemple:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.services import product as product_service
from app.schemas.product import ProductCreate

client = TestClient(app)

def test_create_product(db: Session, superuser_token_headers):
    data = {"name": "Test Product", "price": 99.99, "description": "Test description"}
    response = client.post(
        "/api/v1/products/", 
        headers=superuser_token_headers, 
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert content["price"] == data["price"]
    assert content["description"] == data["description"]
    assert "id" in content
```

## Authentification et autorisation

Ce projet utilise OAuth2 avec JWT pour l'authentification. 

### Ajouter un nouvel endpoint sécurisé

Pour sécuriser un nouvel endpoint, utilisez les dépendances Depends:

- `get_current_user`: Vérifie que l'utilisateur est authentifié
- `get_current_active_user`: Vérifie que l'utilisateur est authentifié et actif
- `get_current_superuser`: Vérifie que l'utilisateur est authentifié, actif et a des droits d'administrateur

Exemple:

```python
from fastapi import APIRouter, Depends
from app.api.v1.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/secure-endpoint")
def secure_endpoint(current_user: User = Depends(get_current_active_user)):
    return {"message": "Cet endpoint est sécurisé", "user_id": current_user.id}
```

### Modifier le comportement d'authentification

Pour modifier le comportement d'authentification, vous pouvez ajuster:

1. La durée de validité des tokens dans `app/core/config.py`:
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Par exemple, 60 minutes au lieu de 30
   ```

2. L'algorithme de hachage des mots de passe dans `app/core/security.py` 