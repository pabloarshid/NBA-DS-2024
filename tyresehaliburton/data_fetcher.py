from datetime import datetime, timedelta
import pytz  # For timezone handling, install with 'pip install pytz'
from nba_api.stats.endpoints import leagueleaders, playergamelog
from models import GameLog, AssistLeader
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
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24', date_from_nullable=formatted_yesterday, date_to_nullable=formatted_today)
            player_game_data = gamelog.get_data_frames()[0]

            # Insert data into the database
            for _, row in player_game_data.iterrows():
                game_date = datetime.strptime(row['GAME_DATE'], '%b %d, %Y')
                if game_date.date() == yesterday:  # Check if the game happened yesterday
                    existing_entry = GameLog.query.filter_by(player_id=row['Player_ID'], game_date=game_date).first()
                    if not existing_entry:
                        game_log_entry = GameLog(
                            player_id=row['Player_ID'],
                            game_date=game_date,
                            assists=row['AST'],
                            turnovers=row['TOV']
                        )
                        db.session.add(game_log_entry)
            db.session.commit()
if __name__ == '__main__':
    fetch_and_store_nba_data()
