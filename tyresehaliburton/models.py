from extensions import db  # Import db instance

class AssistData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String, nullable=False)
    game_date = db.Column(db.DateTime, nullable=False)
    assists = db.Column(db.Integer, nullable=False)
    # Add more fields as needed
