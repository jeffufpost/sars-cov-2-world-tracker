## Dash app (https://dash.plot.ly/getting-started)

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

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

#print("Create series of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet
fda100 = conf_df[conf_df > 100].apply(pd.Series.first_valid_index, axis=1)

# Create dataframe for probability plot
probevent = iso_alpha.join(inf_df)
probevent['prev'] = probevent.iloc[:,-1] / probevent['SP.POP.TOTL']

fig_map = go.Figure(data=go.Choropleth(
    locations=iso_alpha['alpha-3'], # Spatial coordinates
    z = conf_df[conf_df.columns[-1]], # Data to be color-coded (=last day in dataframe)
    locationmode = 'ISO-3', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Cases"
))

fig_map.update_layout(
    title_text = 'World map - Click on country of interest',
    geo_scope='world'
)

app.layout = html.Div([
    html.H2('COVID-19 around the world',
            style={
                'textAlign': 'center',
                "background": "lightblue"
            }),
    html.Div([
        dcc.Graph(
            id='country-selector',
            figure=fig_map,
            clickData={'points': [{'location': 'FRA'}]}
        ),
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20','margin': 'auto'}, className="one columns"),

    html.Div([
            html.Div([
                dcc.Graph(id='pd-time-series')
                ], className="six columns"),
            html.Div([
                dcc.Graph(id='total-time-series')
                ], className="six columns"),
            ], className="row"),

    html.Div([
        dcc.Graph(
            id='prob-group-size'
        ),
    ], style={'width': '80%', 'display': 'inline-block', 'padding': '0 20','margin': 'auto'}, className="one columns")

])


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

@app.callback(
    dash.dependencies.Output('pd-time-series', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_pd_timeseries(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = iso_alpha['alpha-3'][iso_alpha['alpha-3'].values == country_iso].index[0]
    dffc = conf_df_pd[conf_df_pd.index == country_name]
    dffd = deaths_df_pd[deaths_df_pd.index == country_name]
    dffr = rec_df_pd[rec_df_pd.index == country_name]
    dffi = inf_df[inf_df.index==country_name].diff(axis=1)
    if type(fda100[country_name]) == datetime.date:
        xc = pd.Series(dffc.T[fda100[country_name]:].index.T)
        yc = pd.Series(dffc.T[fda100[country_name]:].values.T[0])
        xd = pd.Series(dffd.T[fda100[country_name]:].index.T)
        yd = pd.Series(dffd.T[fda100[country_name]:].values.T[0])
        xr = pd.Series(dffr.T[fda100[country_name]:].index.T)
        yr = pd.Series(dffr.T[fda100[country_name]:].values.T[0])
        xi = pd.Series(dffi.T[fda100[country_name]:].index.T)
        yi = pd.Series(dffi.T[fda100[country_name]:].values.T[0])
        title = '<b>{}</b><br>Daily numbers since {}'.format(country_name, fda100[country_name])
    else:
        xc = pd.Series(dffc.T.index.T)
        yc = pd.Series(dffc.values[0].T)
        xd = pd.Series(dffd.T.index.T)
        yd = pd.Series(dffd.values[0].T)
        xr = pd.Series(dffr.T.index.T)
        yr = pd.Series(dffr.values[0].T)
        xi = pd.Series(dffi.T.index.T)
        yi = pd.Series(dffi.values[0].T)
        title = '<b>{}</b><br>Daily numbers (since Jan 22nd, 2020 - still less than 100 confirmed cases)'.format(country_name)
    return create_bar_series(xc, yc, xd, yd, xr, yr, title)

@app.callback(
    dash.dependencies.Output('total-time-series', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_total_timeseries(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = iso_alpha['alpha-3'][iso_alpha['alpha-3'].values == country_iso].index[0]
    dffc = conf_df[conf_df.index == country_name]
    dffd = deaths_df[deaths_df.index == country_name]
    dffr = rec_df[rec_df.index == country_name]
    dffi = inf_df[inf_df.index == country_name]
    if type(fda100[country_name]) == datetime.date:
        xc = pd.Series(dffc.T[fda100[country_name]:].index.T)
        yc = pd.Series(dffc.T[fda100[country_name]:].values.T[0])
        xd = pd.Series(dffd.T[fda100[country_name]:].index.T)
        yd = pd.Series(dffd.T[fda100[country_name]:].values.T[0])
        xr = pd.Series(dffr.T[fda100[country_name]:].index.T)
        yr = pd.Series(dffr.T[fda100[country_name]:].values.T[0])
        xi = pd.Series(dffi.T[fda100[country_name]:].index.T)
        yi = pd.Series(dffi.T[fda100[country_name]:].values.T[0])
        title = '<b>{}</b><br>Total numbers since {}'.format(country_name, fda100[country_name])
    else:
        xc = pd.Series(dffc.T.index.T)
        yc = pd.Series(dffc.values[0].T)
        xd = pd.Series(dffd.T.index.T)
        yd = pd.Series(dffd.values[0].T)
        xr = pd.Series(dffr.T.index.T)
        yr = pd.Series(dffr.values[0].T)
        xi = pd.Series(dffi.T.index.T)
        yi = pd.Series(dffi.values[0].T)
        title = '<b>{}</b><br>Total numbers (since Jan 22nd, 2020 - still less than 100 confirmed cases)'.format(country_name)
    return create_time_series(xc, yc, xd, yd, xr, yr, xi, yi, title)

@app.callback(
    dash.dependencies.Output('prob-group-size', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_prob_group_size(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = iso_alpha['alpha-3'][iso_alpha['alpha-3'].values == country_iso].index[0]
    xi = np.arange(10000)
    yi = 100 * (1 - (1 - probevent.loc[country_name].prev) ** np.arange(10000))
    yi5 = 100 * (1 - (1 - 5*probevent.loc[country_name].prev) ** np.arange(10000))
    yi10 = 100 * (1 - (1 - 10*probevent.loc[country_name].prev) ** np.arange(10000))
    title = '<b>{}</b><br>Probability of having at least 1 infected person at a gathering depending on group size'.format(country_name)
    return create_prob_series(xi, yi, yi5, yi10, title)

if __name__ == '__main__':
    app.run_server(debug=True)

