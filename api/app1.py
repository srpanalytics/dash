# import dash
# from dash import html, dcc, Input, Output, State, ctx
# import pandas as pd
# import plotly.express as px
# from datetime import datetime
# import requests
# from requests.auth import HTTPBasicAuth

# # API Configuration
# API_URL = "https://apps.greenitco.com/shyammetalics/api/ticket-export"
# USERNAME = "greenitcoITM"
# PASSWORD = "gr@8N@hS#~44"
# APP_TOKEN = "A4uhcLJc1XrAbYUPyxEZlMChDcRzLWVj"

# HEADERS = {
#     "Content-Type": "application/x-www-form-urlencoded",
#     "apptoken": APP_TOKEN,
# }

# def fetch_api_data():
#     today = datetime.now().strftime("%d-%m-%Y")
#     all_data = []
#     index = 1

#     while True:
#         payload = {
#             "index": index,
#             "list_size": 200,
#             "filters[based_on]": 1,
#             "filters[date_range]": f"24-07-2024 00:00:00 - {today} 23:59:59",
#         }
#         try:
#             response = requests.post(API_URL, headers=HEADERS, data=payload,
#                                      auth=HTTPBasicAuth(USERNAME, PASSWORD))
#             if response.status_code != 200:
#                 break
#             data = response.json()
#             if data.get("status") == "success" and "data" in data:
#                 all_data.extend(data["data"])
#                 if not data.get("is_next_index"):
#                     break
#                 index += 1
#             else:
#                 break
#         except Exception as e:
#             print("API Error:", e)
#             break

#     return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# # Fetch once globally (you can optimize by caching later)
# df = fetch_api_data()
# if df.empty:
#     raise ValueError("No data fetched from API.")

# # Data Cleaning
# df['created_at_format'] = pd.to_datetime(df['created_at_format'], errors='coerce')
# df['status'] = df['status'].fillna("Unknown")
# df['problem_category'] = df['problem_category'].fillna("Unknown")
# df['assigned_to_name'] = df['assigned_to_name'].fillna("Unassigned")
# df['department'] = df['department'].fillna("Unknown")

# # Ageing
# today = pd.Timestamp.now()
# df['age_days'] = (today - df['created_at_format']).dt.days
# df['age_bucket'] = df['age_days'].apply(
#     lambda x: "> 180 Days" if x > 180 else
#               "121 to 180 Days" if x > 120 else
#               "61 to 120 Days" if x > 60 else
#               "31 to 60 Days" if x > 30 else
#               "0 to 30 Days"
# )

# departments = sorted(df['department'].dropna().unique())
# min_date, max_date = df['created_at_format'].min(), df['created_at_format'].max()

# # App
# app = dash.Dash(__name__)
# app.title = "ITSM Dashboard"

# statuses = ['Open', 'Closed', 'In Progress', 'Resolved', 'Reopened', 'Under Observation']
# card_colors = ["#0b7912", "#dd321b", '#f39c12', '#3498db', '#9b59b6', '#1abc9c']

# app.layout = html.Div(style={'fontFamily': 'Segoe UI, sans-serif', 'backgroundColor': "#000000", 'padding': '20px'}, children=[

#     html.H2("ITSM Dashboard - SHYAM METALICS AND ENERGY LIMITED", style={'textAlign': 'center', 'color': "#ffffff"}),

#     html.Div([
#         dcc.Dropdown(
#             id='department-filter',
#             options=[{'label': i, 'value': i} for i in departments],
#             placeholder="Select Department",
#             multi=True,
#             style={'width': '180px'}
#         ),
#         dcc.DatePickerRange(
#             id='date-filter',
#             start_date=min_date,
#             end_date=max_date,
#             display_format='DD/MM/YYYY',
#             style={'marginLeft': '10px'}
#         ),
#         html.Button("Reset Filters", id='reset-button', n_clicks=0, style={'marginLeft': '20px'})
#     ], style={'display': 'flex', 'gap': '10px', 'justifyContent': 'center', 'marginTop': '30px'}),

#     dcc.Store(id='selected-status'),

#     html.Div(id='kpi-cards', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '20px'}),

#     html.Div([
#         dcc.Graph(id='tech-chart', style={'width': '33%'}),
#         dcc.Graph(id='assigned-chart', style={'width': '33%'}),
#         dcc.Graph(id='age-chart', style={'width': '33%'})
#     ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'marginTop': '50px'})
# ])

# @app.callback(
#     [Output('kpi-cards', 'children'),
#      Output('tech-chart', 'figure'),
#      Output('assigned-chart', 'figure'),
#      Output('age-chart', 'figure'),
#      Output('department-filter', 'value'),
#      Output('date-filter', 'start_date'),
#      Output('date-filter', 'end_date')],
#     [Input('department-filter', 'value'),
#      Input('date-filter', 'start_date'),
#      Input('date-filter', 'end_date'),
#      Input('tech-chart', 'clickData'),
#      Input('assigned-chart', 'clickData'),
#      Input('age-chart', 'clickData'),
#      Input('reset-button', 'n_clicks'),
#      Input('selected-status', 'data')],
#     [State('department-filter', 'value'),
#      State('date-filter', 'start_date'),
#      State('date-filter', 'end_date')]
# )
# def update_dashboard(dept_filter, start_date, end_date, tech_click, assigned_click, age_click, reset_click, status_filter, state_dept, state_start, state_end):
#     triggered = ctx.triggered_id

#     dff = df.copy()

#     if triggered == 'reset-button':
#         dept_filter = []
#         start_date = min_date
#         end_date = max_date
#         status_filter = None
#     else:
#         if dept_filter:
#             dff = dff[dff['department'].isin(dept_filter)]
#         if start_date and end_date:
#             dff = dff[(dff['created_at_format'] >= start_date) & (dff['created_at_format'] <= end_date)]
#         if status_filter:
#             dff = dff[dff['status'] == status_filter]
#         if tech_click:
#             val = tech_click['points'][0]['y']
#             dff = dff[dff['problem_category'] == val]
#         if assigned_click:
#             val = assigned_click['points'][0]['y']
#             dff = dff[dff['assigned_to_name'] == val]
#         if age_click:
#             val = age_click['points'][0]['x']
#             dff = dff[dff['age_bucket'] == val]

#     kpis = [len(dff[dff['status'] == s]) for s in statuses]
#     cards = [
#         html.Button([
#             html.H3(str(count), style={'margin': 0, 'color': '#fff'}),
#             html.P(label, style={'margin': 0, 'color': '#fff'})
#         ], id={'type': 'status-button', 'index': label},
#            style={
#                'padding': '15px 25px',
#                'background': card_colors[i % len(card_colors)],
#                'borderRadius': '10px',
#                'textAlign': 'center',
#                'minWidth': '130px',
#                'border': 'none',
#                'cursor': 'pointer'
#            }) for i, (label, count) in enumerate(zip(statuses, kpis))
#     ]

#     tech = dff[dff['status'].isin(['Open', 'In Progress'])]['problem_category'].value_counts().reset_index()
#     tech.columns = ['Technician', 'Count']
#     fig1 = px.bar(tech.sort_values(by='Count'), x='Count', y='Technician', orientation='h', text='Count',
#                   title='Ticket Count by Technician', template='plotly_white')
#     fig1.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='black',
#                        paper_bgcolor='black', font_color='white',
#                        title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

#     assigned = dff['assigned_to_name'].value_counts().reset_index()
#     assigned.columns = ['Assigned To', 'Count']
#     fig2 = px.bar(assigned.head(20), x='Count', y='Assigned To', orientation='h', text='Count',
#                   title='Ticket by Assigned', template='plotly_white')
#     fig2.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='black',
#                        paper_bgcolor='black', font_color='white',
#                        title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

#     age = dff['age_bucket'].value_counts().reset_index()
#     age.columns = ['Age Group', 'Count']
#     fig3 = px.bar(age.sort_values('Age Group'), x='Age Group', y='Count', text='Count',
#                   title='Ticket by Ageing', template='plotly_white')
#     fig3.update_layout(margin=dict(l=20, r=20, t=50, b=20), plot_bgcolor='black',
#                        paper_bgcolor='black', font_color='white',
#                        title_font_color='white', xaxis=dict(color='white'), yaxis=dict(color='white'))

#     return cards, fig1, fig2, fig3, dept_filter, start_date, end_date

# # Handle card clicks
# @app.callback(
#     Output('selected-status', 'data'),
#     Input({'type': 'status-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
#     State({'type': 'status-button', 'index': dash.dependencies.ALL}, 'id')
# )
# def update_status_filter(n_clicks_list, ids):
#     for n, i in zip(n_clicks_list, ids):
#         if n:
#             return i['index']
#     return dash.no_update

# if __name__ == '__main__':
#     app.run(debug=True)
