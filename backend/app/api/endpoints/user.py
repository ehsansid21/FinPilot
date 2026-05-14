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
