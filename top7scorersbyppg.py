import plotly.express as px
from nba_api.stats.endpoints import leaguedashplayerstats
from nba_api.stats.static import teams
import pandas as pd

def hex_to_rgb(hex_color):
    # Convert HEX to RGB
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r/255, g/255, b/255)

def get_top_scorers_by_ppg(season):
    player_stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, measure_type_detailed_defense='Base').get_data_frames()[0]
     # Calculate Points Per Game
    player_stats['PPG'] = player_stats['PTS'] / player_stats['GP']

    # Sort players by Points Per Game (PTS) within each team and get the top 7 scorers
    top_scorers = player_stats.sort_values(by=['TEAM_ID', 'PPG'], ascending=[True, False]).groupby('TEAM_ID').head(7)
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
    season = '2023-24'
    top_scorers = get_top_scorers_by_ppg(season)

    # Map team IDs to team names and colors
    top_scorers['Team Name'] = top_scorers['TEAM_ID'].map(get_team_name_mapping())
    team_colors = get_team_colors()
    top_scorers['Color'] = top_scorers['TEAM_ID'].map(team_colors)

    # Convert HEX colors to RGB
    top_scorers['Color'] = top_scorers['Color'].apply(hex_to_rgb)

    # Rank players within each team
    top_scorers['Rank'] = top_scorers.groupby('TEAM_ID')['PPG'].rank(ascending=False, method='min')

    # Create a color mapping for the teams
    color_discrete_map = {team: hex_to_rgb(color) for team, color in team_colors.items()}

    # Create an interactive plot with Plotly
    fig = px.scatter(top_scorers, x='Rank', y='PPG', color='Team Name',
                     hover_data=['PLAYER_NAME', 'Team Name', 'PPG'],
                     color_discrete_map=color_discrete_map)

    fig.update_layout(title=f'Top 7 NBA Scorers by Points Per Game ({season})',
                      xaxis_title='Player Rank in Team',
                      yaxis_title='Points Per Game')
    fig.show()

if __name__ == "__main__":
    main()
