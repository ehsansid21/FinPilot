from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from typing import List

from app.crud import user as crud_user
from app.schemas import user as schemas_user
from app.db.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User as UserModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login-oauth2")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas_user.TokenData(user_id=int(user_id))
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception
        
    user = crud_user.get_user(db, user_id=token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=schemas_user.User, status_code=201)
def create_user(user: schemas_user.UserCreate, db: Session = Depends(get_db)):
    """
    Create new user.
    """
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)

@router.post("/login", response_model=schemas_user.Token)
def login(login_data: schemas_user.UserLogin, db: Session = Depends(get_db)):
    """
    User login with email and password, returns JWT token.
    """
    user = crud_user.authenticate_user(db, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-oauth2", response_model=schemas_user.Token, include_in_schema=False)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2 compatible token login, for Swagger UI.
    """
    user = crud_user.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas_user.User)
def read_user_me(current_user: UserModel = Depends(get_current_user)):
    """
    Get the currently logged-in user profile.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas_user.User)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Get a specific user by ID. Only accessible if it's the current user.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    return current_user

@router.get("/", response_model=List[schemas_user.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve users. Only authenticated users can access the list.
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.put("/{user_id}", response_model=schemas_user.User)
def update_user(user_id: int, user_update: schemas_user.UserUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Update a user's details. Only accessible if it's the current user.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    # If email is being updated, check if it's already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud_user.get_user_by_email(db, email=user_update.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.update_user(db=db, user_id=user_id, user=user_update)

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Delete a user. Only accessible if it's the current user.
    """
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    crud_user.delete_user(db=db, user_id=user_id)
    return None

