from extensions import db  # Import db instance
from datetime import datetime
from sqlalchemy import Numeric

class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    player_name = db.Column(db.String(255), nullable=False)
    season_stats = db.relationship('SeasonStats', backref='player', lazy=True)

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
    assists = db.Column(db.Float)
    games_played = db.Column(db.Integer)
    turnovers = db.Column(db.Float)
    points = db.Column(db.Float)
    game_logs = db.relationship('GameLog', back_populates='season_stats')
    
class GameLog(db.Model):
    __tablename__ = 'game_log'
    id = db.Column(db.Integer, primary_key=True)
    season_stats_id = db.Column(db.Integer, db.ForeignKey('season_stats.id'), nullable=False)  # Connect to SeasonStats
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

    # Relationship to SeasonStats
    season_stats = db.relationship('SeasonStats', back_populates='game_logs')
