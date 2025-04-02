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
import urllib
import time

def train_and_save_models(df, config):

    target_columns = config.get("targets", [])
    output_dir = config.get("output_dir", "models")
    os.makedirs(output_dir, exist_ok=True)

    df = df[df["Player"] != "Team Totals"].copy()
    df.drop(columns=["Awards", "Pos", "Age", "Rk", "Player", "TEAM"], errors="ignore", inplace=True)

    numeric_cols = df.select_dtypes(include=np.number).columns
    imputer = SimpleImputer(strategy="median")
    df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

    for target in target_columns:
        if target not in df.columns:
            logging.warning(f"Skipping target {target}: not found in data")
            continue

        logging.info(f"Training models for target: {target}")
        X = df.drop(columns=target_columns)
        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        logging.info(f"X_train shape: {X_train.shape}")

        scaler = StandardScaler()
        X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns)
        X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)

        models_to_test = {
            "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
            "GradientBoosting": GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, max_depth=5, random_state=42)
        }

        best_model = None
        best_r2 = -np.inf
        best_name = ""
        best_selector = None

        for name, model in models_to_test.items():
            selector = RFECV(estimator=model, step=5, cv=5, scoring="r2", n_jobs=-1, min_features_to_select=5)
            X_train_selected = selector.fit_transform(X_train_scaled, y_train)
            X_test_selected = selector.transform(X_test_scaled)

            model.fit(X_train_selected, y_train)
            y_pred = model.predict(X_test_selected)

            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            logging.info(f"{target} | {name} - R2: {r2:.4f}, MAE: {mae:.4f}")

            if r2 > best_r2:
                best_model = model
                best_selector = selector
                best_r2 = r2
                best_name = name

        joblib.dump(best_model, f"{output_dir}/{target}_best_model.pkl")
        joblib.dump(scaler, f"{output_dir}/{target}_scaler.pkl")
        joblib.dump(best_selector, f"{output_dir}/{target}_selector.pkl")

        logging.info(f"Saved best model ({best_name}) for target '{target}' with R²: {best_r2:.4f}")
        print(f"Saved best model ({best_name}) for target '{target}' with R²: {best_r2:.4f}")
