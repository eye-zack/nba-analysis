import os
import pandas as pd
import numpy as np
import joblib
import requests
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.compose import ColumnTransformer
from sqlalchemy import create_engine
import logging
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import RFECV
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

input_csv = "nba_historical_stats.csv"
try:
    df = pd.read_csv(input_csv)
    logging.info(f"Dataset loaded: {input_csv}")
except FileNotFoundError:
    logging.error(f"Dataset not found: {input_csv}")
    raise SystemExit


# DB_CONNECTION = "mysql+mysqlconnector://root:Adex127!Apple@localhost:3306/nba_analysis" # Change creds
# TABLE_NAME = "historical_data_table"

# engine = create_engine(DB_CONNECTION)
# try:
#     with engine.connect() as connection:
#         df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE Player != 'Team Totals'", con=connection)
#     logging.info(f"Dataset loaded: {TABLE_NAME}")
# except Exception as e:
#     logging.error(f"Dataset not loaded: {e}")
#     raise SystemExit

df_team_totals = df[df["Player"] == "Team Totals"]
df_players = df[df["Player"] != "Team Totals"]
df = df_players.copy()
logging.info("Team totals separated from player data.")

remove_columns = ["Age","Rk","Player","TEAM"]
df.drop(columns=remove_columns, inplace=True)
logging.info(f"Columns removed: {remove_columns}")

numeric_features = df.select_dtypes(include=np.number).columns
imputer = SimpleImputer(strategy="median")
df[numeric_features] = imputer.fit_transform(df[numeric_features])
logging.info(f"Missing values handled using median strategy.")

#df.drop_duplicates(inplace=True)
#df.loc[:, df.select_dtypes(include=[np.number]).columns] = df.select_dtypes(include=[np.number]).fillna(df.mean())
#df.fillna(df.mean(), inplace=True)

target_column = "3PA"
if target_column not in df.columns:
    logging.error(f"Column {target_column} not found in dataset")
    raise ValueError("Target column not found")

x = df.drop(columns=[target_column])
y = df[target_column]

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
logging.info(f"X_train shape: {X_train.shape}")

# Feature Selection
scaler = StandardScaler()
X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

# Forest Regression
rf_model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
selector = RFECV(estimator=rf_model, step=5, cv=5, scoring="r2", n_jobs=-1, min_features_to_select=5)
X_train_selected = selector.fit_transform(X_train_scaled, y_train)
X_test_selected = selector.transform(X_test_scaled)

# Get selected feature names
selected_features = X_train.columns[selector.support_]
logging.info(f"Selected features: {selected_features}")

X_train_selected = pd.DataFrame(X_train_selected, columns=selected_features)
X_test_selected = pd.DataFrame(X_test_selected, columns=selected_features)

print("\n Selected Important Features:")
print(selected_features)

start_time = time.time()
rf_model.fit(X_train_selected, y_train)
rf_time = time.time() - start_time

rf_y_pred = rf_model.predict(X_test_selected)
rf_mae = mean_absolute_error(y_test, rf_y_pred)
rf_r2 = r2_score(y_test, rf_y_pred)

# Uncomment to compare forest regression and gradient boosting (Forest regression was best)
# Gradient Boosting
gb_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)

start_time = time.time()
gb_model.fit(X_train_selected, y_train)
gb_time = time.time() - start_time

gb_y_pred = gb_model.predict(X_test_selected)
gb_mae = mean_absolute_error(y_test, gb_y_pred)
gb_r2 = r2_score(y_test, gb_y_pred)

#print(f"Training is complete")
#print(f"MAE: {mae}")
#print(f"R2: {r2}")

print(f"Random Forest - MAE: {rf_mae:.4f}, R²: {rf_r2:.4f}, Training Time: {rf_time:.2f} sec")
print(f"Gradient Boosting - MAE: {gb_mae:.4f}, R²: {gb_r2:.4f}, Training Time: {gb_time:.2f} sec")

# Save the Best Model
if rf_r2 > gb_r2:
    joblib.dump(rf_model, "3PA_best_model.pkl")
    logging.info("Best Model (Random Forest) saved as '3PA_best_model.pkl'")
else:
    joblib.dump(gb_model, "3PA_best_model.pkl")
    logging.info("Best Model (Gradient Boosting) saved as '3PA_best_model.pkl'")

# Uncomment these after testing Forest and boosting
#joblib.dump(scaler, "scaler.pkl")
#joblib.dump(model, "model.pkl")

#logging.info(f"Model saved: {model}")
print(f"Training is complete.")