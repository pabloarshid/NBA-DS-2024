import pandas as pd
from nba_api.stats.endpoints import leagueleaders, teamplayeronoffsummary
from datetime import datetime

def get_team_offensive_rating(team_id, player_id, season):
    team_stats = teamplayeronoffsummary.TeamPlayerOnOffSummary(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]  # Selecting the correct DataFrame

    # Filter for the specific player using player_id
    player_row = df[df['VS_PLAYER_ID'] == player_id]

    # Extract offensive rating
    offensive_rating = player_row['OFF_RATING'].iloc[0] if not player_row.empty else None

    return offensive_rating

def get_top_assist_leaders_team_stats(seasons_back=10):
    current_year = datetime.now().year
    team_stats_data = []

    for year in range(current_year - seasons_back, current_year + 1):
        season = f"{year-1}-{str(year)[-2:]}"
        print(f"Fetching data for season: {season}")

        try:
            assist_leaders = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season)
            df_leaders = assist_leaders.league_leaders.get_data_frame()

            if not df_leaders.empty:
                top_leader = df_leaders.iloc[0]
                offensive_rating = get_team_offensive_rating(top_leader['TEAM_ID'], top_leader['PLAYER_ID'], season)

                team_stats_data.append({
                    'Season': season,
                    'Player': top_leader['PLAYER'],
                    'Team': top_leader['TEAM'],
                    'Offensive Rating': offensive_rating
                })
        except Exception as e:
            print(f"Error fetching data for season {season}: {e}")
            continue

    return pd.DataFrame(team_stats_data)

top_assist_leaders_team_stats = get_top_assist_leaders_team_stats()
print(top_assist_leaders_team_stats)
