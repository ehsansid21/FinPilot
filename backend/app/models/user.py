from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, index=True)
    
    # Financial relationships
    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    expenses = relationship("Expense", back_populates="user")
    goals = relationship("Goal", back_populates="user")
