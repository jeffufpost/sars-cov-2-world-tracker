# Data
import pandas as pd
import numpy as np
import datetime
import math
from urllib.request import urlopen
import json
import requests
import urllib.request
import urllib.parse
import time
import io
from bs4 import BeautifulSoup
# Graphing
import plotly.graph_objects as go
import plotly.express as px
# Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
# Navbar
from navbar import Navbar

def create_time_series2(x, yrea, yrad, ydc, yhosp, title):
    return {
        'data': [
            {'name': 'Patients en Reanimation',
             "x": x,
             "y": yrea,
             'type': 'scatter',
             'line': {'color':'firebrick'}
            },
            {'name': 'Recoveries cumulative',
             "x": x,
             "y": yrad,
             'type': 'scatter',
             'line': {'color':'green'}
            },
            {'name': 'Deaths cumulative',
             "x": x,
             "y": ydc,
             'type': 'scatter',
             'line': {'color':'black'}
            },
            {'name': 'Hospitalisations actuelles',
             "x": x,
             "y": yhosp,
             'type': 'scatter',
             'line': {'color':'royalblue'}
            }
        ],
        'layout': {
            #'height': 350,
            #'margin': {'l': 30, 'b': 30, 'r': 30, 't': 30},
            'title': {'text': title},
            'legend':{'traceorder': 'reversed'}
        }
    }


##################################
##################################
# Import french data
url_cases = 'https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/'
casescsvurl = BeautifulSoup(requests.get(url_cases).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[1].get('href')

FR = pd.read_csv(io.StringIO(requests.get(casescsvurl).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'hosp': int, 'rea': int, 'rad': int, 'dc': int})

# Import french geojson data
with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
  departments = json.load(response)

# Wrangle the data
animation_shot = FR[FR.sexe==0].groupby(['dep','jour']).sum().reset_index()

single_shot = FR[FR.jour==FR.jour.iloc[-1]][FR[FR.jour==FR.jour.iloc[-1]].sexe==0].groupby('dep').sum().reset_index()

# Make map
fig_map = go.Figure(go.Choroplethmapbox(geojson=departments, locations=single_shot.dep, z=single_shot.rea,
                                    colorscale="Reds",
                                    featureidkey="properties.code",
                                    customdata=np.array(single_shot[['dep', 'hosp']]),
                                    colorbar={'title':{'text':'# ICU'}},
                                    hovertemplate =
                                        "Rea: %{z}<br>" +
                                        "Hosp: %{customdata[1]}<br>" +
                                        "<extra><b>Departement: %{customdata[0]} </b><br><br></extra>",
                                    marker_opacity=0.5, marker_line_width=0))
fig_map.update_layout(mapbox_style="carto-darkmatter",
                  mapbox_zoom=4, mapbox_center = {"lat": 46.372103, "lon": 1.677944})
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

dd = FR[FR.sexe==0].groupby('jour').sum().reset_index()
fig_fr = create_time_series2(dd.jour.values, dd.rea.values, dd.rad.values, dd.dc.values, dd.hosp.values, '<b>Total pour la France</b>')

##################################
##################################


nav = Navbar()

header = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    'COVID-19 in France',
                    style= {
                        'textAlign': 'center',
                        "background": "lightblue"
                    }
                )
            )
        )
    ]
)

map = html.Div(
    [
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='map_france',
                    figure=fig_map,
                    clickData={'points': [{'location': '01'}]}
                )
            )
        )
    ]
)

doubleplots = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            id='france-time-series',
                            figure=fig_fr)]),
                    width=12,
                    lg=6
                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(id='dep-time-series')]),
                    width=12,
                    lg=6
                )
            ]
        )
    ]
)

def App():
    layout = html.Div([
        nav,
        header,
        map,
        doubleplots
    ])
    return layout


