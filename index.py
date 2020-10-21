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

from app import App, create_time_series2, create_bar_series2
from homepage import Homepage, create_bar_series, create_time_series, create_prob_series

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

app.config.suppress_callback_exceptions = True

server = app.server

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

# Get world GeoJSON
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
  countries = json.load(response)

##################################
##################################
# Import french data
url_cases = 'https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/'
url_tests = 'https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/'

casescsvurl = BeautifulSoup(requests.get(url_cases).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[1].get('href')
casescsvurl2 = BeautifulSoup(requests.get(url_cases).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[3].get('href')
testscsvurl_dep = BeautifulSoup(requests.get(url_tests).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[1].get('href')
testscsvurl_nat = BeautifulSoup(requests.get(url_tests).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[5].get('href')

# get csv files
cases = pd.read_csv(io.StringIO(requests.get(casescsvurl2).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'incid_hosp': int, 'incid_rea': int, 'incid_rad': int, 'incid_dc': int}, parse_dates = ['jour'])
tests_nat = pd.read_csv(io.StringIO(requests.get(testscsvurl_nat).content.decode('utf-8')), sep=';', dtype={'fra': str, 'jour': str, 'cl_age90': int, 'P_f': int, 'P_h': int, 'P': int, 'T_f': int, 'T_h': int, 'T': int}, parse_dates = ['jour'])
tests_dep = pd.read_csv(io.StringIO(requests.get(testscsvurl_dep).content.decode('utf-8')), sep=';', dtype={'de': str, 'jour': str, 'cl_age90': int, 'P': int, 'T': int}, parse_dates = ['jour'])
FR = pd.read_csv(io.StringIO(requests.get(casescsvurl).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'hosp': int, 'rea': int, 'rad': int, 'dc': int}, parse_dates = ['jour'])

# Wrangle the data
animation_shot = FR[FR.sexe==0].groupby(['dep','jour']).sum().reset_index()

single_shot = FR[FR.jour==FR.jour.iloc[-1]][FR[FR.jour==FR.jour.iloc[-1]].sexe==0].groupby('dep').sum().reset_index()

dfdbs=pd.merge(cases, tests_dep[tests_dep.cl_age90==0].reset_index(drop=True), how='outer',on=['dep', 'jour'])


app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/france':
        return App()
    else:
        return Homepage()

@app.callback(
    dash.dependencies.Output('country-bar-series', 'figure'),
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
    dash.dependencies.Output('country-time-series', 'figure'),
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

@app.callback(
    dash.dependencies.Output('dep-time-series', 'figure'),
    [dash.dependencies.Input('map_france', 'clickData')]
)
def update_total_timeseries(clickData):
    departement = clickData['points'][0]['location']
    dfdts = animation_shot[animation_shot.dep==departement]
    x = dfdts.jour
    yrea  = dfdts.rea.values
    yrad  = dfdts.rad.values
    ydc   = dfdts.dc.values
    yhosp = dfdts.hosp.values
    title = '<b>Departement du {}</b>'.format(departement)
    return create_time_series2(x, yrea, yrad, ydc, yhosp, title)

@app.callback(
    dash.dependencies.Output('dep-bar-series', 'figure'),
    [dash.dependencies.Input('map_france', 'clickData')]
)
def update_total_barseries(clickData):
    departement = clickData['points'][0]['location']
    dfdbs2 = dfdbs[dfdbs.dep == departement]
    dfdbs2=dfdbs2.fillna(0)
    dfdbs2 = dfdbs2[dfdbs2.cl_age90==0].groupby(['jour']).sum()

    x = dfdbs2.index
    yc = dfdbs2.P.values
    yd = dfdbs2.incid_dc.values
    yr = dfdbs2.incid_rad.values
    yt = dfdbs2['T'].values
    yh = dfdbs2.incid_hosp.values
    yicu = dfdbs2.incid_rea.values
    title = '<b>Departement du {}</b>'.format(departement)
    return create_bar_series2(x, yc, yd, yr, yt, yh, yicu, title)

if __name__ == '__main__':
    app.run_server(debug=True)
