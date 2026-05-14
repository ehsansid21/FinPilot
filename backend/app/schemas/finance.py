from pydantic import BaseModel

# --- Financial Profile ---
class FinancialProfileBase(BaseModel):
    monthly_income: float
    current_savings: float = 0.0

class FinancialProfileCreate(FinancialProfileBase):
    pass

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

class Goal(GoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
