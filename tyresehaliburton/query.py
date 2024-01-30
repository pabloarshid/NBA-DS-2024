from app import create_app
from models import GameLog  # Replace with your actual model
from extensions import db

app = create_app()
with app.app_context():
    results = GameLog.query.all()  # Replace 'YourModel' with your actual model class
    for result in results:
        print(f'Field1: {result.player_id}, Field2: {result.game_date}, Field3: {result.assists}')  # Customize based on your model's fields
