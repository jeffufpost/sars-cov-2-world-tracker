# Data
import pandas as pd
import numpy as np
import datetime
import math
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

##################################
##################################
# With this:

# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

#Import deaths data
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

# Import recovery data
rec_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

#iso_alpha = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/iso_alpha.csv', index_col=0, header=0).T.iloc[0]
iso_alpha = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/iso_alpha.csv', index_col=0, header=0)

# Wrangle the data

#print("Wrangling data by country.......")
# Consolidate countries (ie. frenc dom tom are included in France, etc..)
conf_df = conf_df.groupby("Country/Region")
conf_df = conf_df.sum().reset_index()
conf_df = conf_df.set_index('Country/Region')

deaths_df = deaths_df.groupby("Country/Region")
deaths_df = deaths_df.sum().reset_index()
deaths_df = deaths_df.set_index('Country/Region')

rec_df = rec_df.groupby("Country/Region")
rec_df = rec_df.sum().reset_index()
rec_df = rec_df.set_index('Country/Region')

# Remove Lat and Long columns
conf_df = conf_df.iloc[:,2:]
deaths_df = deaths_df.iloc[:,2:]
rec_df = rec_df.iloc[:,2:]

# Convert country names to correct format for search with pycountry
conf_df = conf_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})
# Convert country names to correct format for search with pycountry
deaths_df = deaths_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})
# Convert country names to correct format for search with pycountry
rec_df = rec_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

# Convert dates to datime format
conf_df.columns = pd.to_datetime(conf_df.columns).date
deaths_df.columns = pd.to_datetime(deaths_df.columns).date
rec_df.columns = pd.to_datetime(rec_df.columns).date

# Create a per day dataframe
#print("Creating new per day dataframes......")
# Create per day dataframes for cases, deaths, and recoveries - by pd.DatafRame.diff
conf_df_pd = conf_df.diff(axis=1)
deaths_df_pd = deaths_df.diff(axis=1)
rec_df_pd = rec_df.diff(axis=1)

#print("Create infected dataframe = conf - deaths - recoveries")
inf_df = conf_df - deaths_df - rec_df

#print("Adding dataframes of 1st, 2nd, and 3rd derivatives of number of infected")
firstdev = inf_df.apply(np.gradient, axis=1)
seconddev = firstdev.apply(np.gradient)
thirddev = seconddev.apply(np.gradient)

# Another one to display customdata on hover of the map
conf = pd.DataFrame(conf_df.stack())
conf.rename(columns={0: 'Conf'}, inplace=True)
deaths = pd.DataFrame(deaths_df.stack())
deaths.rename(columns={0: 'Deaths'}, inplace=True)
rec = pd.DataFrame(rec_df.stack())
rec.rename(columns={0:'Recovered'}, inplace=True)
aa = conf.join(deaths.join(rec))
bb = aa.join(iso_alpha).reset_index()
cc = bb[bb.level_1 == bb.level_1.iloc[-1]].reset_index(drop=True)
dd  = cc[~cc.region.isna()].set_index('alpha-3')
dd['Active'] = dd.Conf-dd.Deaths-dd.Recovered

#print("Create series of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet
fda100 = conf_df[conf_df > 100].apply(pd.Series.first_valid_index, axis=1)

# Create dataframe for probability plot
probevent = iso_alpha.join(inf_df)
probevent['prev'] = probevent.iloc[:,-1] / probevent['SP.POP.TOTL']

# Create map
fig_map = go.Figure(
    data=go.Choropleth(
        locations=iso_alpha[~iso_alpha.region.isna()]['alpha-3'],
        z = probevent[~probevent.region.isna()]['prev'],
        locationmode = 'ISO-3',
        colorscale = 'Reds',
        colorbar_title = "Prevalence",        
        customdata=np.array(dd[['Country/Region', 'Conf', 'Deaths', 'Recovered', 'Active']]),
        hovertemplate = 
            "<b>Active:</b> %{customdata[4]}<br>" +
            "<b>Deaths:</b> %{customdata[2]}<br>" +
            "<b>Recoveries:</b> %{customdata[3]}<br>" +
            "<extra><b>%{customdata[0]}</b><br><b>Total cases: </b>%{customdata[1]}<br></extra>",
    ))



fig_map.update_layout(
    title= {
        'text': 'Click on country of interest',
        'x':0.5,
        'y':0.85
    },
    geo_scope='world',
    annotations = [dict(
        x=0.50,
        y=0.1,
        xref='paper',
        yref='paper',
        text='Source: <a href="https://github.com/CSSEGISandData/COVID-19">John Hopkins University CSSE</a>',
        showarrow = False
    )]
)


##################################
##################################

nav = Navbar()

header = html.H2(
    'COVID-19 around the world',
    style= {
        'textAlign': 'center',
        "background": "lightblue"
    }
)

map = html.Div([
    dcc.Graph(
        id='country-selector',
        figure=fig_map,
        clickData={'points': [{'location': 'FRA'}]}
    ),
], className="container")

doubleplots = html.Div([
    html.Div([
        dcc.Graph(id='country-bar-series')
    ], className="six columns"),
    html.Div([
        dcc.Graph(id='country-time-series')
    ], className="six columns"),
], className="row")

probplot = html.Div([
    dcc.Graph(id='prob-group-size'),
], className="container")


def Homepage():
    layout = html.Div([
    nav,
    header,
    map,
    doubleplots,
    probplot
    ])
    return layout

def create_prob_series(xi, yi, yi5, yi10, title):
    return {
        'data': [
            {'name': 'Probability curve given current active cases',
             "x": xi,
             "y": yi,
             'type': 'scatter',
             'line': {'color':'royalblue', 'width':3}
            },
            {'name': 'Probability curve if active cases are underestimated by a factor of 5',
             "x": xi,
             "y": yi5,
             'type': 'scatter',
             'line': {'color':'firebrick', 'width':2, 'dash':'dot'}
            },
            {'name': 'Probability curve if active cases are underestimated by a factor of 10',
             "x": xi,
             "y": yi10,
             'type': 'scatter',
             'line': {'color':'black', 'width':2, 'dash':'dot'}
            }
        ],
        'layout': {
            'title': {'text': title},
            'xaxis': {'title': {'text': "Group size"}, 'type': 'log'},
            'yaxis': {'title': {'text': "Chance of at least 1 active case being present"}, 'type': 'log'}
        }
    }



def create_time_series(xc, yc, xd, yd, xr, yr, xi, yi, title):
    return {
        'data': [
            {'name': 'Active',
             "x": xi,
             "y": yi,
             'type': 'scatter',
             'line': {'color':'firebrick'}
            },
            {'name': 'Recoveries',
             "x": xr,
             "y": yr,
             'type': 'scatter',
             'line': {'color':'green'}
            },
            {'name': 'Deaths',
             "x": xd,
             "y": yd,
             'type': 'scatter',
             'line': {'color':'black'}
            },
            {'name': 'Cases since start of epidemic',
             "x": xc,
             "y": yc,
             'type': 'scatter',
             'line': {'color':'royalblue', 'width':4, 'dash':'dot'}
            }
        ],
        'layout': {
            #'height': 350,
            #'margin': {'l': 30, 'b': 30, 'r': 30, 't': 30},
            'title': {'text': title},
            'legend':{'traceorder': 'reversed'},
            'updatemenus': [{
                'active': 1,
                'buttons': [
                    {'args': [
                        {'visible': [True, True]},
                        {'yaxis': {'type': 'log'}}
                    ],
                    'label': 'Log Scale',
                    'method': 'update'
                    },

                    {'args': [
                        {'visible': [True, True]},
                        {'yaxis': {'type': 'linear'}}
                    ],
                     'label': 'Linear Scale',
                     'method': 'update'}
                ],
                'direction': 'down',
                'pad': {'r': 10, 't': 10},
                'showactive': True,
                'x': 0.1,
                'xanchor': 'left',
                'y': 1.1,
                'yanchor': 'top'
            }]
        }
    }

def create_bar_series(xc, yc, xd, yd, xr, yr, title):
    return {
        'data': [
            {'name': 'Recoveries',
             "x": xr,
             "y": yr,
             'marker': {'color':'green'},
             'type': 'bar'},
            {'name': 'Deaths',
             "x": xd,
             "y": yd,
             'marker': {'color':'black'},
             'type': 'bar'},
            {'name': 'New cases',
             "x": xc,
             "y": yc,
             'marker': {'color':'firebrick'},
             'type': 'bar',
             'barmode': 'group',}
        ],
        'layout': {
            #'height': 350,
            #'margin': {'l': 30, 'b': 30, 'r': 30, 't': 30},
            'title': {'text': title},
            'legend':{'traceorder': 'reversed'}
        }
    }

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = Homepage()
if __name__ == "__main__":
    app.run_server()

