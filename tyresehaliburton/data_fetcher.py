from datetime import datetime, timedelta
import pytz  # For timezone handling, install with 'pip install pytz'
from nba_api.stats.endpoints import leagueleaders, playergamelog, shotchartdetail
from models import GameLog, Season, SeasonStats, Player, Shotchart
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
        print(leaders_df.columns)
        top_assist_value = leaders_df.iloc[0]['AST']  # Get the highest assists per game value

        for index, row in leaders_df.iterrows():
            player_id = int(row['PLAYER_ID'])
            player_name = row['PLAYER']
            ast = row['AST']
            is_assist_leader = ast == top_assist_value  # Flag as assist leader if matches top value
            # Extracting additional stats from the row
            gp = row['GP']
            min_per_game = row['MIN']
            fgm = row['FGM']
            fga = row['FGA']
            fg_pct = row['FG_PCT']
            fg3m = row['FG3M']
            fg3a = row['FG3A']
            fg3_pct = row['FG3_PCT']
            ftm = row['FTM']
            fta = row['FTA']
            ft_pct = row['FT_PCT']
            oreb = row['OREB']
            dreb = row['DREB']
            reb = row['REB']
            stl = row['STL']
            blk = row['BLK']
            tov = row['TOV']
            pts = row['PTS']
            eff = row.get('EFF', None)  # Assuming EFF might not be in some responses
            ast_tov = row.get('AST_TOV', None)
            stl_tov = row.get('STL_TOV', None)

            # Insert or update Player in the database
            player = Player.query.filter_by(player_id=player_id).first()
            if not player:
                player = Player(player_id=player_id, player_name=player_name)
                db.session.add(player)
                db.session.commit()  # Commit to ensure player ID is available

            # Update SeasonStats for the player and season
            season_stats = SeasonStats.query.filter_by(player_id=player.player_id, season_id=season.id).first()
            if not season_stats:
                season_stats = SeasonStats(
                    player_id=player.player_id,
                    season_id=season.id,
                    assist_leader=is_assist_leader,
                    player_name=player_name,
                    ast=ast,
                    gp=gp,
                    tov=tov,
                    pts=pts,
                    # Initialize all other fields for a new record
                    min=min_per_game,
                    fgm=fgm,
                    fga=fga,
                    fg_pct=fg_pct,
                    fg3m=fg3m,
                    fg3a=fg3a,
                    fg3_pct=fg3_pct,
                    ftm=ftm,
                    fta=fta,
                    ft_pct=ft_pct,
                    oreb=oreb,
                    dreb=dreb,
                    reb=reb,
                    stl=stl,
                    blk=blk,
                    eff=eff,
                    ast_tov=ast_tov,
                    stl_tov=stl_tov
                )
                db.session.add(season_stats)
            else:
                # Directly update attributes for an existing record
                season_stats.assist_leader = is_assist_leader
                season_stats.ast = ast
                season_stats.gp = gp
                season_stats.pts = pts
                # Update all additional stats here
                season_stats.min = min_per_game
                season_stats.fgm = fgm
                season_stats.fga = fga
                season_stats.fg_pct = fg_pct
                season_stats.fg3m = fg3m
                season_stats.fg3a = fg3a
                season_stats.fg3_pct = fg3_pct
                season_stats.ftm = ftm
                season_stats.fta = fta
                season_stats.ft_pct = ft_pct
                season_stats.oreb = oreb
                season_stats.dreb = dreb
                season_stats.reb = reb
                season_stats.stl = stl
                season_stats.blk = blk
                season_stats.tov = tov
                season_stats.eff = eff if 'eff' in leaders_df.columns else None  # Check if EFF is present
                season_stats.ast_tov = ast_tov if 'AST_TOV' in leaders_df.columns else None
                season_stats.stl_tov = stl_tov if 'STL_TOV' in leaders_df.columns else None

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

                        season_stats = SeasonStats.query.filter_by(player_id=player.player_id, season_id=season.id).first()
                        if not season_stats:
                            season_stats = SeasonStats(player_id=player.player_id, season_id=season.id, assist_leader=True, player_name=player_name, assists=assists_per_game, games_played=games_played, turnovers=turnovers, points=points)
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
            season_stats_entries = SeasonStats.query.filter_by(player_id=player.player_id).all()
            
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
def fetch_and_load_shot_charts_for_all_players():
    # Fetch all players from your database
    app = create_app()
    with app.app_context():
        all_players = Player.query.all()

        for player in all_players:
            season_stats_records = SeasonStats.query.filter_by(player_id=player.player_id).all()
            for season_stats in season_stats_records:
                season = Season.query.filter_by(id=season_stats.season_id).first()
                if not season:
                    continue

                try:
                    shotchart_info = shotchartdetail.ShotChartDetail(
                        team_id=0,
                        player_id=player.player_id,
                        context_measure_simple='FGA',
                        season_nullable=season.year,
                        season_type_all_star='Regular Season'
                    )

                    shots = shotchart_info.get_data_frames()[0]

                    for _, row in shots.iterrows():
                        shot = Shotchart(
                            season_stats_id=season_stats.id,
                            player_id=player.id,
                            game_date=datetime.strptime(row['GAME_DATE'], '%Y%m%d').date(),
                            x_coordinate=row['LOC_X'],
                            y_coordinate=row['LOC_Y'],
                            shot_made=bool(row['SHOT_MADE_FLAG']),
                            # Map all new fields here,
                            game_id=row['GAME_ID'],
                            game_event_id=row['GAME_EVENT_ID'],
                            player_name=row['PLAYER_NAME'],
                            team_id=row['TEAM_ID'],
                            team_name=row['TEAM_NAME'],
                            period=row['PERIOD'],
                            minutes_remaining=row['MINUTES_REMAINING'],
                            seconds_remaining=row['SECONDS_REMAINING'],
                            event_type=row['EVENT_TYPE'],
                            action_type=row['ACTION_TYPE'],
                            shot_type=row['SHOT_TYPE'],
                            shot_zone_basic=row['SHOT_ZONE_BASIC'],
                            shot_zone_area=row['SHOT_ZONE_AREA'],
                            shot_zone_range=row['SHOT_ZONE_RANGE'],
                            shot_distance=row['SHOT_DISTANCE'],
                            shot_attempted_flag=bool(row['SHOT_ATTEMPTED_FLAG']),
                            htm=row.get('HTM', None),
                            vtm=row.get('VTM', None),
                        )
                        db.session.add(shot)
                except Exception as e:
                    print(f"Error fetching shot chart for {player.player_name} for season {season.year}: {e}")

        db.session.commit()

            
            
if __name__ == '__main__':
    try:
        fetch_top_assist_leaders()
        print("Top 20 assist leaders fetched successfully.")
        # fetch_top_assist_leaders_past_40_years()
        # print("Top assist leaders up to 40 years ago fetched successfully.")
        fetch_and_save_game_logs()
        print("PLayer game logs fetched successfully.")
        fetch_and_load_shot_charts_for_all_players()
        print("fetch_and_load_shot_charts_for_all_players succeeded")
    except Exception as e:
        print(f"An error occurred: {e}")
        db.session.rollback()