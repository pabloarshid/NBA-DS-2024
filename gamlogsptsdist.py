import plotly.express as px
from nba_api.stats.endpoints import playergamelog, leaguedashplayerstats
from nba_api.stats.static import teams
import pandas as pd

def get_top_scorers_game_by_game(season):
    # Get list of NBA teams
    nba_teams = teams.get_teams()

    # DataFrame to store game logs of the top two scorers from each team
    all_top_scorers_game_logs = pd.DataFrame()

    for team in nba_teams:
        team_id = team['id']
        team_name = team['full_name']

        # Get player stats for the team
        player_stats = leaguedashplayerstats.LeagueDashPlayerStats(team_id_nullable=team_id, season=season).get_data_frames()[0]

        # Find the top two scorers for the team
        top_scorers = player_stats.sort_values(by='PTS', ascending=False).head(2)

        for _, scorer in top_scorers.iterrows():
            scorer_name = scorer['PLAYER_NAME']
            scorer_ppg = scorer['PTS'] / scorer['GP']

            # Get game log for each top scorer
            game_log = playergamelog.PlayerGameLog(player_id=scorer['PLAYER_ID'], season=season).get_data_frames()[0]
            game_log['Player'] = f"{scorer_name} ({scorer_ppg:.1f} PPG, {scorer['GP']} GP)"

            # Append to the main DataFrame
            all_top_scorers_game_logs = pd.concat([all_top_scorers_game_logs, game_log[['Player', 'GAME_DATE', 'PTS']]])

    return all_top_scorers_game_logs

# Example usage
season = '2023-24'
all_top_scorers_game_logs = get_top_scorers_game_by_game(season)

# Convert GAME_DATE to datetime for sorting
all_top_scorers_game_logs['GAME_DATE'] = pd.to_datetime(all_top_scorers_game_logs['GAME_DATE'])

# Calculate average PPG for sorting players
sorted_top_scorers = all_top_scorers_game_logs.groupby('Player')['PTS'].mean().sort_values(ascending=False).reset_index()

# Create a box plot with Plotly
fig = px.box(all_top_scorers_game_logs, x='Player', y='PTS', 
             title='Points Distribution of Top 2 Scorers in NBA Teams (' + season + ')',
             labels={'PTS': 'Points Scored', 'Player': 'Player'},
             category_orders={'Player': sorted_top_scorers['Player'].tolist()})

fig.show()
