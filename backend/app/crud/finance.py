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

def update_financial_profile(db: Session, user_id: int, profile_update: finance_schemas.FinancialProfileUpdate):
    db_profile = get_financial_profile(db, user_id=user_id)
    if db_profile:
        update_data = profile_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_profile, key, value)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
    return db_profile

def delete_financial_profile(db: Session, user_id: int):
    db_profile = get_financial_profile(db, user_id=user_id)
    if db_profile:
        db.delete(db_profile)
        db.commit()
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

def get_expense(db: Session, expense_id: int, user_id: int):
    return db.query(finance_models.Expense).filter(finance_models.Expense.id == expense_id, finance_models.Expense.user_id == user_id).first()

def update_expense(db: Session, expense_id: int, user_id: int, expense_update: finance_schemas.ExpenseUpdate):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        update_data = expense_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int, user_id: int):
    db_expense = get_expense(db, expense_id, user_id)
    if db_expense:
        db.delete(db_expense)
        db.commit()
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

def get_goal(db: Session, goal_id: int, user_id: int):
    return db.query(finance_models.Goal).filter(finance_models.Goal.id == goal_id, finance_models.Goal.user_id == user_id).first()

def update_goal(db: Session, goal_id: int, user_id: int, goal_update: finance_schemas.GoalUpdate):
    db_goal = get_goal(db, goal_id, user_id)
    if db_goal:
        update_data = goal_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_goal, key, value)
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int, user_id: int):
    db_goal = get_goal(db, goal_id, user_id)
    if db_goal:
        db.delete(db_goal)
        db.commit()
    return db_goal
