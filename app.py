import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

conf_df = pd.read_csv('data/conf.csv', index_col=0)
conf_df_pd = pd.read_csv('data/conf_pd.csv', index_col=0)
deaths_df = pd.read_csv('data/deaths.csv', index_col=0)
deaths_df_pd = pd.read_csv('data/deaths_pd.csv', index_col=0)
rec_df = pd.read_csv('data/rec.csv', index_col=0)
rec_df_pd = pd.read_csv('data/rec_pd.csv', index_col=0)

fig_map = go.Figure(data=go.Choropleth(
    locations=conf_df['iso_alpha'], # Spatial coordinates
    z = conf_df[conf_df.columns[-3]], # Data to be color-coded (=last day in dataframe)
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

def create_time_series(xc, yc, xd, yd, xr, yr, title):
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
             'type': 'line'}
        ],
        'layout': {
            #'height': 350,
            #'margin': {'l': 30, 'b': 30, 'r': 30, 't': 30},
            'title': {'text': title},
            'legend':{'traceorder': 'reversed'}
        }
    }

def create_bar_series(xc, yc, xd, yd, xr, yr, title):
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
    country_name = conf_df_pd[conf_df_pd.iso_alpha == country_iso].index[0]
    dffc = conf_df_pd[conf_df_pd.iso_alpha == country_iso]
    dffd = deaths_df_pd[deaths_df_pd.iso_alpha == country_iso]
    dffr = rec_df_pd[rec_df_pd.iso_alpha == country_iso]
    xc = pd.Series(range(len(dffc.loc[country_name,dffc['Firstdayabove100df'].loc[country_name]:dffc.columns[-3]].index)))
    yc = pd.Series(dffc.loc[country_name,dffc['Firstdayabove100df'].loc[country_name]:dffc.columns[-3]].values)
    xd = pd.Series(range(len(dffd.loc[country_name,dffd['Firstdayabove100df'].loc[country_name]:dffd.columns[-3]].index)))
    yd = pd.Series(dffd.loc[country_name,dffd['Firstdayabove100df'].loc[country_name]:dffd.columns[-3]].values)
    xr = pd.Series(range(len(dffr.loc[country_name,dffr['Firstdayabove100df'].loc[country_name]:dffr.columns[-3]].index)))
    yr = pd.Series(dffr.loc[country_name,dffr['Firstdayabove100df'].loc[country_name]:dffr.columns[-3]].values)
    title = '<b>{}</b><br>Daily numbers (days since 100 confirmed cases)'.format(country_name)
    return create_bar_series(xc, yc, xd, yd, xr, yr, title)

@app.callback(
    dash.dependencies.Output('total-time-series', 'figure'),
    [dash.dependencies.Input('country-selector', 'clickData')]
)
def update_total_timeseries(clickData):
    country_iso = clickData['points'][0]['location']
    country_name = conf_df[conf_df.iso_alpha == country_iso].index[0]
    dffc = conf_df[conf_df.iso_alpha == country_iso]
    dffd = deaths_df[deaths_df.iso_alpha == country_iso]
    dffr = rec_df[rec_df.iso_alpha == country_iso]
    xc = pd.Series(range(len(dffc.loc[country_name,dffc['Firstdayabove100df'].loc[country_name]:dffc.columns[-3]].index)))
    yc = pd.Series(dffc.loc[country_name,dffc['Firstdayabove100df'].loc[country_name]:dffc.columns[-3]].values)
    xd = pd.Series(range(len(dffd.loc[country_name,dffd['Firstdayabove100df'].loc[country_name]:dffd.columns[-3]].index)))
    yd = pd.Series(dffd.loc[country_name,dffd['Firstdayabove100df'].loc[country_name]:dffd.columns[-3]].values)
    xr = pd.Series(range(len(dffr.loc[country_name,dffr['Firstdayabove100df'].loc[country_name]:dffr.columns[-3]].index)))
    yr = pd.Series(dffr.loc[country_name,dffr['Firstdayabove100df'].loc[country_name]:dffr.columns[-3]].values)

    title = '<b>{}</b><br>Total cases (days since 100 confirmed cases)'.format(country_name)
    return create_time_series(xc, yc, xd, yd, xr, yr, title)

if __name__ == '__main__':
    app.run_server(debug=True)