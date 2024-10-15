import pathlib
import os
import sys
# Avoid having to add PYTHONPATH to env.
PROJECT_ROOT = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute())
sys.path.append(PROJECT_ROOT)

import configparser
import subprocess
import click
import colorama
from  h2ktohpxml.h2ktohpxml import h2ktohpxml
from configparser import NoOptionError, NoSectionError


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='1.7.0.1')



def cli():
    pass


@cli.command(help=f"People that worked on this.")
def credits():
    from colorama import Fore, Style
    import pyfiglet
    import random
    print(Fore.GREEN + "H2K to HPXML Team" + Style.RESET_ALL)
    colors = [Fore.RED,
              Fore.GREEN,
              Fore.MAGENTA,
              Fore.CYAN,
              Fore.YELLOW,
              Fore.BLUE
              ]
    for x in [
        'Phylroy Lopex\n'
        "Leigh St. Hilaire\n",
        "Aidan Brookson\n"
    ]:
        print(random.choice(colors) + pyfiglet.figlet_format(x) + Fore.RESET)

@cli.command(help="Convert H2K files to HPXML format.")
@click.option('--input_path','-i', default=os.path.join(PROJECT_ROOT,'cli','input'), help='h2k file or folder containing h2k files.')
@click.option('--output_path','-o', default=os.path.join(PROJECT_ROOT,'cli','output'), help='Path to output hpxml files.')
@click.option('--weather_file','-w', default=os.path.join(PROJECT_ROOT,'cli','weather'), help='Path to output hpxml files.')
@click.option('--timestep','-t', multiple=True, default=[], help='Output variables for hourly data. Defaults to ALL.')
@click.option('--hourly','-h', multiple=True, default=[], help='Output variables for hourly data. Defaults to ALL.')
@click.option('--monthly','-m', multiple=True, default=[], help='Monthly data to output. Defaults to fuels and temperature.')
@click.option('--add-component-loads','-l', is_flag=True, default=True, help='Add component loads.')
@click.option('--debug','-d',  is_flag=True, default=True, help='Enable debug mode.')
@click.option('--output-format','-f', default='csv_dview', help='Path to output hpxml files.')


def convert(input_path,
            output_path,
            weather_file,
            timestep,
            hourly,
            monthly,
            add_component_loads,
            debug,
            output_format):
    """
    Convert H2K files to HPXML format based on the provided configuration file.

    Args:
        config_path (str): Path to the configuration file.
    """


    # Create string with all the flags
    flags = ""
    if hourly:
        flags += ' ' + ' '.join(f'--hourly {h}' for h in hourly)
    if monthly:
        flags += ' ' + ' '.join(f'--monthly {m}' for m in monthly)
    if add_component_loads:
        flags += ' --add-component-loads'
    if debug:
        flags += ' --debug'
    if output_format:
        flags += ' --output-format ' + output_format
    print("flags", flags)





    # Initialize the config parser and read the configuration file
    config = configparser.ConfigParser()
    config.read(os.path.join(PROJECT_ROOT,'conversionconfig.ini'))
    hpxml_os_path = config.get("paths", "hpxml_os_path")
    ruby_hpxml_path = os.path.join(hpxml_os_path,'workflow','run_simulation.rb')
    
    # Get source and destination paths from the configuration
    source_h2k_path = input_path
    dest_hpxml_path = output_path

    # Determine if the source path is a single file or a directory of files
    h2k_files = [source_h2k_path] if source_h2k_path.lower().endswith(".h2k") else [
        os.path.join(source_h2k_path, x) for x in os.listdir(source_h2k_path)
    ]

    #translate files to hpxml
    # Process each H2K file
    for filepath in h2k_files:
        print("================================================")
        print("Processing file:", filepath)
        
        # Read the content of the H2K file
        with open(filepath, "r", encoding="utf-8") as f:
            h2k_string = f.read()
        
        # Convert the H2K content to HPXML format
        hpxml_string = h2ktohpxml(h2k_string)
        
        # Define the output path for the converted HPXML file
        hpxml_path = os.path.join(dest_hpxml_path, pathlib.Path(filepath).stem + ".xml")

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(hpxml_path), exist_ok=True)
        
        print("Saving converted file to:", hpxml_path)
        
        # Write the converted HPXML content to the output file
        with open(hpxml_path, "w") as f:
            f.write(hpxml_string)

        #pause 3 seconds
        import time
        time.sleep(3)

        path_to_log = f"{output_path}/run"
        # Run the OpenStudio simulation
        result = subprocess.run(
            f"openstudio {ruby_hpxml_path} -x {hpxml_path} {flags}",
            cwd=config.get("paths", "hpxml_os_path"),
            check=True
        )

        print("Simulation result:", result)
        
        print("================================================")







            

@cli.command(help="Convert H2K files to HPXML format.")
@click.option('--input_path','-i', default=os.path.join(PROJECT_ROOT,'cli','input'), help='h2k file or folder containing h2k files.')
@click.option('--output_path','-o', default=os.path.join(PROJECT_ROOT,'cli','output'), help='Path to output hpxml files.')
# @click.option('--hourly','-h', multiple=True, default=['ALL'], help='Output variables for hourly data. Defaults to ALL.')
# @click.option('--monthly','-m', multiple=True, default=['fuels','temperature'], help='Monthly data to output. Defaults to fuels and temperature.')
# @click.option('--add-component-loads','-l', is_flag=True, default=True, help='Add component loads.')
# @click.option('--debug','-d',  is_flag=True, default=True, help='Enable debug mode.')
def convert_and_run(input_path, output_path):
    config = configparser.ConfigParser()
    config.read(os.path.join(PROJECT_ROOT, 'conversionconfig.ini'))
    hpxml_os_path = config.get("paths", "hpxml_os_path")

    # Initialize the config parser and read the configuration file
    config = configparser.ConfigParser()
    config.read(os.path.join(PROJECT_ROOT,'conversionconfig.ini'))
    
    # Get source and destination paths from the configuration
    source_h2k_path = input_path
    dest_hpxml_path = output_path

    # Determine if the source path is a single file or a directory of files
    h2k_files = [source_h2k_path] if source_h2k_path.lower().endswith(".h2k") else [
        os.path.join(source_h2k_path, x) for x in os.listdir(source_h2k_path)
    ]


    
    # # Add the hourly and monthly options to the flags
    # flags = ""
    # if hourly:
    #     flags += ' ' + ' '.join(f'--hourly {h}' for h in hourly)
    # if monthly:
    #     flags += ' ' + ' '.join(f'--monthly {m}' for m in monthly)
    # if add_component_loads:
    #     flags += ' --add-component-loads'
    # if debug:
    #     flags += ' --debug'
    
    # print("flags", flags)
    # raise(flags)
    flags = " --add-component-loads --debug"

    path_to_log = f"{hpxml_os_path}/{input_path}/run"
    success = False
    result = {}

    try:
        result = subprocess.run(
            f"openstudio workflow/run_simulation.rb -x {input_path} {flags}",
            cwd=hpxml_os_path,
            check=True
        )
        success = True
    except subprocess.CalledProcessError:
        print("Error in input file, check logs")
    finally:
        print({"result": result, "success": success, "path_to_log": path_to_log})

if __name__ == '__main__':
    cli()