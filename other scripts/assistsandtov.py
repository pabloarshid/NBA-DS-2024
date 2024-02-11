import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leagueleaders, playergamelog
from datetime import datetime


def get_game_logs(player_id, season):
    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = game_logs.get_data_frames()[0]
    return df[['AST', 'TOV']]  # Fetch both assists and turnovers

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
                game_data = get_game_logs(top_leader['PLAYER_ID'], season)
                print(game_data)
                for _, row in game_data.iterrows():
                    leaders.append({
                        'Player-Season': f"{top_leader['PLAYER']} ({season})",
                        'Stat Type': 'Assists',
                        'Count': row['AST']
                    })
                    leaders.append({
                        'Player-Season': f"{top_leader['PLAYER']} ({season})",
                        'Stat Type': 'Turnovers',
                        'Count': row['TOV']
                    })
        except Exception as e:
            print(f"Error fetching data for season {season}: {e}")
            continue

    return leaders

top_assist_leaders = get_top_assist_leaders()

# Preparing data for the boxplot
df_plot = pd.DataFrame(top_assist_leaders)
print(df_plot)
# Extract the season year for sorting
# df_plot['Season Year'] = df_plot['Player-Season'].apply(lambda x: x.split('(')[-1].split(')')[0])
# # Sort the DataFrame by 'Season Year' and 'Player-Season' in descending order
# df_plot.sort_values(by=['Season Year', 'Player-Season'], ascending=False, inplace=True)

# # Creating the boxplot using Plotly
# fig = px.box(df_plot, x='Player-Season', y='Count', color='Stat Type', 
#              title='Game-by-Game Assist and Turnover Distribution of Top Assist Leaders by Season')
# fig.update_layout(xaxis_title='Player (Season)', yaxis_title='Count', boxmode='group')
# fig.update_xaxes(categoryorder='array', categoryarray=df_plot['Player-Season'].unique())
# fig.show()
