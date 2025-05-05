from fastapi import APIRouter

from app.api.v1.endpoints import auth, items, users

api_router = APIRouter()

# Routes pour l'authentification
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Routes pour les utilisateurs
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Routes pour les items
api_router.include_router(items.router, prefix="/items", tags=["items"]) 