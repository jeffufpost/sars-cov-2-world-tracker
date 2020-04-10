#####
### This script is to create a dataframe containing the country names and corresponding iso_alph3 codes
#####
import pandas as pd
import pycountry as pc

print("Downloading data from github.......")
# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

# Consolidate countries (ie. frenc dom tom are included in France, etc..)
conf_df = conf_df.groupby("Country/Region")
conf_df = conf_df.sum().reset_index()
conf_df = conf_df.set_index('Country/Region')

# Convert country names to correct format for search with pycountry
conf_df = conf_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

print("Looking up ISO_3 country codes and adding them to dataframes.......")
# Add this as a column
def countrycodes(x):
    try:
        return pc.countries.search_fuzzy(x)[0].alpha_3
    except LookupError:
        return 'none'

iso_alpha = conf_df.index.to_series().apply(lambda x: countrycodes(x))

# Save dataframes to csv files
print("Saving the dataframes to csv files.....")
iso_alpha.to_csv('data/iso_alpha.csv', encoding='utf-8', header='Country/Region')