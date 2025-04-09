from fastapi import FastAPI, APIRouter, HTTPException
from predictions import predict_all_targets
from training_program import train_and_save_models
from db_loader import load_data_from_rds
import yaml
import os

app = FastAPI()
router = APIRouter()

@router.get("/predict")
def predict():
    with open("../../config.yaml", "r") as file:
        config = yaml.safe_load(file)

    targets = config.get("targets", [])
    new_table = "current_data_table"
    reference_table = "historical_data_table"

    try:
        prediction_df = predict_all_targets(new_table, reference_table, targets)
        return prediction_df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
def train():
    with open("../../config.yaml", "r") as file:
        config = yaml.safe_load(file)

    try:
        df = load_data_from_rds()
        train_and_save_models(df, config)
        return {"message": "Training complete and models saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

# Run with: uvicorn this_file_name:app --reload
