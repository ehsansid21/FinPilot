from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinPilot"
    
    # We use SQLite for local development
    # sqlite:///./finpilot.db means it will create a file named finpilot.db in the root backend directory
    DATABASE_URL: str = "sqlite:///./finpilot.db"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

# Create a global instance of settings that we can import everywhere
settings = Settings()
