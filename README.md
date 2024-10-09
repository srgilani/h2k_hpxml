# h2k-hpxml
Translator functions to convert h2k files to HPXML format, run files via OpenStudio workflow, and compare results.

Compatible Software Versions:
HOT2000 v11.10, v11.11 and v11.12
OpenStudio 3.7.0 - https://github.com/NREL/OpenStudio/releases/tag/v3.7.0
OpenStudio-HPXML 1.7.0 - https://github.com/NREL/OpenStudio-HPXML/releases


# Setup
1. Ensure that the software versions above are installed
2. Add "C:/openstudio-3.7.0/bin to your PATH environment variables, and ensure no older versions of OS are referenced. 
3. Clone or download this repository
4. Download the required CWEC .epw weather files for Canada or by province (https://climate.weather.gc.ca/prods_servs/engineering_e.html)
5. Add the Canadian weather files to the "weather" folder in the OpenStudio-HPXML directory (e.g. C:\OpenStudio-HPXML-v1.7.0\OpenStudio-HPXML\weather)



### conversionconfig.ini
Use the conversionconfig.ini to specify the file or folder path of the h2k file(s) you would like to convert to HPXML.
This file can also be used to define non-h2k parameters for the translation process.


# Running the translator
1. Ensure the virtual environment is activated (run `.\.venv\Scripts\Activate.ps1`) and the required packages are installed (`pip install -r .\requirements.txt`)
2. Run main.py (`py main.py`) to translate a single file or a directory of files based on the `source_h2k_path` specified in conversionconfig.ini
3. Run run.py (`py run.py`) to run an hpxml file through the HPXML-OS workflow
4. Run simulateh2k.py (`py simulateh2k.py`) to translate a file and simulate it using the HPXML-OS workflow


## h2ktohpxml
Flow (to implement):
1. Pull in blank HPXML template, remove what's needed
2. HPXML Section: Software Info (complete)
3. HPXML Section: Building (complete)
4. HPXML Section: Building Site (complete)
5. HPXML Section: Building Summary (complete)
6. HPXML Section: Climate Zones (complete)
7. HPXML Section: Enclosure (complete)
8. HPXML Section: Systems (OUT OF SCOPE)
9. HPXML Section: Appliances (complete)
10. HPXML Section: Lighting & Ceiling Fans (complete)
11. HPXML Section: Pools & Permanent Spas(complete)
12. HPXML Section: Misc Loads(complete)


## Assumptions
- Attic/gable ceilings are assumed to not have gable walls defined in the h2k file. They are created in the translation process by assuming conventional rectangular geometry, where half the "length" ceiling input is assumed to be one side of the rectangle.
- All attics are assumed to be vented
- Area of gable ends of cathedral ceilings are assumed to have been defined within h2k wall components.
- Attic/Hip type ceilings assume that the "length" input provided is the ceiling perimeter (all edges are compressed)
- Scissor ceiling surfaces are assumed to be at half the pitch of the roof (i.e. if a roof slope is 4/12, ceiling surface slope is 2/12)
- HPXML's default occupant and appliance schedules are used.
- Split level and split entry options in HOT2000 are treated as 2 storeys when counting the number of conditioned floors in HPXML.
- The HPXML workflow states that enclosed spaces such as garages should be explicitly included in the model. However, HOT2000 files do not account for these spaces, so they are ignored in the translation process.

- The "Adjacent to unconditioned space" checkbox in HOT2000 is assumed to be equivalent to "other non-freezing space" for attached buildings, and but there is no allowable HPXML equivalent for detached buildings. Therefore, we must use "outside" for buffered wall exteriors for detached buildings unless we model the entire garage or there is another HPXML workaround


- Windows can only be attached to wall components in HPXML, not doors. The current solution is to attach windows on doors to the parent wall of the door, and subtract the window area from the door area.
- For basement walls, the AssemblyEffectiveRValue includes the concrete or wood wall portion.
- Pony wall area is calculated as `pony wall height` * `exposed basement perimeter`.
- Above slab insulation is mapped to below slab insulation in HPXML, which has no above slab option.
- For slab perimeter insulation (UnderSlabInsulation), we include any under-footing measurement in the width provided to HPXML, if applicable.
- Carpet fraction and R-value for slabs overwritten with 0, otherwise HPXML defaults to values >0.
- Standard operating conditions are hard coded for base loads.
- Appliance Energy Guide Label inputs have been reverse engineered to achieve appliance water and energy consumption results that match HOT2000's standard operating conditions.
- All "exterior use" consumption in HOT2000's baseloads are lumped under exterior lighting in HPXML.


### Field Assumptions:
- Building Site Type = suburban
- Building Site Surroundings = stand-alone


Questions:
- Are there any fields in an H2k Ceiling code that would indicate a radiant barrier?

### Issues:

#### Attached Surfaces
If you tell HPXML that the house is attached (i.e. row house end), but do not specify any attached surfaces then the calculation will break. This is a problem because attached surfaces are not modeled in HOT2000. The following workaround is proposed.

1. Check the ratio of exposed foundation perimeter to foundation perimeter. The non-exposed fraction will represent the amount of attached wall perimeter we need to add.
2. Filter all non buffered HOT2000 walls and calculate their total area, average wall height, and most common R-value.
3. Multiply the total non-buffered wall area from (2.) by the non-exposed fraction from (1.) to determine the area of the attached wall.
4. Create a new wall component with the attached wall area, average wall height, and most common R-value. 

All added walls from this method will have their ExteriorAdjacentTo field set to "other housing unit", meaning they should be adiabatic surfaces since the exterior temperature will be the same as the interior temperature for this location type.

This method requires testing with houses having:
- Complex multi-component foundations
- Only exposed floors as foundations (will need to use a common ratio)

#### ConditionedFloorArea restrictions
Error message: "Error: Expected ConditionedFloorArea to be greater than or equal to the sum of conditioned slab/floor areas."
This error message means that we cannot include floors above a basement in the model. 
However, the workflow does require a floor above a crawlspace.