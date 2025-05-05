from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


def get_by_id(db: Session, item_id: int) -> Optional[Item]:
    return db.query(Item).filter(Item.id == item_id).first()


def get_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
    return db.query(Item).filter(Item.owner_id == owner_id).offset(skip).limit(limit).all()


def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[Item]:
    return db.query(Item).offset(skip).limit(limit).all()


def create_item(db: Session, item_in: ItemCreate, owner_id: int) -> Item:
    db_item = Item(
        title=item_in.title,
        description=item_in.description,
        owner_id=owner_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, db_item: Item, item_in: ItemUpdate) -> Item:
    update_data = item_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
        
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> bool:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True 