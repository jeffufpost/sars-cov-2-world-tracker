import pandas as pd
import pycountry as pc

# Read data from github

#print("Downloading data from github.......")
# Import confirmed cases
conf_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

#Import deaths data
deaths_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

# Import recovery data
rec_df = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

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

# Create a per day dataframe
#print("Creating new per day dataframes......")
conf_df_pd = conf_df.copy()
deaths_df_pd = deaths_df.copy()
rec_df_pd = rec_df.copy()

for i in range(len(conf_df)):
    for j in range(len(conf_df.columns)-1,3,-1):
        conf_df_pd.iloc[i,j] = conf_df.iloc[i,j] - conf_df.iloc[i,j-1]
        deaths_df_pd.iloc[i,j] = deaths_df.iloc[i,j] - deaths_df.iloc[i,j-1]
        rec_df_pd.iloc[i,j] = rec_df.iloc[i,j] - rec_df.iloc[i,j-1]

#print("Adding columns of first date above 100 confirmed cases.....")
# Create a column containing date at which 100 confirmed cases were reached, NaN if not reached yet        
Firstdayabove100df = []
for row in range(len(conf_df[conf_df.columns[3:]])):
    if conf_df[conf_df.columns[-1]][0] > 100:
        Firstdayabove100df.append(conf_df[conf_df.columns[3:]][conf_df[conf_df.columns[3:]] > 100].iloc[row].idxmin())
    else:
        Firstdayabove100df.append('NaN')
    
conf_df['Firstdayabove100df'] = Firstdayabove100df
conf_df_pd['Firstdayabove100df'] = Firstdayabove100df
deaths_df['Firstdayabove100df'] = Firstdayabove100df
deaths_df_pd['Firstdayabove100df'] = Firstdayabove100df
rec_df['Firstdayabove100df'] = Firstdayabove100df
rec_df_pd['Firstdayabove100df'] = Firstdayabove100df
      
#df = df.replace('Congo (Brazzaville)', 'Congo')
#df = df.replace('Congo (Kinshasa)', 'Congo, the Democratic Republic of the')
#df = df.replace('Burma', 'Myanmar')

# Add a column with ISO_3 country codes for map locating:
# Need to modify some country names first:
conf_df = conf_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

conf_df_pd = conf_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

rec_df = rec_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

rec_df_pd = rec_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

deaths_df = deaths_df.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

deaths_df_pd = deaths_df_pd.rename(index={'Congo (Brazzaville)': 'Congo', 'Congo (Kinshasa)': 'Congo, the Democratic Republic of the', 'Burma': 'Myanmar', 'Korea, South': 'Korea, Republic of', 'Laos': "Lao People's Democratic Republic", 'Taiwan*': 'Taiwan', "West Bank and Gaza":"Palestine, State of"})

# Only the two cruise ships are excluded from this

#print("Looking up ISO_3 country codes and adding them to dataframes.......")
# Add this as a column
iso_alpha = []
for row in range(len(conf_df)):
    try:
        iso_alpha.append(pc.countries.search_fuzzy(conf_df.index[row])[0].alpha_3)
    except LookupError:
        iso_alpha.append('NaN')

conf_df['iso_alpha'] = iso_alpha
conf_df_pd['iso_alpha'] = iso_alpha
deaths_df['iso_alpha'] = iso_alpha
deaths_df_pd['iso_alpha'] = iso_alpha
rec_df['iso_alpha'] = iso_alpha
rec_df_pd['iso_alpha'] = iso_alpha

# Save dataframes to csv files
#print("Saving the dataframes to csv files.....")
conf_df.to_csv('data/conf.csv', encoding='utf-8')
conf_df_pd.to_csv('data/conf_pd.csv', encoding='utf-8')
deaths_df.to_csv('data/deaths.csv', encoding='utf-8')
deaths_df_pd.to_csv('data/deaths_pd.csv', encoding='utf-8')
rec_df.to_csv('data/rec.csv', encoding='utf-8')
rec_df_pd.to_csv('data/rec_pd.csv', encoding='utf-8')
