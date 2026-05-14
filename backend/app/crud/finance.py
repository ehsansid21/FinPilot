from sqlalchemy.orm import Session
from app.models import finance as finance_models
from app.schemas import finance as finance_schemas

# --- Financial Profile ---
def get_financial_profile(db: Session, user_id: int):
    return db.query(finance_models.FinancialProfile).filter(finance_models.FinancialProfile.user_id == user_id).first()

def create_financial_profile(db: Session, profile: finance_schemas.FinancialProfileCreate, user_id: int):
    db_profile = finance_models.FinancialProfile(**profile.model_dump(), user_id=user_id)
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# --- Expenses ---
def get_expenses(db: Session, user_id: int):
    return db.query(finance_models.Expense).filter(finance_models.Expense.user_id == user_id).all()

def create_expense(db: Session, expense: finance_schemas.ExpenseCreate, user_id: int):
    db_expense = finance_models.Expense(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

# --- Goals ---
def get_goals(db: Session, user_id: int):
    return db.query(finance_models.Goal).filter(finance_models.Goal.user_id == user_id).all()

def create_goal(db: Session, goal: finance_schemas.GoalCreate, user_id: int):
    db_goal = finance_models.Goal(**goal.model_dump(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal
