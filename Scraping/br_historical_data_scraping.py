'''
We scrape from two different sources for the historical date: 
    Basketball Reference: 1979-80 to 1996-97
    Official NBA website: 1997-98 to 2023-24

There are a couple reasons why we split up the sources for this data. The main reason is to deal with timeouts when it came to scraping. 
Splitting the data between two sources decreases the likelihood that we would be timed out while testing the scraping scripts. 

The reason we landed on these specific years for the two sources has to do with the NBA's stats in particular. Unfortunately, 
the NBA does not track the general stats for players prior to the 1996-97 season. Therefore, we use basketball-reference for every season before that,
limited by the season in which the 3PT shot was introduced (1979-80)

Note: these scripts were ran using a Jupyter Notebook, but for ease-of-access the scripts have been put in this python file. 

'''

# scraping basketball reference (1979-80 to 1996-97)
import pandas as pd 

# we define the range of years that we will scrape,  
start_season_br = 1979 
end_season_br = 1996 

# create an empty list to store the dataframes of each season
all_seasons_data = []

# funciton responsible for scraping the data from basketball-reference
def fetch_basketball_reference(year):
    
    # we initialized the start and end seasons as the leading year values for each season, so we need to do some formatting 
    season = f"{year}-{str(year + 1)[-2:]}"     # formatted as YYYY-YY
    
    # print a message to indicate that the stats for the season are being scraped
    print(f"Fetching data from Basketball-Reference for season: {season}")
    
    # try-except loop for fetching data
    try: 
        # URL for the season's player stats
        url = f"https://www.basketball-reference.com/leagues/NBA_{year + 1}_per_game.html"
        
        # read the html table into a dataframe 
        df = pd.read_html(url)[0]
        
        df = df[df['RK'].ne('RK')]          # remove the header rows from the table 
        df = df.dropna(subset=['Player'])   # remove rows with missing player names 
        
        # the table has both 'G', which is games played, and 'GS', which is games started. four our purposes, we do not need the games started value 
        if 'GS' in df.columns:
            df = df.drop(columns=['GS'])
            
        # drop the position column so that it matches the format of the nba_api data
        if 'Pos' in df.columns:
            df = df.drop(columns=['Pos'])
        
        # add a column for the year value, corresponding to the latter half of the season (i.e. a player's 1979-80 season stats will have 1980)
        df["YR"] = year + 1 
        
        return df
    
    except Exception as e:
        # print an error message if data cannot be fetched 
        print(f"Error fetching data for {season}: {e}")
        return None 
    
# loop through each season within the range of 1979-80 to 1995-96
for year in range(start_season_br, end_season_br + 1):
    df = fetch_basketball_reference(year)
    if df is not None:
        all_seasons_data.append(df)

# check to see if the data was fetched 
if not all_seasons_data:
    print("No data fetched for any season.")
else:
    # combine all seasons into one dataframe 
    combined_df = pd.concat(all_seasons_data, ignore_index=True)
    
    # rename the columns to match our database
    column_mapping = {
        "Player": "Player",
        "Age": "Age",
        "Team": "TEAM",
        "G": "GS",     
        "MP": "MP",
        "FG": "FG",
        "FGA": "FGA",
        "FG%": "FG%",
        "3P": "3P",
        "3PA": "3PA",
        "3P%": "3P%",
        "FT": "FT",
        "FTA": "FTA",
        "FT%": "FT%",
        "ORB": "ORB",
        "DRB": "DRB",
        "TRB": "TRB",
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
        "Rk", "Player", "Age", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%",
        "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL",
        "BLK", "TOV", "PF", "PTS", "YR", "TEAM"
    ]]

    # display the first few rows
    print(combined_df.head())

    # save to CSV
    combined_df.to_csv("nba_player_stats_basketball_reference_1979_to_1996.csv", index=False)
    