from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
import plotly.express as px
import pandas as pd
from models import  GameLog, SeasonStats, Player, Season
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
            current_year = datetime.now().year
            season_str_this_year = f"{current_year-1}-{str(current_year)[-2:]}"
            season_str_40_years_ago = f"{current_year-41}-{str(current_year-40)[-2:]}"

            # Fetch this year's assist leaders
            this_year_stats = db.session.query(SeasonStats, Player, Season).join(Player).join(Season).filter(Season.year == season_str_this_year).all()

            # Fetch past 40 years' assist leaders
            past_40_years_stats = db.session.query(SeasonStats, Player, Season).join(Player).join(Season).filter(Season.year.between(season_str_40_years_ago, season_str_this_year)).all()

            # Prepare data for this year's plot
            data_this_year = [{'Player': stats.Player.player_name, 'Assists': stats.SeasonStats.assists, 'Season': stats.Season.year} for stats in this_year_stats]
            df_this_year = pd.DataFrame(data_this_year)

            # Prepare data for past 40 years' plot
            data_past_40_years = [{'Player': stats.Player.player_name, 'Assists': stats.SeasonStats.assists, 'Season': stats.Season.year} for stats in past_40_years_stats]
            df_past_40_years = pd.DataFrame(data_past_40_years)

            # Generate Plotly figures
            fig_this_year = px.box(df_this_year, x='Player', y='Assists', title="Assist Leaders of This Year", color='Season')
            fig_past_40_years = px.box(df_past_40_years, x='Player', y='Assists', title="Assist Leaders of the Past 40 Years", color='Season')

            # Update layout for transparency and label rotation
            fig_this_year.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-90)
            fig_past_40_years.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-90)

            # Convert to HTML
            graph_html_this_year = fig_this_year.to_html(full_html=False)
            graph_html_past_40_years = fig_past_40_years.to_html(full_html=False)
 # Crea te Plotly figure
            # fig = px.bar(x=names, y=assists, title="Top 20 NBA Assist Leaders")
            #     # Update layout for transparent background
            # fig.update_layout(
            #     plot_bgcolor='rgba(0,0,0,0)',
            #     paper_bgcolor='rgba(0,0,0,0)',
            #     xaxis_tickangle=-90  # Rotate x-axis labels to vertical
            # )
            # # Convert to HTML
            # graph_html = fig.to_html(full_html=False)
            # fig2.update_layout(
            #     height=600,
            #     xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            #     yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            #     title_font=dict(color='#BEC0C2'),
            #     paper_bgcolor='rgba(0,0,0,0)',
            #     plot_bgcolor='rgba(0,0,0)'
            # )

            # # Convert to HTML
            # graph_html2 = fig2.to_html(full_html=False)

            
            return render_template('haliburton.html',plot_html = graph_html_this_year, plot_html2=graph_html_past_40_years)
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