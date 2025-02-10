from nba_api.stats.endpoints import playergamelog
import pandas as pd
from nba_api.stats.static import players
import time
import random

# Get a list of all player IDs
player_list = players.get_players()

all_player_logs = []

for player in player_list:
    player_id = str(player['id'])
    print(f"Getting game logs for player ID: {player_id}")
    for season in range(2014, 2025):
        season_str = str(season) + "-" + str(season + 1)[2:]
        season_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season_str, timeout=2)
        season_logs_df = season_logs.get_data_frames()[0]
        print(f"Player ID: {player_id}, Season: {season_str}, Number of games: {season_logs_df.shape[0]}")
        all_player_logs.append(season_logs_df)
        # Sleep for a random amount of time between 1 and 2 seconds to avoid rate limiting
        time.sleep(random.uniform(1, 2))

# Combine all player logs into a single DataFrame
all_player_logs_df = pd.concat(all_player_logs, ignore_index=True)

# Save to CSV
all_player_logs_df.to_csv('all_player_game_logs_2014_2024.csv', index=False)
print("Game logs for all players from 2014 to 2024 saved to all_player_game_logs_2014_2024.csv")

# Also save the player list for reference
pd.DataFrame(player_list).to_csv('all_players.csv', index=False)
