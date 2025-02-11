from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.static import players
import time
import random


# Run the main function
if __name__ == "__main__":
    # Data is downloaded from the https://github.com/shufinskiy/nba_data as of 2025-02-11

    # For all the data in nba, we read all shotdetail_<year> csv into a dataframe
    full_df = pd.DataFrame()
    for year in range(2014, 2025):
        df = pd.read_csv(f"nba_data/shotdetail_{year}.csv")
        print(f"Dataframe for year {year} has shape {df.shape}")
        # filter out the non 3pt shots
        df = df[df['SHOT_TYPE'] == '3PT Field Goal']
        # Here we aggregate the dataframe to calculate the number of shots made and missed by each player
        df_p = df.groupby('PLAYER_ID').agg({'SHOT_MADE_FLAG': 'sum', 'SHOT_ATTEMPTED_FLAG': 'sum'}).reset_index()
        df_p['SEASON'] = year
        df_p['X_ID'] = df_p['PLAYER_ID']
        # drop the PLAYER_ID column
        df_p.drop(columns=['PLAYER_ID'], inplace=True)
        full_df = pd.concat([full_df, df_p], ignore_index=True)

        # A trick is that here we treat the team the same as the player, so we can aggregate the data
        df_t = df.groupby('TEAM_ID').agg({'SHOT_MADE_FLAG': 'sum', 'SHOT_ATTEMPTED_FLAG': 'sum'}).reset_index()
        df_t['SEASON'] = year
        df_t['X_ID'] = df_t['TEAM_ID']
        # drop the TEAM_ID column
        df_t.drop(columns=['TEAM_ID'], inplace=True)
        full_df = pd.concat([full_df, df_t], ignore_index=True)

    # Save the aggregated dataframe to a CSV file
    full_df.to_csv('x_shot_summary_2014_2024.csv', index=False)
