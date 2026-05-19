from pydantic import BaseModel, EmailStr
from typing import Optional

# Base schema for reading data (properties shared across all actions)
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# Schema for creating a user (e.g., what the frontend sends)
class UserCreate(UserBase):
    password: str

# Schema for updating a user
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

# Schema for reading a user from the API (includes ID from database)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Allows Pydantic to read data from SQLAlchemy models

# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schemas for JWT tokens
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

