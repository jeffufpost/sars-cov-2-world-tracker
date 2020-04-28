#####
### This script is to create a dataframe containing the country names and corresponding iso_alph3 codes
### Edit April 28th to add population and continent
#####
import pandas as pd
import pycountry as pc
import world_bank_data as wb

print("Downloading data from github.......")
# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

# Consolidate countries (ie. french dom tom are included in France, etc..)
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

# Use as dataframe and rename column as alpha-3
iso_alpha = pd.DataFrame(iso_alpha)
iso_alpha.rename(columns={'Country/Region': 'alpha-3'}, inplace=True)

# Download continental region
gitdata = pd.read_csv('https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv')
iso_alpha = iso_alpha.reset_index().merge(gitdata[['alpha-3','region']], how='left').set_index('Country/Region')

# Download population data
population = pd.DataFrame(wb.get_series('SP.POP.TOTL', id_or_value='id', simplify_index=True, mrv=1))
population.index.names = ['alpha-3']
iso_alpha = iso_alpha.reset_index().merge(pd.DataFrame(population).reset_index(), how='left').set_index('Country/Region')

# Save dataframes to csv files
print("Saving the dataframes to csv files.....")
iso_alpha.to_csv('data/iso_alpha.csv', encoding='utf-8', header='Country/Region')
