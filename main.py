import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

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
