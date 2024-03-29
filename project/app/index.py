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
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
# Navbar
from navbar import Navbar

from app import create_time_series2, create_bar_series2, create_time_series_vacs, create_bar_series_vacs
from homepage import create_bar_series, create_time_series, create_prob_series

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

app.config.suppress_callback_exceptions = True

server = app.server

###################################
#####   DATA    ###################
###################################
# With this:

# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

#Import deaths data
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

# Import recovery data
# Not reliable anymore, simply use shift of 14 days of cases minus the deaths to estimate
#rec_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

#iso_alpha = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/iso_alpha.csv', index_col=0, header=0).T.iloc[0]
iso_alpha = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/project/app/data/iso_alpha.csv', index_col=0, header=0)


# Wrangle the data

#print("Wrangling data by country.......")
# Consolidate countries (ie. frenc dom tom are included in France, etc..)
conf_df = conf_df.groupby("Country/Region")
conf_df = conf_df.sum().reset_index()
conf_df = conf_df.set_index('Country/Region')

deaths_df = deaths_df.groupby("Country/Region")
deaths_df = deaths_df.sum().reset_index()
deaths_df = deaths_df.set_index('Country/Region')

#rec_df = rec_df.groupby("Country/Region")
#rec_df = rec_df.sum().reset_index()
#rec_df = rec_df.set_index('Country/Region')

# Remove Lat and Long columns
conf_df = conf_df.iloc[:,2:]
deaths_df = deaths_df.iloc[:,2:]
#rec_df = rec_df.iloc[:,2:]

# Convert country names to correct format for search with pycountry
conf_df = conf_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})
# Convert country names to correct format for search with pycountry
deaths_df = deaths_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})
# Convert country names to correct format for search with pycountry
#rec_df = rec_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

# Convert dates to datime format
conf_df.columns = pd.to_datetime(conf_df.columns).date
deaths_df.columns = pd.to_datetime(deaths_df.columns).date
#rec_df.columns = pd.to_datetime(rec_df.columns).date

# Create a per day dataframe
#print("Creating new per day dataframes......")
# Create per day dataframes for cases, deaths, and recoveries - by pd.DatafRame.diff
#conf_df_pd = conf_df.diff(axis=1)
#deaths_df_pd = deaths_df.diff(axis=1)
#rec_df_pd = rec_df.diff(axis=1)

rec_df = conf_df.shift(periods=14, axis=1)-deaths_df#.shift(periods=-7, axis=1)
rec_df = rec_df#.fillna(0).astype(int)
#rec_df_pd = rec_df.diff(axis=1)

#print("Create infected dataframe = conf - deaths - recoveries")
inf_df = conf_df - deaths_df - rec_df

#print("Adding dataframes of 1st, 2nd, and 3rd derivatives of number of infected")
#firstdev = inf_df.apply(np.gradient, axis=1)
#seconddev = firstdev.apply(np.gradient)
#thirddev = seconddev.apply(np.gradient)

# Another one to display customdata on hover of the map
#conf = pd.DataFrame(conf_df.stack())
#conf.rename(columns={0: 'Conf'}, inplace=True)
#deaths = pd.DataFrame(deaths_df.stack())
#deaths.rename(columns={0: 'Deaths'}, inplace=True)
#rec = pd.DataFrame(rec_df.stack())
#rec.rename(columns={0:'Recovered'}, inplace=True)
#aa = conf.join(deaths.join(rec))
#bb = aa.join(iso_alpha).reset_index()
#cc = bb[bb.level_1 == bb.level_1.iloc[-1]].reset_index(drop=True)
#dd  = cc[~cc.region.isna()].set_index('alpha-3')
dd = pd.DataFrame({'Conf':conf_df.iloc[:,-1], 'Deaths':deaths_df.iloc[:,-1], 'Recovered':rec_df.iloc[:,-1]}).join(iso_alpha).reset_index() #.set_index('alpha-3')
dd = dd[~dd['region'].isna()].set_index('alpha-3')
dd['Active'] = dd.Conf-dd.Deaths-dd.Recovered
#ee = ee[ee.index.isin(iso_alpha['alpha-3'])]
#ee['Active'] = ee.Conf-ee.Deaths-ee.Recovered

#print("Create series_vacs of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet
fda100 = conf_df[conf_df > 100].apply(pd.Series.first_valid_index, axis=1)

# Create dataframe for probability plot
probevent = iso_alpha.join(inf_df)
probevent['prev'] = probevent.iloc[:,-1] / probevent['SP.POP.TOTL']
#probevent['prev'] = probevent.iloc[:,-8] / probevent['SP.POP.TOTL']

#del aa
#del bb
#del cc

#del inf_df
#del rec_df
#del rec
#del conf_df
#del conf
#del deaths_df
#del deaths

# Get world GeoJSON
#with urlopen('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson') as response:
#    countries_geojson = json.load(response)
countries_geojson = json.load(open('data/countries.geojson', 'r'))

##################################
##################################
# Import french data
#url_cases = 'https://legacy.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/'
#url_tests = 'https://legacy.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/'
#url_vaccines = 'https://legacy.data.gouv.fr/fr/datasets/donnees-relatives-aux-personnes-vaccinees-contre-la-covid-19-1/'

#casescsvurl = BeautifulSoup(requests.get(url_cases).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[3].get('href')
#casescsvurl2 = BeautifulSoup(requests.get(url_cases).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[5].get('href')
#testscsvurl_dep = BeautifulSoup(requests.get(url_tests).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[1].get('href')
#testscsvurl_nat = BeautifulSoup(requests.get(url_tests).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[5].get('href')
#vacscsvurl_dep = BeautifulSoup(requests.get(url_vaccines).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[35].get('href')
#vacscsvurl_nat = BeautifulSoup(requests.get(url_vaccines).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[31].get('href')
#vacscsvurl_dep = BeautifulSoup(requests.get(url_vaccines).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[19].get('href')
#vacscsvurl_nat = BeautifulSoup(requests.get(url_vaccines).text, "html.parser").find_all('a', class_="btn btn-sm btn-primary")[15].get('href')
vacscsvurl_dep = 'https://data.gouv.fr/fr/datasets/r/535f8686-d75d-43d9-94b3-da8cdf850634'
vacscsvurl_nat = 'https://data.gouv.fr/fr/datasets/r/b273cf3b-e9de-437c-af55-eda5979e92fc'
casescsvurl = 'https://data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7'
casescsvurl2 = 'https://data.gouv.fr/fr/datasets/r/6fadff46-9efd-4c53-942a-54aca783c30c'
#testscsvurl_dep = 'https://data.gouv.fr/fr/datasets/r/406c6a23-e283-4300-9484-54e78c8ae675'
testscsvurl_dep = 'https://www.data.gouv.fr/fr/datasets/r/674bddab-6d61-4e59-b0bd-0be535490db0'
testscsvurl_nat = 'https://data.gouv.fr/fr/datasets/r/dd0de5d9-b5a5-4503-930a-7b08dc0adc7c'

# get csv files
cases_daily = pd.read_csv(io.StringIO(requests.get(casescsvurl2).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'incid_hosp': int, 'incid_rea': int, 'incid_rad': int, 'incid_dc': int}, parse_dates = ['jour'])
cases_cum = pd.read_csv(io.StringIO(requests.get(casescsvurl).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'hosp': int, 'rea': int, 'rad': int, 'dc': int}, parse_dates = ['jour'])
#tests_nat = pd.read_csv(io.StringIO(requests.get(testscsvurl_nat).content.decode('utf-8')), sep=';', dtype={'fra': str, 'jour': str, 'cl_age90': int, 'P_f': int, 'P_h': int, 'P': int, 'T_f': int, 'T_h': int, 'T': int}, parse_dates = ['jour'])
tests_dep = pd.read_csv(io.StringIO(requests.get(testscsvurl_dep).content.decode('utf-8')), sep=';', dtype={'dep': str, 'jour': str, 'cl_age90': int, 'P': float, 'T': float}, decimal=',', parse_dates = ['jour'])

#tests_dep.P.replace(',','.', inplace=True)
#tests_dep.T.replace(',','.', inplace=True)

tests_dep['P'] = tests_dep['P'].astype(int)
tests_dep['T'] = tests_dep['T'].astype(int)

# change in May to reflect change of dataframe from legacy.data.gouv.fr
vacs_dep = pd.read_csv(io.StringIO(requests.get(vacscsvurl_dep).content.decode('utf-8')), sep=';', dtype={'dep': str, 'vaccin': int, 'jour': str, 'n_dose1': int, 'n_dose2': int, 'n_dose3': int, 'n_dose4': int, 'n_cum_dose1': int, 'n_cum_dose2': int, 'n_cum_dose3': int, 'n_cum_dose4': int}, parse_dates = ['jour'])
#vacs_nat = pd.read_csv(io.StringIO(requests.get(vacscsvurl_nat).content.decode('utf-8')), sep=';', dtype={'fra': str, 'vaccin': int, 'jour': str, 'n_dose1': int, 'n_dose2': int, 'n_dose3': int, 'n_dose4': int, 'n_cum_dose1': int, 'n_cum_dose2': int, 'n_cum_dose3': int, 'n_cum_dose4': int}, parse_dates = ['jour']).drop(columns=['fra'])

cases_cum = cases_cum[cases_cum.sexe==0]
#tests_dep = tests_dep[tests_dep['cl_age90']==0]
tests_dep = tests_dep.groupby(['dep','jour']).sum().reset_index()  #use this instead as cl_age90 == 0 does not exist anymore, need to sum all others


### Delete data
#del url_cases
#del url_vaccines
#del url_tests
#del casescsvurl
#del casescsvurl2
#del testscsvurl_dep
#del testscsvurl_nat
#del vacscsvurl_dep
#del vacscsvurl_nat

# Add numer of ICU beds
lits=pd.read_csv('data/lits.csv', sep=',', dtype={'dep': str, 'num1': int, 'num2': int})
lits['num']=lits['num1']+lits['num2']

#FR=FR[FR.sexe==0]  #remove gender distinction

cases_cum=cases_cum.join(lits.set_index('dep'), on='dep')
cases_cum=cases_cum[cases_cum.dep.isin(lits.dep)]

#del lits

# Import french geojson data
#with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
#with urlopen('https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson') as response:
#    dep_geojson = json.load(response)
dep_geojson = json.load(open('data/departements.geojson', 'r'))

# Wrangle the data
#animation_shot = FR[FR.sexe==0].groupby(['dep','jour']).sum().reset_index()
#animation_shot = pd.merge(animation_shot, vacs_dep, how='outer',on=['dep', 'jour']).fillna(0)

#single_shot = FR[FR.jour==FR.jour.iloc[-1]][FR[FR.jour==FR.jour.iloc[-1]].sexe==0].groupby('dep').sum().reset_index()

## Change colors to hospitalization rate since last week:
#def get_hosp_rate(i):
#  return (animation_shot[animation_shot.dep==i][animation_shot[animation_shot.dep==i].jour==animation_shot.jour.iloc[-1]].hosp.values[0]+1)/(animation_shot[animation_shot.dep==i][animation_shot[animation_shot.dep==i].jour==animation_shot.jour.iloc[-15]].hosp.values[0]+1)

#def hosp_to_max(i):
#  return animation_shot[animation_shot.dep==i][animation_shot[animation_shot.dep==i].jour==animation_shot.jour.iloc[-1]].hosp.values[0]/animation_shot[animation_shot.dep==i].hosp.max()

#single_shot['hosp_to_max']=single_shot.dep.apply(lambda x: hosp_to_max(x))

#single_shot['Hosp_rate']=single_shot.dep.apply(lambda x: get_hosp_rate(x))

single_shot=cases_cum[cases_cum.jour==cases_cum.jour.max()].copy()
single_shot['cap']=100*single_shot.rea/(single_shot.num+1)
single_shot['cap']=single_shot['cap'].astype(int)

#single_shot['pot']=(0.1*single_shot['hosp']+single_shot['rea'])/(single_shot.num+1)

# NAtional data
cases_cum_fr=cases_cum.groupby('jour').sum().reset_index()
cases_daily_fr=cases_daily.groupby('jour').sum().reset_index()
tests_fr=tests_dep.groupby(['jour']).sum().reset_index()
vacs_fr=vacs_dep.groupby(['jour', 'vaccin']).sum().reset_index()


#single_shot['color']=np.log(single_shot['Hosp_rate']*single_shot['pot']*single_shot['pot'])
#single_shot['color']=single_shot.cap #/(single_shot.num+1)

# Make french map
fig_map_FR = go.Figure(go.Choroplethmapbox(geojson=dep_geojson, 
                                    locations=single_shot.dep, 
                                    z=single_shot.cap,
                                    zmin=0,
                                    zmax=100,
                                    colorscale="Reds",
                                    featureidkey="properties.code",
                                    customdata=np.array(single_shot[['dep', 'hosp', 'rea', 'cap']]),
                                    colorbar={'title':{'text':'Occupation Réa'}},
                                    hovertemplate =
                                        "Rea: %{customdata[2]} (%{customdata[3]}%)<br>" +
                                        "Hosp: %{customdata[1]}<br>" +
                                        "<extra><b>Departement: %{customdata[0]} </b><br><br></extra>",
                                    marker_opacity=0.5, marker_line_width=0))
fig_map_FR.update_layout(mapbox_style="carto-darkmatter",
                  mapbox_zoom=4, mapbox_center = {"lat": 46.372103, "lon": 1.677944})
fig_map_FR.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


#ddd = FR[FR.sexe==0].groupby('jour').sum().reset_index()

#del FR

#ddd = pd.merge(ddd, vacs_nat, how='outer',on=['jour']).fillna(0)


#dfdbs = pd.merge(cases, tests_dep[tests_dep.cl_age90==0].reset_index(drop=True), how='outer',on=['dep', 'jour']).fillna(0)

#del cases
#del tests_dep

#dfdbs = pd.merge(dfdbs, vacs_dep, how='outer',on=['dep', 'jour']).fillna(0)
#dd2 = dfdbs.groupby(['jour']).sum()
bar_dep = pd.merge(cases_daily, tests_dep, how='outer',on=['dep','jour']).fillna(0)
bar_fr = pd.merge(cases_daily_fr, tests_fr, how='outer',on=['jour']).fillna(0)

#dfdbs = dfdbs[dfdbs.cl_age90==0].groupby(['dep','jour']).sum()
#del dfdbs

#fig_fr = create_time_series2(ddd.jour, ddd.rea.values, ddd.rad.values, ddd.dc.values, ddd.hosp.values, ddd.num1.values, ddd.num.values, '<b>Total pour la France</b>')
fig_fr = create_time_series2(cases_cum_fr.jour, cases_cum_fr.rea.values, cases_cum_fr.rad.values, cases_cum_fr.dc.values, cases_cum_fr.hosp.values, cases_cum_fr.num1.values, cases_cum_fr.num.values, '<b>Total pour la France</b>')

#del ddd

fig_fr_bar = create_bar_series2(bar_fr.jour, bar_fr['P'].values, bar_fr['incid_dc'].values, bar_fr['incid_rad'].values, bar_fr['T'].values, bar_fr['incid_hosp'].values, bar_fr['incid_rea'].values, '<b>Total pour la France</b>')

#del dd2

fig_fr_vacs = create_bar_series_vacs(
    vacs_fr.jour,
    vacs_fr[vacs_fr.vaccin==1].n_dose1.values,
    vacs_fr[vacs_fr.vaccin==1].n_dose2.values,
    vacs_fr[vacs_fr.vaccin==2].n_dose1.values,
    vacs_fr[vacs_fr.vaccin==2].n_dose2.values,
    vacs_fr[vacs_fr.vaccin==3].n_dose1.values,
    vacs_fr[vacs_fr.vaccin==3].n_dose2.values,
    vacs_fr[vacs_fr.vaccin==4].n_dose1.values,
    vacs_fr[vacs_fr.vaccin==4].n_dose2.values,
    title = '<b>Vaccinations en France</b>')

#del vacs_nat
    

# Create map
fig_map_WD = go.Figure(
    data=go.Choroplethmapbox(
        geojson=countries_geojson,
        locations=iso_alpha[~iso_alpha.region.isna()]['alpha-3'],
        z=probevent[~probevent.region.isna()]['prev']*100000,
        colorscale="Reds",
        zmin=0,
        zmax=600,
        featureidkey="properties.adm0_a3",
        colorbar={'title':{'text':'Active/100k'}},
        customdata=np.array(dd[['Country/Region', 'Conf', 'Deaths', 'Recovered', 'Active']]),
        hovertemplate =
            "<b>Active cases:</b> %{customdata[4]}<br>" +
            "<b>Deaths:</b> %{customdata[2]}<br>" +
            "<b>Recoveries:</b> %{customdata[3]}<br>" +
            "<extra><b>%{customdata[0]}</b><br><b>Total cases: </b>%{customdata[1]}<br></extra>",
        marker_opacity=1, marker_line_width=2))
fig_map_WD.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=2, mapbox_center = {"lat": 46.372103, "lon": 1.677944})
fig_map_WD.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#del countries_geojson
#del dep_geojson

##################################
##################################

nav = Navbar()

header_FR = html.Div(
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

map_FR = html.Div(
    [
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='map_france',
                    figure=fig_map_FR,
                    clickData={'points': [{'location': '01'}]}
                )
            )
        )
    ]
)

doubleplots_time = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div([dcc.Graph(id='dep-time-series')]),width=12,lg=6),
                dbc.Col(html.Div([dcc.Graph(id='france-time-series',figure=fig_fr)]),width=12,lg=6)])
    ]
)

doubleplots_vacs = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div([dcc.Graph(id='dep-bar-series_vacs_dep')]),width=12,lg=6),
                dbc.Col(html.Div([dcc.Graph(id='dep-bar-series_vacs_nat', figure=fig_fr_vacs)]),width=12,lg=6)])
    ]
)

doubleplots_bar = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(html.Div([dcc.Graph(id='dep-bar-series')]),width=12,lg=6),
                dbc.Col(html.Div([dcc.Graph(id='france-bar-series', figure=fig_fr_bar)]),width=12,lg=6)])
    ]
)

def App():
    layoutapp = html.Div([
        nav,
        header_FR,
        map_FR,
        doubleplots_time,
        doubleplots_vacs,
        doubleplots_bar
    ])
    return layoutapp


header_WD = html.Div(
    [
        dbc.Row(
            dbc.Col(
                html.H2(
                    'COVID-19 around the World',
                    style= {
                        'textAlign': 'center',
                        "background": "lightblue"
                    }
                )
            )
        )
    ]
)

map_WD = html.Div(
    [
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='country-selector',
                    figure=fig_map_WD,
                    clickData={'points': [{'location': 'FRA'}]}
                )
            )
        )
    ]
)


doubleplots_WD = html.Div(
    [
        dbc.Row(
            [
                dbc.Col([dcc.Graph(id='country-time-series_vacs')], width=12, lg=6),
                dbc.Col([dcc.Graph(id='country-bar-series_vacs')], width=12, lg=6),
            ]
        )
    ]
)

probplot = html.Div(
    [
        dbc.Row(dbc.Col(dcc.Graph(id='prob-group-size')))
    ]
)

def Homepage():
    layouthome = html.Div([
    nav,
    header_WD,
    map_WD,
    doubleplots_WD,
    probplot
    ])
    return layouthome

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = True),
    html.Div(id = 'page-content')
])

@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/france':
        try:
            del fig_map_WD
        except UnboundLocalError:
            pass
        return App()
    else:
        try:
            del fig_map_FR
        except UnboundLocalError:
            pass        
        try:
            del fig_fr_vacs
        except UnboundLocalError:
            pass
        try:
            del fig_fr
        except UnboundLocalError:
            pass
        try:
            del fig_fr_bar
        except UnboundLocalError:
            pass
        return Homepage()

@app.callback(
    dash.dependencies.Output('country-bar-series_vacs', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_pd_timeseries(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = iso_alpha['alpha-3'][iso_alpha['alpha-3'].values == country_iso].index[0]
    dffc = conf_df.diff(axis=1)[conf_df.diff(axis=1).index == country_name]
    dffd = deaths_df.diff(axis=1)[deaths_df.diff(axis=1).index == country_name]
    dffr = rec_df.diff(axis=1)[rec_df.diff(axis=1).index == country_name]
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
    dash.dependencies.Output('country-time-series_vacs', 'figure'),
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
    dfdts = cases_cum[cases_cum.dep==departement]
    x = dfdts.jour
    yrea  = dfdts.rea.values
    yrad  = dfdts.rad.values
    ydc   = dfdts.dc.values
    yhosp = dfdts.hosp.values
    ynum1  = dfdts.num1.values
    ynum  = dfdts.num.values
    title = '<b>Departement du {}</b>'.format(departement)
    return create_time_series2(x, yrea, yrad, ydc, yhosp, ynum1, ynum, title)

@app.callback(
    dash.dependencies.Output('dep-bar-series', 'figure'),
    [dash.dependencies.Input('map_france', 'clickData')]
)
def update_total_barseries(clickData):
    departement = clickData['points'][0]['location']
    #dfdbs2 = dfdbs[dfdbs.dep == departement]
    #dfdbs2 = dfdbs.loc[[departement]]
    #dfdbs2 = dfdbs2.fillna(0)
    #dfdbs2 = dfdbs2[dfdbs2.cl_age90==0].groupby(['jour']).sum()
    dfdbs = bar_dep[bar_dep.dep==departement]
    x = dfdbs.jour
    yc = dfdbs['P'].values
    yd = dfdbs['incid_dc'].values
    yr = dfdbs['incid_rad'].values
    yt = dfdbs['T'].values
    yh = dfdbs['incid_hosp'].values
    yicu = dfdbs['incid_rea'].values
    title = '<b>Departement du {}</b>'.format(departement)
    return create_bar_series2(x, yc, yd, yr, yt, yh, yicu, title)

@app.callback(
    dash.dependencies.Output('dep-time-series_vacs', 'figure'),
    [dash.dependencies.Input('map_france', 'clickData')]
)
def update_total_timeseries(clickData):
    departement = clickData['points'][0]['location']
    dfdts = vacs_dep[vacs_dep.dep==departement]
    x = dfdts.jour
    yrea  = dfdts.rea.values
    yrad  = dfdts.rad.values
    ydc   = dfdts.dc.values
    yhosp = dfdts.hosp.values
    ynum1  = dfdts.num1.values
    ynum  = dfdts.num.values
    title = '<b>Departement du {}</b>'.format(departement)
    return create_time_series2(x, yrea, yrad, ydc, yhosp, ynum1, ynum, title)

@app.callback(
    dash.dependencies.Output('dep-bar-series_vacs_dep', 'figure'),
    [dash.dependencies.Input('map_france', 'clickData')]
)
def update_total_timeseries(clickData):
    departement = clickData['points'][0]['location']
    dfdtsv = vacs_dep[vacs_dep.dep == departement]
    x = dfdtsv.jour
    y10 = dfdtsv[dfdtsv.vaccin==1].n_dose1.values
    y11 = dfdtsv[dfdtsv.vaccin==1].n_dose2.values
    y20 = dfdtsv[dfdtsv.vaccin==2].n_dose1.values
    y21 = dfdtsv[dfdtsv.vaccin==2].n_dose2.values
    y30 = dfdtsv[dfdtsv.vaccin==3].n_dose1.values
    y31 = dfdtsv[dfdtsv.vaccin==3].n_dose2.values
    y40 = dfdtsv[dfdtsv.vaccin==4].n_dose1.values
    y41 = dfdtsv[dfdtsv.vaccin==4].n_dose2.values
    title = '<b>Vaccinations dans le {}</b>'.format(departement)
    return create_bar_series_vacs(x, y10, y11, y20, y21, y30, y31, y40, y41, title)

#if __name__ == '__main__':
#    app.run_server(debug=True)
