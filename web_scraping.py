import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

# Sending request to ;List of United States cities by population' wikipedia page
website_url = requests.get(
    "https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population#Locations_of_50_most_populous_cities").text
soup = BeautifulSoup(website_url, "lxml")

# Extracting table contents of all the 311 incorporated places in the United States
us_places = soup.find("table", {"class": "wikitable sortable"})


# Defining a function to convert the HTML response into a list
def parse_data_from_table(place):
    rows = place.findAll('tr')
    parsed_table_data = []
    for row in rows:
        children = row.findChildren(recursive=False)
        row_text = []
        for child in children:
            clean_text = child.text # Discard reference/citation links
            clean_text = clean_text.split('&#91;')[0] # Clean the header row of the sort icons
            clean_text = clean_text.split('&#160;')[-1]
            clean_text = clean_text.strip()
            row_text.append(clean_text)
        parsed_table_data.append(row_text)
    return parsed_table_data


# Converting list into a dataframe and selecting the top 8 cities with the highest population
us_cities_population_data = parse_data_from_table(us_places)
df = pd.DataFrame(us_cities_population_data, columns=['2017 rank', 'City', 'State', '2017 estimate', '2010 Census',
                                                      'Change', '2016 land area(sq mi)', '2016 land area(km sq)', '2016 population density(sq mi)',
                                                      '2016 population density(km sq)', 'Location'])
df.drop(df.index[:1], inplace=True)
top8 = df.head(8)

# Creating a dictionary with the wikipedia link for each city
cities_urls = dict()
for city in us_places.findAll('tr'):
    cities = city.findAll('td')
    if len(cities)>1:
        city_info = cities[1].find('a')
        cities_urls[city_info.attrs.get('title')] = city_info.attrs.get('href')

result = pd.DataFrame()
final_df = pd.DataFrame()

# Extracting the racial composition data for each city
for index, row in top8.iterrows():
    city_name = row['City']
    url = 'https://en.wikipedia.org'
    for k,v in cities_urls.items(): # Defining URL for each city
        if k.lower() in city_name.lower():
            url = url + v
    req_url = requests.get(url).text # Sending a request
    soup = BeautifulSoup(req_url, "lxml")
    temp = soup.find("table", {"class": "wikitable sortable collapsible"}) # Parcing the demographic data from the page

    # if statement to check if there is a response or not
    if temp != None :
        city_temp_data = parse_data_from_table(temp)
        new_df = pd.DataFrame(city_temp_data)
        new_df.drop(new_df.index[:1], inplace=True) # Restructuring the dataframe so that it can be appended to the original dataframe
        new_df = new_df.iloc[:, [0,1]]
        new_df = new_df.transpose()
        new_df.columns = new_df.iloc[0, :]
        new_df.drop(new_df.index[:1], inplace=True)
        new_df.reset_index(drop=True, inplace=True)
        result = pd.concat([result, new_df], sort=False)
        result.reset_index(drop=True, inplace=True)

    else:
        result.append(pd.Series([np.nan]), ignore_index=True) # Adding a null row if table not found
        result.reset_index(drop=True, inplace=True)


top8.reset_index(drop=True,inplace=True)
result = result[['White', '—Non-Hispanic', 'Black or African American', 'Hispanic or Latino (of any race)','Asian']]


# Extracting information about each city's Government
gov_info =pd.DataFrame()
for index, row in top8.iterrows():
    city_name = row['City']
    link = 'https://en.wikipedia.org'
    for k,v in cities_urls.items():
        if k.lower() in city_name.lower():
            link = link + v
    req_url = requests.get(link).text
    soup = BeautifulSoup(req_url, "lxml")
    temp = soup.find("table", {"class": "infobox geography vcard"})
    if temp != None :
        city_temp_data = parse_data_from_table(temp)
        new_df = pd.DataFrame(city_temp_data)
        new_df = new_df.transpose()
        new_df.columns = new_df.iloc[0, :]
        new_df.drop(new_df.index[:1], inplace=True)
        new_df.reset_index(drop=True, inplace=True)
        new_df = new_df[['• Type', '• Body', '• Mayor', 'Time zone', 'Website']]
        new_df.columns = ['Government Type', 'Government Body', 'Government Mayor', 'Time Zone', 'Government Website']
        gov_info = pd.concat([gov_info, new_df], sort=False)
        gov_info.reset_index(drop=True, inplace=True)
    else:
        gov_info.append(pd.Series([np.nan]), ignore_index=True)
        gov_info.reset_index(drop=True, inplace=True)

# Concatenation the US cities population data with their respective racial composition and Governemt information
US_city_info = pd.concat([top8, result, gov_info], axis=1, sort=False)

# Exporting the data to a CSV file
US_city_info.to_csv('US Cities Information.csv', index=False)


