from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine
from app.models import user
from app.api.api import api_router

# Create all tables stored in the Base metadata
user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinPilot API", description="AI-powered financial goal planning system")

# Configure CORS (Cross-Origin Resource Sharing)
# This allows our frontend (HTML/JS) to communicate with our backend API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api")
@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "FinPilot API is running"}
