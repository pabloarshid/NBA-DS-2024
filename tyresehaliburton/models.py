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
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    assist_leader = db.Column(db.Boolean, default=False, nullable=False)
    player_name = db.Column(db.String, nullable=False)
    assists = db.Column(db.Float)
    games_played = db.Column(db.Integer)
    turnovers = db.Column(db.Float)
    points = db.Column(db.Float)
    game_logs = db.relationship('GameLog', backref='season_stats', lazy=True)

class GameLog(db.Model):
    __tablename__ = 'game_log'
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    season_stats_id = db.Column(db.Integer, db.ForeignKey('season_stats.id'), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    points = db.Column(db.Float, nullable=False)
    minutes_played = db.Column(db.Float, nullable=False)  # Assuming you want to store minutes as a float
    assists = db.Column(db.Float, nullable=False)
    turnovers = db.Column(db.Float, nullable=False)