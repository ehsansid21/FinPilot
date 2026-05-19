from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinPilot"
    
    # We use SQLite for local development
    # sqlite:///./finpilot.db means it will create a file named finpilot.db in the root backend directory
    DATABASE_URL: str = "sqlite:///./finpilot.db"
    GEMINI_API_KEY: str = ""
    SECRET_KEY: str = "309bf14a29a101f37b98bfdc600b3e5cb3a0d9b4db73e72251a14b3d7589d8cf"  # generate a secure fallback
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    class Config:
        env_file = ".env"

# Create a global instance of settings that we can import everywhere
settings = Settings()
