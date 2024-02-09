from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
import plotly.express as px
import pandas as pd
from models import  GameLog
from extensions import db  # Import the SQLAlchemy instance
from nba_api.stats.endpoints import leagueleaders, playergamelog
from datetime import datetime
import numpy as np


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newerjeans@localhost:5432/postgres2'

    db.init_app(app)  # Initialize the db instance with the app
    migrate = Migrate(app, db)  # Initialize Flask-Migrate

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/haliburton')
    def haliburton():
        try:
            # Fetch data from database
            leaders = AssistLeader.query.order_by(AssistLeader.assists.desc()).limit(20).all()
            
            # Prepare data for plotting
            names = [leader.player_name for leader in leaders]
            assists = [leader.assists for leader in leaders]
 # Crea te Plotly figure
            fig = px.bar(x=names, y=assists, title="Top 20 NBA Assist Leaders")
                # Update layout for transparent background
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_tickangle=-90  # Rotate x-axis labels to vertical
            )
            # Convert to HTML
            graph_html = fig.to_html(full_html=False)
            
            # Fetch the top 20 assist leaders
            top_20_leaders = AssistLeader.query.order_by(AssistLeader.assists.desc()).limit(20).all()

            # Prepare data for plotting
            data = []
            for leader in top_20_leaders:
                for log in leader.game_logs:
                    data.append({'Player': leader.player_name, 'Category': 'Assists', 'Count': log.assists})
                    data.append({'Player': leader.player_name, 'Category': 'Turnovers', 'Count': log.turnovers})
            df = pd.DataFrame(data)     # Create Plotly figure for boxplot
            # Create the box plot
            fig2 = px.box(df, x='Player', y='Count', color='Category', title="Assists and Turnovers Distribution of Top 20 NBA Assist Leaders")
    
            # fig2.update_traces(marker_color='#FDBB30', line_color='#FDBB30')
            fig2.update_layout(
                height=600,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                title_font=dict(color='#BEC0C2'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0)'
            )

            # Convert to HTML
            graph_html2 = fig2.to_html(full_html=False)

            
            return render_template('haliburton.html',plot_html = graph_html, plot_html2=graph_html2)
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