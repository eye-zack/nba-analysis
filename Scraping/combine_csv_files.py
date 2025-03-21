import pandas as pd

# load the two CSV files
df_br = pd.read_csv("nba_player_stats_basketball_reference_1979_to_1996.csv")
df_nba = pd.read_csv("nba_player_stats_nba_api_1997_to_2023.csv")

# combine the DataFrames
combined_df = pd.concat([df_br, df_nba], ignore_index=True)

# save the combined DataFrame to a new CSV file
combined_df.to_csv("nba_player_stats_combined_1979_to_2023.csv", index=False)