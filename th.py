from nba_api.stats.static import players
from nba_api.stats.endpoints import playerdashboardbyyearoveryear, leaguedashplayerstats
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# from pergamecategories import add_per_game_stats
def add_per_game_stats(df, categories, games_played_col):
    for category in categories:
        per_game_col = category + '/G'
        df[per_game_col] = df[category] / df[games_played_col]
    return df
# Get player ID for Tyrese Haliburton
players_list = players.get_players()
haliburton = [player for player in players_list if player['full_name'] == 'Tyrese Haliburton'][0]
player_id = haliburton['id']

# Fetch Tyrese Haliburton's stats for the 2023-24 season
haliburton_stats = playerdashboardbyyearoveryear.PlayerDashboardByYearOverYear(player_id=player_id, season='2023-24').get_data_frames()[1]

# Fetch league average stats for the 2023-24 season for comparison
league_avg_stats = leaguedashplayerstats.LeagueDashPlayerStats(season='2023-24', measure_type_detailed_defense='Base').get_data_frames()[0]

# Categories to calculate per game stats
categories = ["OREB", "DREB", "REB", "AST", "TOV", "STL", "BLK", "BLKA", "PF", "PTS"]

# Add per game stats to Haliburton's stats
haliburton_stats = add_per_game_stats(haliburton_stats, categories, 'GP')

# Add per game stats to league average stats
league_avg_stats = add_per_game_stats(league_avg_stats, categories, 'GP')
league_avg_stats.to_csv('league_avg_stats.csv')

print(haliburton_stats.to_string())
# ================================================================================
# ================================================================================
# ================================================================================
# ================================================================================
# ================================================================================
# Load data as before
# Create scatter plot

# Define a function to determine the color based on the value
# def determine_color(value):
#     if value > 20:
#         return 'GREEN'
#     if value > 10:
#         return 'yellow'
#     elif value > 5:
#         return 'orange'
#     else:
#         return 'red'

# Apply the function to create a new color column
# league_avg_stats['color'] = league_avg_stats['PTS/G'].apply(determine_color) # Replace 'ColumnY' with the column based on which color is determined

# Set the background style of the plot


# scatter_plot = sns.scatterplot(data=league_avg_stats, x='PTS/G', y='AST/G', hue='color', palette=['red', 'peach', 'orange','green'], legend=False)# Set the background color
# plt.gca().set_facecolor('black')
# for _, row in league_avg_stats.iterrows():
#     plt.scatter(row['ColumnX'], row['ColumnY'], color=row['color'], edgecolor='black', linewidth=1)


# Change the color of the axes and ticks
# plt.gca().spines['top'].set_color('white')
# plt.gca().spines['bottom'].set_color('white')
# plt.gca().spines['left'].set_color('white')
# plt.gca().spines['right'].set_color('white')
# plt.gca().tick_params(axis='x', colors='white')
# plt.gca().tick_params(axis='y', colors='white')

# plt.xlabel('ColumnX', color='white', fontsize=14, bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.5'))
# plt.ylabel('ColumnY', color='white', fontsize=14, bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.5'))

# Change the color of the tick labels to white
# scatter_plot.tick_params(colors='white', labelsize=12)

# Enlarge the figure size if needed
# scatter_plot.figure.set_size_inches(10, 6)

# plt.show()
