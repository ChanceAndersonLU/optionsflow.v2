"""
Professional Options Flow Dashboard
Real-time web-based interface with advanced visualizations
"""

import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(__file__))
from advanced_analytics import AdvancedFlowAnalyzer, BlackScholesCalculator
from data_collector import OptionsDataCollector

# Professional styling
external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
]

class ProfessionalOptionsDashboard:
    """Professional-grade options flow dashboard"""
    
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.collector = OptionsDataCollector()
        self.analyzer = AdvancedFlowAnalyzer()
        self.logger = logging.getLogger(__name__)
        
        # Dashboard state
        self.current_symbol = 'AAPL'
        self.data_cache = {}
        self.last_update = None
        
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Create the professional dashboard layout"""
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.Div([
                    html.H1("⚡ Options Flow Analyzer Pro", 
                           className="dashboard-title"),
                    html.P("Real-time institutional options flow monitoring", 
                           className="dashboard-subtitle"),
                ], className="header-text"),
                
                html.Div([
                    html.Div(id="live-status", className="status-indicator"),
                    html.Span("LIVE", className="status-text")
                ], className="status-container")
                
            ], className="header"),
            
            # Control Panel
            html.Div([
                html.Div([
                    html.Label("Symbol", className="control-label"),
                    dcc.Input(
                        id='symbol-input',
                        type='text',
                        value='AAPL',
                        className='symbol-input',
                        placeholder="Enter ticker..."
                    ),
                    html.Button('Analyze', id='analyze-btn', 
                               className='analyze-button', n_clicks=0)
                ], className="symbol-control"),
                
                html.Div([
                    html.Label("Flow Filter", className="control-label"),
                    dcc.Dropdown(
                        id='flow-filter',
                        options=[
                            {'label': 'All Flows', 'value': 'all'},
                            {'label': 'Unusual Only', 'value': 'unusual'},
                            {'label': 'Institutional', 'value': 'institutional'},
                            {'label': 'Blocks & Sweeps', 'value': 'blocks_sweeps'}
                        ],
                        value='all',
                        className='flow-dropdown'
                    )
                ], className="filter-control"),
                
                html.Div([
                    html.Label("Min Premium", className="control-label"),
                    dcc.Input(
                        id='min-premium',
                        type='number',
                        value=25000,
                        className='premium-input',
                        placeholder="Minimum premium..."
                    )
                ], className="premium-control")
                
            ], className="control-panel"),
            
            # Key Metrics Row
            html.Div([
                html.Div([
                    html.H3("—", id="stock-price", className="metric-value"),
                    html.P("Stock Price", className="metric-label")
                ], className="metric-card"),
                
                html.Div([
                    html.H3("—", id="total-premium", className="metric-value"),
                    html.P("Total Premium", className="metric-label")
                ], className="metric-card"),
                
                html.Div([
                    html.H3("—", id="unusual-count", className="metric-value"),
                    html.P("Unusual Flows", className="metric-label")
                ], className="metric-card"),
                
                html.Div([
                    html.H3("—", id="pc-ratio", className="metric-value"),
                    html.P("Put/Call Ratio", className="metric-label")
                ], className="metric-card"),
                
                html.Div([
                    html.H3("—", id="sentiment-score", className="metric-value"),
                    html.P("Sentiment", className="metric-label")
                ], className="metric-card")
                
            ], className="metrics-row"),
            
            # Main Charts Row
            html.Div([
                html.Div([
                    dcc.Graph(id='flow-heatmap', className="chart-container")
                ], className="chart-half"),
                
                html.Div([
                    dcc.Graph(id='volume-by-strike', className="chart-container")
                ], className="chart-half")
            ], className="charts-row"),
            
            # Secondary Charts Row
            html.Div([
                html.Div([
                    dcc.Graph(id='time-series-flow', className="chart-container")
                ], className="chart-half"),
                
                html.Div([
                    dcc.Graph(id='greeks-analysis', className="chart-container")
                ], className="chart-half")
            ], className="charts-row"),
            
            # Data Table
            html.Div([
                html.H3("🔥 Live Options Flow", className="table-title"),
                dash_table.DataTable(
                    id='flow-table',
                    columns=[
                        {'name': 'Time', 'id': 'timestamp', 'type': 'datetime'},
                        {'name': 'Contract', 'id': 'contractSymbol', 'type': 'text'},
                        {'name': 'Type', 'id': 'option_type', 'type': 'text'},
                        {'name': 'Strike', 'id': 'strike', 'type': 'numeric', 'format': {'specifier': '.2f'}},
                        {'name': 'Volume', 'id': 'volume', 'type': 'numeric'},
                        {'name': 'Premium', 'id': 'total_premium', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                        {'name': 'IV', 'id': 'impliedVolatility', 'type': 'numeric', 'format': {'specifier': '.2%'}},
                        {'name': 'Delta', 'id': 'delta', 'type': 'numeric', 'format': {'specifier': '.3f'}},
                        {'name': 'Flow', 'id': 'flow_type', 'type': 'text'},
                        {'name': 'Score', 'id': 'unusual_score', 'type': 'numeric', 'format': {'specifier': '.0f'}}
                    ],
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'backgroundColor': '#2d2d2d',
                        'color': 'white',
                        'fontFamily': 'Inter',
                        'fontSize': '12px',
                        'textAlign': 'left',
                        'padding': '8px'
                    },
                    style_header={
                        'backgroundColor': '#1e1e1e',
                        'color': '#00ff88',
                        'fontWeight': 'bold',
                        'border': '1px solid #444'
                    },
                    style_data_conditional=[
                        {
                            'if': {'filter_query': '{flow_type} = block'},
                            'backgroundColor': '#ff6b6b20',
                            'border': '1px solid #ff6b6b'
                        },
                        {
                            'if': {'filter_query': '{flow_type} = sweep'},
                            'backgroundColor': '#ffd93d20',
                            'border': '1px solid #ffd93d'
                        },
                        {
                            'if': {'filter_query': '{unusual_score} > 75'},
                            'backgroundColor': '#00ff8820',
                            'border': '1px solid #00ff88'
                        }
                    ],
                    sort_action="native",
                    page_size=20,
                    className="professional-table"
                )
            ], className="table-container"),
            
            # Auto-refresh component
            dcc.Interval(
                id='interval-component',
                interval=5000,  # 5 seconds
                n_intervals=0
            ),
            
            # Data store
            dcc.Store(id='options-data-store')
            
        ], className="dashboard-container")
        
        # Add custom CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    
                    body {
                        font-family: 'Inter', sans-serif;
                        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                        color: white;
                        min-height: 100vh;
                    }
                    
                    .dashboard-container {
                        max-width: 1400px;
                        margin: 0 auto;
                        padding: 20px;
                        min-height: 100vh;
                    }
                    
                    .header {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 30px;
                        padding: 20px 0;
                        border-bottom: 2px solid #444;
                    }
                    
                    .dashboard-title {
                        font-size: 2.5rem;
                        font-weight: 700;
                        background: linear-gradient(45deg, #00ff88, #00d4ff);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        margin: 0;
                    }
                    
                    .dashboard-subtitle {
                        color: #aaa;
                        margin: 5px 0 0 0;
                        font-size: 1.1rem;
                    }
                    
                    .status-container {
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    
                    .status-indicator {
                        width: 12px;
                        height: 12px;
                        background: #00ff88;
                        border-radius: 50%;
                        animation: pulse 2s infinite;
                    }
                    
                    @keyframes pulse {
                        0% { opacity: 1; }
                        50% { opacity: 0.5; }
                        100% { opacity: 1; }
                    }
                    
                    .status-text {
                        color: #00ff88;
                        font-weight: 600;
                        font-size: 0.9rem;
                    }
                    
                    .control-panel {
                        display: flex;
                        gap: 20px;
                        margin-bottom: 25px;
                        padding: 20px;
                        background: rgba(45, 45, 45, 0.5);
                        border-radius: 12px;
                        border: 1px solid #444;
                    }
                    
                    .control-label {
                        display: block;
                        color: #ccc;
                        font-size: 0.9rem;
                        font-weight: 500;
                        margin-bottom: 8px;
                    }
                    
                    .symbol-input, .premium-input {
                        background: #1e1e1e;
                        border: 1px solid #555;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 8px;
                        font-size: 1rem;
                        width: 150px;
                    }
                    
                    .symbol-input:focus, .premium-input:focus {
                        outline: none;
                        border-color: #00ff88;
                        box-shadow: 0 0 0 3px rgba(0, 255, 136, 0.1);
                    }
                    
                    .analyze-button {
                        background: linear-gradient(45deg, #00ff88, #00d4ff);
                        color: black;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 8px;
                        font-weight: 600;
                        cursor: pointer;
                        margin-left: 10px;
                        transition: transform 0.2s;
                    }
                    
                    .analyze-button:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
                    }
                    
                    .metrics-row {
                        display: grid;
                        grid-template-columns: repeat(5, 1fr);
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    
                    .metric-card {
                        background: rgba(45, 45, 45, 0.8);
                        padding: 20px;
                        border-radius: 12px;
                        border: 1px solid #444;
                        text-align: center;
                        transition: transform 0.2s;
                    }
                    
                    .metric-card:hover {
                        transform: translateY(-2px);
                        border-color: #00ff88;
                    }
                    
                    .metric-value {
                        font-size: 1.8rem;
                        font-weight: 700;
                        color: #00ff88;
                        margin: 0 0 5px 0;
                    }
                    
                    .metric-label {
                        color: #aaa;
                        font-size: 0.9rem;
                        margin: 0;
                    }
                    
                    .charts-row {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    
                    .chart-half {
                        background: rgba(45, 45, 45, 0.5);
                        border-radius: 12px;
                        border: 1px solid #444;
                        padding: 15px;
                    }
                    
                    .table-container {
                        background: rgba(45, 45, 45, 0.5);
                        border-radius: 12px;
                        border: 1px solid #444;
                        padding: 20px;
                    }
                    
                    .table-title {
                        color: #00ff88;
                        margin-bottom: 15px;
                        font-size: 1.3rem;
                    }
                    
                    .professional-table {
                        border-radius: 8px;
                        overflow: hidden;
                    }
                    
                    @media (max-width: 1200px) {
                        .metrics-row {
                            grid-template-columns: repeat(3, 1fr);
                        }
                        .charts-row {
                            grid-template-columns: 1fr;
                        }
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def setup_callbacks(self):
        """Set up dashboard callbacks for interactivity"""
        
        @self.app.callback(
            [Output('stock-price', 'children'),
             Output('total-premium', 'children'),
             Output('unusual-count', 'children'),
             Output('pc-ratio', 'children'),
             Output('sentiment-score', 'children'),
             Output('flow-table', 'data'),
             Output('options-data-store', 'data')],
            [Input('analyze-btn', 'n_clicks'),
             Input('interval-component', 'n_intervals')],
            [dash.dependencies.State('symbol-input', 'value')]
        )
        def update_data(n_clicks, n_intervals, symbol):
            """Update all dashboard data"""
            
            if not symbol:
                symbol = 'AAPL'
            
            try:
                # Get fresh data
                result = self.collector.get_full_analysis(symbol.upper())
                
                if 'error' in result:
                    return "—", "—", "—", "—", "—", [], {}
                
                # Calculate metrics
                stock_price = f"${result['stock_price']:.2f}"
                total_premium = f"${result['total_premium_volume']:,.0f}"
                unusual_count = str(result['unusual_activity_count'])
                
                # Calculate P/C ratio
                options_data = result['data']
                pc_metrics = self.analyzer.calculate_put_call_ratio(options_data)
                pc_ratio = f"{pc_metrics.get('volume_put_call_ratio', 0):.2f}"
                
                # Sentiment
                sentiment = pc_metrics.get('sentiment', 'neutral').replace('_', ' ').title()
                
                # Prepare table data
                table_data = self.prepare_table_data(options_data)
                
                return (stock_price, total_premium, unusual_count, pc_ratio, 
                       sentiment, table_data, result)
                
            except Exception as e:
                self.logger.error(f"Error updating data: {e}")
                return "Error", "Error", "Error", "Error", "Error", [], {}
        
        @self.app.callback(
            Output('flow-heatmap', 'figure'),
            [Input('options-data-store', 'data')]
        )
        def update_heatmap(stored_data):
            """Update flow heatmap chart"""
            
            if not stored_data or 'data' not in stored_data:
                return self.create_empty_chart("Flow Heatmap")
            
            options_data = pd.DataFrame(stored_data['data'])
            
            if options_data.empty:
                return self.create_empty_chart("Flow Heatmap")
            
            # Create heatmap data
            heatmap_data = options_data.pivot_table(
                index='option_type',
                columns='moneyness',
                values='total_premium',
                aggfunc='sum',
                fill_value=0
            )
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                colorbar=dict(title="Total Premium")
            ))
            
            fig.update_layout(
                title="Premium Flow Heatmap",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(title="Moneyness"),
                yaxis=dict(title="Option Type")
            )
            
            return fig
        
        @self.app.callback(
            Output('volume-by-strike', 'figure'),
            [Input('options-data-store', 'data')]
        )
        def update_volume_chart(stored_data):
            """Update volume by strike chart"""
            
            if not stored_data or 'data' not in stored_data:
                return self.create_empty_chart("Volume by Strike")
            
            options_data = pd.DataFrame(stored_data['data'])
            
            if options_data.empty:
                return self.create_empty_chart("Volume by Strike")
            
            # Aggregate volume by strike and type
            volume_data = options_data.groupby(['strike', 'option_type'])['volume'].sum().reset_index()
            
            fig = go.Figure()
            
            # Add calls
            calls = volume_data[volume_data['option_type'] == 'call']
            fig.add_trace(go.Bar(
                x=calls['strike'],
                y=calls['volume'],
                name='Calls',
                marker_color='#00ff88',
                opacity=0.8
            ))
            
            # Add puts
            puts = volume_data[volume_data['option_type'] == 'put']
            fig.add_trace(go.Bar(
                x=puts['strike'],
                y=-puts['volume'],  # Negative for puts
                name='Puts',
                marker_color='#ff6b6b',
                opacity=0.8
            ))
            
            # Add current stock price line
            stock_price = stored_data.get('stock_price', 0)
            fig.add_vline(
                x=stock_price,
                line_dash="dash",
                line_color="white",
                annotation_text=f"Stock: ${stock_price:.2f}"
            )
            
            fig.update_layout(
                title="Volume by Strike",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                xaxis=dict(title="Strike Price"),
                yaxis=dict(title="Volume (Calls +, Puts -)"),
                barmode='overlay'
            )
            
            return fig
    
    def prepare_table_data(self, options_data: pd.DataFrame) -> List[Dict]:
        """Prepare data for the flow table"""
        
        if options_data.empty:
            return []
        
        # Add flow analysis
        table_rows = []
        for _, row in options_data.iterrows():
            flow_analysis = self.analyzer.analyze_single_trade(row.to_dict())
            
            table_row = {
                'timestamp': row.get('timestamp', datetime.now()).strftime('%H:%M:%S'),
                'contractSymbol': row.get('contractSymbol', ''),
                'option_type': row.get('option_type', '').upper(),
                'strike': row.get('strike', 0),
                'volume': row.get('volume', 0),
                'total_premium': row.get('total_premium', 0),
                'impliedVolatility': row.get('impliedVolatility', 0),
                'delta': row.get('delta', 0),
                'flow_type': flow_analysis.flow_type,
                'unusual_score': flow_analysis.unusual_score
            }
            table_rows.append(table_row)
        
        # Sort by unusual score descending
        table_rows.sort(key=lambda x: x['unusual_score'], reverse=True)
        
        return table_rows[:50]  # Limit to top 50
    
    def create_empty_chart(self, title: str):
        """Create empty chart placeholder"""
        
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            x=0.5, y=0.5,
            xref="paper", yref="paper",
            font=dict(size=16, color="gray"),
            showarrow=False
        )
        
        fig.update_layout(
            title=title,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        
        return fig
    
    def run(self, host='127.0.0.1', port=8050, debug=True):
        """Run the dashboard"""
        print(f"🚀 Starting Professional Options Dashboard...")
        print(f"📊 Dashboard will be available at: http://{host}:{port}")
        self.app.run_server(host=host, port=port, debug=debug)

# Main execution
if __name__ == "__main__":
    dashboard = ProfessionalOptionsDashboard()
    dashboard.run()