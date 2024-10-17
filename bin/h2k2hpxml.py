import pathlib
import os
import sys
# Avoid having to add PYTHONPATH to env.
PROJECT_ROOT = str(pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute())
sys.path.append(PROJECT_ROOT)
import configparser
import subprocess
import click
from  h2ktohpxml.h2ktohpxml import h2ktohpxml
from configparser import NoOptionError, NoSectionError
from colorama import Fore, Style
import pyfiglet
import random


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])
@click.group(context_settings=CONTEXT_SETTINGS)
# This should match the version of OSHPXML with a suffix for our CLI version
@click.version_option(version='1.7.0.1')

def cli():
    pass

@cli.command(help=f"People that worked on this.")
def credits():
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

@cli.command(help="Convert and Simulate H2K file to OS/E+.")
@click.option('--input_path','-i', default=os.path.join(PROJECT_ROOT,'cli','input'), help='h2k file or folder containing h2k files.')
@click.option('--output_path','-o', default=os.path.join(PROJECT_ROOT,'cli','output'), help='Path to output hpxml files.')
@click.option('--timestep', multiple=True, default=[], help='Request monthly output type (ALL, total, fuels, enduses, systemuses, emissions, emissionfuels, emissionenduses, hotwater, loads, componentloads, unmethours, temperatures, airflows, weather, resilience); can be called multiple times')
@click.option('--daily', multiple=True, default=[], help='Request daily output type (ALL, total, fuels, enduses, systemuses, emissions, emissionfuels, emissionenduses, hotwater, loads, componentloads, unmethours, temperatures, airflows, weather, resilience); can be called multiple times')
@click.option('--hourly', multiple=True, default=[], help='Request hourly output type (ALL, total, fuels, enduses, systemuses, emissions, emissionfuels, emissionenduses, hotwater, loads, componentloads, unmethours, temperatures, airflows, weather, resilience); can be called multiple times')
@click.option('--monthly', multiple=True, default=[], help='Request monthly output type (ALL, total, fuels, enduses, systemuses, emissions, emissionfuels, emissionenduses, hotwater, loads, componentloads, unmethours, temperatures, airflows, weather, resilience); can be called multiple times')
@click.option('--add-component-loads','-l', is_flag=True, default=True, help='Add component loads.')
@click.option('--debug','-d',  is_flag=True, default=False, help='Enable debug mode.')
@click.option('--skip-validation','-s',  is_flag=True, default=False, help='Skip Schema/Schematron validation for faster performance')
@click.option('--output-format','-f', default='csv', help='Output format for the simulation resultsOutput file format type (csv, json, msgpack, csv_dview)')
@click.option('--add-stochastic-schedules',  is_flag=True, default=False, help='Add detailed stochastic occupancy schedules')
@click.option('--add-timeseries-output-variable', multiple=True, default=[], help='Add timeseries output variable; can be called multiple times; can be called multiple times')
@click.option('--do-not-sim',  is_flag=True, default=False, help='Convert only, do not run simulation')
def run(input_path,
            output_path,
            timestep,
            daily,
            hourly,
            monthly,
            add_component_loads,
            debug,
            skip_validation,
            output_format,
            add_stochastic_schedules,
            add_timeseries_output_variable,
            do_not_sim):
    """
    Convert H2K files to HPXML format based on the provided configuration file.

    Args:
        config_path (str): Path to the configuration file.
    """

    # Ensure that only one of the hourly, monthly or timeseries options is provided
    if sum(bool(x) for x in [hourly, monthly, timestep]) > 1:
        raise ValueError("Only one of the options --hourly, --monthly, or --timestep can be provided at a time.")

    # Create string with all the flags
    flags = ""
    if add_component_loads:
        flags += " --add-component-loads"
    if debug:
        flags += " --debug"
    if output_format:
        flags += f" --output-format {output_format}"
    if timestep:
        flags += " " + " ".join(f"--timestep {t}" for t in timestep)
    if hourly:
        flags += " " + " ".join(f"--hourly {h}" for h in hourly)
    if monthly:
        flags += " " + " ".join(f"--monthly {m}" for m in monthly)
    if skip_validation:
        flags += " --skip-validation"
    if daily:
        flags += " " + " ".join(f"--daily {d}" for d in daily)
    if add_stochastic_schedules:
        flags += " --add-stochastic-schedules"
    if add_timeseries_output_variable:
        flags += " " + " ".join(f"--add-timeseries-output-variable {v}" for v in add_timeseries_output_variable)

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

    # Translate files to hpxml
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

        if not do_not_sim:
            # Pause 3 seconds
            import time
            time.sleep(3)

            path_to_log = f"{output_path}/run"
            # Run the OpenStudio simulation
            command = [
                f"/usr/local/bin/openstudio",
                ruby_hpxml_path,
                "-x",
                hpxml_path
            ]
            
            # Convert flags to a list of strings
            flags = flags.split()
            command.extend(flags)
            
            try:
                print("Running simulation...")
                result = subprocess.run(
                    command,
                    cwd=hpxml_os_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("Simulation result:", result)
            except subprocess.CalledProcessError as e:
                print("Error during simulation:", e.stderr)
        
if __name__ == '__main__':
    cli()