# Program inserts data from csv into DB
import pandas as pd
from sqlalchemy import create_engine, text

# change these creds
DB_HOST = "nbadatabase.cpqyso4akjr1.us-east-2.rds.amazonaws.com"
DB_USER = "[username]"  # Replace with your MySQL username
DB_PASSWORD = "[password]"  # Replace with your MySQL password
DB_NAME = "nba_analysis"
TABLE_NAME = "historical_data_table"
CSV_FILE = "nba_historical_stats.csv"

# create the connection string
DB_CONNECTION = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# create the SQLAlchemy engine
engine = create_engine(DB_CONNECTION)

try:
    # load the CSV file into a DataFrame
    df = pd.read_csv(CSV_FILE)
    print(f"Loaded dataset from: {CSV_FILE}")

    # Clean up column names
    df.columns = [col.strip() for col in df.columns]

    # insert data into the database table
    df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
    print(f"Data inserted into: {TABLE_NAME}")

except Exception as e:
    print(f"Error inserting data into table: {e}")