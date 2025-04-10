from backend.ML_training.predictions import predict_all_targets

def run_predictions(targets, team=None, season=None, model_dir="backend/ML_training/models/production"):
    from backend.ML_training.predictions import predict_all_targets

    return predict_all_targets(
        new_table="current_data_table",
        reference_table="historical_data_table",
        targets=targets,
        team=team,
        season=season,
        model_dir=model_dir
    ).to_dict(orient="records")

