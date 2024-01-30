from extensions import db  # Import db instance
from datetime import datetime

class AssistLeader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, unique=True, nullable=False)
    player_name = db.Column(db.String, nullable=False)
    assists = db.Column(db.Integer, nullable=False)

class GameLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, nullable=False)
    game_date = db.Column(db.DateTime, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    turnovers = db.Column(db.Integer, nullable=False)
    # Add other fields as necessary