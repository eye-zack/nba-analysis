# Verifies table and dataset are located in Power BI
# Extracts data from MySQL database
# Cleans and prepares the data
# used both RobustScaler and StandardScaler for data standardizing
# Trains and evaluates model
# formats data sends data to training table in Power BI 

# skleran - It provides a wide range of tools for preprocessing, modeling, evaluating and deploying machine learning models.
import os
import mysql.connector
import pandas as pd # helps load the data fram in a 2D array format and has multiple functions to perform analysis
import numpy as np # Fast and performs large computations in a short time
import joblib
import sys
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, RobustScaler # This class is used to standardize features by removing the mean and scaling to unit variance.
from sklearn.ensemble import RandomForestRegressor # This class is sued to train a random forest regression model.
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.compose import ColumnTransformer
import requests

# Power BI Configurations
POWER_BI_ACCESS_TOKEN = "your_access_token"
POWER_BI_DATASET_ID = "your_dataset_id"
POWER_BI_TABLE_NAME = "your_table_name"
POWER_BI_BASE_URL = "https://api.powerbi.com/v1.0/myorg/datasets"

# Function to check existence of dataset and table in Power BI
def check_power_bi_table():
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {POWER_BI_ACCESS_TOKEN}"
    }
    table_url = f"{POWER_BI_BASE_URL}/{POWER_BI_DATASET_ID}/tables"
    response = requests.get(table_url, headers=headers)
    if response.status_code == 200:
        tables = response.json().get("value", [])
        for table in tables:
            if table["name"] == POWER_BI_TABLE_NAME:
                return True
        log_result("Power BI Table Check", False, "Dataset found, but the expected table does not exist.")
        return False
    else:
        log_result("Power BI Table Check", False, f"Error {response.status_code}: {response.text}")
        return False

# Display success or failure after each phase
def log_result(phase, success=True, message=""):
    status = "Success" if success else "Failure"
    print(f"{status} - {phase}: {message}")
    if not success:
        sys.exit(1)

# Phase 1: Database Connection Test
# Load data from Database.
db_config = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DB")
}

try:
    conn = mysql.connector.connect(**db_config)
    print("Secure Database Connection Successful")
except mysql.connector.Error as err:
    log_result("Database Connection", False, f"Error: {err}")


# Phase 2: Proper fetching of data
# Pulls from two separate tables, one contains historical data, the other real-time data.
try:
    query_historical = "SELECT * FROM historical_data_table"
    df_historical = pd.read_sql(query_historical, conn)
    query_real_time = "SELECT * FROM real_time_data_table"
    df_real_time = pd.read_sql(query_real_time, conn)
    
    if df_historical.empty:
        log_result("Data Fetching (Historical)", False, "No historical data retrieved from database")
    else:
        log_result("Data Fetching (Historical)")
    
    if df_real_time.empty:
        log_result("Data Fetching (Real-Time)", False, "No real-time data retrieved from database")
    else:
        log_result("Data Fetching (Real-Time)")

except mysql.connector.Error as err:
    log_result("Database Fetching", False, f"Error: {err}")

    conn.close()

# define feature categories
high_variability_features = [
    "three_point_attempts", "points_per_game", "assists_per_game", "turnovers_per_game",
    "defensive_rebounds_per_game", "offensive_rebounds_per_game", "steals_per_game",
    "blocks_per_game", "personal_fouls_per_game"
]

normal_features = [
    "three_point_percentage", "field_goal_percentage", "free_throw_percentage",
    "win_percentage", "opponent_points_allowed"
]

# Phase 3: Cleaning the data and Feature Extraction
try:
    df_historical.drop_duplicates(inplace=True) # check for duplicate rows
    df_historical.dropna(inplace=True) # Dynamically removes missing values
    df_historical = df_historical.loc[:, df_historical.apply(pd.Series.nunique) > 1] # Removes features containing one unique value

    # Dynamically selects features
    # X contains potential predictor features while y is the target variable (i.e three-point percentages)
    X = df_historical.drop(columns=['target_column']) # Independent variables
    y = df_historical['target_column'] # Dependent Variable

    # Select best features based on statistical test
    # Each feature in X is evaluated for how strongly it correlates with y.
    selector = SelectKBest(score_func=f_regression, k=3) # Selects top 3 features
    X_selected = selector.fit_transform(X, y)

    # Get selected feature names and scores
    selected_features = X.columns[selector.get_support()]
    feature_scores = dict(zip(X.columns, selector.scores_))
    

    # Save score to log file
    with open("feature_scores.log", "w") as log_file:
        for feature, score in feature_scores.items():
            log_file.write(f"{feature}: {score:.4f}\n")
            
    print(f"Selected Features: {list(selected_features)}")
    log_result("Phase 3: Feature Engineering")
except Exception as e:
    log_result("Feature Engineering", False, str(e))

# Phase 4: Data Preprocessing
try:
    # If needed the strategy value can be changed to (median, most_frequent, or constant)
    # SimpleImputer works by filling missing values with the 'strategy' value
    imputer = SimpleImputer(strategy="mean")
    X_imputed = imputer.fit_transform(X_selected)
    # StandardScaler normalizes the data ensuring all fetaures are on the same scale.
    scaler = ColumnTransformer([
        ("robust", RobustScaler(), high_variability_features),
        ("standard", StandardScaler(), normal_features)
    ])
    X_scaled = scaler.fit_transform(X_imputed)

    # Save the scalers
    joblib.dump(scaler, 'scaler.pkl')
    log_result("Data Preprocessing")
except Exception as e:
    log_result("Data Preprocessing", False, str(e))

# Phase 5: Model Training
# randomregression is used to produce a more accurate and stable prediction. (utilizes decision trees)
try:
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, 'model.pkl')

    log_result("Model Training")
except Exception as e:
    log_result("Model Training", False, str(e))

# Phase 6: Evaluate model on Historical data and real-time data
try:
    # Historical Test Evaluation
    y_pred_historical = model.predict(X_test)
    mae_historical = mean_absolute_error(y_test, y_pred_historical)
    r2_historical = r2_score(y_test, y_pred_historical)
    log_result("Model Evaluation (Historical Data)", True, f"MAE: {mae_historical:.4f}, R²: {r2_historical:.4f}")

    # Real-Time Data Evaluation (if real-time data is available)
    real_time_df = pd.read_sql("SELECT * FROM real_time_table", conn)  # Fetch real-time data
    if not real_time_df.empty:
        X_real_time = real_time_df.drop(columns=['target_column'])
        y_real_time = real_time_df['target_column']
        X_real_time_scaled = scaler.transform(X_real_time)  # Ensure correct scaling
        y_pred_real_time = model.predict(X_real_time_scaled)

        mae_real_time = mean_absolute_error(y_real_time, y_pred_real_time)
        r2_real_time = r2_score(y_real_time, y_pred_real_time)
        log_result("Model Evaluation (Real-Time Data)", True, f"MAE: {mae_real_time:.4f}, R²: {r2_real_time:.4f}")
    else:
        log_result("Model Evaluation (Real-Time Data)", False, "No real-time data available")

except Exception as e:
    log_result("Model Evaluation", False, str(e))

# Phase 7: Prediction and data sent to Power BI
def send_data_to_power_bi():
    if df_real_time.empty:
        log_result("Power BI Data Upload", False, "Skipped: No real-time data available.")
        return
    
    if not check_power_bi_table():
        log_result("Power BI Data Upload", False, "Dataset or Table does not exist")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {POWER_BI_ACCESS_TOKEN}"
    }
    data_to_send = {"value": df_real_time.to_dict(orient="records")}
    power_bi_url = f"{POWER_BI_BASE_URL}/{POWER_BI_DATASET_ID}/tables/{POWER_BI_TABLE_NAME}/rows"
    response = requests.post(power_bi_url, json=data_to_send, headers=headers)
    if response.status_code == 200:
        log_result("Power BI Data Upload")
    else:
        log_result("Power BI Data Upload", False, f"Error {response.status_code}: {response.text}")

send_data_to_power_bi()

print("Full Training & Testing Process Completed Successfully!")