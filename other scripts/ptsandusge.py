from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.endpoints import playergamelog, boxscoreusagev3

import pandas as pd

# Function to get player game logs
def get_player_game_logs(player_id, season='2023-24'):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    return game_logs['Game_ID'].tolist()

# Function to calculate average Usage Percentage
def calculate_avg_usage(player_id, season='2023-24'):
    game_ids= get_player_game_logs(player_id, season)
    # print(player_id,game_ids)
    usage_percentages = []
    for game_id in game_ids:
        usage_data = boxscoreusagev3.BoxScoreUsageV3(game_id=game_id).get_data_frames()[0]
        player_usage_data = usage_data[usage_data['personId'] == player_id]
        if not player_usage_data.empty:
            usage_percentage = player_usage_data['usagePercentage'].iloc[0]
            usage_percentages.append(usage_percentage)
# Calculate average usage percentage
    return sum(usage_percentages) / len(usage_percentages) if usage_percentages else 0


# Initialize DataFrame to store top scorers' data

top_scorers_df = pd.DataFrame(columns=['Team', 'Player', 'PPG', 'AvgUsage%'])
# Get all NBA teams

nba_teams = teams.get_teams()
# Fetch player stats for the current season

player_stats = leaguedashplayerstats.LeagueDashPlayerStats(per_mode_detailed='PerGame').get_data_frames()[0]
# Iterate over each team and fetch top 2 scorers

for team in nba_teams:
    team_players = player_stats[player_stats['TEAM_ID'] == team['id']]
    top_scorers = team_players.nlargest(2, 'PTS')[['PLAYER_ID', 'PLAYER_NAME', 'PTS']]
    for _, scorer in top_scorers.iterrows():
        player_id = scorer['PLAYER_ID']
        avg_usage = calculate_avg_usage(player_id)
        top_scorers_df = top_scorers_df._append({
            'Team': team['full_name'],
            'Player': scorer['PLAYER_NAME'],
            'PPG': scorer['PTS'],
            'AvgUsage%': avg_usage
        }, ignore_index=True)

# Display the DataFrame

print(top_scorers_df)