import re
import pandas as pd
import os
import json
import difflib
from unidecode import unidecode



def get_numbers_and_provinces(file_path="/workspaces/h2k_hpxml/h2ktohpxml/utils/h2k_weather_names.txt"):
    
    prov_terr_codes = {
    "BRITISH COLUMBIA": "BC",
    "ALBERTA": "AB",
    "SASKATCHEWAN": "SK",
    "MANITOBA": "MB",
    "ONTARIO": "ON",
    "NEW BRUNSWICK": "NB",
    "NOVA SCOTIA": "NS",
    "QUEBEC": "QC",
    "PRINCE EDWARD ISLAND": "PE",
    "NEWFOUNDLAND AND LABRADOR": "NL",
    "YUKON": "YT",
    "NORTHWEST TERRITORIES": "NT",
    "NUNAVUT": "NU",
}
    
    weather_library = "historic"
    with open(
        os.path.join(
            os.path.dirname(__file__),"..", "resources", "weather","historic.json"
        ),
        "r",
    ) as f:
        canadian_cwec_files = json.load(f)
    
    
    with open(file_path, 'r') as file:
        # Read the first line to get the number of cities and provinces
        first_line = file.readline().strip()
        numbers = first_line.split()
        number_of_cities = int(numbers[0])
        number_of_provinces = int(numbers[1])
        
        # Continue reading lines from file until procinces_english length is equal to number_of_provinces
        provinces_english = []
        while len(provinces_english) < number_of_provinces:
            line = file.readline().strip()
            # Capture the provinces in the line using regular expressions
            # The regex pattern assumes that provinces are separated by multiple spaces
            provinces = re.split(r'\s{2,}', line)
            provinces_english.extend(provinces)
            
        provinces_city_map = []
        while len(provinces_city_map) < number_of_cities:
            line = file.readline().strip()
            # Capture the provinces in the line using regular expressions
            # The regex pattern assumes that provinces are separated by multiple spaces
            map = re.split(r'\s{2,}', line)
            provinces_city_map.extend(map)
            
        cities_english = []
        while len(cities_english) < number_of_cities:
            line = file.readline().strip()
            # Capture the provinces in the line using regular expressions
            # The regex pattern assumes that provinces are separated by multiple spaces
            map = re.split(r'\s{3,}', line)
            cities_english.extend(map)
            
        provinces_french = []
        while len(provinces_french) < number_of_provinces:
            line = file.readline().strip()
            # Capture the provinces in the line using regular expressions
            # The regex pattern assumes that provinces are separated by multiple spaces
            provinces = re.split(r'\s{2,}', line)
            provinces_french.extend(provinces)
        
        cities_french = []
        while len(cities_french) < number_of_cities:
            line = file.readline().strip()
            # Capture the provinces in the line using regular expressions
            # The regex pattern assumes that provinces are separated by multiple spaces
            map = re.split(r'\s{3,}', line)
            cities_french.extend(map)
            
    print(f"Number of cities: {number_of_cities}")
    print(f"Number of french cities: {len(cities_french)}")
    print(f"Number of provinces: {number_of_provinces}")
    print(f"Number of french provinces: {len(provinces_french)}")
    print(f"Number of provinces city map: {len(provinces_city_map)}")
    print(f"Number of english cities: {len(cities_english)}")
    print(f"Number of english provinces: {len(provinces_english)}")
    # Create a data frame with the extracted data
    city_df = pd.DataFrame({ 
    #     'provinces_english': provinces_english,
         'provinces_city_map': provinces_city_map,
         'cities_english': cities_english,
    #     'provinces_french': provinces_french,
         'cities_french': cities_french
    })
    
    # Convert the provinces_city_map column to integers
    city_df['provinces_city_map'] = city_df['provinces_city_map'].astype(int)

    
    province_df = pd.DataFrame({
        'provinces_english': provinces_english,
        'provinces_french': provinces_french
    })
    
    # Add an index column to the data frame
    province_df.index += 1
    city_df.index += 1
    # Merge the two data frames on the index column from the province_df and the provinces_city_map column from the city_df
    merged_df = city_df.merge(province_df, left_on='provinces_city_map', right_index=True, how='left')
    print(merged_df)
    
    # Apply unidecode to the provinces_english and cities_english columns
    merged_df['provinces_english'] = merged_df['provinces_english'].apply(unidecode)
    merged_df['cities_english'] = merged_df['cities_english'].apply(unidecode)
    
    
    # Add weatherfile name and location to merged_df based on the provinces_english and cities_english.
    historic_types = [
       #"CWEC2016.zip",
       #"TMYx.2004-2018.zip",
       #"TMYx.2007-2021.zip",
       "CWEC2020.zip",
       #"TMYx.zip",
       #"CWEC.zip"
    ]

    # Create new empty dataframe
    
    new_df = pd.DataFrame()
    # Iterate over provinces_english
    for province in prov_terr_codes:
    # Iterate over historic_types
        filtered_df = merged_df[merged_df['provinces_english'] == province]
        filtered_cwec_files_by_province = [file for file in canadian_cwec_files if f"CAN_{prov_terr_codes[province]}" in file]
        for historic_type in historic_types:
            filtered_cwec_files = [file for file in filtered_cwec_files_by_province if historic_type in file]
            print(historic_type)
            filtered_df[historic_type] = filtered_df.apply(lambda x: difflib.get_close_matches(f"CAN_{prov_terr_codes[unidecode(x['provinces_english']).upper()]}_{unidecode(x['cities_english'])}_{historic_type}".lower(), filtered_cwec_files, n=1, cutoff=0.1)[0], axis=1)
        new_df = pd.concat([new_df, filtered_df],ignore_index=True)
    # write the merged_df to a csv file
    new_df.to_csv("h2k_weather_names.csv", index=False)
    return number_of_cities, number_of_provinces, provinces_english,provinces_city_map,cities_english,provinces_french,cities_french


number_of_cities, number_of_provinces, provinces_english,provinces_city_map,cities_english,provinces_french,cities_french = get_numbers_and_provinces()