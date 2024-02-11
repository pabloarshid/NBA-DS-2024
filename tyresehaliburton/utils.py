# utils.py - Utility functions and business logic
from models import GameLog, SeasonStats, Player, Season, Shotchart
from extensions import db
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import func

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
     .limit(20)\
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
        .limit(20)\
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
    game_logs_data = []

    # Fetch game logs for the given players and season
    game_logs = GameLog.query.join(SeasonStats)\
                             .filter(SeasonStats.player_id.in_(player_ids),
                                     SeasonStats.season_id == season_id)\
                             .all()
    # game_logs = GameLog.query.filter(GameLog.season_stats_id.in_(season_stats_ids)).all()
    # Extract data from game logs
    
    return game_logs
def fetch_player_shot_chart_for_season(player_name, season_year):
    # Find the player by name
    player = Player.query.filter_by(player_name=player_name).first()
    if not player:
        print('Player not found')
        return None

    # Find the season by year
    season = Season.query.filter_by(year=season_year).first()
    if not season:
        print('Season not found')
        return None

    # Find the SeasonStats for the player for the given season
    season_stats = SeasonStats.query.filter_by(player_id=player.player_id, season_id=season.id).first()
    if not season_stats:
        print('Season stats not found for this player and season')
        return None

    # Fetch all Shotchart records for the SeasonStats id
    shotcharts = Shotchart.query.filter_by(season_stats_id=season_stats.id).all()

    if not shotcharts:
        print('No shot chart data found for this player and season')
        return None

    # Convert shot chart data to a pandas DataFrame
    shots_data = {
        'game_date': [shot.game_date for shot in shotcharts],
        'x_coordinate': [shot.x_coordinate for shot in shotcharts],
        'y_coordinate': [shot.y_coordinate for shot in shotcharts],
        'shot_made': [shot.shot_made for shot in shotcharts],
        
          # Add all new fields here
        'game_id': [shot.game_id for shot in shotcharts],
        'game_event_id': [shot.game_event_id for shot in shotcharts],
        'team_id': [shot.team_id for shot in shotcharts],
        'team_name': [shot.team_name for shot in shotcharts],
        'period': [shot.period for shot in shotcharts],
        'minutes_remaining': [shot.minutes_remaining for shot in shotcharts],
        'seconds_remaining': [shot.seconds_remaining for shot in shotcharts],
        'event_type': [shot.event_type for shot in shotcharts],
        'action_type': [shot.action_type for shot in shotcharts],
        'shot_type': [shot.shot_type for shot in shotcharts],
        'shot_zone_basic': [shot.shot_zone_basic for shot in shotcharts],
        'shot_zone_area': [shot.shot_zone_area for shot in shotcharts],
        'shot_zone_range': [shot.shot_zone_range for shot in shotcharts],
        'shot_distance': [shot.shot_distance for shot in shotcharts],
        'shot_attempted_flag': [shot.shot_attempted_flag for shot in shotcharts],
        'htm': [shot.htm for shot in shotcharts],
        'vtm': [shot.vtm for shot in shotcharts],
    }

    df_shots = pd.DataFrame(shots_data)
    return df_shots
# -----------Prepare data for Graph---------
def prepare_data_for_plotting(game_logs):
    game_logs_data = [] 
    for log in game_logs:
        # print(log)
        # Append assists data
        game_logs_data.append({
            'Player-Season': f"{log.season_stats.player.player_name} ({log.season_stats.season.year})",
            'Stat Type': 'Assists',
            'Count': log.ast
        })
        # Append turnovers data
        game_logs_data.append({
            'Player-Season': f"{log.season_stats.player.player_name} ({log.season_stats.season.year})",
            'Stat Type': 'Turnovers',
            'Count': log.tov
        })
    return game_logs_data

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
                plot_bgcolor='#BEC0C2'
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
                plot_bgcolor='#BEC0C2'
            )

    # Convert plot to HTML for Flask rendering
    return fig.to_html(full_html=False)
def create_boxplot(game_data):
    df_plot = pd.DataFrame(game_data)

    fig = px.box(df_plot, x='Player-Season', y='Count', color='Stat Type', 
             title='Game-by-Game Assist and Turnover Distribution of Top Assist Leaders by Season')
    fig.update_layout(xaxis_title='Player', yaxis_title='Count', boxmode='group')
    fig.update_layout(
            height=600,
            xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
            title_font=dict(color='#BEC0C2'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='#BEC0C2'
        )

    return fig.to_html(full_html=False)

def create_court():
    # Create a figure
    fig = go.Figure()
    #Baseline
    fig.add_shape(type="line",
        x0=-245, y0=-25, x1=245, y1=-25,
        line=dict(width=2, color="white")) 
    
    fig.add_shape(type="line",
        x0=245, y0=-25, x1=245, y1=440,
        line=dict(width=2, color="white")) 
    fig.add_shape(type="line",
        x0=-245, y0=-25, x1=-245, y1=440,
        line=dict(width=2, color="white")) 
   # Short corner 3PT lines
    fig.add_shape(type="line",
              x0=-215, y0=-25, x1=-215, y1=115,
              line=dict(width=2, color="white"))  # Use "white" or any desired color for the line
    fig.add_shape(type="line",
            x0=215, y0=-25, x1=215, y1=115,
            line=dict(width=2, color="white"))  # Use "white" or any desired color for the line
    # Lane and Key
    fig.add_shape(type="line",
            x0=-80, y0=-25, x1=-80, y1=150,
            line=dict(width=2, color="white")) 
    fig.add_shape(type="line",
            x0=80, y0=-25, x1=80, y1=150,
            line=dict(width=2, color="white")) 
    fig.add_shape(type="line",
            x0=-60, y0=-25, x1=-60, y1=150,
            line=dict(width=2, color="white")) 
    fig.add_shape(type="line",
            x0=60, y0=-25, x1=60, y1=150,
            line=dict(width=2, color="white")) 
    fig.add_shape(type="line",
            x0=-80, y0=150, x1=80, y1=150,
            line=dict(width=2, color="white"))         
    # fig.add_shape(type="circle", xref="x", yref="y", x0=-7.5, y0=7.5, x1=7.5, y1=-7.5, line_color="white")
    #Basket 
    fig.add_shape(type="circle",
              xref="x", yref="y",
              x0=-60, y0=90,  # Lower left point of the bounding box
              x1=60, y1=200,   # Upper right point of the bounding box
              line=dict(width=2, color="white"))  # Replace "color" with the actual color you want)
    radius = 15
    center_x, center_y = 0, 0
    x0, y0 = center_x - radius, center_y - radius
    x1, y1 = center_x + radius, center_y + radius
    # Add a circle to the figure
    fig.add_shape(type="circle",
                xref="x", yref="y",
                x0=x0, y0=y0, x1=x1, y1=y1,
                line=dict(width=2, color="white"))
    # Parameters for the 3PT Arc
    center_x, center_y = 0, 62.5  # Center of the arc
    radius_x = 225  # Half the width of the arc, making the total width 440
    radius_y = 172.5  # Half the height of the arc, making the total height 315
    theta1, theta2 = 17.5, 162.5  # Start and end angles in degrees

    # Generate the SVG path for the arc
    # Note: Plotly's SVG path uses the same commands as HTML's SVG path. For an arc, we use the "A" command.
    # However, Plotly currently does not directly support the elliptical arc ("A") command in SVG paths for `add_shape`.
    # As a workaround, we will use a series of line segments to approximate the arc.
    angle_range = np.radians(np.linspace(theta1, theta2, num=180))  # Generate angles
    x_arc = center_x + radius_x * np.cos(angle_range)
    y_arc = center_y + radius_y * np.sin(angle_range)

    # Create the line segments
    path = 'M ' + ' L '.join([f'{x:.2f},{y:.2f}' for x, y in zip(x_arc, y_arc)])

    # Add the arc (approximated with line segments) to the figure
    fig.add_shape(type="path",
                path=path,
                line=dict( width=2, color="white"))

    # Set figure properties
    #  Set figure background color and other properties
    fig.update_layout(paper_bgcolor='#001484',
                    plot_bgcolor='#001484',
                    margin=dict(l=0, r=0, t=0, b=0),  # Adjust margins to fit your needs
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),  # Hide x-axis lines and labels
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))  # Hide y-axis lines and labels
    fig.update_layout(
    xaxis=dict(autorange=True, fixedrange=False),
    yaxis=dict(autorange=True, fixedrange=False)
)

                    
    return fig
def create_shotsmadeplot(playerdata):
    # Draw basketball court
    fig = create_court()
    
    # Define categories and their colors
    # Assuming playerdata is your DataFrame
    conditions = [
        ('2PT Field Goal', True, 'rgba(25,255,0,1)', '2PT Made'),  # Fully opaque green for made 2PT shots
        ('2PT Field Goal', False, 'rgba(255,0,0,0.50)', '2PT Missed'),  # 25% opaque red for missed 2PT shots
        ('3PT Field Goal', True, 'rgba(255,255,0,1)', '3PT Made'),  # Highlighter yellow (fully opaque) for made 3PT shots
        ('3PT Field Goal', False, 'rgba(255,165,0,0.5)', '3PT Missed'),  # 25% opaque orange for missed 3PT shots
    ]
    # Loop through conditions to create traces
    for shot_type, shot_made, color, name in conditions:
        filtered_df = playerdata[(playerdata['shot_type'] == shot_type) & (playerdata['shot_made'] == shot_made)]
        
        fig.add_trace(go.Scatter(
            x=filtered_df['x_coordinate'], 
            y=filtered_df['y_coordinate'], 
            mode='markers', 
            marker=dict(color=color),
            name=name
        ))

    # Customize layout
    fig.update_layout(
        title="Tyrese Haliburtons's Shot Chart",
        legend_title="Shot Outcome"
    )
    # Set axes properties to not show grid or tick labels
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False, range=[-250, 250])
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False, range=[0, 470])

    # Set figure properties
    fig.update_layout(height=500, width=600, title=f"'s Field Goals Made Scatter", font=dict(color='white'))

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
def shots_made_plot(playername,season_year):
    fetch = fetch_player_shot_chart_for_season(playername, season_year)
    fig = create_shotsmadeplot(fetch)
    return fig

