import math

from ..utils import obj, h2k


# Here we always return an array of objects, because we could be dealing with a primary + secondary system configuration
def get_hot_water_systems(h2k_dict, model_data):

    hpxml_dhw = []
    system_dict = {}

    primary_dhw = get_single_dhw_system(system_dict, model_data)
    hpxml_dhw = [primary_dhw]

    secondary_dhw = get_single_dhw_system(system_dict, model_data)

    return []


def get_single_dhw_system(system_dict, model_data):

    return {}
