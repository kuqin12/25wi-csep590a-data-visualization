import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playergamelog

def get_all_players_stats(season):
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]
    return player_stats

def save_stats_to_csv(season, file_name='player_stats.csv'):
    player_stats = get_all_players_stats(season)
    player_stats.to_csv(file_name, index=False)
    return f"Player stats for {season} saved to {file_name}"

# Example usage
season = '2022-23'
print(save_stats_to_csv(season))

player_logs = playergamelog.PlayerGameLog(player_id='203999', season=season)
player_logs_df = player_logs.get_data_frames()[0]

# Save to CSV
player_logs_df.to_csv('player_game_logs.csv', index=False)
