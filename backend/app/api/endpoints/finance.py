from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import finance as crud_finance
from app.crud import user as crud_user
from app.schemas import finance as schemas_finance
from app.db.database import get_db

router = APIRouter()

# Dependency to check if user exists
def get_existing_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Financial Profile Endpoints ---

@router.post("/{user_id}/profile", response_model=schemas_finance.FinancialProfile, status_code=201)
def create_profile(user_id: int, profile: schemas_finance.FinancialProfileCreate, db: Session = Depends(get_db)):
    # Check if user exists
    get_existing_user(user_id, db)
    
    # Check if profile already exists (One-to-One)
    existing_profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Financial profile already exists for this user")
        
    return crud_finance.create_financial_profile(db=db, profile=profile, user_id=user_id)

@router.get("/{user_id}/profile", response_model=schemas_finance.FinancialProfile)
def get_profile(user_id: int, db: Session = Depends(get_db)):
    get_existing_user(user_id, db)
    profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile

# --- Expense Endpoints ---

@router.post("/{user_id}/expenses", response_model=schemas_finance.Expense, status_code=201)
def create_expense(user_id: int, expense: schemas_finance.ExpenseCreate, db: Session = Depends(get_db)):
    get_existing_user(user_id, db)
    return crud_finance.create_expense(db=db, expense=expense, user_id=user_id)

@router.get("/{user_id}/expenses", response_model=List[schemas_finance.Expense])
def get_expenses(user_id: int, db: Session = Depends(get_db)):
    get_existing_user(user_id, db)
    return crud_finance.get_expenses(db, user_id=user_id)

# --- Goal Endpoints ---

@router.post("/{user_id}/goals", response_model=schemas_finance.Goal, status_code=201)
def create_goal(user_id: int, goal: schemas_finance.GoalCreate, db: Session = Depends(get_db)):
    get_existing_user(user_id, db)
    return crud_finance.create_goal(db=db, goal=goal, user_id=user_id)

@router.get("/{user_id}/goals", response_model=List[schemas_finance.Goal])
def get_goals(user_id: int, db: Session = Depends(get_db)):
    get_existing_user(user_id, db)
    return crud_finance.get_goals(db, user_id=user_id)
