import math

from ..utils import obj, h2k


# Returns the HVAC distribution system based on the specified type
# "air"
# "hydronic"
# Distribution System Efficiency (DSE) is NOT SUPPORTED (no h2k representation)
def get_hvac_distribution(h2k_dict, model_data):

    hvac_dist_type = model_data.get_hvac_distribution_type()
    primary_heating_id = model_data.get_system_id("primary_heating")
    air_conditioner_id = model_data.get_system_id("air_conditioner")
    air_heat_pump_id = model_data.get_system_id("air_heat_pump")
    ground_heat_pump_id = model_data.get_system_id("ground_heat_pump")
    water_heat_pump_id = model_data.get_system_id("water_heat_pump")

    hvac_dist_dict = {}

    if hvac_dist_type == "air":
        pass

    elif hvac_dist_type == "hydronic":
        pass

    return hvac_dist_dict
