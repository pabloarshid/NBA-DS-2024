from datetime import datetime, timedelta
import pytz  # For timezone handling, install with 'pip install pytz'
from nba_api.stats.endpoints import leagueleaders, playergamelog
from models import GameLog, AssistLeader, Player
from extensions import db
from app import create_app


today = datetime.now()
yesterday = today - timedelta(days=1)
formatted_yesterday = yesterday.strftime('%m/%d/%Y')
formatted_today = today.strftime('%m/%d/%Y')

def fetch_and_store_nba_data():
    app = create_app()
    with app.app_context():
        # Fetch top 20 assist leaders
        leaders = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season='2023-24', per_mode48='PerGame')
        leaders_df = leaders.get_data_frames()[0]
        top_20_assist_leaders = leaders_df.head(20)
        # print(leaders_df.columns)
        # Save assist leaders to the database
        for _, leader in top_20_assist_leaders.iterrows():
            existing_leader = AssistLeader.query.filter_by(player_id=leader['PLAYER_ID']).first()
            if existing_leader:
                # Update existing record
                existing_leader.games_played = leader['GP']  # Assuming 'G' is the games played field from your data source
                existing_leader.turnovers = leader['TOV'] 
                existing_leader.points = leader['PTS'] 
                db.session.commit()
            else:
                # Add new record
                new_leader = AssistLeader(
                    player_id=leader['PLAYER_ID'],
                    player_name=leader['PLAYER'],
                    assists=leader['AST'],
                    games_played=leader['GP'],
                    turnovers=leader['TOV'],
                    points=leader['PTS']
                )
                db.session.add(new_leader)
                db.session.commit()
       # Fetch only today's game log data

        for index, player in top_20_assist_leaders.iterrows():
            player_id = player['PLAYER_ID']
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
            player_game_data = gamelog.get_data_frames()[0]
            # print(player_game_data.head())
            # Insert data into the database
            for _, row in player_game_data.iterrows():
                game_date = datetime.strptime(row['GAME_DATE'], '%b %d, %Y')
                # print(yesterday)
                # print(game_date)
                # if game_date.date() == yesterday:
                existing_entry = GameLog.query.filter_by(player_id=row['Player_ID'], game_date=game_date).first()
                if not existing_entry:
                    game_log_entry = GameLog(
                        player_id=row['Player_ID'],
                        game_date=game_date,
                        assists=row['AST'],
                        turnovers=row['TOV']
                    )
                    db.session.add(game_log_entry)

            # Commit all new entries outside the loop
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error during commit: {e}")
                db.session.rollback()
                
def fetch_and_store_assist_leaders(seasons_back=10):
    app = create_app()
    with app.app_context():
        current_year = datetime.now().year
        for year in range(current_year - seasons_back, current_year):
            season = f"{year-1}-{str(year)[2:]}"
            print(f"Fetching data for season: {season}")
            try:
                # Fetch the assist leader for the season
                data = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season=season, per_mode48='PerGame')
                df = data.get_data_frames()[0]
                
                if not df.empty:
                    assist_leader = df.iloc[0]
                    # print(assist_leader.columns)
                    player_name = assist_leader['PLAYER']
                    player_id = assist_leader['PLAYER_ID']

                    # Check if player for the season already exists
                    player = Player.query.filter_by(name=player_name, season=season).first()
                    if not player:
                        player = Player(name=player_name, season=season)
                        db.session.add(player)
                        db.session.commit()

                    # Fetch game logs
                    game_logs = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
                    for _, row in game_logs.iterrows():
                        game_date = datetime.strptime(row['GAME_DATE'], '%b %d, %Y').date()
                        # Check if game log already exists to prevent duplicates
                        if not GameLog.query.filter_by(player_id=player.id, game_date=game_date).first():
                            game_log_entry = GameLog(player_id=player.id, game_date=game_date, assists=row['AST'], turnovers=row['TOV'])
                            db.session.add(game_log_entry)
                    db.session.commit()
            except Exception as e:
                print(f"Error fetching data for season {season}: {e}")

            
if __name__ == '__main__':
    # fetch_and_store_nba_data()
    fetch_and_store_assist_leaders()