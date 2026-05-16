from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import user as crud_user
from app.schemas import user as schemas_user
from app.db.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas_user.User, status_code=201)
def create_user(user: schemas_user.UserCreate, db: Session = Depends(get_db)):
    """
    Create new user.
    """
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas_user.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/", response_model=List[schemas_user.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve users.
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=schemas_user.User)
def update_user(user_id: int, user_update: schemas_user.UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user's details.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # If email is being updated, check if it's already taken
    if user_update.email and user_update.email != db_user.email:
        existing_user = crud_user.get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.update_user(db=db, user_id=user_id, user=user_update)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user.
    """
    db_user = crud_user.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.delete_user(db=db, user_id=user_id)
    return None
