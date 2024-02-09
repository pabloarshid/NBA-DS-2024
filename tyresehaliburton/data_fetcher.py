from datetime import datetime, timedelta
import pytz  # For timezone handling, install with 'pip install pytz'
from nba_api.stats.endpoints import leagueleaders, playergamelog
from models import GameLog, Season, SeasonStats, Player
from extensions import db
from app import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
import numpy as np

sqlalchemy_database_uri='postgresql://postgres:newerjeans@localhost:5432/postgres2'

# Assuming 'sqlalchemy_database_uri' is your database URI
engine = create_engine(sqlalchemy_database_uri)
Session = sessionmaker(bind=engine)
                
def fetch_top_assist_leaders():
    app = create_app()
    with app.app_context():
        current_year = datetime.now().year
        season_str = f"{current_year-1}-{str(current_year)[-2:]}"  # Season format: "YYYY-YY"

        # Ensure the Season exists
        season = Season.query.filter_by(year=season_str).first()
        if not season:
            season = Season(year=season_str)
            db.session.add(season)
            db.session.commit()

        # Fetching the top 20 assist leaders
        assist_leaders_data = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season_str, per_mode48='PerGame')
        leaders_df = assist_leaders_data.get_data_frames()[0].head(20)

        top_assist_value = leaders_df.iloc[0]['AST']  # Get the highest assists per game value

        for index, row in leaders_df.iterrows():
            player_id = int(row['PLAYER_ID'])
            player_name = row['PLAYER']
            assists_per_game = row['AST']
            is_assist_leader = assists_per_game == top_assist_value  # Flag as assist leader if matches top value
            # Other stats processing...
            games_played = row['GP']
            turnovers = row['TOV']
            points = row['PTS']

            # Insert or update Player in the database
            player = Player.query.filter_by(player_id=player_id).first()
            if not player:
                player = Player(player_id=player_id, player_name=player_name)
                db.session.add(player)
                db.session.commit()  # Commit to ensure player ID is available

            # Update SeasonStats for the player and season
            season_stats = SeasonStats.query.filter_by(player_id=player.id, season_id=season.id).first()
            if not season_stats:
                season_stats = SeasonStats(player_id=player.id, season_id=season.id, assist_leader=is_assist_leader, player_name=player_name, assists=assists_per_game, games_played=games_played, turnovers=turnovers, points=points)
                db.session.add(season_stats)
            else:
                # Update existing stats, potentially adjust the assist_leader flag
                season_stats.assist_leader = is_assist_leader
                season_stats.assists = assists_per_game
                season_stats.games_played = games_played
                season_stats.turnovers = turnovers
                season_stats.points = points

        db.session.commit()        
def fetch_top_assist_leaders_past_40_years():
    app = create_app()
    with app.app_context():
        current_year = datetime.now().year
        for year in range(current_year - 40, current_year):
            season_str = f"{year-1}-{str(year)[-2:]}"  # Season format: "YYYY-YY"
            print(f"Fetching top assist leader for season: {season_str}")

            try:
                season = Season.query.filter_by(year=season_str).first()
                if not season:
                    season = Season(year=season_str)
                    db.session.add(season)
                    db.session.commit()

                assist_leaders_data = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season_str, per_mode48='PerGame')
                leaders_df = assist_leaders_data.get_data_frames()[0]

                if not leaders_df.empty:
                    for index, row in leaders_df.iterrows():
                        # No need to use .head(1) now, just break after processing the first row
                        player_id = int(row['PLAYER_ID'])
                        player_name = row['PLAYER']
                        assists_per_game = row['AST']
                        
                        games_played = row['GP']
                        turnovers = row['TOV']
                        points = row['PTS']

                        player = Player.query.filter_by(player_id=player_id).first()
                        if not player:
                            player = Player(player_id=player_id, player_name=player_name)
                            db.session.add(player)
                            db.session.commit()

                        season_stats = SeasonStats.query.filter_by(player_id=player.id, season_id=season.id).first()
                        if not season_stats:
                            season_stats = SeasonStats(player_id=player.id, season_id=season.id, assist_leader=True, player_name=player_name, assists=assists_per_game, games_played=games_played, turnovers=turnovers, points=points)
                            db.session.add(season_stats)
                        else:
                            season_stats.assist_leader = True
                            season_stats.assists = assists_per_game
                            season_stats.games_played = games_played
                            season_stats.turnovers = turnovers
                            season_stats.points = points

                        db.session.commit()
                        break  # Ensure only the first row is processed
                        
            except Exception as e:
                print(f"Error fetching data for season {season_str}: {e}")
                db.session.rollback()

def fetch_and_save_game_logs():
    app = create_app()
    with app.app_context():
        players = Player.query.all()
        
        for player in players:
            season_stats_entries = SeasonStats.query.filter_by(player_id=player.id).all()
            
            for season_stats in season_stats_entries:
                season = Season.query.get(season_stats.season_id)
                if not season:
                    continue  # Skip if season not found
                
                season_str = season.year
                print(f"Fetching game logs for {player.player_name} for the {season_str} season.")
                
                try:
                    game_logs_data = playergamelog.PlayerGameLog(player_id=player.player_id, season=season_str).get_data_frames()[0]
                except Exception as e:
                    print(f"Error fetching game logs: {e}")
                    continue
                
                for _, row in game_logs_data.iterrows():
                    game_id = row['Game_ID']
                    # Check if game log entry already exists
                    existing_log = GameLog.query.filter_by(game_id=game_id, season_stats_id=season_stats.id).first()
                    
                    if existing_log:
                        print(f"Game log for game {game_id} already exists. Skipping.")
                        continue  # Skip existing entries
                    
                    # Create new game log entry
                    new_log = GameLog(
                        season_stats_id=season_stats.id,
                        game_id=game_id,
                        game_date=datetime.strptime(row['GAME_DATE'], '%b %d, %Y'),
                        matchup=row['MATCHUP'],
                        wl=row['WL'],
                        min=row['MIN'],
                        fgm=row['FGM'],
                        fga=row['FGA'],
                        fg_pct=row['FG_PCT'],
                        fg3m=row['FG3M'],
                        fg3a=row['FG3A'],
                        fg3_pct=row['FG3_PCT'],
                        ftm=row['FTM'],
                        fta=row['FTA'],
                        ft_pct=row['FT_PCT'],
                        oreb=row['OREB'],
                        dreb=row['DREB'],
                        reb=row['REB'],
                        ast=row['AST'],
                        stl=row['STL'],
                        blk=row['BLK'],
                        tov=row['TOV'],
                        pf=row['PF'],
                        pts=row['PTS'],
                        plus_minus=row['PLUS_MINUS'],
                    )
                    db.session.add(new_log)
                
                db.session.commit()
                print(f"Finished updating game logs for {player.player_name} for the {season_str} season.")


            
            
if __name__ == '__main__':
    try:
        # fetch_top_assist_leaders()
        # print("Top 20 assist leaders fetched successfully.")
        # fetch_top_assist_leaders_past_40_years()
        # print("Top assist leaders up to 40 years ago fetched successfully.")
        fetch_and_save_game_logs()
        print("PLayer game logs fetched successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()