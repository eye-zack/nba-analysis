import os
import pandas as pd
import numpy as np
import joblib
import requests
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.compose import ColumnTransformer
from sqlalchemy import create_engine
import logging
from sklearn.impute import SimpleImputer

# Configure logging 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database Configuration
DB_USERNAME = os.getenv("DB_USERNAME", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_NAME = os.getenv("DB_NAME", "nba_analysis")


# Power BI Configuration
POWER_BI_ACCESS_TOKEN = os.getenv("POWER_BI_ACCESS_TOKEN", "your_access_token")
POWER_BI_DATASET_ID = os.getenv("POWER_BI_DATASET_ID", "your_dataset_id")
POWER_BI_TABLE_NAME = os.getenv("POWER_BI_TABLE_NAME", "your_table_name")
POWER_BI_BASE_URL = "https://api.powerbi.com/v1.0/myorg/datasets"

# Database Connection
def create_db_engine():
    try:
        engine = create_engine(f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")
        logger.info("Database connection created successfully.")
        return engine
    except Exception as e:
        logger.error(f"Error creating database connection: {e}")
        sys.exit(1)

# Historical Data from DB
def fetch_historical_data(engine):
    try:
        query_historical = "SELECT * FROM historical_data_table"
        df_historical = pd.read_sql(query_historical, engine)

        if df_historical.empty:
            logger.error("No historical data retrieved from the database.")
            sys.exit(1)
        else:
            logger.info(f"Fetched {df_historical.shape[0]} rows of historical data.")
            logger.info(f"Columns in the table: {df_historical.columns.tolist()}")
            # Check structure
            logger.info(f"First few rows: {df_historical.head()}")
        return df_historical
    except Exception as err:
        logger.error(f"Error fetching historical data: {err}")
        sys.exit(1)

# Define High and Low Variability Features
high_variability_features = [
    "PTS", "FG", "FGA", "3P", "3PA", "AST", "STL", "BLK", "TOV", "PF", "ORB", "DRB", "TRB"
]

low_variability_features = [
    "Age", "GS", "FG%", "3P%", "2P%", "eFG%", "FT", "FTA", "FT%", "Awards", "YR"
]

# Data Preprocessing and Feature Selection
def preprocess_and_select_features(df_historical):
    try:
        logger.info("Starting data cleaning and feature extraction...")

        # Clean data: remove duplicates, drop rows with missing values
        df_historical.drop_duplicates(inplace=True)
        df_historical.dropna(inplace=True)

        # Remove columns with only one unique value (low variability)
        df_historical = df_historical.loc[:, df_historical.apply(pd.Series.nunique) > 1]

        logger.info(f"After cleaning: {df_historical.shape[0]} rows, {df_historical.shape[1]} columns.")

        target_column = '3PA'
        if target_column not in df_historical.columns:
            logger.error(f"Target column '{target_column}' is missing in historical data.")
            sys.exit(1)

        # Feature selection: remove non-numeric columns
        non_numeric_columns = df_historical.select_dtypes(exclude=['number']).columns.tolist()

        # Drop non-numeric columns and target column from the feature set
        X = df_historical.drop(columns=[target_column] + non_numeric_columns)
        y = df_historical[target_column]

        # Select features based on statistical test
        selector = SelectKBest(score_func=f_regression, k=3)
        X_selected = selector.fit_transform(X, y)

        selected_features = X.columns[selector.get_support()]
        feature_scores = dict(zip(X.columns, selector.scores_))

        logger.info(f"Selected Features: {list(selected_features)}")
        logger.info("Feature extraction completed.")

        return X_selected, selected_features, feature_scores, X, y
    except Exception as e:
        logger.error(f"Error during data preprocessing and feature extraction: {e}")
        sys.exit(1)

# Scaling and Data Imputation
def scale_and_impute_data(X_selected_df, selected_features):
    try:
        logger.info("Starting data scaling and imputation...")
        # Impute missing values with mean
        imputer = SimpleImputer(strategy="mean")
        X_imputed = imputer.fit_transform(X_selected_df)
        X_imputed_df = pd.DataFrame(X_imputed, columns=selected_features)

        valid_selected_features = [feat for feat in selected_features if feat in X_imputed_df.columns]

        scaler = ColumnTransformer([
            ("robust", RobustScaler(), high_variability_features),
            ("standard", StandardScaler(), low_variability_features)
        ], remainder="passthrough")
        
        X_scaled = scaler.fit_transform(X_imputed_df[valid_selected_features])

        logger.info("Feature scaling completed successfully.")
        joblib.dump(scaler, 'scaler.pkl')
        return X_scaled
    except Exception as e:
        logger.error(f"Error during scaling and imputation: {e}")
        sys.exit(1)

# Train Random Forest Model
def train_model(X_scaled, y):
    try:
        logger.info("Starting model training with RandomForestRegressor...")
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        logger.info("Model training complete.")
        joblib.dump(model, 'model.pkl')
        return model, X_test, y_test
    except Exception as e:
        logger.error(f"Error during model training: {e}")
        sys.exit(1)

# Evaluate Model Performance
def evaluate_model(model, X_test, y_test):
    try:
        logger.info("Starting model evaluation...")
        y_pred_historical = model.predict(X_test)
        mae_historical = mean_absolute_error(y_test, y_pred_historical)
        r2_historical = r2_score(y_test, y_pred_historical)
        logger.info(f"Model Evaluation (Historical Data) - MAE: {mae_historical:.4f}, R²: {r2_historical:.4f}")
    except Exception as e:
        logger.error(f"Error during model evaluation: {e}")
        sys.exit(1)

# Main Execution
if __name__ == "__main__":
    # Establish Database Connection
    engine = create_db_engine()

    # Fetch historical data (real-time data handling is modular and can be added later)
    df_historical = fetch_historical_data(engine)

    # Preprocess the data and select features
    X_selected, selected_features, feature_scores, X, y = preprocess_and_select_features(df_historical)

    selected_features = [feat for feat in selected_features if feat in X.columns]

    # Scale and impute the data
    X_scaled = scale_and_impute_data(X_selected, selected_features)

    # Train the model
    model, X_test, y_test = train_model(X_scaled, y)

    # Evaluate model performance
    evaluate_model(model, X_test, y_test)

    logger.info("Full Training & Testing Process Completed Successfully!")