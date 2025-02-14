from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.static import players, teams
import time
import random
from nba_api.stats.endpoints import playerdashptshots, leaguehustlestatsplayer, leaguehustlestatsteam
import get_nba_data
import os


# Run the main function
if __name__ == "__main__":
    # Get the list of all players
    player_list = players.get_players()
    if not os.path.exists('all_players.csv'):
        pd.DataFrame(player_list).to_csv('all_players.csv', index=False)

    # Get the list of all teams
    team_list = teams.get_teams()
    if not os.path.exists('all_teams.csv'):
        pd.DataFrame(team_list).to_csv('all_teams.csv', index=False)

    # # Data is downloaded from the https://github.com/shufinskiy/nba_data as of 2025-02-11
    # if not os.path.exists('nba_data'):
    #     get_nba_data.get_nba_data(path='nba_data', seasons=range(2014, 2025), data=['shotdetail'], untar=True)

    # # For all the data in nba, we read all shotdetail_<year> csv into a dataframe
    # full_df = pd.DataFrame()
    # for year in range(2014, 2025):
    #     df = pd.read_csv(f"nba_data/shotdetail_{year}.csv")
    #     print(f"Dataframe for year {year} has shape {df.shape}")
    #     # filter out the non 3pt shots
    #     df = df[df['SHOT_TYPE'] == '3PT Field Goal']
    #     # Here we aggregate the dataframe to calculate the number of shots made and missed by each player
    #     df_p = df.groupby('PLAYER_ID').agg({'SHOT_MADE_FLAG': 'sum', 'SHOT_ATTEMPTED_FLAG': 'sum'}).reset_index()
    #     df_p['SEASON'] = year
    #     df_p['X_ID'] = df_p['PLAYER_ID']
    #     # drop the PLAYER_ID column
    #     df_p.drop(columns=['PLAYER_ID'], inplace=True)
    #     full_df = pd.concat([full_df, df_p], ignore_index=True)

    #     # A trick is that here we treat the team the same as the player, so we can aggregate the data
    #     df_t = df.groupby('TEAM_ID').agg({'SHOT_MADE_FLAG': 'sum', 'SHOT_ATTEMPTED_FLAG': 'sum'}).reset_index()
    #     df_t['SEASON'] = year
    #     df_t['X_ID'] = df_t['TEAM_ID']
    #     # drop the TEAM_ID column
    #     df_t.drop(columns=['TEAM_ID'], inplace=True)
    #     full_df = pd.concat([full_df, df_t], ignore_index=True)

    # # Save the aggregated dataframe to a CSV file
    # if not os.path.exists('x_shot_summary_2014_2024.csv'):
    #     full_df.to_csv('x_shot_summary_2014_2024.csv', index=False)

    # The repo above does not provide the contested data, so we need to get it from the nba_api
    contested_df = pd.DataFrame()
    for year in range(2014, 2025):
        # Get the player hustle stats for the year
        player_hustle_stats = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
            season=str(year) + "-" + str(year + 1)[2:]
        )
        player_hustle_stats_df = player_hustle_stats.get_data_frames()[0]
        # Keep the CONTESTED_SHOTS_3PT and PLAYER_NAME columns
        player_hustle_stats_df = player_hustle_stats_df[['CONTESTED_SHOTS_3PT', 'PLAYER_ID']]
        player_hustle_stats_df['SEASON'] = year
        player_hustle_stats_df.rename(columns={'PLAYER_ID': 'X_ID'}, inplace=True)
        contested_df = pd.concat([contested_df, player_hustle_stats_df], ignore_index=True)
        print(f"Dataframe for year {year} has shape {player_hustle_stats_df.shape}")

        # Do the same for the team hustle stats
        teams_hustle_stats = leaguehustlestatsteam.LeagueHustleStatsTeam(
            season=str(year) + "-" + str(year + 1)[2:]
        )
        team_hustle_stats_df = teams_hustle_stats.get_data_frames()[0]
        # Keep the CONTESTED_SHOTS_3PT and PLAYER_NAME columns
        team_hustle_stats_df = team_hustle_stats_df[['CONTESTED_SHOTS_3PT', 'TEAM_NAME']]
        team_hustle_stats_df['SEASON'] = year
        team_hustle_stats_df.rename(columns={'TEAM_NAME': 'X_ID'}, inplace=True)
        contested_df = pd.concat([contested_df, team_hustle_stats_df], ignore_index=True)
        print(f"Dataframe for year {year} has shape {team_hustle_stats_df.shape}")

        # Sleep for a random time between 1 and 5 seconds
        time.sleep(random.randint(1, 5))

    # Save the contested shots dataframe to a CSV file
    if not os.path.exists('contested_shots_2014_2024.csv'):
        contested_df.to_csv('contested_shots_2014_2024.csv', index=False)    
