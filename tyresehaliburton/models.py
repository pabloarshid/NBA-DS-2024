from extensions import db  # Import db instance
from datetime import datetime
from sqlalchemy import Numeric

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    player_name = db.Column(db.String(255), nullable=False)
    season_stats = db.relationship('SeasonStats', backref='player', lazy=True)
    shotcharts = db.relationship('Shotchart', backref='player', lazy=True)

class Season(db.Model):
    __tablename__ = 'season'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(9), unique=True, nullable=False)
    stats = db.relationship('SeasonStats', backref='season', lazy=True)

class SeasonStats(db.Model):
    __tablename__ = 'season_stats'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    assist_leader = db.Column(db.Boolean, default=False, nullable=False)
    player_name = db.Column(db.String, nullable=False)
    ast = db.Column(db.Float)
    pts = db.Column(db.Float)
    game_logs = db.relationship('GameLog', back_populates='season_stats')
    shotcharts = db.relationship('Shotchart', backref='season_stats', lazy=True)
    # New fields from API
    team = db.Column(db.String)
    gp = db.Column(db.Integer)
    min = db.Column(db.Float)
    fgm = db.Column(db.Float)
    fga = db.Column(db.Float)
    fg_pct = db.Column(db.Float)
    fg3m = db.Column(db.Float)
    fg3a = db.Column(db.Float)
    fg3_pct = db.Column(db.Float)
    ftm = db.Column(db.Float)
    fta = db.Column(db.Float)
    ft_pct = db.Column(db.Float)
    oreb = db.Column(db.Float)
    dreb = db.Column(db.Float)
    reb = db.Column(db.Float)
    stl = db.Column(db.Float)
    blk = db.Column(db.Float)
    tov = db.Column(db.Float)
    pf = db.Column(db.Float)
    eff = db.Column(db.Float)
    ast_tov = db.Column(db.Float)
    stl_tov = db.Column(db.Float)
    
class GameLog(db.Model):
    __tablename__ = 'game_log'
    id = db.Column(db.Integer, primary_key=True)
    season_stats_id = db.Column(db.Integer, db.ForeignKey('season_stats.id'), nullable=False)
    game_id = db.Column(db.String, nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    matchup = db.Column(db.String, nullable=False)
    wl = db.Column(db.String(1))
    min = db.Column(db.Float, nullable=False)
    fgm = db.Column(db.Integer)
    fga = db.Column(db.Integer)
    fg_pct = db.Column(db.Float)
    fg3m = db.Column(db.Integer)
    fg3a = db.Column(db.Integer)
    fg3_pct = db.Column(db.Float)
    ftm = db.Column(db.Integer)
    fta = db.Column(db.Integer)
    ft_pct = db.Column(db.Float)
    oreb = db.Column(db.Integer)
    dreb = db.Column(db.Integer)
    reb = db.Column(db.Integer)
    ast = db.Column(db.Integer)
    stl = db.Column(db.Integer)
    blk = db.Column(db.Integer)
    tov = db.Column(db.Integer)
    pf = db.Column(db.Integer)
    pts = db.Column(db.Integer)
    plus_minus = db.Column(db.Integer)

    season_stats = db.relationship('SeasonStats', back_populates='game_logs')

class Shotchart(db.Model):
    __tablename__ = 'shotchart'
    id = db.Column(db.Integer, primary_key=True)
    season_stats_id = db.Column(db.Integer, db.ForeignKey('season_stats.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    x_coordinate = db.Column(db.Float, nullable=False)
    y_coordinate = db.Column(db.Float, nullable=False)
    shot_made = db.Column(db.Boolean, nullable=False)
    
    # New fields
    grid_type = db.Column(db.String)
    game_id = db.Column(db.String, nullable=False)
    game_event_id = db.Column(db.Integer)
    player_name = db.Column(db.String)
    team_id = db.Column(db.Integer)
    team_name = db.Column(db.String)
    period = db.Column(db.Integer)
    minutes_remaining = db.Column(db.Integer)
    seconds_remaining = db.Column(db.Integer)
    event_type = db.Column(db.String)
    action_type = db.Column(db.String)
    shot_type = db.Column(db.String)
    shot_zone_basic = db.Column(db.String)
    shot_zone_area = db.Column(db.String)
    shot_zone_range = db.Column(db.String)
    shot_distance = db.Column(db.Integer)
    shot_attempted_flag = db.Column(db.Boolean)
    htm = db.Column(db.String)
    vtm = db.Column(db.String)
