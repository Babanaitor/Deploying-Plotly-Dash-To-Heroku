import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.figure_factory as ff
import dash
import dash_table
import flask
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output, State

colors = ['rgb(255, 0, 0)', 'rgb(0, 255, 0)', 'rgb(0, 0, 255)', 'rgb(139,0,0)', 'rgb(0,191,255)',
          'rgb(0,0,128)', 'rgb(138,43,226)', 'rgb(34,139,34)', 'rgb(0,128,0)', 'rgb(0,255,127)',
          'rgb(107,142,35)', 'rgb(128,128,0)', 'rgb(255,215,0)', 'rgb(255,140,0)', 'rgb(255,0,255)',
          'rgb(210, 19, 180)']

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        multiple=True
    ),
    html.Div(id='output-data-upload'),
])


def mainF(file_name):
    # <editor-fold desc="Gantt Chart Data">
    df = pd.read_excel(file_name)
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



    url_bar_and_content_div = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    # world map
    layout_index = html.Div([
        dcc.Link('Gantt Chart', href='/page-1'),
        html.Br(),
        dcc.Link('Table View', href='/page-2'),
        html.Br(),
        html.H2('World Map Representation of database'),
        dcc.Graph(figure=fig1, id='country'),
    ],
        style={'text-align': 'center'})

    # gantt chart
    layout_page_1 = html.Div([
        dcc.Link('World Map', href='/'),
        html.Br(),
        dcc.Link('Table View', href='/page-2'),
        html.H2('Gantt Chart Representation of database'),
        dcc.Graph(figure=fig, id='gantt'),
    ],
        style={'text-align': 'center'})

    # table view
    layout_page_2 = html.Div([
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
    ],
        style={'text-align': 'center'})

    def serve_layout():
        if flask.has_request_context():
            return url_bar_and_content_div
        return html.Div([
            url_bar_and_content_div,
            layout_index,
            layout_page_1,
            layout_page_2,
        ])

    app.layout = serve_layout

    # Index callbacks
    @app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == "/page-1":
            return layout_page_1
        elif pathname == "/page-2":
            return layout_page_2
        else:
            return layout_index

    if __name__ == '__main__':
        app.run_server()


def parse_contents(contents, filename, date):
    mainF(filename)
    return html.Div([
        html.H5(filename),
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


if __name__ == '__main__':
    app.run_server()
