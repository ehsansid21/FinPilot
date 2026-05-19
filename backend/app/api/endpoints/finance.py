from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud import finance as crud_finance
from app.schemas import finance as schemas_finance
from app.db.database import get_db
from app.services.calculator import calculate_simulation
from app.services.ai_advisor import generate_financial_advice
from app.api.endpoints.user import get_current_user
from app.models.user import User as UserModel

router = APIRouter()

# Security helper to check user authorization
def check_user_access(user_id: int, current_user: UserModel):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these financial details")

# --- Financial Profile Endpoints ---

@router.post("/{user_id}/profile", response_model=schemas_finance.FinancialProfile, status_code=201)
def create_profile(user_id: int, profile: schemas_finance.FinancialProfileCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    
    # Check if profile already exists (One-to-One)
    existing_profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if existing_profile:
        raise HTTPException(status_code=400, detail="Financial profile already exists for this user")
        
    return crud_finance.create_financial_profile(db=db, profile=profile, user_id=user_id)

@router.get("/{user_id}/profile", response_model=schemas_finance.FinancialProfile)
def get_profile(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return profile

@router.put("/{user_id}/profile", response_model=schemas_finance.FinancialProfile)
def update_profile(user_id: int, profile_update: schemas_finance.FinancialProfileUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    return crud_finance.update_financial_profile(db=db, user_id=user_id, profile_update=profile_update)

@router.delete("/{user_id}/profile", status_code=204)
def delete_profile(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    profile = crud_finance.get_financial_profile(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Financial profile not found")
    crud_finance.delete_financial_profile(db=db, user_id=user_id)
    return None

# --- Expense Endpoints ---

@router.post("/{user_id}/expenses", response_model=schemas_finance.Expense, status_code=201)
def create_expense(user_id: int, expense: schemas_finance.ExpenseCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    return crud_finance.create_expense(db=db, expense=expense, user_id=user_id)

@router.get("/{user_id}/expenses", response_model=List[schemas_finance.Expense])
def get_expenses(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    return crud_finance.get_expenses(db, user_id=user_id)

@router.put("/{user_id}/expenses/{expense_id}", response_model=schemas_finance.Expense)
def update_expense(user_id: int, expense_id: int, expense_update: schemas_finance.ExpenseUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    expense = crud_finance.get_expense(db, expense_id=expense_id, user_id=user_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return crud_finance.update_expense(db=db, expense_id=expense_id, user_id=user_id, expense_update=expense_update)

@router.delete("/{user_id}/expenses/{expense_id}", status_code=204)
def delete_expense(user_id: int, expense_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    expense = crud_finance.get_expense(db, expense_id=expense_id, user_id=user_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    crud_finance.delete_expense(db=db, expense_id=expense_id, user_id=user_id)
    return None

# --- Goal Endpoints ---

@router.post("/{user_id}/goals", response_model=schemas_finance.Goal, status_code=201)
def create_goal(user_id: int, goal: schemas_finance.GoalCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    return crud_finance.create_goal(db=db, goal=goal, user_id=user_id)

@router.get("/{user_id}/goals", response_model=List[schemas_finance.Goal])
def get_goals(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    return crud_finance.get_goals(db, user_id=user_id)

@router.put("/{user_id}/goals/{goal_id}", response_model=schemas_finance.Goal)
def update_goal(user_id: int, goal_id: int, goal_update: schemas_finance.GoalUpdate, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    goal = crud_finance.get_goal(db, goal_id=goal_id, user_id=user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return crud_finance.update_goal(db=db, goal_id=goal_id, user_id=user_id, goal_update=goal_update)

@router.delete("/{user_id}/goals/{goal_id}", status_code=204)
def delete_goal(user_id: int, goal_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    goal = crud_finance.get_goal(db, goal_id=goal_id, user_id=user_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    crud_finance.delete_goal(db=db, goal_id=goal_id, user_id=user_id)
    return None

# --- Simulation and AI Advice Endpoints ---

@router.get("/{user_id}/simulation")
def get_simulation(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    return calculate_simulation(user_id, db)

@router.get("/{user_id}/advice")
def get_ai_advice(user_id: int, query: Optional[str] = None, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    check_user_access(user_id, current_user)
    advice = generate_financial_advice(user_id, db, query)
    return {"advice": advice}
