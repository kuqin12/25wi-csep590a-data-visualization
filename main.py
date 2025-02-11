from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.static import players
import time
import random


def try_collecting_player_data():
    # Get a list of all player IDs
    player_list = players.get_players()

    all_player_logs = []

    # if player_game_logs directory does not exist, create it
    import os
    if not os.path.exists('player_game_logs'):
        os.makedirs('player_game_logs')

    for player in player_list:
        player_id = str(player['id'])
        # Check if we already have logs for this player
        if os.path.exists(f'player_game_logs/{player_id}.csv'):
            print(f"Logs for player ID: {player_id} already exist, skipping")
            # Load the logs and append to the list
            player_logs_df = pd.read_csv(f'player_game_logs/{player_id}.csv')
            all_player_logs.append(player_logs_df)
            continue

        print(f"Getting game logs for player ID: {player_id}")
        player_logs = []
        for season in range(2014, 2025):
            season_str = str(season) + "-" + str(season + 1)[2:]
            season_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season_str, timeout=5)
            season_logs_df = season_logs.get_data_frames()[0]
            print(f"Player ID: {player_id}, Season: {season_str}, Number of games: {season_logs_df.shape[0]}")
            all_player_logs.append(season_logs_df)
            player_logs.append(season_logs_df)
            # Sleep for a random amount of time between 0.1 and 0.5 seconds to avoid rate limiting
            time.sleep(random.uniform(0.1, 0.5))

        # Save the logs for each player to a CSV file, in case the script is interrupted
        player_logs_df = pd.concat(player_logs, ignore_index=True)
        player_logs_df.to_csv(f'player_game_logs/{player_id}.csv', index=False)

    # Combine all player logs into a single DataFrame
    all_player_logs_df = pd.concat(all_player_logs, ignore_index=True)

    # Save to CSV
    all_player_logs_df.to_csv('all_player_game_logs_2014_2024.csv', index=False)
    print("Game logs for all players from 2014 to 2024 saved to all_player_game_logs_2014_2024.csv")

    # Also save the player list for reference
    pd.DataFrame(player_list).to_csv('all_players.csv', index=False)

    return 0


# Run the main function
if __name__ == "__main__":
    # keep trying to collect data until it is successful
    while True:
        try:
            ret = try_collecting_player_data()
            if ret == 0:
                print("Data collection successful")
                break
        except Exception as e:
            print(e)
            print("Error collecting data, trying again...")
            time.sleep(random.uniform(5, 10))
