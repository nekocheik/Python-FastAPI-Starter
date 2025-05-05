from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.services import item as item_service

router = APIRouter()


@router.get("/", response_model=List[Item])
async def read_items(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupérer tous les items.
    """
    # Si l'utilisateur est admin, retourner tous les items
    if current_user.is_superuser:
        return item_service.get_items(db, skip=skip, limit=limit)
    # Sinon, retourner uniquement les items de l'utilisateur connecté
    return item_service.get_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=Item)
async def create_item(
    *,
    db: Session = Depends(get_db),
    item_in: ItemCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Créer un nouvel item.
    """
    item = item_service.create_item(db, item_in=item_in, owner_id=current_user.id)
    return item


@router.get("/{item_id}", response_model=Item)
async def read_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Récupérer un item par son ID.
    """
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    # Vérifier que l'utilisateur est le propriétaire ou un admin
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé"
        )
    return item


@router.put("/{item_id}", response_model=Item)
async def update_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: ItemUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mettre à jour un item.
    """
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    # Vérifier que l'utilisateur est le propriétaire ou un admin
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé"
        )
    item = item_service.update_item(db, db_item=item, item_in=item_in)
    return item


@router.delete("/{item_id}", response_model=dict)
async def delete_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Supprimer un item.
    """
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item non trouvé")
    # Vérifier que l'utilisateur est le propriétaire ou un admin
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé"
        )
    result = item_service.delete_item(db, item_id=item_id)
    return {"success": result} 