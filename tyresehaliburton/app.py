from flask import Flask, render_template
import plotly.express as px
import pandas as pd
from models import AssistData
from extensions import db  # Import the SQLAlchemy instance

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:newerjeans@localhost:5432/postgres'

    db.init_app(app)  # Initialize db with app context

    with app.app_context():
        from models import AssistData  # Import models after db initialization
        db.create_all()  # Create tables

    return app

app = create_app()

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/haliburton')
def haliburton():
    try:
        # Load and process data (Consider caching this if it doesn't change often)
        df1 = pd.read_csv('assistdata.csv')
        plot_html = create_box_plot(df1, 'Player-Season', 'Assists', 'Game-by-Game Assist Distribution of Top Assist Leaders by Season')

        df2 = pd.read_csv('nba_top_20_assist_leaders_game_log.csv')
        plot_html2 = create_box_plot(df2, 'PLAYER_NAME', 'AST', 'Game-by-Game Assist Distribution of Top 20 NBA Assist Leaders')

        return render_template('haliburton.html', plot_html=plot_html, plot_html2=plot_html2)
    except Exception as e:
        # Handle errors like file not found, invalid format etc.
        return str(e), 500

def create_box_plot(df, x_column, y_column, title):
    # Calculate average assists per player
    avg_assists = df.groupby(x_column)[y_column].mean().round(2)

    # Create a new column for modified x-axis labels
    df['x_labels'] = df[x_column].apply(lambda x: f"{x} (Avg: {avg_assists[x]} AST/G)")

    # Create the box plot
    fig = px.box(df, x='x_labels', y=y_column, title=title)
    fig.update_traces(marker_color='#FDBB30', line_color='#FDBB30')
    fig.update_layout(
        height=600,
        xaxis=dict(tickangle=-45, tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
        yaxis=dict(tickfont=dict(size=10, color='#BEC0C2'), title_font=dict(color='#BEC0C2')),
        title_font=dict(color='#BEC0C2'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig.to_html(full_html=False)



if __name__ == '__main__':
    app.run(debug=True)