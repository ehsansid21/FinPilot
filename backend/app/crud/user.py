from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    """Retrieve a single user by their ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Retrieve a single user by their email address."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve a list of users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user in the database."""
    # Create a SQLAlchemy model instance with the data from the Pydantic schema
    db_user = User(email=user.email, name=user.name)
    
    # Add that instance object to your database session
    db.add(db_user)
    
    # Commit the changes to the database (so that they are saved)
    db.commit()
    
    # Refresh your instance (so that it contains any new data from the database, like the generated ID)
    db.refresh(db_user)
    
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate):
    """Update a user in the database."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Delete a user from the database."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
