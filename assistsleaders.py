import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leagueleaders, playergamelog
from datetime import datetime

def get_game_logs(player_id, season):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_logs.get_data_frames()[0]
    return df['AST']

def get_top_assist_leaders(seasons_back=10):
    current_year = datetime.now().year
    leaders = []

    for year in range(current_year - seasons_back, current_year + 1):
        season = f"{year-1}-{str(year)[-2:]}"
        print(f"Fetching data for season: {season}")

        try:
            data = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season)
            df = data.league_leaders.get_data_frame()

            if not df.empty:
                top_leader = df.iloc[0]
                assists_data = get_game_logs(top_leader['PLAYER_ID'], season)
                leaders.append({
                    'Season': season,
                    'Player': top_leader['PLAYER'],
                    'Assists Data': assists_data
                })
        except Exception as e:
            print(f"Error fetching data for season {season}: {e}")
            continue

    return leaders

top_assist_leaders = get_top_assist_leaders()

# Preparing data for the boxplot
plot_data = []
for leader in top_assist_leaders:
    player_name = leader['Player']
    season = leader['Season']
    player_season = f"{player_name} ({season})"
    assists_data = leader['Assists Data']

    for assist in assists_data:
        plot_data.append({'Player-Season': player_season, 'Season': season, 'Assists': assist})

df_plot = pd.DataFrame(plot_data)

# Sort the DataFrame by season in descending order for plotting
df_plot.sort_values(by='Season', ascending=False, inplace=True)

# Creating the boxplot using Plotly
fig = px.box(df_plot, x='Player-Season', y='Assists', title='Game-by-Game Assist Distribution of Top Assist Leaders by Season')
fig.update_layout(xaxis_title='Player (Season)', yaxis_title='Assists', boxmode='group')
fig.update_xaxes(categoryorder='array', categoryarray=df_plot['Player-Season'].unique())
fig.show()
