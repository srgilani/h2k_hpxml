import pytest
import pathlib
import os
import sys
PROJECT_ROOT = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute())
sys.path.append(PROJECT_ROOT)
from h2ktohpxml.utils.weather import get_cwec_file

@pytest.mark.filterwarnings("ignore:Unverified HTTPS request")
def test_get_cwec_file():
    # Test with valid inputs
    weather_location="LoNdOn"
    weather_region="OnTaRiO"
    weather_folder=os.path.join("/OpenStudio-HPXML/weather/")
    weather_file_name = "CAN_ON_London.AP.716230_CWEC2020"
    weather_vintage="CWEC2020"
    weather_library="historic"
    
    # Delete file if it exists

    if os.path.exists(os.path.join(weather_folder,weather_file_name+'.epw')):
        print(f"Deleting file {os.path.join(weather_folder,weather_file_name+'.epw')}")
        os.remove(os.path.join(weather_folder,weather_file_name+'.epw'))
    
    expected_output = os.path.join(weather_folder,weather_file_name)  # Replace with the actual expected output
    result = get_cwec_file(weather_region=weather_region,
                           weather_location=weather_location, 
                           weather_folder=weather_folder,
                           weather_vintage=weather_vintage,
                           weather_library=weather_library)
    assert result == expected_output, f"Expected {expected_output}, but got {result}"
    # Assert that the output file was downloaded
    assert os.path.exists(os.path.join(weather_folder,weather_file_name+'.epw')), f"File {result} does not exist"

if __name__ == "__main__":
    pytest.main()