from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time
import os
from requests.exceptions import ReadTimeout
from sqlalchemy import create_engine
from dotenv import load_dotenv
import schedule
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
TABLE_NAME = os.getenv("TABLE_NAME", "current_data_table")

# Create the connection string
DB_CONNECTION = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Define the range of years to scrape from environment variables
start_season_nba = int(os.getenv("START_SEASON", "2024"))
end_season_nba = int(os.getenv("END_SEASON", "2024"))

def run_scrape_job():
    """Main scraping function that contains all your existing logic"""
    logger.info("Starting NBA data scrape job")
    start_time = datetime.now()
    
    # Create an empty list to store the dataframes of each season
    all_seasons_data = []

    # Function to scrape data from NBA API with retries and delays
    def fetch_nba_api_data(year, retries=3, delay=5):
        season = f"{year}-{str(year + 1)[-2:]}"  # Format: YYYY-YY (e.g., 1996-97)
        logger.info(f"Fetching data from NBA API for season: {season}")
        
        for attempt in range(retries):
            try:
                player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                    season=season,
                    season_type_all_star="Regular Season",
                    per_mode_detailed="PerGame",
                    timeout=60
                )

                df = player_stats.get_data_frames()[0]
                df["YR"] = year + 1  # Add year column
                return df

            except ReadTimeout as e:
                logger.warning(f"Attempt {attempt + 1} failed for season {season}: {e}")
                if attempt < retries - 1:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries reached for season {season}. Skipping...")
                    return None
            except Exception as e:
                logger.error(f"Error fetching data for season {season}: {e}")
                return None

    # Scrape data for each season
    for year in range(start_season_nba, end_season_nba + 1):
        df = fetch_nba_api_data(year)
        if df is not None:
            all_seasons_data.append(df)
        time.sleep(2)  # Delay between requests

    if not all_seasons_data:
        logger.error("No data fetched for any season.")
        return False

    try:
        # Combine all seasons into one dataframe
        combined_df = pd.concat(all_seasons_data, ignore_index=True)
        
        # Rename columns to match database schema
        column_mapping = {
            "PLAYER_NAME": "Player",
            "AGE": "Age",
            "TEAM_ABBREVIATION": "TEAM",
            "GP": "GS",
            "MIN": "MP",
            "FGM": "FG",
            "FGA": "FGA",
            "FG_PCT": "FG%",
            "FG3M": "3P",
            "FG3A": "3PA",
            "FG3_PCT": "3P%",
            "FTM": "FT",
            "FTA": "FTA",
            "FT_PCT": "FT%",
            "OREB": "ORB",
            "DREB": "DRB",
            "REB": "TRB",
            "AST": "AST",
            "STL": "STL",
            "BLK": "BLK",
            "TOV": "TOV",
            "PF": "PF",
            "PTS": "PTS",
        }
        combined_df.rename(columns=column_mapping, inplace=True)
        
        # Add rank column
        combined_df['Rk'] = range(1, len(combined_df) + 1)
        
        # Reorder columns
        combined_df = combined_df[[
            "Rk", "Player", "Age", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
            "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL",
            "BLK", "TOV", "PF", "PTS", "YR", "TEAM"
        ]]

        logger.info(f"Scraped data sample:\n{combined_df.head()}")
        
        # Insert data into database
        engine = create_engine(DB_CONNECTION)
        
        # Clean up column names
        combined_df.columns = [col.strip() for col in combined_df.columns]

        # Insert data into the database table
        combined_df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
        logger.info(f"Data successfully inserted into: {TABLE_NAME}")

        return True

    except Exception as e:
        logger.error(f"Error in scrape job: {e}")
        return False
    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Scrape job completed in {duration:.2f} seconds")

def main():
    """Main function that handles scheduling"""
    # Determine run mode from environment variable
    test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'
    
    if test_mode:
        logger.info("Running in TEST MODE (every 5 minutes)")
        schedule.every(5).minutes.do(run_scrape_job)
    else:
        logger.info("Running in PRODUCTION MODE (daily at 3AM)")
        schedule.every().day.at("03:00").do(run_scrape_job)
    
    # Initial run
    run_scrape_job()
    
    # Continuous scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()