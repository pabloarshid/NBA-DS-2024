from flask import render_template
from utils import fetch_current_season_assist_leaders, create_assist_leaders_bar_graph, fetch_top_10_players_avg_assists_2023_24, create_avg_assists_bar_plot, assist_turnover_boxplot, shots_made_plot, fetch_player_gen_stats

def configure_routes(app):
    @app.route('/')        
    def home():
        return render_template('home.html')

    @app.route('/haliburton')
    def haliburton():
        try:
            name = "Tyrese Haliburton"
            season_str = "2023-24" 
            # Assuming player_name is "Tyrese Haliburton", adjust as necessary
            gen_stats = fetch_player_gen_stats(name)
            # print(gen_stats)
            assist_leaders = fetch_current_season_assist_leaders()
            graph_html = create_assist_leaders_bar_graph(assist_leaders)
            top_players_avg_assists = fetch_top_10_players_avg_assists_2023_24()
            graph_html2 = create_avg_assists_bar_plot(top_players_avg_assists)
            graph_html3=assist_turnover_boxplot(season_str)
            graph_html4 = shots_made_plot(name, season_str)
            
            return render_template('haliburton.html',  graph_html = graph_html, graph_html2 = graph_html2, graph_html3=graph_html3, graph_html4=graph_html4, stats = gen_stats)

        except Exception as e:
            # Handle errors like file not found, invalid format etc.
            return str(e), 500