print("Importing required libraries")
import pandas as pd
import pycountry as pc

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

# Create a per day dataframe
print("Creating new per day dataframes......")
# Create per day dataframes for cases, deaths, and recoveries - by pd.DatafRame.diff
conf_df_pd = conf_df.diff(axis=1)
deaths_df_pd = deaths_df.diff(axis=1)
rec_df_pd = rec_df.diff(axis=1)

print("Adding columns of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet
fda100 = conf_df[conf_df > 100].apply(pd.Series.first_valid_index, axis=1)

conf_df['fda100'] = fda100
conf_df_pd['fda100'] = fda100
deaths_df['fda100'] = fda100
deaths_df_pd['fda100'] = fda100
rec_df['fda100'] = fda100
rec_df_pd['fda100'] = fda100

# Add a column with ISO_3 country codes for map locating:
# Need to modify some country names first:
conf_df = conf_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

conf_df_pd = conf_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

rec_df = rec_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

rec_df_pd = rec_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

deaths_df = deaths_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

deaths_df_pd = deaths_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

# Only the two cruise ships are excluded from this

print("Looking up ISO_3 country codes and adding them to dataframes.......")
# Add this as a column
def countrycodes(x):
    try:
        return pc.countries.search_fuzzy(x)[0].alpha_3
    except LookupError:
        return 'none'

iso_alpha = conf_df.index.to_series().apply(lambda x: countrycodes(x))

conf_df['iso_alpha'] = iso_alpha
conf_df_pd['iso_alpha'] = iso_alpha
deaths_df['iso_alpha'] = iso_alpha
deaths_df_pd['iso_alpha'] = iso_alpha
rec_df['iso_alpha'] = iso_alpha
rec_df_pd['iso_alpha'] = iso_alpha

# Save dataframes to csv files
print("Saving the dataframes to csv files.....")
conf_df.to_csv('data/conf.csv', encoding='utf-8')
conf_df_pd.to_csv('data/conf_pd.csv', encoding='utf-8')
deaths_df.to_csv('data/deaths.csv', encoding='utf-8')
deaths_df_pd.to_csv('data/deaths_pd.csv', encoding='utf-8')
rec_df.to_csv('data/rec.csv', encoding='utf-8')
rec_df_pd.to_csv('data/rec_pd.csv', encoding='utf-8')
