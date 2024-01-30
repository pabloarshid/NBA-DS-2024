from app import create_app
from models import AssistLeader  # Replace with your actual model
from extensions import db

app = create_app()
with app.app_context():
    results = AssistLeader.query.all()  # Replace 'YourModel' with your actual model class
    for result in results:
        print(f'Field1: {result.player_id}, Field2: {result.player_name}, Field3: {result.points}')  # Customize based on your model's fields
