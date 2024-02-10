from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate  # Import Flask-Migrate
import plotly.express as px
import pandas as pd
from models import  GameLog, SeasonStats, Player, Season
from extensions import db  # Import the SQLAlchemy instance
from nba_api.stats.endpoints import leagueleaders, playergamelog
from datetime import datetime
import numpy as np
# -----------Fetch Functions-----------------
def fetch_current_season_assist_leaders():
    current_year = datetime.now().year
    season_str = f"{current_year-1}-{str(current_year)[-2:]}"

    # Assuming you have a Season table where the year is stored as "YYYY-YY"
    season = Season.query.filter_by(year=season_str).first()
    if not season:
        return []

    assist_leaders = db.session.query(
        Player.player_name,
        func.sum(GameLog.ast).label('total_assists')
    ).join(SeasonStats, SeasonStats.player_id == Player.id)\
     .join(GameLog, GameLog.season_stats_id == SeasonStats.id)\
     .filter(SeasonStats.season_id == season.id)\
     .group_by(Player.player_name)\
     .order_by(func.sum(GameLog.ast).desc())\
     .limit(20)\
     .all()

    return assist_leaders
def fetch_top_10_players_avg_assists_2023_24():
    season_str = "2023-24"  # Define the season string

    # Query to fetch top 10 players' names and their average points for the 2023-24 season
    top_players_avg_assists = db.session.query(
        Player.player_name,
        (SeasonStats.assists).label('avg_assists_per_game')
    ).join(SeasonStats, SeasonStats.player_id == Player.id)\
     .join(Season, SeasonStats.season_id == Season.id)\
     .filter(Season.year == season_str)\
     .order_by((SeasonStats.assists).desc())\
     .limit(10)\
     .all()

    return top_players_avg_assists

    game_logs = []
    for player in top_10_players:
        player_id = player.SeasonStats.player_id
        season_stats = SeasonStats.query.filter_by(player_id=player_id, season_id=season.id).first()
        
        if season_stats:
            player_game_logs = GameLog.query.filter_by(season_stats_id=season_stats.id).all()
            for log in player_game_logs:
                game_logs.append({
                    'Player': player.player_name,
                    'Game Date': log.game_date,
                    'Assists': log.ast,
                    'Turnovers': log.tov
                })
    return game_logs
# -----------Graph Functions-----------------
def create_assist_leaders_bar_graph(assist_leaders):
    # Convert query results to a DataFrame
    df = pd.DataFrame(assist_leaders, columns=['Player Name', 'Total Assists'])

    # Create a bar graph
    fig = px.bar(df, x='Player Name', y='Total Assists', title='NBA Assist Leaders This Season')

    # Update layout for better readability
    fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    fig.update_traces(marker_color='blue')  # Optional: update marker color
    fig.update_layout(
                height=600,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                title_font=dict(color='#BEC0C2'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0)'
            )
    return fig.to_html(full_html=False)  # Convert the figure to HTML for embedding in Flask template
def create_avg_assists_bar_plot(top_players_avg_assists):
    # Convert the fetched data into a DataFrame
    df = pd.DataFrame(top_players_avg_assists, columns=['Player Name', 'Average Assists Per Game'])

    # Create a bar plot
    fig = px.bar(df, x='Player Name', y='Average Assists Per Game', title='Top 10 Players by Average Points Per Game in 2023-24 Season')
   
    fig.update_layout(
                height=600,
                xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
                title_font=dict(color='#BEC0C2'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0)'
            )

    # Convert plot to HTML for Flask rendering
    return fig.to_html(full_html=False)

def create_assists_turnovers_boxplot(game_logs):
    df = pd.DataFrame(game_logs)
    
    # Plot assists
    fig = px.box(df, x='Player', y='Assists', color='Player',
                 title='Game-by-Game Assist and Turnover Distribution for Top 10 Assist Leaders in 2023-24')
                 
    # Overlay turnovers on the same plot
    fig.add_trace(px.box(df, x='Player', y='Turnovers', color='Player').data[0])
    
    fig.update_layout(xaxis={'categoryorder':'total descending'}, boxmode='group')
    fig.update_layout(
            height=600,
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            title_font=dict(color='#BEC0C2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0)'
        )
    return fig

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
            assist_leaders = fetch_current_season_assist_leaders()
            graph_html = create_assist_leaders_bar_graph(assist_leaders)
            top_players_avg_assists = fetch_top_10_players_avg_assists_2023_24()
            graph_html2 = create_avg_assists_bar_plot(top_players_avg_assists)
            
            
            return render_template('haliburton.html', graph_html=graph_html, graph_html2=graph_html2)
            # Convert to HTML
            # graph_html_this_year = fig_this_year.to_html(full_html=False)
     

        except Exception as e:
            # Handle errors like file not found, invalid format etc.
            return str(e), 500
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)