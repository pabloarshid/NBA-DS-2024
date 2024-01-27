from flask import Flask, render_template
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/haliburton')
def haliburton():
    #  Read data from CSV
    df = pd.read_csv('assistdata.csv')  # Update with your CSV file path

    # Create a boxplot
    fig=  px.box(df, x='Player-Season', y='Assists', title='Game-by-Game Assist Distribution of Top Assist Leaders by Season') # Update with your column names
     # Update box color
    fig.update_traces(marker_color='#FDBB30', line_color='#FDBB30')

    # Update layout for titles and labels
    fig.update_layout(
        height=600,  # Adjust height as needed
        xaxis=dict(
            tickfont=dict(size=9, color='#BEC0C2'),
            title_font=dict(color='#BEC0C2')
        ),
        yaxis=dict(
            tickfont=dict(size=10, color='#BEC0C2'),
            title_font=dict(color='#BEC0C2')
        ),
        title_font=dict(color='#BEC0C2'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    # Convert the figure to HTML
    plot_html = fig.to_html(full_html=False)
    
    return render_template('haliburton.html', plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True)