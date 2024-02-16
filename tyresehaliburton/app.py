############
# TODO
# 1. clean up so app.py and transform is seperated.
#############

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from routes import configure_routes
import os
#-------------------------------------------------
#  APP
#-------------------------------------------------

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:newerjeans@localhost:5432/postgres2')
    
    from models import db
    db.init_app(app)
    
    Migrate(app, db)
    
    configure_routes(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)