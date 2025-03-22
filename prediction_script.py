import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def predict_3pa_for_new_season(new_data_path, historical_data_path, player_names_included=True):
    """
    Predict 3PA for NBA players in the 2025-26 season without relying on saved scaler.
    
    Parameters:
    new_data_path (str): Path to the CSV file containing new player stats
    historical_data_path (str): Path to the CSV file containing historical stats used for training
    player_names_included (bool): Whether the input CSV contains player names
    
    Returns:
    DataFrame: DataFrame with player names and predicted 3PA
    """
    # load the model that we got from the training program 
    logging.info("Loading trained model")
    best_model = joblib.load("best_model.pkl")
    
    # get the selected features by looking at the model's feature names
    try:
        selected_features = best_model.feature_names_in_
        logging.info(f"Retrieved {len(selected_features)} features from model")
    except AttributeError:
        # ff feature names aren't stored in the model, we need to reconstruct the feature selection process
        logging.warning("Model doesn't contain feature names, using hardcoded selected features")
        # replace with the actual features printed during training
        selected_features = [
            'GS', 'FG', 'FGA', 'FG%', '3P', '3P%', 'ORB', 'AST', 'PF', 'YR'
        ]
    
    # load historical data to recreate the scaler
    logging.info(f"Loading historical data from {historical_data_path}")
    try:
        historical_df = pd.read_csv(historical_data_path)
    except FileNotFoundError:
        logging.error(f"Historical dataset not found: {historical_data_path}")
        raise SystemExit
    
    # store target column separately
    target_column = "3PA"
    
    # filter out team totals as we did in the training_program
    historical_df = historical_df[historical_df["Player"] != "Team Totals"].copy()
    
    # remove columns that we do not need for prediction
    remove_columns = ["Age", "Rk", "Player", "TEAM"]
    historical_df.drop(columns=remove_columns, inplace=True, errors='ignore')
    
    # drop the target column (3PA) before preprocessing
    x_historical = historical_df.drop(columns=[target_column])
    
    # recreate the imputer and scaler on historical data
    logging.info("Recreating preprocessing steps from training")
    numeric_features = x_historical.select_dtypes(include=np.number).columns
    imputer = SimpleImputer(strategy="median")
    x_historical[numeric_features] = imputer.fit_transform(x_historical[numeric_features])
    
    # recreate the scaler
    scaler = StandardScaler()
    scaler.fit(x_historical)
    logging.info("Scaler recreated with historical data")
    
    # load and prepare new player data
    logging.info(f"Loading new player data from {new_data_path}")
    try:
        new_players_df = pd.read_csv(new_data_path)
    except FileNotFoundError:
        logging.error(f"File not found: {new_data_path}")
        raise SystemExit
    
    # store player names if included in the input
    if player_names_included:
        player_names = new_players_df["Player"].copy()
        team_names = new_players_df["TEAM"].copy() if "TEAM" in new_players_df.columns else None
    
    # remove columns not used in training
    new_players_df.drop(columns=remove_columns, inplace=True, errors='ignore')
    
    # remove the target column from new data if it exists
    if target_column in new_players_df.columns:
        logging.info(f"Removing {target_column} column from new data as it's the prediction target")
        new_players_df.drop(columns=[target_column], inplace=True)
    
    # ensure the new data has exactly the same columns as the training data
    missing_cols = set(x_historical.columns) - set(new_players_df.columns)
    if missing_cols:
        logging.warning(f"Missing columns in new data: {missing_cols}")
        for col in missing_cols:
            new_players_df[col] = 0  # Fill with zeros as placeholder
    
    # ensure columns are in the same order
    new_players_df = new_players_df[x_historical.columns]
    
    # handle missing values
    numeric_features = new_players_df.select_dtypes(include=np.number).columns
    new_players_df[numeric_features] = imputer.transform(new_players_df[numeric_features])
    
    # transform and select features
    logging.info("Scaling features and selecting relevant ones")
    new_players_scaled = pd.DataFrame(
        scaler.transform(new_players_df), 
        columns=new_players_df.columns
    )
    
    # ensure only selected features are used
    if set(selected_features).issubset(set(new_players_scaled.columns)):
        new_players_selected = new_players_scaled[selected_features]
    else:
        logging.error(f"Selected features {selected_features} not found in scaled data columns: {new_players_scaled.columns}")
        raise ValueError("Feature mismatch between model and input data")
    
    # make predictions
    logging.info("Making predictions")
    predicted_3pa = best_model.predict(new_players_selected)
    
    # create results dataframe
    if player_names_included:
        results = {
            "Player": player_names,
            "Predicted_3PA": predicted_3pa
        }
        if team_names is not None:
            results["TEAM"] = team_names
        
        results_df = pd.DataFrame(results)
    else:
        results_df = pd.DataFrame({"Predicted_3PA": predicted_3pa})
    
    logging.info("Prediction complete")
    return results_df

if __name__ == "__main__":
    historical_data_path = "nba_historical_stats.csv"  # same file used for training
    new_data_path = "nba_player_stats_nba_api_2024-25.csv"  # data for predictions
    
    predictions = predict_3pa_for_new_season(new_data_path, historical_data_path)
    
    # save predictions
    predictions.to_csv("predicted_3pa_2025-26.csv", index=False)
    
    print("\nTop 10 players by predicted 3PA:")
    print(predictions.sort_values("Predicted_3PA", ascending=False).head(10))