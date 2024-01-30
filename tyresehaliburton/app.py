from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
import plotly.express as px
import pandas as pd
from models import AssistLeader, GameLog
from extensions import db  # Import the SQLAlchemy instance
from nba_api.stats.endpoints import leagueleaders, playergamelog
from datetime import datetime


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newerjeans@localhost:5432/postgres'

    db.init_app(app)  # Initialize the db instance with the app
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/haliburton')
    def haliburton():
        try:
            return render_template('haliburton.html')
        except Exception as e:
            # Handle errors like file not found, invalid format etc.
            return str(e), 500
    return app

# def create_box_plot(df, x_column, y_column, title):
#     # Calculate average assists per player
#     avg_assists = df.groupby(x_column)[y_column].mean().round(2)

#     # Create a new column for modified x-axis labels
#     df['x_labels'] = df[x_column].apply(lambda x: f"{x} (Avg: {avg_assists[x]} AST/G)")

#     # Create the box plot
#     fig = px.box(df, x='x_labels', y=y_column, title=title)
#     fig.update_traces(marker_color='#FDBB30', line_color='#FDBB30')
#     fig.update_layout(
#         height=600,
#         xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
#         yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
#         title_font=dict(color='#BEC0C2'),
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(0,0,0,0)'
#     )
#     return fig.to_html(full_html=False)



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)