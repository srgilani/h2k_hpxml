import math

from ..utils import obj, h2k


# TODO: DWHR not yet supported
def get_hot_water_distribution(h2k_dict, model_data):

    return {
        "SystemIdentifier": {"@id": model_data.get_system_id("dhw_distribution")},
        "SystemType": {"Standard": None},
        "PipeInsulation": {"PipeRValue": 0},
    }
