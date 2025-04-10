from fastapi import APIRouter, Query, HTTPException
from backend.services.model_services import run_predictions
import os
import traceback

router = APIRouter()
@router.get("/predict")
def predict(
    team: str = Query(None),
    season: int = Query(None),
    targets: list[str] = Query(default=["3P", "3PA"])
):
    model_dir = "backend/ML_training/models/production"
    available_models = {f.split("_")[0] for f in os.listdir(model_dir) if f.endswith("_best_model.pkl")}
    unsupported = [t for t in targets if t not in available_models]

    if unsupported:
        raise HTTPException(status_code=400, detail=f"Unsupported targets: {unsupported}")

    try:
        results = run_predictions(
            targets=targets,
            team=team,
            season=season,
            model_dir=model_dir
        )
        return results
    except Exception as e:
        print("Exception in /predict:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))