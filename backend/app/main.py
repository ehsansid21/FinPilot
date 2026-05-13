from fastapi import FastAPI
from app.db.database import engine
from app.models import user

# Create all tables stored in the Base metadata
user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinPilot API", description="AI-powered financial goal planning system")

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "FinPilot API is running"}
