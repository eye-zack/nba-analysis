from fastapi import FastAPI
from backend.services import router as predict_router

app = FastAPI(title="NBA 3PT Analysis API")
app.include_router(predict_router)

# Run with: uvicorn backend.ml_api:app --reload
