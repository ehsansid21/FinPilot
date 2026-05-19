from pydantic import BaseModel
from typing import Optional

# --- Financial Profile ---
class FinancialProfileBase(BaseModel):
    monthly_income: float
    current_savings: float = 0.0
    risk_tolerance: str = "50%"
    target_savings: float = 0.0

class FinancialProfileCreate(FinancialProfileBase):
    pass

class FinancialProfileUpdate(BaseModel):
    monthly_income: Optional[float] = None
    current_savings: Optional[float] = None
    risk_tolerance: Optional[str] = None
    target_savings: Optional[float] = None

class FinancialProfile(FinancialProfileBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Expense ---
class ExpenseBase(BaseModel):
    name: str
    amount: float
    is_recurring: bool = True

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    is_recurring: Optional[bool] = None

class Expense(ExpenseBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Goal ---
class GoalBase(BaseModel):
    name: str
    target_amount: float
    months_to_goal: int

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    months_to_goal: Optional[int] = None

class Goal(GoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
