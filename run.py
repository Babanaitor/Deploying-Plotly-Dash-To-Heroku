
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.figure_factory as ff
import mysql.connector
import dash
import dash_table
import flask
import xlrd
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output, State

########### Define your variables
colors = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)', 'rgb(139,0,0)', 'rgb(0,191,255)',
          'rgb(0,0,128)', 'rgb(138,43,226)', 'rgb(34,139,34)', 'rgb(0,128,0)', 'rgb(0,255,127)',
          'rgb(107,142,35)', 'rgb(128,128,0)', 'rgb(255,215,0)', 'rgb(255,140,0)', 'rgb(255,0,255)',
          'rgb(210, 19, 180)']
df = pd.read_excel("Test.xlsx")
df1 = pd.DataFrame()
for i in range(df['FSS1 assigned'].count()):
    if pd.isnull(df.loc[i, 'FSS2 assigned']):
        df1.loc[i, 'Task'] = df.loc[i, 'FSS1 assigned']
    else:
        df1.loc[i, 'Task'] = df.loc[i, 'FSS1 assigned'] + ' AND ' + df.loc[i, 'FSS2 assigned']
df1['Task'] = df['FSS1 assigned'] + '___' + df['FSS2 assigned']
df1['Start'] = df['Expected date']
df1['Finish'] = df['Finish date']
df1['Complete'] = df['Customer']
df1['text'] = df['Job']

fig = ff.create_gantt(df1, group_tasks=True, colors=colors, index_col='Complete', reverse_colors=True,
                      show_colorbar=True)
map_df = pd.DataFrame()
map_df['names'] = df['FSS1 assigned'] + '     ' + df['FSS2 assigned']
map_df['country'] = df['Country']
map_df['job'] = df['Job']
conditions1 = [
    (map_df['country'] == 'Egypt'),
    (map_df['country'] == 'Pakistan'),
    (map_df['country'] == 'Libya'),
    (map_df['country'] == 'Kurdistan'),
    (map_df['country'] == 'Tunisia')
]
choices1 = [26.8, 30.38, 26.33, 36.41, 33.88]
map_df['lat'] = np.select(conditions1, choices1, default=0)
conditions2 = [
    (map_df['country'] == 'Egypt'),
    (map_df['country'] == 'Pakistan'),
    (map_df['country'] == 'Libya'),
    (map_df['country'] == 'Kurdistan'),
    (map_df['country'] == 'Tunisia')
]
choices2 = [30.8, 69.34, 17.22, 44.38, 9.53]
map_df['lon'] = np.select(conditions2, choices2, default=0)

map_df['BOOLa'] = map_df['lat'].duplicated(keep='first')
for j in range(map_df['lat'].count()):
    map_df['BOOLa'] = map_df['lat'].duplicated(keep='first')
    for i in range(map_df['lat'].count()):
        if map_df.loc[i, 'BOOLa']:
            map_df.loc[i, 'lat'] = map_df.loc[i, 'lat'] + 0.3
        else:
            map_df.loc[i, 'lat'] = map_df.loc[i, 'lat']

fig1 = px.scatter_mapbox(map_df, lat="lat", lon="lon", hover_name="names", hover_data=["country", "job"],
                         color_discrete_sequence=["fuchsia"], zoom=3, height=700, )
fig1.update_layout(mapbox_style="carto-positron")
fig1.update_layout(margin={"r": 20, "t": 20, "l": 20, "b": 20})

beers = ['Chesapeake Stout', 'Snake Dog IPA', 'Imperial Porter', 'Double Dog IPA']
ibu_values = [35, 60, 85, 75]
abv_values = [5.4, 7.1, 9.2, 4.3]
color1 = 'lightblue'
color2 = 'darkgreen'
mytitle = 'Beer Comparison'
tabtitle = 'beer!'
myheading = 'Flying Dog Beers'
label1 = 'IBU'
label2 = 'ABV'
githublink = 'https://github.com/austinlasseter/flying-dog-beers'
sourceurl = 'https://www.flyingdog.com/beers/'

########### Set up the chart
bitterness = go.Bar(
    x=beers,
    y=ibu_values,
    name=label1,
    marker={'color': color1}
)
alcohol = go.Bar(
    x=beers,
    y=abv_values,
    name=label2,
    marker={'color': color2}
)

beer_data = [bitterness, alcohol]
beer_layout = go.Layout(
    barmode='group',
    title=mytitle
)

beer_fig = go.Figure(data=beer_data, layout=beer_layout)

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = tabtitle

########### Set up the layout
app.layout = html.Div(children=[
    dcc.Link('Gantt Chart', href='/page-1'),
    html.Br(),
    dcc.Link('Table View', href='/page-2'),
    html.Br(),
    html.H2('World Map Representation of database'),
    dcc.Graph(figure=fig1, id='country'),
    dcc.Link('World Map', href='/'),
    html.Br(),
    dcc.Link('Table View', href='/page-2'),
    html.H2('Gantt Chart Representation of database'),
    dcc.Graph(figure=fig, id='gantt'),

    dcc.Link('World Map', href='/'),
    html.Br(),
    dcc.Link('Gantt Chart', href='/page-1'),
    html.Br(),
    html.Div(id='page-2-display-value'),
    html.Br(),
    html.H2('Table View'),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        editable=False,
        row_deletable=False,
        style_as_list_view=True,
        style_header={'backgroundColor': 'rgb(30, 30, 30)'},
        style_cell={
            'backgroundColor': 'rgb(50, 50, 50)',
            'color': 'white',
            'textAlign': 'left',
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'Region'},
                'textAlign': 'left'
            }
        ]
    ),

    html.H1(myheading),
    dcc.Graph(
        id='flyingdog',
        figure=beer_fig
    ),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A('Data Source', href=sourceurl),
]
)

if __name__ == '__main__':
    app.run_server()
