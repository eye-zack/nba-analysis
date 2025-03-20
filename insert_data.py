# Program inserts data from csv into DB
import pandas as pd
from sqlalchemy import create_engine, text

# Change creds.
DB_CONNECTION = "mysql+mysqlconnector://root:root@localhost:3306/nba_analysis"
TABLE_NAME = "historical_data_table"
CSV_FILE = "nba_historical_stats.csv"

engine = create_engine(DB_CONNECTION)

try:
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded dataset from: {CSV_FILE}")

    df.columns = [col.strip() for col in df.columns]
    df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
    print(f"Data inserted into: {TABLE_NAME}")

except Exception as e:
    print(f"Error inserting data into table: {e}")
