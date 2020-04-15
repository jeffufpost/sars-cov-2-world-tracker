print("Importing required libraries")
import pandas as pd
import numpy as np

# Read data from github

print("Downloading data from github.......")
# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

#Import deaths data
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

# Import recovery data
rec_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

# Wrangle the data

print("Wrangling data by country.......")
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
print("Creating new per day dataframes......")
# Create per day dataframes for cases, deaths, and recoveries - by pd.DatafRame.diff
conf_df_pd = conf_df.diff(axis=1)
deaths_df_pd = deaths_df.diff(axis=1)
rec_df_pd = rec_df.diff(axis=1)

print("Create infected dataframe = conf - deaths - recoveries")
inf_df = conf_df - deaths_df - rec_df

print("Adding dataframes of 1st, 2nd, and 3rd derivatives of number of infected")
firstdev = inf_df.apply(np.gradient, axis=1)
seconddev = firstdev.apply(np.gradient)
thirddev = seconddev.apply(np.gradient)

print("Create series of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet
fda100 = conf_df[conf_df > 100].apply(pd.Series.first_valid_index, axis=1)

# Below can only be done in the main app.py program instead
# print("Create series of iso_alpha country codes.....")
# Nee to run get_iso_alpha3.py first
# iso_alpha = pd.read_csv('sars-cov-2-world-tracker/data/iso_alpha.csv', index_col=0, header=None).T.iloc[0]

# Save dataframes to csv files
print("Saving the dataframes to csv files.....")
conf_df.to_csv('data/conf.csv', encoding='utf-8')
conf_df_pd.to_csv('data/conf_pd.csv', encoding='utf-8')
deaths_df.to_csv('data/deaths.csv', encoding='utf-8')
deaths_df_pd.to_csv('data/deaths_pd.csv', encoding='utf-8')
rec_df.to_csv('data/rec.csv', encoding='utf-8')
rec_df_pd.to_csv('data/rec_pd.csv', encoding='utf-8')
inf_df.to_csv('data/inf.csv', encoding='utf-8')
firstdev.to_csv('data/firstdev.csv', encoding='utf-8', header='Country/Region')
seconddev.to_csv('data/seconddev.csv', encoding='utf-8', header='Country/Region')
thirddev.to_csv('data/thirddev.csv', encoding='utf-8', header='Country/Region')
fda100.to_csv('data/fda100.csv', encoding='utf-8', header='Country/Region')