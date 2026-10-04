import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

def create_dashboard(simulation_data=None):
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("Intent-Driven Autonomy Dashboard"),
        
        # Color-coded intent health status
        html.Div(id='health-status', style={'padding': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
        
        html.Div([
            # KPI Time Series
            html.Div([
                dcc.Graph(id='kpi-time-series')
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            # Drift Detection Alerts
            html.Div([
                dcc.Graph(id='drift-alerts')
            ], style={'width': '48%', 'display': 'inline-block'})
        ]),
        
        html.Div([
            # Causal Graph
            html.Div([
                dcc.Graph(id='causal-graph')
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            # SLA Predictions
            html.Div([
                dcc.Graph(id='sla-predictions')
            ], style={'width': '48%', 'display': 'inline-block'})
        ]),
        
        dcc.Interval(
            id='interval-update',
            interval=1000, # in milliseconds
            n_intervals=0
        )
    ])
    
    @app.callback(
        [Output('kpi-time-series', 'figure'),
         Output('drift-alerts', 'figure'),
         Output('causal-graph', 'figure'),
         Output('sla-predictions', 'figure'),
         Output('health-status', 'children'),
         Output('health-status', 'style')],
        [Input('interval-update', 'n_intervals')]
    )
    def update_metrics(n):
        # Mock data generation
        x_data = list(range(n, n+20))
        y_data = np.random.normal(50, 5, 20)
        
        # KPI Figure
        fig_kpi = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode='lines+markers'))
        fig_kpi.update_layout(title='KPI Time Series', xaxis_title='Time', yaxis_title='Value')
        
        # Drift Figure
        drift_y = np.random.choice([0, 1], size=20, p=[0.9, 0.1])
        fig_drift = go.Figure(data=go.Scatter(x=x_data, y=drift_y, mode='markers', marker=dict(color='red')))
        fig_drift.update_layout(title='Drift Detection Alerts (1=Alert)', xaxis_title='Time', yaxis_title='Alert')
        
        # Causal Figure
        fig_causal = go.Figure(data=[go.Sankey(
            node = dict(pad = 15, thickness = 20, line = dict(color = "black", width = 0.5), label = ["A", "B", "C"], color = "blue"),
            link = dict(source = [0, 1], target = [1, 2], value = [8, 4])
        )])
        fig_causal.update_layout(title='Causal Graph')
        
        # SLA Predictions
        fig_sla = go.Figure(data=go.Bar(x=['Metric 1', 'Metric 2'], y=[95, 80]))
        fig_sla.update_layout(title='SLA Predictions (%)')
        
        # Health Status
        health_score = np.random.uniform(0, 100)
        if health_score > 80:
            status = "HEALTHY"
            color = "green"
        elif health_score > 50:
            status = "WARNING"
            color = "goldenrod"
        else:
            status = "CRITICAL"
            color = "red"
            
        style = {'padding': '20px', 'fontSize': '24px', 'fontWeight': 'bold', 'color': 'white', 'backgroundColor': color}
        status_text = f"Intent Health Status: {status} ({health_score:.1f}%)"
        
        return fig_kpi, fig_drift, fig_causal, fig_sla, status_text, style

    return app

if __name__ == '__main__':
    app = create_dashboard()
    app.run_server(debug=True)
