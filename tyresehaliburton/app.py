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
    ).join(SeasonStats, SeasonStats.player_id == Player.player_id)\
     .join(GameLog, GameLog.season_stats_id == SeasonStats.id)\
     .filter(SeasonStats.season_id == season.id)\
     .group_by(Player.player_name)\
     .order_by(func.sum(GameLog.ast).desc())\
     .limit(20)\
     .all()

    return assist_leaders

def fetch_top_10_players_avg_assists_2023_24():
    season_str = "2023-24"  # Define the season string
    season = Season.query.filter_by(year=season_str).first()
    if not season:
        return []
    # Query to fetch top 10 players' names and their average points for the 2023-24 season
    top_players_avg_assists = db.session.query(
        Player.player_name,
        (SeasonStats.assists).label('avg_assists_per_game')
    ).join(SeasonStats, SeasonStats.player_id == Player.player_id)\
     .join(Season, SeasonStats.season_id == Season.id)\
     .filter(Season.year == season_str)\
     .order_by((SeasonStats.assists).desc())\
     .limit(10)\
     .all()

    return top_players_avg_assists
def get_top_10_assist_leaders_for_season(season_year):
    season = Season.query.filter_by(year=season_year).first()
    if not season:
        return []

    top_10_assist_leaders = db.session.query(
            Player.player_id,
            Player.player_name,
            SeasonStats.assists.label('avg_assists')
        ).join(SeasonStats, Player.player_id == SeasonStats.player_id)\
        .filter(SeasonStats.season_id == season.id)\
        .order_by(SeasonStats.assists.desc())\
        .limit(10)\
        .all()
     
    return top_10_assist_leaders

def fetch_game_logs_for_players(player_ids, season_id):
    season_year = "2023-24" 
    # First, get the season object to ensure we have the correct season_id
    season = Season.query.filter_by(year=season_year).first()
    if not season:
        print(f"No season found for {season_year}")
        return []

    # Get SeasonStats ids for the given players and season
    season_stats_ids = db.session.query(SeasonStats.id)\
        .filter(SeasonStats.player_id.in_(player_ids), SeasonStats.season_id == season.id)\
        .all()
    season_stats_ids = [id[0] for id in season_stats_ids]  # Extracting ids from the tuples

    if not season_stats_ids:
        print("No SeasonStats found for the given players and season")
        return []

    # Now, fetch the GameLog entries using the season_stats_ids
    game_logs = GameLog.query.filter(GameLog.season_stats_id.in_(season_stats_ids)).all()

    return game_logs
# -----------Prepare data for Graph---------
def prepare_data_for_plotting(game_logs):
    data = []
    for log in game_logs:
        player_name = Player.query.filter_by(player_id=log.season_stats.player_id).first().player_name
        data.append({
            'Player': player_name,
            'Game Date': log.game_date,
            'Assists': log.ast,
            'Turnovers': log.tov
        })
    return data

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

def create_boxplot(game_data):
    df = pd.DataFrame(game_data)
    print(df.columns)
    fig = px.box(df, x='Player', y=['Assists', 'Turnovers'], color='Player', 
                 title='Game-by-Game Assist and Turnover Distribution for Top 10 Assist Leaders')
    fig.update_layout(xaxis_title='Player', yaxis_title='Count', boxmode='group')
    fig.update_layout(
            height=600,
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            title_font=dict(color='#BEC0C2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0)'
        )

    return fig.to_html(full_html=False)

# -----------App functions-----------------
def assist_turnover_boxplot(season_year):
    top_10_leaders = get_top_10_assist_leaders_for_season(season_year)

    player_ids = [leader[0] for leader in top_10_leaders]
    season = Season.query.filter_by(year=season_year).first()
    game_logs = fetch_game_logs_for_players(player_ids, season.id)
    # print(game_logs)
    game_data = prepare_data_for_plotting(game_logs)
    fig = create_boxplot(game_data)
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
            season_str = "2023-24" 
            assist_leaders = fetch_current_season_assist_leaders()
            print("hi")
            graph_html = create_assist_leaders_bar_graph(assist_leaders)
            top_players_avg_assists = fetch_top_10_players_avg_assists_2023_24()
            print("bi")
            graph_html2 = create_avg_assists_bar_plot(top_players_avg_assists)
            graph_html3=assist_turnover_boxplot(season_str)
            return render_template('haliburton.html',  graph_html = graph_html, graph_html2 = graph_html2, graph_html3=graph_html3)


            # Convert to HTML
            # graph_html_this_year = fig_this_year.to_html(full_html=False)
     

        except Exception as e:
            # Handle errors like file not found, invalid format etc.
            return str(e), 500
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)