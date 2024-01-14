# Updated script with HEX to RGB conversion for team colors

from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import teams
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def hex_to_rgb(hex_color):
    # Convert HEX to RGB
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r/255, g/255, b/255)

def get_top_scorers(season):
    # Get player statistics for the season
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season).get_data_frames()[0]

    # Sort players by points per game and group by team
    top_scorers = player_stats.sort_values(by='PTS', ascending=False).groupby('TEAM_ID').head(7)

    return top_scorers

def get_team_name_mapping():
    nba_teams = teams.get_teams()
    return {team['id']: team['full_name'] for team in nba_teams}

def get_team_colors():
    # Example team colors (in HEX format); add more as needed
    team_colors = {
        1610612737: '#C8102E',  # Atlanta Hawks
        1610612738: '#007A33',  # Boston Celtics
        1610612751: '#000000',  # Brooklyn Nets
        1610612739: '#860038', #Cleveland Cavs
        1610612740: '#0C2340', #NOP
        1610612741: '#CE1141', #Bulls
        1610612742: '#00538C', #DAL
        1610612743: '#0E2240', #DEN
        1610612744: '#006BB6', #GSW
        1610612745: '#BA0C2F', #HOU
        1610612746: '#c8102E', #LAC
        1610612747: '#FDB927', #LAL
        1610612748: '#98002E', #MIA
        1610612749: '#00471B', #MIL
        1610612750: '#78BE20', #MIN
        1610612752: '#F58426', #NYK
        1610612753: '#0077c0', #ORL
        1610612754: '#FDBB30', #IND
        1610612755: '#006BB6', #PHI
        1610612756: '#1d1160', #PHX
        1610612757: '#E03A3E', #PORT
        1610612758: '#5a2d81', #SAC
        1610612759: '#c4ced4', #SAS
        1610612760: '#007ac1', #OKC
        1610612761: '#B4975A', #TOR
        1610612762: '#002B5C', #UTA
        1610612763: '#5D76A9', #MEM
        1610612764: '#e31837', #WASH
        1610612765: '#1d42ba', #DET
        1610612766: '#00788C', #CHA
    }
    return team_colors

def main():
    season = '2023-24'  # Define the NBA season
    top_scorers = get_top_scorers(season)
    team_name_mapping = get_team_name_mapping()
    print(team_name_mapping)
    team_colors = get_team_colors()

    # Create a DataFrame for plotting
    plot_data = top_scorers[['TEAM_ID', 'PLAYER_NAME', 'PTS']].copy()
    plot_data['Rank'] = plot_data.groupby('TEAM_ID')['PTS'].rank(ascending=False, method='min')

    # Add a 'Team Name' and 'Color' column to the DataFrame
    plot_data['Team Name'] = plot_data['TEAM_ID'].map(team_name_mapping)
    plot_data['Color'] = plot_data['TEAM_ID'].map(team_colors)

    # Convert HEX colors to RGB
    plot_data['Color'] = plot_data['Color'].apply(hex_to_rgb)

    # Plotting
    plt.figure(figsize=(10, 6))

    for _, row in plot_data.iterrows():
        plt.scatter(row['Rank'], row['PTS'], color=row['Color'], label=row['Team Name'], s=50)

    plt.title('Top 7 NBA Scorers by Team (' + season + ')')
    plt.xlabel('Player Rank in Team')
    plt.ylabel('Points Scored')
    plt.legend(title='Teams', loc='upper left', bbox_to_anchor=(1, 1))  # Positioning the legend outside
    plt.xticks(range(1, 8))  # Assuming top 7 scorers per team
    plt.grid(True)

    plt.tight_layout()  # Adjust layout to fit everything
    plt.show()

if __name__ == "__main__":
    main()
