# data_fetcher.py
from nba_api.stats.endpoints import leagueleaders, playergamelog
from models import GameLog, AssistLeader
from datetime import datetime
from extensions import db 
from app import create_app


def fetch_and_store_nba_data():
    app = create_app()
    with app.app_context():
        # Fetch top 20 assist leaders
        leaders = leagueleaders.LeagueLeaders(stat_category_abbreviation='AST', season='2023-24', per_mode48='PerGame')
        leaders_df = leaders.get_data_frames()[0]
        top_20_assist_leaders = leaders_df.head(20)

        # Save assist leaders to the database
        for _, leader in top_20_assist_leaders.iterrows():
            # Check if the player is already in the database
            existing_leader = AssistLeader.query.filter_by(player_id=leader['PLAYER_ID']).first()
            if not existing_leader:
                new_leader = AssistLeader(
                    player_id=leader['PLAYER_ID'],
                    player_name=leader['PLAYER'],
                    assists=leader['AST']
                )
                db.session.add(new_leader)
        
        db.session.commit()
        # Step 2: Fetch Game-by-Game Assists and Turnovers Data
        for index, player in top_20_assist_leaders.iterrows():
            player_id = player['PLAYER_ID']
            gamelog = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
            player_game_data = gamelog.get_data_frames()[0]
            print(list(player_game_data.columns))
            # Step 3: Insert data into the database
            for _, row in player_game_data.iterrows():
                game_date = datetime.strptime(row['GAME_DATE'], '%b %d, %Y')  # Adjust format as necessary
                # Check if entry exists to avoid duplicates
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
