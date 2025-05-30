import os
import joblib
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import urllib
import logging
from dotenv import load_dotenv
import yaml

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
load_dotenv()

# load model, scaler, and selector artifacts
def load_target_artifacts(target, model_dir="models"):
    model = joblib.load(os.path.join(model_dir, f"{target}_best_model.pkl"))
    scaler = joblib.load(os.path.join(model_dir, f"{target}_scaler.pkl"))
    selector = joblib.load(os.path.join(model_dir, f"{target}_selector.pkl"))
    return model, scaler, selector

# preprocesses new input data using structure of reference data
def preprocess_new_data(new_df, reference_df):
    imputer = SimpleImputer(strategy='median')

    # verifies all columns in reference data exist in new data.
    # adds 0 value to missing columns
    for col in reference_df.columns:
        if col not in new_df.columns:
            new_df[col] = 0

    # reorders columns to match both df
    new_df = new_df[reference_df.columns]
    # apply imputation on numeric columns (filling in missing data)
    new_df[new_df.select_dtypes(include=np.number).columns] = imputer.fit(reference_df).transform(new_df.select_dtypes(include=np.number))
    return new_df

# loads from database table with optional features for team and season
def load_data_from_db(table_name, team=None, season=None): # can add more filters (player_name=None, min_minutes=None.. etc)
    DB_USER = os.getenv("DB_USER")
    DB_PASS = urllib.parse.quote_plus(os.getenv("DB_PASS"))
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    # SSL_CERT = os.getenv("RDS_SSL_CERT")

    DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(DB_URL)
    # build query with the optional filters
    with engine.connect() as conn:
        query = f"SELECT * FROM {table_name} WHERE Player != 'Team Totals'"
        if team:
            query += f" AND TEAM = '{team}'"
        if season:
            query += f" AND Season = {season}"
        # if player_name:
            # query += f" AND player = '{player_name}'"
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    return df

# run predictions for all specified target columns
def predict_all_targets(new_table, reference_table, targets, model_dir="models", team=None, season=None):
    logging.info("Loading data from database")
    # load new and reference datasets
    new_df = load_data_from_db(new_table, team=team, season=season)
    ref_df = load_data_from_db(reference_table)
    # clean reference data
    ref_df = ref_df[ref_df["Player"] != "Team Totals"].copy()
    ref_df.drop(columns=["Awards", "Pos", "Age", "Rk", "Player", "TEAM"], inplace=True, errors='ignore')
    ref_df.drop(columns=targets, inplace=True, errors='ignore')
    # save player/team info separately before dropping
    # drops non-numerical data since these are not used as features for prediction
    player_names = new_df.get("Player")
    team_names = new_df.get("TEAM")
    new_df.drop(columns=["Awards", "Pos", "Age", "Rk", "Player", "TEAM"] + targets, inplace=True, errors='ignore')
    # align and preprocess new data to match reference data
    new_df = preprocess_new_data(new_df, ref_df)

    # creates a results dataframe
    results = pd.DataFrame()
    if player_names is not None:
        results["Player"] = player_names
    if team_names is not None:
        results["TEAM"] = team_names
    # run prediction for each target value
    for target in targets:
        logging.info(f"Predicting target: {target}")
        model, scaler, selector = load_target_artifacts(target, model_dir)

        expected_columns = scaler.feature_names_in_
        new_df_aligned = new_df[expected_columns]
        # scale and transform features before prediction
        scaled = scaler.transform(new_df_aligned)
        selected = selector.transform(scaled)
        preds = model.predict(selected)
        """
        Scaling - adjusts all feature values to a standard scale (e.g., mean = 0, std = 1)
            helps models treat all features equally
        Transforming - using RFECV means applying feature selection - keeping only the best predictors based on training performance
        """

        results[f"Predicted_{target}"] = preds

    logging.info("Prediction complete for all targets")
    return results

# helper function to find most recent saved model for a target
def get_latest_model_prefix(target, staging_dir):
    matching_files = [f for f in os.listdir(staging_dir) if f.startswith(target) and f.endswith("_best_model.pkl")]
    if not matching_files:
        raise FileNotFoundError(f"No model files found for target '{target}' in {staging_dir}")

    # Sort by version timestamp (assuming format target_vX_YYYYMMDD_HHMM)
    matching_files.sort(reverse=True)
    latest = matching_files[0]
    return "_".join(latest.split("_")[:-2])

if __name__ == "__main__":
    new_table_name = "current_data_table"
    reference_table_name = "historical_data_table"

    with open("../../config.yaml", "r") as file:
        config = yaml.safe_load(file)
    targets = config.get("targets", [])

    prediction_df = predict_all_targets(new_table_name, reference_table_name, targets)
    prediction_df.to_csv("predictions_multi_target.csv", index=False)

    logging.info("Prediction results saved to predictions_multi_target.csv")
    print(f"Prediction program successfully completed")
