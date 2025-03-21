'''
We scrape from two different sources for the historical date: 
    Basketball Reference: 1979-80 to 1995-96
    Official NBA website: 1996-97 to 2023-24

There are a couple reasons why we split up the sources for this data. The main reason is to deal with timeouts when it came to scraping. 
Splitting the data between two sources decreases the likelihood that we would be timed out while testing the scraping scripts. 

The reason we landed on these specific years for the two sources has to do with the NBA's stats in particular. Unfortunately, 
the NBA does not track the general stats for players prior to the 1996-97 season. Therefore, we use basketball-reference for every season before that,
limited by the season in which the 3PT shot was introduced (1979-80)

Note: these scripts were ran using a Jupyter Notebook, but for ease-of-access the scripts have been put in this python file. 

'''

# scraping NBA using the nba_api libary (1996-97 to 2023-24)
from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time
from requests.exceptions import ReadTimeout

# we define the range of years that we will scrape,  
start_season_nba = 1997  
end_season_nba = 2023    

# create an empty list to store the dataframes of each season
all_seasons_data = []

# funciton responsible for scraping the data with the nba_api. set retries and delays to prevent timeouts
def fetch_nba_api_data(year, retries=3, delay=5):
    # we initialized the start and end seasons as the leading year values for each season, so we need to do some formatting 
    season = f"{year}-{str(year + 1)[-2:]}"  # Format: YYYY-YY (e.g., 1996-97)
    # print a message to indicate that the stats for the season are being scraped
    print(f"Fetching data from NBA API for season: {season}")
    
    
    for attempt in range(retries):
    # try-except loop for fetching data
        try:
            # fetch player stats for the season
            player_stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                season_type_all_star="Regular Season",  # Options: Regular Season, Playoffs, Pre Season, All Star
                per_mode_detailed="PerGame",  # Options: PerGame, Totals, Per36, etc.
                timeout=60  # Increase timeout to 60 seconds
            )

            # convert the data to a DataFrame
            df = player_stats.get_data_frames()[0]

           # add a column for the year value, corresponding to the latter half of the season (i.e. a player's 1979-80 season stats will have 1980)
            df["YR"] = year + 1  

            return df

        except ReadTimeout as e:
            print(f"Attempt {attempt + 1} failed for season {season}: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Max retries reached for season {season}. Skipping...")
                return None
        except Exception as e:
            # print an error message if data cannot be fetched 
            print(f"Error fetching data for season {season}: {e}")
            return None
    
# loop through each season for NBA API
for year in range(start_season_nba, end_season_nba + 1):
    df = fetch_nba_api_data(year)
    if df is not None:
        all_seasons_data.append(df)
    time.sleep(2)  # add a delay between requests to avoid overwhelming the server

# check to see if the data was fetched 
if not all_seasons_data:
    print("No data fetched for any season.")
else:
    # combine all seasons into one dataframe 
    combined_df = pd.concat(all_seasons_data, ignore_index=True)
    
    # rename the columns to match our database
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
    
    # add a rank column 
    combined_df['Rk'] = range(1, len(combined_df) + 1)
    
    # reorder the columns to match the schema of the database
    combined_df = combined_df[[
        "Rk", "Player", "Pos", "Age", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
        "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL",
        "BLK", "TOV", "PF", "PTS", "YR", "TEAM"
    ]]

    # display the first few rows
    print(combined_df.head())

    # save to CSV
    combined_df.to_csv("nba_player_stats_nba_api_1997_to_2023.csv", index=False)
    