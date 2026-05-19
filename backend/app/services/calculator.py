from sqlalchemy.orm import Session
from app.crud import finance as crud_finance

def calculate_simulation(user_id: int, db: Session):
    profile = crud_finance.get_financial_profile(db, user_id=user_id)
    expenses = crud_finance.get_expenses(db, user_id=user_id)
    goals = crud_finance.get_goals(db, user_id=user_id)

    monthly_income = profile.monthly_income if profile else 0.0
    current_savings = profile.current_savings if profile else 0.0
    risk_tolerance = profile.risk_tolerance if profile else "50%"
    target_savings = profile.target_savings if profile else 0.0

    total_monthly_expenses = sum(exp.amount for exp in expenses)
    monthly_capacity = monthly_income - total_monthly_expenses

    required_monthly_for_goals = 0.0
    goals_data = []

    for goal in goals:
        if goal.months_to_goal > 0:
            required = goal.target_amount / goal.months_to_goal
        else:
            required = 0.0
        required_monthly_for_goals += required
        goals_data.append({
            "name": goal.name,
            "target_amount": goal.target_amount,
            "months_to_goal": goal.months_to_goal,
            "required_monthly": required
        })

    is_feasible = target_savings >= required_monthly_for_goals
    savings_plan_feasible = target_savings <= monthly_capacity

    return {
        "monthly_income": monthly_income,
        "current_savings": current_savings,
        "risk_tolerance": risk_tolerance,
        "target_savings": target_savings,
        "total_monthly_expenses": total_monthly_expenses,
        "monthly_savings_capacity": monthly_capacity,
        "required_monthly_for_goals": required_monthly_for_goals,
        "is_feasible": is_feasible,
        "savings_plan_feasible": savings_plan_feasible,
        "goals": goals_data,
        "expenses": [{"name": exp.name, "amount": exp.amount} for exp in expenses]
    }
