"""
AI Showcase Dash App - Enhanced Version

Interactive dashboard showcasing the results of AI-optimized cardiac coordination
vs baseline (no coordination) and static cardiac parameters.

IMPORTANT: This showcase uses SINGLE SEED (seed=42) for demonstration purposes.
- Represents a real-world deployment scenario where initial machine states are programmed
- Validation testing (13/15 scenarios improved) uses 5-seed AVERAGES for statistical robustness
- Your actual deployment performance will match one of the 5 seed runs from validation
- See docs/DETAILED_VALIDATION_RESULTS.md for complete per-seed breakdown
- See docs/METRICS_EXPLAINED.md for metric definitions and methodology

Usage:
    python app_enhanced.py

Then open browser to: http://localhost:8051
"""

import sys
import os
from pathlib import Path
import pickle
import json
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.heart_sim.cost import TaiwanCostCalculator


# =============================================================================
# Load Preloaded Results
# =============================================================================

DATA_DIR = Path(__file__).parent / 'data'

print("\n" + "="*60)
print("🚀 AI Showcase App - Loading Data...")
print("="*60)
print("⏳ Loading preloaded simulation results (8.7 MB optimized)...")

import time
start_time = time.time()

# Use optimized file (8.7 MB instead of 115 MB)
with open(DATA_DIR / 'showcase_results_optimized.pkl', 'rb') as f:
    ALL_RESULTS = pickle.load(f)

load_time = time.time() - start_time
print(f"✓ Loaded data in {load_time:.1f} seconds")

with open(DATA_DIR / 'metadata.json', 'r') as f:
    METADATA = json.load(f)

SUMMARY_DF = pd.read_csv(DATA_DIR / 'showcase_summary.csv')

print(f"✓ Loaded {len(ALL_RESULTS)} scenarios")
print(f"  Static params: {METADATA['static_params']}")
print("="*60 + "\n")


# =============================================================================
# Custom Styling
# =============================================================================

# Professional color palette
COLORS = {
    'primary': '#0066CC',      # Professional blue
    'secondary': '#00A86B',    # Success green
    'danger': '#DC3545',       # Alert red
    'warning': '#FFC107',      # Warning amber
    'info': '#17A2B8',        # Info cyan
    'dark': '#2C3E50',        # Dark slate
    'light': '#F8F9FA',       # Light gray
    'muted': '#6C757D',       # Muted gray
    'background': '#FFFFFF',   # Clean white
    'card_bg': '#FFFFFF',     # Card background
    'border': '#DEE2E6',      # Border gray
}

# Chart color scheme
CHART_COLORS = {
    'baseline': '#DC3545',     # Red for baseline
    'static': '#0066CC',       # Blue for static
    'ai': '#00A86B',          # Green for AI
}


# =============================================================================
# Initialize Dash App with Theme
# =============================================================================

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ]
)

app.title = "AI Cardiac Coordination Dashboard"

# Expose server for gunicorn deployment
server = app.server

# Inject custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .metric-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 40px rgba(0,0,0,0.15);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                color: white;
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: rgba(255,255,255,0.9);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .card-modern {
                border: none;
                border-radius: 12px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
            }
            
            .card-modern:hover {
                box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            }
            
            .header-gradient {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 2rem 0;
                margin-bottom: 2rem;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
            
            .control-card {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 3px 15px rgba(0,0,0,0.08);
                margin-bottom: 25px;
            }
            
            .table-modern {
                font-size: 0.95rem;
            }
            
            .table-modern th {
                background-color: #F8F9FA;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 0.5px;
                color: #495057;
                border-bottom: 2px solid #DEE2E6;
            }
            
            .badge-custom {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85rem;
                font-weight: 500;
            }
            
            .improvement-positive {
                color: #00A86B;
                font-weight: 600;
            }
            
            .improvement-negative {
                color: #DC3545;
                font-weight: 600;
            }
            
            .section-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: #2C3E50;
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #E9ECEF;
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


# =============================================================================
# Utilities
# =============================================================================

def calculate_cost_savings(baseline_peak, cardiac_peak):
    """
    Calculate annual cost savings from peak reduction.

    Returns:
        Dictionary with 'ntd' and 'usd' keys
    """
    calculator = TaiwanCostCalculator()

    # Calculate monthly demand charges
    baseline_monthly_ntd = calculator.calculate_demand_charge(baseline_peak)
    cardiac_monthly_ntd = calculator.calculate_demand_charge(cardiac_peak)

    # Annual savings (monthly × 12)
    annual_savings_ntd = (baseline_monthly_ntd - cardiac_monthly_ntd) * 12

    # Convert to USD (using official Taiwan rate: ~31 NTD/USD)
    annual_savings_usd = annual_savings_ntd / 31.0

    return {
        'ntd': annual_savings_ntd,
        'usd': annual_savings_usd
    }


def format_currency(value):
    """Format value as currency with proper styling."""
    return f"${value:,.0f}"


def format_percent(value):
    """Format value as percentage with proper styling."""
    return f"{value:+.1f}%"


def get_scenario_key(n_presses, mix):
    """Get scenario key for results dict."""
    return f"{n_presses}p_{mix}"


# =============================================================================
# Enhanced Layout Components
# =============================================================================

def create_header():
    """Create enhanced app header with gradient background."""
    return html.Div([
        html.Div([
            html.Div([
                html.I(className="fas fa-heartbeat fa-3x mb-3"),
                html.H1(
                    "AI-Optimized Cardiac Coordination System",
                    className="display-4 fw-bold mb-3"
                ),
                html.P(
                    "Advanced Peak Power Management Through Biomimetic Coordination",
                    className="lead mb-0"
                ),
                html.Hr(style={'backgroundColor': 'rgba(255,255,255,0.3)', 'height': '2px'}),
                html.P([
                    html.I(className="fas fa-chart-line me-2"),
                    "Real-time Comparison: Baseline vs Static vs AI-Optimized Performance"
                ], className="mb-0"),
            ], className="text-center text-white py-5"),
        ], className="header-gradient"),
    ])


def create_controls():
    """Create enhanced control panel with modern styling."""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-sliders-h me-2"),
                "Configuration Panel"
            ], className="section-title"),
            
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-industry me-2"),
                            "Number of Servo Presses"
                        ], className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='press-count-dropdown',
                            options=[
                                {'label': f'🏭 {n} Press System', 'value': n}
                                for n in [4, 5, 6, 7, 8]
                            ],
                            value=7,
                            clearable=False,
                            className="shadow-sm",
                            style={'borderRadius': '8px'}
                        ),
                        html.Small("Select facility size", className="text-muted mt-1"),
                    ])
                ], lg=4, md=6, className="mb-3"),

                dbc.Col([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-cogs me-2"),
                            "Fleet Composition"
                        ], className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id='mix-dropdown',
                            options=[
                                {'label': '⚡ Realistic Industrial Mix', 'value': 'realistic'},
                                {'label': '🔀 Varied Power Mix', 'value': 'varied'},
                                {'label': '📊 Uniform Fleet', 'value': 'uniform'},
                            ],
                            value='realistic',
                            clearable=False,
                            className="shadow-sm",
                            style={'borderRadius': '8px'}
                        ),
                        html.Small("Power distribution profile", className="text-muted mt-1"),
                    ])
                ], lg=4, md=6, className="mb-3"),

                dbc.Col([
                    html.Div([
                        html.Label([
                            html.I(className="fas fa-info-circle me-2"),
                            "Active Scenario"
                        ], className="fw-bold mb-2"),
                        html.Div(
                            id='scenario-info',
                            className="p-3 bg-light rounded shadow-sm",
                            style={'minHeight': '60px'}
                        ),
                    ])
                ], lg=4, md=12, className="mb-3"),
            ]),
        ], className="control-card"),
    ])


def create_metrics_cards():
    """Create placeholder for enhanced metrics cards."""
    return html.Div(id='metrics-cards', className="mb-4")


def create_power_curve_plot():
    """Create enhanced power curve plot card."""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-chart-area me-2"),
                "Power Demand Timeline"
            ], className="section-title"),
            dcc.Loading(
                dcc.Graph(id='power-curve-plot', style={'height': '500px'}),
                type="circle",
                color=COLORS['primary']
            ),
        ], className="card-modern p-4"),
    ], className="mb-4")


def create_comparison_table():
    """Create enhanced comparison table card."""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-table me-2"),
                "Performance Metrics Analysis"
            ], className="section-title"),
            html.Div(id='comparison-table'),
        ], className="card-modern p-4"),
    ], className="mb-4")


def create_parameter_table():
    """Create enhanced parameter table card."""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-brain me-2"),
                "AI Optimization Parameters"
            ], className="section-title"),
            html.Small("Comparing static defaults with AI-discovered optimal values", className="text-muted d-block mb-3"),
            html.Div(id='parameter-table'),
        ], className="card-modern p-4"),
    ], className="mb-4")


def create_distribution_plot():
    """Create enhanced power distribution plot card."""
    return html.Div([
        html.Div([
            html.H5([
                html.I(className="fas fa-chart-bar me-2"),
                "Power Distribution Analysis"
            ], className="section-title"),
            dcc.Loading(
                dcc.Graph(id='distribution-plot', style={'height': '400px'}),
                type="circle",
                color=COLORS['primary']
            ),
        ], className="card-modern p-4"),
    ], className="mb-4")


def create_intro():
    """Create introduction section explaining the system."""
    return html.Div([
        dbc.Card([
            dbc.CardBody([
                html.H5([
                    html.I(className="fas fa-info-circle me-2"),
                    "About This System"
                ], className="mb-3"),
                html.P([
                    "This dashboard demonstrates AI-powered optimization of servo press coordination to reduce peak power demand. ",
                    "Industrial facilities pay demand charges based on their highest 15-minute power usage, making peak reduction critical for cost savings."
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("🔴 ", style={'fontSize': '1.2rem'}),
                            html.Strong("Baseline", className="me-2"),
                            html.Span("Independent operation with no coordination between presses.", className="text-muted")
                        ], className="mb-2"),
                    ], lg=4),
                    dbc.Col([
                        html.Div([
                            html.Span("🔵 ", style={'fontSize': '1.2rem'}),
                            html.Strong("Static Cardiac", className="me-2"),
                            html.Span("Bio-inspired coordination using default parameters (ring topology, 5s delay, 30% refractory).", className="text-muted")
                        ], className="mb-2"),
                    ], lg=4),
                    dbc.Col([
                        html.Div([
                            html.Span("🟢 ", style={'fontSize': '1.2rem'}),
                            html.Strong("AI-Optimized", className="me-2"),
                            html.Span("Machine learning discovers optimal coordination parameters for each scenario.", className="text-muted")
                        ], className="mb-2"),
                    ], lg=4),
                ]),
            ])
        ], className="card-modern mb-4"),
    ])


def create_footer():
    """Create professional footer."""
    return html.Div([
        html.Hr(className="mt-5"),
        html.Div([
            html.P([
                html.I(className="fas fa-graduation-cap me-2"),
                "Bio-Servo Project | 2025 SEYI Cup Competition | ",
                html.Span("Cardiac Rhythm Coordination System", className="fw-bold")
            ], className="text-center text-muted mb-2"),
            html.P([
                "Powered by ",
                html.I(className="fas fa-heart text-danger mx-1"),
                " and Claude Code"
            ], className="text-center text-muted small"),
        ], className="py-3"),
    ])


# =============================================================================
# App Layout
# =============================================================================

app.layout = html.Div([
    # Header
    create_header(),

    # Main container
    dbc.Container([
        # Introduction
        create_intro(),

        # Controls
        create_controls(),
        
        # Metrics cards
        create_metrics_cards(),
        
        # Charts row
        dbc.Row([
            dbc.Col([
                create_power_curve_plot(),
            ], width=12),
        ]),
        
        # Tables row
        dbc.Row([
            dbc.Col([
                create_comparison_table(),
            ], lg=6, className="mb-4"),
            dbc.Col([
                create_parameter_table(),
            ], lg=6, className="mb-4"),
        ]),
        
        # Distribution plot
        dbc.Row([
            dbc.Col([
                create_distribution_plot(),
            ], width=12),
        ]),
        
        # Footer
        create_footer(),
    ], fluid=True, className="px-4"),
])


# =============================================================================
# Callbacks
# =============================================================================

@app.callback(
    [
        Output('scenario-info', 'children'),
        Output('metrics-cards', 'children'),
        Output('power-curve-plot', 'figure'),
        Output('comparison-table', 'children'),
        Output('parameter-table', 'children'),
        Output('distribution-plot', 'figure'),
    ],
    [
        Input('press-count-dropdown', 'value'),
        Input('mix-dropdown', 'value'),
    ]
)
def update_dashboard(n_presses, mix):
    """Update all dashboard components based on selected scenario."""
    
    # Get scenario data
    scenario_key = get_scenario_key(n_presses, mix)
    scenario_data = ALL_RESULTS[scenario_key]
    
    baseline = scenario_data['baseline']
    static = scenario_data['static']
    ai = scenario_data['ai']
    
    # Extract power curves
    baseline_power = np.array(baseline['aggregate_power'])
    static_power = np.array(static['aggregate_power'])
    ai_power = np.array(ai['aggregate_power'])
    time_steps = np.array(baseline['time']) / 60  # Convert to minutes
    
    # Extract key metrics
    baseline_peak = baseline['summary']['peak_power']
    static_peak = static['summary']['peak_power']
    ai_peak = ai['summary']['peak_power']
    
    # Calculate improvements
    static_reduction_pct = (baseline_peak - static_peak) / baseline_peak * 100
    ai_reduction_pct = (baseline_peak - ai_peak) / baseline_peak * 100
    ai_vs_static_pct = (static_peak - ai_peak) / static_peak * 100
    
    # Calculate cost savings
    static_savings = calculate_cost_savings(baseline_peak, static_peak)
    ai_savings = calculate_cost_savings(baseline_peak, ai_peak)
    ai_additional_savings_usd = ai_savings['usd'] - static_savings['usd']
    
    # ==================================================================
    # 1. Scenario Info with Icons
    # ==================================================================
    fleet_info = {
        'realistic': '200-600 kW mix',
        'varied': 'Diverse power range',
        'uniform': 'All presses identical'
    }
    
    scenario_info = html.Div([
        html.Div([
            html.I(className="fas fa-server me-2 text-primary"),
            html.Strong(f"{n_presses} Presses"),
        ], className="mb-2"),
        html.Div([
            html.I(className="fas fa-bolt me-2 text-warning"),
            html.Span(fleet_info[mix]),
        ]),
    ])
    
    # ==================================================================
    # 2. Enhanced Metrics Cards with Gradients
    # ==================================================================
    
    def create_metric_card(value, label, icon, gradient_colors, comparison=None):
        """Create a modern metric card with gradient background."""
        card_style = {
            'background': f'linear-gradient(135deg, {gradient_colors[0]} 0%, {gradient_colors[1]} 100%)',
            'borderRadius': '12px',
            'padding': '25px',
            'boxShadow': '0 10px 30px rgba(0,0,0,0.1)',
            'transition': 'transform 0.3s ease',
            'height': '100%',
        }
        
        return html.Div([
            html.Div([
                html.I(className=f"{icon} fa-2x mb-3", style={'opacity': '0.8', 'color': 'white'}),
                html.Div(value, className="metric-value text-white"),
                html.Div(label, className="metric-label"),
                html.Div(comparison, className="mt-2 text-white small") if comparison else None,
            ], className="text-center"),
        ], style=card_style, className="h-100")
    
    metrics_cards = dbc.Row([
        dbc.Col([
            create_metric_card(
                f"{baseline_peak:.0f} kW",
                "Baseline Peak",
                "fas fa-exclamation-triangle",
                ['#DC3545', '#C82333'],
                "No coordination"
            )
        ], lg=3, md=6, className="mb-4"),
        
        dbc.Col([
            create_metric_card(
                f"{static_peak:.0f} kW",
                "Static Cardiac",
                "fas fa-heart",
                ['#0066CC', '#0056B3'],
                f"{-static_reduction_pct:+.1f}% vs baseline"
            )
        ], lg=3, md=6, className="mb-4"),
        
        dbc.Col([
            create_metric_card(
                f"{ai_peak:.0f} kW",
                "AI-Optimized",
                "fas fa-robot",
                ['#00A86B', '#00875A'],
                f"{-ai_reduction_pct:+.1f}% vs baseline"
            )
        ], lg=3, md=6, className="mb-4"),
        
        dbc.Col([
            create_metric_card(
                format_currency(ai_savings['usd']),
                "Annual Savings",
                "fas fa-dollar-sign",
                ['#28A745', '#1E7E34'],
                f"+${ai_additional_savings_usd:,.0f} vs static"
            )
        ], lg=3, md=6, className="mb-4"),
    ])
    
    # ==================================================================
    # 3. Enhanced Power Curve Plot
    # ==================================================================
    fig_power = go.Figure()
    
    # Add traces with custom styling
    fig_power.add_trace(go.Scatter(
        x=time_steps,
        y=baseline_power,
        name='Baseline (No Coordination)',
        mode='lines',
        line=dict(color=CHART_COLORS['baseline'], width=2.5, dash='dot'),
        hovertemplate='<b>Baseline</b><br>Time: %{x:.1f}m<br>Power: %{y:.1f} kW<extra></extra>'
    ))

    fig_power.add_trace(go.Scatter(
        x=time_steps,
        y=static_power,
        name='Static Cardiac',
        mode='lines',
        line=dict(color=CHART_COLORS['static'], width=2.5),
        hovertemplate='<b>Static Cardiac</b><br>Time: %{x:.1f}m<br>Power: %{y:.1f} kW<extra></extra>'
    ))

    fig_power.add_trace(go.Scatter(
        x=time_steps,
        y=ai_power,
        name='AI-Optimized Cardiac',
        mode='lines',
        line=dict(color=CHART_COLORS['ai'], width=3),
        hovertemplate='<b>AI-Optimized</b><br>Time: %{x:.1f}m<br>Power: %{y:.1f} kW<extra></extra>'
    ))

    # Add peak annotations
    fig_power.add_annotation(
        x=time_steps[np.argmax(baseline_power)],
        y=baseline_peak,
        text=f"Baseline: {baseline_peak:.0f} kW",
        showarrow=True,
        arrowhead=2,
        arrowcolor=CHART_COLORS['baseline'],
        bgcolor="white",
        bordercolor=CHART_COLORS['baseline'],
        borderwidth=2,
        font=dict(color=CHART_COLORS['baseline'], size=11),
    )

    fig_power.add_annotation(
        x=time_steps[np.argmax(static_power)],
        y=static_peak,
        text=f"Static: {static_peak:.0f} kW<br>{-static_reduction_pct:.1f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor=CHART_COLORS['static'],
        bgcolor="white",
        bordercolor=CHART_COLORS['static'],
        borderwidth=2,
        font=dict(color=CHART_COLORS['static'], size=11),
    )

    fig_power.add_annotation(
        x=time_steps[np.argmax(ai_power)],
        y=ai_peak,
        text=f"AI: {ai_peak:.0f} kW<br>{-ai_reduction_pct:.1f}%",
        showarrow=True,
        arrowhead=2,
        arrowcolor=CHART_COLORS['ai'],
        bgcolor="white",
        bordercolor=CHART_COLORS['ai'],
        borderwidth=2,
        font=dict(color=CHART_COLORS['ai'], size=11, weight='bold'),
    )
    
    fig_power.update_layout(
        xaxis=dict(
            title="Time (minutes)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
        ),
        yaxis=dict(
            title="Power Demand (kW)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=12),
        ),
        margin=dict(l=60, r=40, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", size=12),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        ),
    )
    
    # ==================================================================
    # 4. Enhanced Comparison Table
    # ==================================================================
    
    # Determine improvements
    static_is_better = static_peak < baseline_peak
    ai_is_better = ai_peak < baseline_peak
    ai_better_than_static = ai_peak < static_peak
    ai_improvement_pct = (static_peak - ai_peak) / static_peak * 100 if static_peak > 0 else 0
    
    comparison_table = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Metric", style={'width': '30%'}),
                html.Th("Baseline", className="text-center"),
                html.Th("Static", className="text-center"),
                html.Th("AI-Optimized", className="text-center"),
                html.Th("AI Advantage", className="text-center"),
            ], className="bg-light"),
        ]),
        html.Tbody([
            html.Tr([
                html.Td([
                    html.I(className="fas fa-bolt me-2 text-warning"),
                    "Peak Power (kW)"
                ]),
                html.Td(f"{baseline['summary']['peak_power']:.1f}", className="text-center"),
                html.Td([
                    f"{static['summary']['peak_power']:.1f}",
                    html.Br(),
                    html.Span(
                        f"({-static_reduction_pct:+.1f}%)",
                        className="improvement-positive" if static_is_better else "improvement-negative"
                    )
                ], className="text-center"),
                html.Td([
                    html.Strong(f"{ai['summary']['peak_power']:.1f}"),
                    html.Br(),
                    html.Span(
                        f"({-ai_reduction_pct:+.1f}%)",
                        className="improvement-positive" if ai_is_better else "improvement-negative"
                    )
                ], className="text-center"),
                html.Td([
                    html.Span(
                        f"{ai_improvement_pct:+.1f}%",
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['secondary'], 'color': 'white'}
                    )
                ], className="text-center"),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-chart-line me-2 text-info"),
                    "Mean Power (kW)"
                ]),
                html.Td(f"{baseline['summary']['mean_power']:.1f}", className="text-center"),
                html.Td(f"{static['summary']['mean_power']:.1f}", className="text-center"),
                html.Td(f"{ai['summary']['mean_power']:.1f}", className="text-center"),
                html.Td("—", className="text-center text-muted"),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-clock me-2 text-primary"),
                    "15-min Peak (kW)"
                ]),
                html.Td(f"{baseline['summary']['peak_15min']:.1f}", className="text-center"),
                html.Td(f"{static['summary']['peak_15min']:.1f}", className="text-center"),
                html.Td(f"{ai['summary']['peak_15min']:.1f}", className="text-center"),
                html.Td("—", className="text-center text-muted"),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-dollar-sign me-2 text-success"),
                    "Annual Savings (USD)"
                ]),
                html.Td("$0", className="text-center text-muted"),
                html.Td([
                    html.Span(
                        format_currency(static_savings['usd']) if static_is_better else f"-${abs(static_savings['usd']):,.0f}",
                        className="improvement-positive" if static_is_better else "improvement-negative"
                    )
                ], className="text-center"),
                html.Td([
                    html.Strong(
                        format_currency(ai_savings['usd']) if ai_is_better else f"-${abs(ai_savings['usd']):,.0f}",
                        className="improvement-positive" if ai_is_better else "improvement-negative"
                    )
                ], className="text-center"),
                html.Td([
                    html.Span(
                        f"+${ai_additional_savings_usd:,.0f}" if ai_additional_savings_usd >= 0 else f"-${abs(ai_additional_savings_usd):,.0f}",
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['secondary'] if ai_additional_savings_usd >= 0 else COLORS['warning'], 'color': 'white'}
                    )
                ], className="text-center"),
            ]),
        ]),
    ], className="table table-hover table-modern")
    
    # ==================================================================
    # 5. Enhanced Parameter Table
    # ==================================================================
    static_params = static['params']
    ai_params = ai['params']
    
    parameter_table = html.Table([
        html.Thead([
            html.Tr([
                html.Th("Parameter", style={'width': '25%'}),
                html.Th("Static Default", className="text-center"),
                html.Th("AI-Optimized", className="text-center"),
                html.Th("Impact"),
            ], className="bg-light"),
        ]),
        html.Tbody([
            html.Tr([
                html.Td([
                    html.I(className="fas fa-network-wired me-2 text-primary"),
                    "Topology"
                ]),
                html.Td(static_params['topology'], className="text-center"),
                html.Td([
                    html.Span(
                        ai_params['topology'],
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['primary'], 'color': 'white'}
                    ) if ai_params['topology'] != static_params['topology'] else ai_params['topology']
                ], className="text-center"),
                html.Td(
                    "Enhanced coordination" if ai_params['topology'] == 'all_to_all' else "Ring structure",
                    className="text-muted"
                ),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-hourglass-half me-2 text-warning"),
                    "Max Delay"
                ]),
                html.Td(f"{static_params['max_delay_sec']}s", className="text-center"),
                html.Td([
                    html.Span(
                        f"{ai_params['max_delay_sec']}s",
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['warning'], 'color': 'white'}
                    ) if ai_params['max_delay_sec'] != static_params['max_delay_sec'] else f"{ai_params['max_delay_sec']}s"
                ], className="text-center"),
                html.Td("Increased flexibility", className="text-muted"),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-pause me-2 text-info"),
                    "Refractory Period"
                ]),
                html.Td(f"{static_params['refractory_pct']}%", className="text-center"),
                html.Td([
                    html.Span(
                        f"{ai_params['refractory_pct']}%",
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['info'], 'color': 'white'}
                    ) if ai_params['refractory_pct'] != static_params['refractory_pct'] else f"{ai_params['refractory_pct']}%"
                ], className="text-center"),
                html.Td("Rest between cycles", className="text-muted"),
            ]),
            
            html.Tr([
                html.Td([
                    html.I(className="fas fa-random me-2 text-secondary"),
                    "Variation"
                ]),
                html.Td(f"{static_params['variation']}", className="text-center"),
                html.Td([
                    html.Span(
                        f"{ai_params['variation']}",
                        className="badge badge-custom",
                        style={'backgroundColor': COLORS['muted'], 'color': 'white'}
                    ) if ai_params['variation'] != static_params['variation'] else f"{ai_params['variation']}"
                ], className="text-center"),
                html.Td("Timing variability", className="text-muted"),
            ]),
        ]),
    ], className="table table-hover table-modern")
    
    # ==================================================================
    # 6. Enhanced Distribution Plot
    # ==================================================================
    fig_dist = go.Figure()
    
    # Create smooth density curves using KDE
    power_min = min(baseline_power.min(), static_power.min(), ai_power.min())
    power_max = max(baseline_power.max(), static_power.max(), ai_power.max())
    power_range = np.linspace(power_min, power_max, 300)
    
    # Calculate KDEs
    kde_baseline = gaussian_kde(baseline_power)
    density_baseline = kde_baseline(power_range)
    
    kde_static = gaussian_kde(static_power)
    density_static = kde_static(power_range)
    
    kde_ai = gaussian_kde(ai_power)
    density_ai = kde_ai(power_range)
    
    # Add density traces with gradient fills
    fig_dist.add_trace(go.Scatter(
        x=power_range,
        y=density_baseline,
        name='Baseline',
        mode='lines',
        line=dict(color=CHART_COLORS['baseline'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba({int(CHART_COLORS['baseline'][1:3], 16)}, {int(CHART_COLORS['baseline'][3:5], 16)}, {int(CHART_COLORS['baseline'][5:7], 16)}, 0.2)",
        hovertemplate='<b>Baseline</b><br>Power: %{x:.1f} kW<br>Density: %{y:.4f}<extra></extra>'
    ))
    
    fig_dist.add_trace(go.Scatter(
        x=power_range,
        y=density_static,
        name='Static Cardiac',
        mode='lines',
        line=dict(color=CHART_COLORS['static'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba({int(CHART_COLORS['static'][1:3], 16)}, {int(CHART_COLORS['static'][3:5], 16)}, {int(CHART_COLORS['static'][5:7], 16)}, 0.2)",
        hovertemplate='<b>Static</b><br>Power: %{x:.1f} kW<br>Density: %{y:.4f}<extra></extra>'
    ))
    
    fig_dist.add_trace(go.Scatter(
        x=power_range,
        y=density_ai,
        name='AI-Optimized',
        mode='lines',
        line=dict(color=CHART_COLORS['ai'], width=3),
        fill='tozeroy',
        fillcolor=f"rgba({int(CHART_COLORS['ai'][1:3], 16)}, {int(CHART_COLORS['ai'][3:5], 16)}, {int(CHART_COLORS['ai'][5:7], 16)}, 0.2)",
        hovertemplate='<b>AI-Optimized</b><br>Power: %{x:.1f} kW<br>Density: %{y:.4f}<extra></extra>'
    ))
    
    # Add vertical lines for peak values with styled annotations
    fig_dist.add_vline(
        x=baseline_peak,
        line_dash="dash",
        line_color=CHART_COLORS['baseline'],
        annotation_text=f"Baseline: {baseline_peak:.0f} kW",
        annotation_position="top"
    )
    
    fig_dist.add_vline(
        x=static_peak,
        line_dash="dash",
        line_color=CHART_COLORS['static'],
        annotation_text=f"Static: {static_peak:.0f} kW",
        annotation_position="top"
    )
    
    fig_dist.add_vline(
        x=ai_peak,
        line_dash="dash",
        line_color=CHART_COLORS['ai'],
        annotation_text=f"AI: {ai_peak:.0f} kW",
        annotation_position="top"
    )
    
    fig_dist.update_layout(
        xaxis=dict(
            title="Power Demand (kW)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
        ),
        yaxis=dict(
            title="Probability Density",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=12),
        ),
        margin=dict(l=60, r=40, t=60, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", size=12),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
        ),
    )
    
    return (
        scenario_info,
        metrics_cards,
        fig_power,
        comparison_table,
        parameter_table,
        fig_dist,
    )


# =============================================================================
# Main
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting Enhanced AI Showcase Dashboard")
    print("="*70)
    print(f"✓ Loaded {len(ALL_RESULTS)} scenarios")
    print(f"✓ Seed: {METADATA['seed']}")
    print(f"✓ Duration: {METADATA['duration_sec']/3600:.0f}h per simulation")
    print("\n📊 Dashboard Features:")
    print("  • Modern gradient design with professional styling")
    print("  • Interactive charts with enhanced tooltips")
    print("  • Responsive layout for all screen sizes")
    print("  • Icon-enhanced metrics and tables")
    print("  • Smooth animations and transitions")

    # Get port from environment variable (for deployment) or use 8053 (for local)
    port = int(os.environ.get('PORT', 8053))
    host = os.environ.get('HOST', '127.0.0.1')

    # For deployment, use production settings
    if os.environ.get('PORT'):
        print(f"\n🌐 Running in production mode on port {port}")
        print("="*70 + "\n")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print(f"\n🌐 Open browser to: http://localhost:{port}")
        print("="*70 + "\n")
        app.run(host=host, port=port, debug=True)