from datetime import datetime, timedelta
import pytz  # For timezone handling, install with 'pip install pytz'
from nba_api.stats.endpoints import leagueleaders, playergamelog
from models import GameLog, Season, SeasonStats, Player
from extensions import db
from app import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sqlalchemy_database_uri='postgresql://postgres:newerjeans@localhost:5432/postgres2'

# Assuming 'sqlalchemy_database_uri' is your database URI
engine = create_engine(sqlalchemy_database_uri)
Session = sessionmaker(bind=engine)

today = datetime.now()
yesterday = today - timedelta(days=1)
formatted_yesterday = yesterday.strftime('%m/%d/%Y')
formatted_today = today.strftime('%m/%d/%Y')

                
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

        for index, row in leaders_df.iterrows():
            player_id = int(row['PLAYER_ID'])
            player_name = row['PLAYER']
            assists_per_game = row['AST']
            # Assuming 'GP' is the column for games played, 'TOV' for turnovers, and 'PTS' for points
            games_played = row['GP']
            turnovers = row['TOV']
            points = row['PTS']

            # Insert or update Player in the database
            player = Player.query.filter_by(player_id=player_id).first()
            if not player:
                player = Player(player_id=player_id, player_name=player_name)
                db.session.add(player)
                db.session.commit()  # Ensure player is committed to get an ID for foreign key relations
            
            # Update SeasonStats for the player and season
            season_stats = SeasonStats.query.filter_by(player_id=player.id, season_id=season.id).first()
            if not season_stats:
                season_stats = SeasonStats(player_id=player.id, season_id=season.id, assist_leader=True, player_name=player_name, assists=assists_per_game, games_played=games_played, turnovers=turnovers, points=points)
                db.session.add(season_stats)
            else:
                # Update existing stats
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
            season = f"{year-1}-{str(year)[-2:]}"  # Season format: "YYYY-YY"
            print(f"Fetching top assist leader for season: {season}")

            try:
                # Fetching the top assist per game leader for the season
                assist_leaders_data = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season, per_mode48='PerGame')
                leaders_df = assist_leaders_data.get_data_frames()[0]

                if not leaders_df.empty:
                    top_leader = leaders_df.iloc[0]
                    player_id = int(top_leader['PLAYER_ID'])
                    player_name = top_leader['PLAYER']

                    # Use Flask-SQLAlchemy's session to query the database
                    existing_player = db.session.get(Player, player_id)
                    if not existing_player:
                        new_player = Player(player_id=player_id, player_name=player_name, season=season)
                        db.session.add(new_player)
                    else:
                        # Optionally update existing player's data if necessary
                        existing_player.player_name = player_name
                        existing_player.season = season

                db.session.commit()
            except Exception as e:
                print(f"Error fetching data for season {season}: {e}")
                db.session.rollback()
            
if __name__ == '__main__':
    # fetch_and_store_nba_data()
    # fetch_and_store_assist_leaders()
    try:
        fetch_top_assist_leaders()
        print("Top 20 assist leaders fetched successfully.")
        # fetch_top_assist_leaders_past_40_years()
        # print("Top assist leaders up to 40 years ago fetched successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()