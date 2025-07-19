import dash
from dash import html, dcc, Input, Output, State, ctx
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load Excel data
EXCEL_PATH = r"C:/Users/1103775/Downloads/dash/data/SAP_Tickets.xlsx"
df = pd.read_excel(EXCEL_PATH)
df['created_at_format'] = pd.to_datetime(df['created_at_format'], errors='coerce')
df['status'] = df['status'].fillna("Unknown")
df['problem_category'] = df['problem_category'].fillna("Unknown")
df['assigned_to_name'] = df['assigned_to_name'].fillna("Unassigned")
df['department'] = df['department'].fillna("Unknown")

# Ageing
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
min_date, max_date = df['created_at_format'].min(), df['created_at_format'].max()

# App init
app = dash.Dash(__name__)
app.title = "ITSM Dashboard"

statuses = ['Open', 'Closed', 'In Progress', 'Resolved', 'Reopened', 'Under Observation']
card_colors = ["#d4e0d5", "#d4e0d5", '#d4e0d5', '#d4e0d5', '#d4e0d5', '#d4e0d5']

app.layout = html.Div(
    style={
        'fontFamily': 'Segoe UI, sans-serif',
        'backgroundColor': '#0b0c2a',
        'padding': '30px',
        'minHeight': '100vh',
        'color': '#f1f1f1'
    },
    children=[
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

        # Filter Bar
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
                    'color': "#000000",              # Text color
                    'backgroundColor': '#2c2c3e',    # Dropdown box background
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

        # Hidden Store
        dcc.Store(id='selected-status'),

        # KPI Cards
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

        # Graph Section
        html.Div([
            html.Div(dcc.Graph(id='tech-chart'), style={
                'backgroundColor': '#1f1f2e',
                'padding': '15px',
                'borderRadius': '15px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
                'flex': '1',
                'minWidth': '300px'
            }),
            html.Div(dcc.Graph(id='assigned-chart'), style={
                'backgroundColor': '#1f1f2e',
                'padding': '15px',
                'borderRadius': '15px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
                'flex': '1',
                'minWidth': '300px'
            }),
            html.Div(dcc.Graph(id='age-chart'), style={
                'backgroundColor': '#1f1f2e',
                'padding': '15px',
                'borderRadius': '15px',
                'boxShadow': '0 4px 12px rgba(0,0,0,0.2)',
                'flex': '1',
                'minWidth': '300px'
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'gap': '25px',
            'justifyContent': 'center',
            'marginBottom': '40px'
        })
    ]
)



@app.callback(
    [Output('kpi-cards', 'children'),
     Output('tech-chart', 'figure'),
     Output('assigned-chart', 'figure'),
     Output('age-chart', 'figure'),
     Output('department-filter', 'value'),
     Output('date-filter', 'start_date'),
     Output('date-filter', 'end_date')],
    [Input('department-filter', 'value'),
     Input('date-filter', 'start_date'),
     Input('date-filter', 'end_date'),
     Input('tech-chart', 'clickData'),
     Input('assigned-chart', 'clickData'),
     Input('age-chart', 'clickData'),
     Input('reset-button', 'n_clicks'),
     Input('selected-status', 'data')],
    [State('department-filter', 'value'),
     State('date-filter', 'start_date'),
     State('date-filter', 'end_date')]
)
def update_dashboard(dept_filter, start_date, end_date, tech_click, assigned_click, age_click, reset_click, status_filter, state_dept, state_start, state_end):
    triggered = ctx.triggered_id

    if triggered == 'reset-button':
        dff = df.copy()
        dept_filter = []
        start_date = min_date
        end_date = max_date
        status_filter = None
    else:
        dff = df.copy()
        if dept_filter:
            dff = dff[dff['department'].isin(dept_filter)]
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

    # kpis = [len(dff[dff['status'] == s]) for s in statuses]
    kpi_df = df.copy()
    if dept_filter:
        kpi_df = kpi_df[kpi_df['department'].isin(dept_filter)]
    if start_date and end_date:
        kpi_df = kpi_df[(kpi_df['created_at_format'] >= start_date) & (kpi_df['created_at_format'] <= end_date)]

    kpis = [len(kpi_df[kpi_df['status'] == s]) for s in statuses]

    cards = []
    for i, (label, count) in enumerate(zip(statuses, kpis)):
        is_selected = status_filter == label
        if is_selected:
            bg_color = "#117508"
            text_color = "#ECE7E7"
            border = "3px solid #ffffff"
        else: 
            bg_color = "#CECFCD" if is_selected else card_colors[i % len(card_colors)]
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

    tech = dff[dff['status'].isin(['Open', 'In Progress'])]['problem_category'].value_counts().reset_index()
    tech.columns = ['Technician', 'Count']
    fig1 = px.bar(tech.sort_values(by='Count'), x='Count', y='Technician', orientation='h', text='Count',
                  title='Ticket Count by Technician', template='plotly_white')
    fig1.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)', font_color='white',
                       title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

    assigned = dff['assigned_to_name'].value_counts().reset_index()
    assigned.columns = ['Assigned To', 'Count']
    fig2 = px.bar(assigned.head(20), x='Count', y='Assigned To', orientation='h', text='Count',
                  title='Ticket by Assigned', template='plotly_white')
    fig2.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)', font_color='white',
                       title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

    age = dff['age_bucket'].value_counts().reset_index()
    age.columns = ['Age Group', 'Count']
    fig3 = px.bar(age.sort_values('Age Group'), x='Age Group', y='Count', text='Count',
                  title='Ticket by Ageing', template='plotly_white')
    fig3.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='rgba(0,0,0,0)',
                       paper_bgcolor='rgba(0,0,0,0)', font_color='white',
                       title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

    return cards, fig1, fig2, fig3, dept_filter, start_date, end_date

# Callback to store clicked KPI status
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
            return None  # Deselect
        else:
            return ctx_index  # New selection
    return dash.no_update


if __name__ == '__main__':
    app.run(debug=True)
