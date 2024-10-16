import difflib
import os
from unidecode import unidecode
import json
import requests
import zipfile
import configparser

# Load configuration file and get the hpxml_os_path, weather_vintage, and weather_type
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__),"..", "conversionconfig.ini")
config.read("conversionconfig.ini")

prov_terr_codes = {
    "BRITISH COLUMBIA": "BC",
    "ALBERTA": "AB",
    "SASKATCHEWAN": "SK",
    "MANITOBA": "MB",
    "ONTARIO": "ON",
    "QUEBEC": "QC",
    "NEW BRUNSWICK": "NB",
    "NOVA SCOTIA": "NS",
    "PRINCE EDWARD ISLAND": "PE",
    "NEWFOUNDLAND AND LABRADOR": "NL",
    "YUKON": "YT",
    "NORTHWEST TERRITORIES": "NT",
    "NUNAVUT": "NU",
}


def get_cwec_file(weather_region, 
                  weather_location, 
                  weather_folder=os.path.join(config.get("paths", "hpxml_os_path"),"weather"),
                  weather_vintage=config.get("weather", "weather_vintage"),
                  weather_type=config.get("weather", "weather_type"),
                  suffix="CWEC2020"):

    with open(
        os.path.join(
            os.path.dirname(__file__),"..", "resources", "weather",f"{weather_type}.json"
        ),
        "r",
    ) as f:
        canadian_cwec_files = json.load(f)
    # returns the name of the file without the file extension (e.g. .epw)
    default_file = canadian_cwec_files[0]

    weather_region = unidecode(weather_region)
    weather_location = unidecode(weather_location)
    if weather_region not in prov_terr_codes.keys():
        print(f"Invalid weather region: {weather_region}")
        print(f"Valid weather regions: {prov_terr_codes.keys()}")
        return default_file

    prov_terr_code = prov_terr_codes[weather_region]

    search_string = f"CAN_{prov_terr_code}_{weather_location}_{suffix}"
    print('search_string', search_string)
    # Find the closest match to the search_string in the canadian_cwec_files list
    closest_match = difflib.get_close_matches(search_string, canadian_cwec_files, n=1, cutoff=0.0)
    if closest_match:
        zip_file =  closest_match[0]
    else:
        raise(f"No close match found for: {search_string}")
    
    #Check to see if epw file already exists in the weather folder
    epw_file = os.path.join(os.path.join(weather_folder), f"{zip_file[:-4]}.epw")
    if os.path.exists(epw_file):
        print(f"File already exists: {epw_file}")
        return epw_file

    # Download the file from github 
    github_url = f"https://github.com/canmet-energy/btap_weather/raw/refs/heads/main/historic/"
    # Download file from github using the github_url and zip_file name
    file_url = f"{github_url}{zip_file}"
    local_filename = os.path.join(os.path.dirname(__file__), f"{zip_file}")
    
    response = requests.get(file_url, verify=False)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded file to {local_filename}")
    else:
        raise Exception(f"Failed to download file from {file_url}, status code: {response.status_code}")

    # Unzip the downloaded file possible race condition here if done in parallel. 
    with zipfile.ZipFile(local_filename, 'r') as zip_ref:
        extract_path = os.path.join(os.path.join(weather_folder))
        for file in zip_ref.namelist():
            if file.endswith('.epw'):
                zip_ref.extract(file, extract_path)
                print(f"Extracted {file} to {extract_path}")
    return epw_file


    








def get_climate_zone(hdd):
    if hdd < 3000:
        return "4"
    elif hdd >= 3000 & hdd < 4000:
        return "5"
    elif hdd >= 4000 & hdd < 5000:
        return "6"
    elif hdd >= 5000 & hdd < 6000:
        return "7a"
    elif hdd >= 6000 & hdd < 7000:
        return "7b"
    else:
        return "8"
