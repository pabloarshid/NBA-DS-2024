import pandas as pd
from nba_api.stats.endpoints import leagueleaders, playergamelog

# Step 1: Get the Top 20 Assist Leaders among Players for the Current Season
# Using the LeagueLeaders endpoint with stat_category='AST' for assists
leaders = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season='2023-24', per_mode48='PerGame')
leaders_df = leaders.get_data_frames()[0]
top_20_assist_leaders = leaders_df.head(20)


# Step 2: Fetch Game-by-Game Assists and Turnovers Data
game_logs = []

for index, player in top_20_assist_leaders.iterrows():
    print(player)
    player_id = player['PLAYER_ID']
    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
    player_game_data = gamelog.get_data_frames()[0]
    # print(list(player_game_data.columns))
    player_game_data['PLAYER_NAME'] = player['PLAYER']
    game_logs.append(player_game_data[['PLAYER_NAME', 'GAME_DATE', 'AST', 'TOV']])

# Combine all players' game logs into a single DataFrame
all_players_game_log = pd.concat(game_logs)

# Step 3: Save or Process for Visualization
all_players_game_log.to_csv('nba_top_20_assist_leaders_game_log.csv', index=False)

print("Data retrieval complete. Game log saved to 'nba_top_20_assist_leaders_game_log.csv'.")
