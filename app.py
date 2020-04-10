import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import math

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#server = app.server

conf_df = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/conf.csv', index_col=0)
conf_df_pd = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/conf_pd.csv', index_col=0)
deaths_df = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/deaths.csv', index_col=0)
deaths_df_pd = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/deaths_pd.csv', index_col=0)
rec_df = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/rec.csv', index_col=0)
rec_df_pd = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/rec_pd.csv', index_col=0)
inf_df = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/inf.csv', index_col=0)

firstdev = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/firstddev.csv', index_col=0, header=0).T.iloc[0]
seconddev = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/seconddev.csv', index_col=0, header=0).T.iloc[0]
thirddev = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/thirddev.csv', index_col=0, header=0).T.iloc[0]

fda100 = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/fda100.csv', index_col=0, header=0).T.iloc[0]

iso_alpha = pd.read_csv('https://raw.githubusercontent.com/jeffufpost/sars-cov-2-world-tracker/master/data/iso_alpha.csv', index_col=0, header=0).T.iloc[0]

fig_map = go.Figure(data=go.Choropleth(
    locations=iso_alpha, # Spatial coordinates
    z = conf_df[conf_df.columns[-1]], # Data to be color-coded (=last day in dataframe)
    locationmode = 'ISO-3', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Cases"
))

fig_map.update_layout(
    title_text = 'COVID Cases - click on country of interest',
    geo_scope='world'
)

app.layout = html.Div([
    html.H2('COVID-19 around the world - click the country of interest',
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
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20','margin': 'auto'}, className="container"),
    
    html.Div([
            html.Div([
                dcc.Graph(id='pd-time-series')
                ], className="six columns"),
            html.Div([
                dcc.Graph(id='total-time-series')
                ], className="six columns"),
            ], className="row")
])

def create_time_series(xc, yc, xd, yd, xr, yr, xi, yi, title):
    return {
        'data': [
            {'name': 'Recoveries',
             "x": xr,
             "y": yr,
             'type': 'line'
            },
            {'name': 'Deaths',
             "x": xd,
             "y": yd,
             'type': 'line'},
            {'name': 'Cases',
             "x": xc,
             "y": yc,
             'type': 'line'},
            {'name': 'Active',
             "x": xi,
             "y": yi,
             'type': 'line'}
        ],
        'layout': {
            #'height': 350,
            #'margin': {'l': 30, 'b': 30, 'r': 30, 't': 30},
            'title': {'text': title},
            'legend':{'traceorder': 'reversed'}
        }
    }

def create_bar_series(xc, yc, xd, yd, xr, yr, xi, yi, title):
    return {
        'data': [
            {'name': 'Recoveries',
             "x": xr,
             "y": yr,
             'type': 'bar'},
            {'name': 'Deaths',
             "x": xd,
             "y": yd,
             'type': 'bar'},
            {'name': 'Cases',
             "x": xc,
             "y": yc,
             'type': 'bar'},
            {'name': 'Active',
             "x": xi,
             "y": yi,
             'type': 'bar'}
        ],
        'layout': {
            'barmode': 'stack',
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
    country_name = iso_alpha[iso_alpha.values == country_iso].index[0]
    dffc = conf_df_pd[conf_df_pd.index == country_name]
    dffd = deaths_df_pd[deaths_df_pd.index == country_name]
    dffr = rec_df_pd[rec_df_pd.index == country_name]
    dffi = inf_df[inf_df.index==country_name].diff(axis=1)
    if type(fda100[country_name]) == str:
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
    return create_bar_series(xc, yc, xd, yd, xr, yr, xi, yi, title)

@app.callback(
    dash.dependencies.Output('total-time-series', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_total_timeseries(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = iso_alpha[iso_alpha.values == country_iso].index[0]
    dffc = conf_df[conf_df.index == country_name]
    dffd = deaths_df[deaths_df.index == country_name]
    dffr = rec_df[rec_df.index == country_name]
    dffi = inf_df[inf_df.index == country_name]
    if type(fda100[country_name]) == str:
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

if __name__ == '__main__':
    app.run_server(debug=True)
