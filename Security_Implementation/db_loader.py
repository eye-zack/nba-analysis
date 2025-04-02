import pandas as pd
from sqlalchemy import create_engine
import os
import urllib
import logging

def load_data_from_rds():
    DB_USER = os.getenv("DB_USER")
    DB_PASS = urllib.parse.quote_plus(os.getenv("DB_PASS"))
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME", "nba_analysis")
    TABLE_NAME = os.getenv("DB_TABLE", "historical_data_table")
    SSL_CERT = os.getenv("RDS_SSL_CERT", "/path/to/rds-combined-ca-bundle.pem")

    DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?ssl_ca={SSL_CERT}"
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        df = pd.read_sql(f"SELECT * FROM {TABLE_NAME} WHERE Player != 'Team Totals'", conn)
    logging.info(f"Loaded {len(df)} rows from {TABLE_NAME}")
    return df