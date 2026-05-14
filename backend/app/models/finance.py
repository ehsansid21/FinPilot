from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    monthly_income = Column(Float, default=0.0)
    current_savings = Column(Float, default=0.0)

    user = relationship("User", back_populates="financial_profile")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    amount = Column(Float, nullable=False)
    is_recurring = Column(Boolean, default=True)

    user = relationship("User", back_populates="expenses")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    target_amount = Column(Float, nullable=False)
    months_to_goal = Column(Integer, nullable=False)

    user = relationship("User", back_populates="goals")
