from extensions import db  # Import db instance
from datetime import datetime
from sqlalchemy import Numeric



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    player_name = db.Column(db.String(255), nullable=False)
    # Relationship to season stats
    season_stats = db.relationship('SeasonStats', backref='player', lazy='dynamic')

    
class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(9), unique=True, nullable=False)  # "YYYY-YY"
    # Relationship to season stats
    stats = db.relationship('SeasonStats', backref='season', lazy='dynamic')

class SeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    assist_leader = db.Column(db.Boolean, default=False, nullable=False)
    player_name = db.Column(db.String, nullable=False)
    assists = db.Column(Numeric(precision=5, scale=3))
    games_played = games_played = db.Column(db.Integer)
    turnovers = db.Column(Numeric(precision=5, scale=3))
    points = db.Column(Numeric(precision=5, scale=3))
    # game_logs = db.relationship('GameLog', backref='assist_leader', lazy='dynamic')

class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    turnovers = db.Column(db.Integer, nullable=False)
    # assist_leader_id = db.Column(db.Integer, db.ForeignKey('assist_leader.id'))
