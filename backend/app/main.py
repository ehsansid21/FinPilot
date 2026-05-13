from fastapi import FastAPI

app = FastAPI(title="FinPilot API", description="AI-powered financial goal planning system")

@app.get("/ping")
async def ping():
    return {"status": "ok", "message": "FinPilot API is running"}
