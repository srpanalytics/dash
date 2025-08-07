import dash
from dash import html, dcc, Input, Output, State, ctx
import pandas as pd
import plotly.express as px
from datetime import datetime
import os


# Load Excel data
EXCEL_PATH = r"data/SAP_Tickets.xlsx"
df = pd.read_excel(EXCEL_PATH)
df['created_at_format'] = pd.to_datetime(df['created_at_format'], errors='coerce')
df['closed_at_format'] = pd.to_datetime(df['closed_at_format'], errors='coerce')
df['tat_minutes'] = (df['closed_at_format'] - df['created_at_format']).dt.total_seconds() / 3600

df['status'] = df['status'].fillna("Unknown")
df['problem_category'] = df['problem_category'].fillna("Unknown")
df['assigned_to_name'] = df['assigned_to_name'].fillna("Unassigned")
df['department'] = df['department'].fillna("Unknown")
df['base_location_name'] = df['base_location_name'].fillna("Unknown")

today = pd.Timestamp.now()
df['age_days'] = (today - df['created_at_format']).dt.days  
df['age_bucket'] = df['age_days'].apply(
    lambda x: "> 180 Days" if x > 180 else
              "121 to 180 Days" if x > 120 else
              "61 to 120 Days" if x > 60 else
              "31 to 60 Days" if x > 30 else
              "0 to 30 Days"
)

departments = sorted(df['department'].dropna().unique())
locations = sorted(df['base_location_name'].dropna().unique())
min_date, max_date = df['created_at_format'].min(), df['created_at_format'].max()

# App init
app = dash.Dash(__name__)
app.title = "ITSM Dashboard"
statuses = ['Open', 'Closed', 'In Progress', 'Resolved', 'Reopened', 'Under Observation']
card_colors = ["#d4e0d5"] * 6

app.layout = html.Div(
    style={
        'fontFamily': 'Segoe UI, sans-serif',
        'backgroundColor': '#0b0c2a',
        'padding': '30px',
        'minHeight': '100vh',
        'color': '#f1f1f1'
    },
    children=[
        html.Div([
            html.Img(src='../assets/logo.png', style={
                'height': '60px',
                'width': 'auto',
                'marginRight': '20px'
            }),
        ], style={'position': 'absolute', 'top': '30px', 'left': '30px'}),
        html.H1(
            "ITSM Dashboard",
            style={
                'textAlign': 'center',
                'color': '#ffffff',
                'marginBottom': '5px',
                'fontSize': '36px',
                'fontWeight': '600',
                'letterSpacing': '1.5px'
            }
        ),
        html.H4(
            "Shyam Metalics and Energy Limited",
            style={
                'textAlign': 'center',
                'color': '#bbbbbb',
                'marginBottom': '40px',
                'fontWeight': '300'
            }
        ),
        html.Div([
            dcc.DatePickerRange(
                id='date-filter',
                start_date=min_date,
                end_date=max_date,
                display_format='DD/MM/YYYY',
                style={
                    'backgroundColor': '#1e1e2f',
                    'color': 'white',
                    'border': '1px solid #444',
                    'borderRadius': '8px',
                    'padding': '6px 10px',
                    'marginRight': '10px',
                    'fontFamily': 'Segoe UI',
                    'fontSize': '14px'
                }
            ),
            dcc.Dropdown(
                id='department-filter',
                options=[{'label': i, 'value': i} for i in departments],
                placeholder="Select Department",
                multi=True,
                style={
                    'minWidth': '220px',
                    'borderRadius': '10px',
                    'fontSize': '14px',
                    'color': "#000000",
                    'backgroundColor': '#2c2c3e',
                    'border': '1px solid #555',
                }
            ),
            dcc.Dropdown(
                id='location-filter',
                options=[{'label': i, 'value': i} for i in locations],
                placeholder="Select Location",
                multi=True,
                style={
                    'minWidth': '220px',
                    'borderRadius': '10px',
                    'fontSize': '14px',
                    'color': "#000000",
                    'backgroundColor': '#2c2c3e',
                    'border': '1px solid #555',
                }
            ),
            html.Button("Reset Filters", id='reset-button', n_clicks=0, style={
                'marginLeft': '10px',
                'height': '38px',
                'backgroundColor': '#e74c3c',
                'color': '#fff',
                'border': 'none',
                'borderRadius': '10px',
                'padding': '0 15px',
                'cursor': 'pointer',
                'fontWeight': '500'
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'center',
            'alignItems': 'center',
            'gap': '15px',
            'marginBottom': '40px'
        }),

        dcc.Store(id='selected-status'),

        html.Div(
            id='kpi-cards',
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'center',
                'gap': '20px',
                'marginBottom': '40px'
            }
        ),
        # 2x2 grid of graphs
        html.Div([
            html.Div([
                html.Div(dcc.Graph(id='tech-chart'), style={
                    'backgroundColor': '#1f1f2e',
                    'padding': '18px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'flex': '1',
                    'minWidth': '320px',
                    'maxWidth': '480px'
                }),
                html.Div(dcc.Graph(id='assigned-chart'), style={
                    'backgroundColor': '#1f1f2e',
                    'padding': '18px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'flex': '1',
                    'minWidth': '320px',
                    'maxWidth': '480px'
                }),
            ], style={
                'display': 'flex',
                'gap': '25px',
                'justifyContent': 'center',
                'marginBottom': '25px'
            }),
            html.Div([
                html.Div(dcc.Graph(id='age-chart'), style={
                    'backgroundColor': '#1f1f2e',
                    'padding': '18px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'flex': '1',
                    'minWidth': '320px',
                    'maxWidth': '480px'
                }),
                html.Div(dcc.Graph(id='tat-chart'), style={
                    'backgroundColor': '#1f1f2e',
                    'padding': '18px',
                    'borderRadius': '15px',
                    'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                    'flex': '1',
                    'minWidth': '320px',
                    'maxWidth': '480px'
                }),
            ], style={
                'display': 'flex',
                'gap': '25px',
                'justifyContent': 'center',
                'marginBottom': '40px'
            }),
        ]),
    ]
)

@app.callback(
    [Output('kpi-cards', 'children'),
     Output('tech-chart', 'figure'),
     Output('assigned-chart', 'figure'),
     Output('age-chart', 'figure'),
     Output('tat-chart', 'figure'),
     Output('department-filter', 'value'),
     Output('date-filter', 'start_date'),
     Output('date-filter', 'end_date'),
     Output('location-filter', 'value')],
    [Input('department-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('location-filter', 'value'),
     Input('tech-chart', 'clickData'),
     Input('assigned-chart', 'clickData'),
     Input('age-chart', 'clickData'),
     Input('reset-button', 'n_clicks'),
     Input('selected-status', 'data')],
    [State('department-filter', 'value'),
     State('date-filter', 'start_date'),
     State('date-filter', 'end_date'),
     State('location-filter', 'value')]
)
def update_dashboard(dept_filter, start_date, end_date, location_filter, tech_click, assigned_click, age_click, reset_click, status_filter, state_dept, state_start, state_end, state_location):
    triggered = ctx.triggered_id

    # Always apply filters (ALL must be included in dff for both cards and graphs)
    dff = df.copy()
    if triggered == 'reset-button':
        dept_filter = []
        start_date = min_date
        end_date = max_date
        location_filter = []
        status_filter = None
    if dept_filter:
        dff = dff[dff['department'].isin(dept_filter)]
    if location_filter:
        dff = dff[dff['base_location_name'].isin(location_filter)]
    if start_date and end_date:
        dff = dff[(dff['created_at_format'] >= start_date) & (dff['created_at_format'] <= end_date)]
    if status_filter:
        dff = dff[dff['status'] == status_filter]
    if tech_click:
        tech_val = tech_click['points'][0]['y']
        dff = dff[dff['problem_category'] == tech_val]
    if assigned_click:
        assigned_val = assigned_click['points'][0]['y']
        dff = dff[dff['assigned_to_name'] == assigned_val]
    if age_click:
        age_val = age_click['points'][0]['x']
        dff = dff[dff['age_bucket'] == age_val]

    # All KPI cards reflect fully filtered data
    kpis = [len(dff[dff['status'] == s]) for s in statuses]

    cards = []
    for i, (label, count) in enumerate(zip(statuses, kpis)):
        is_selected = status_filter == label
        bg_color = "#117508" if is_selected else card_colors[i % len(card_colors)]
        text_color = "#ECE7E7" if is_selected else "#000000"
        border = "3px solid #ffffff" if is_selected else "none"
        cards.append(
            html.Button([
                html.H3(str(count), style={'margin': 0, 'color': text_color}),
                html.P(label, style={'margin': 0, 'color': text_color})
            ],
            id={'type': 'status-button', 'index': label},
            style={
                'padding': '15px 25px',
                'background': bg_color,
                'borderRadius': '10px',
                'textAlign': 'center',
                'minWidth': '130px',
                'border': border,
                'cursor': 'pointer'
            })
        )

    # Technician chart
    tech = dff[dff['status'].isin(['Open', 'In Progress'])]['problem_category'].value_counts().reset_index()
    tech.columns = ['Technician', 'Count']
    fig1 = px.bar(
        tech.sort_values(by='Count').tail(15),
        x='Count', y='Technician', orientation='h', text='Count',
        title='Ticket Count by Technician'
    )
    fig1.update_layout(
        template='plotly_dark',
        plot_bgcolor='#222140',
        paper_bgcolor='#222140',
        font_color='#f1f1f1',
        xaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888'
        ),
        yaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888',
            automargin=True,
        ),
        title={
            'text': fig1.layout.title.text,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, family='Segoe UI', color='#e9e9e9')
        },
        margin=dict(l=40, r=20, t=60, b=35),
        bargap=0.35,
        showlegend=False
    )
    fig1.update_traces(marker=dict(color='#1484af', line=dict(width=0)), textposition='auto', textfont_color='white')

    # Assigned To chart
    assigned = dff['assigned_to_name'].value_counts().reset_index()
    assigned.columns = ['Assigned To', 'Count']
    fig2 = px.bar(
        assigned.sort_values(by='Count').tail(15),
        x='Count', y='Assigned To', orientation='h', text='Count',
        title='Ticket by Assigned To'
    )
    fig2.update_layout(
        template='plotly_dark',
        plot_bgcolor='#222140',
        paper_bgcolor='#222140',
        font_color='#f1f1f1',
        xaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888'
        ),
        yaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888',
            automargin=True,
        ),
        title={
            'text': fig2.layout.title.text,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, family='Segoe UI', color='#e9e9e9')
        },
        margin=dict(l=40, r=20, t=60, b=35),
        bargap=0.35,
        showlegend=False
    )
    fig2.update_traces(marker=dict(color='#b35a0b', line=dict(width=0)), textposition='auto', textfont_color='white')

    # Ageing chart
    age = dff['age_bucket'].value_counts().reset_index()
    age.columns = ['Age Group', 'Count']
    fig3 = px.bar(
        age.sort_values('Age Group'), x='Age Group', y='Count', text='Count',
        title='Ticket by Ageing'
    )
    fig3.update_layout(
        template='plotly_dark',
        plot_bgcolor='#222140',
        paper_bgcolor='#222140',
        font_color='#f1f1f1',
        xaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888'
        ),
        yaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888'
        ),
        title={
            'text': fig3.layout.title.text,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, family='Segoe UI', color='#e9e9e9')
        },
        margin=dict(l=40, r=20, t=60, b=35),
        bargap=0.35,
        showlegend=False
    )
    fig3.update_traces(marker=dict(color='#287e6f', line=dict(width=0)), textposition='auto', textfont_color='white')

    # TAT chart
    tat_df = dff.dropna(subset=['tat_minutes'])
    tat_avg = tat_df.groupby('assigned_to_name')['tat_minutes'].mean().reset_index()
    tat_avg = tat_avg.sort_values(by='tat_minutes', ascending=False).head(15)
    fig4 = px.bar(
        tat_avg,
        x='tat_minutes', y='assigned_to_name', orientation='h',
        title='Avg TAT (minutes) by Assigned To',
        text=tat_avg['tat_minutes'].round(1)
    )
    fig4.update_layout(
        template='plotly_dark',
        plot_bgcolor='#222140',
        paper_bgcolor='#222140',
        font_color='#f1f1f1',
        xaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888'
        ),
        yaxis=dict(
            color='#f1f1f1',
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor='#888',
            automargin=True,
        ),
        title={
            'text': fig4.layout.title.text,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20, family='Segoe UI', color='#e9e9e9')
        },
        margin=dict(l=40, r=20, t=60, b=35),
        bargap=0.35,
        showlegend=False
    )
    fig4.update_traces(marker=dict(color='#d96389', line=dict(width=0)), textposition='auto', textfont_color='white')

    return cards, fig1, fig2, fig3, fig4, dept_filter, start_date, end_date, location_filter

@app.callback(
    Output('selected-status', 'data'),
    Input({'type': 'status-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
    State({'type': 'status-button', 'index': dash.dependencies.ALL}, 'id'),
    State('selected-status', 'data')
)
def update_status_filter(n_clicks_list, ids, current_selected):
    ctx_index = None
    for n, i in zip(n_clicks_list, ids):
        if n and n > 0:
            ctx_index = i['index']
            break
    if ctx_index:
        if ctx_index == current_selected:
            return None
        else:
            return ctx_index
    return dash.no_update




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 for local dev
    app.run(host="0.0.0.0", port=port)








# if __name__ == '__main__':
#     app.run(debug=True)
