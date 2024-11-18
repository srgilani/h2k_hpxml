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

    # TODO: Better handle determination of which floor areas to include here (total area assumed)
    ag_heated_floor_area = model_data.get_building_detail("ag_heated_floor_area")
    bg_heated_floor_area = model_data.get_building_detail("bg_heated_floor_area")

    hvac_dist_dict = {}

    print("hvac_dist_type", hvac_dist_type)
    if "air_" in str(hvac_dist_type):
        # “regular velocity”, “gravity”, or “fan coil” are the supported types
        # Not all of these are defined in h2k
        [base_type, sub_type] = hvac_dist_type.split("_")
        # Currently only handling regular velocity with default duct inputs
        hvac_dist_dict = {
            "SystemIdentifier": {"@id": model_data.get_system_id("hvac_distribution")},
            "DistributionSystemType": {
                "AirDistribution": {
                    "AirDistributionType": sub_type,
                    "DuctLeakageMeasurement": [
                        {
                            "DuctType": "supply",
                            "DuctLeakage": {
                                "Units": "CFM25",
                                "Value": 0,
                                "TotalOrToOutside": "to outside",
                            },
                        },
                        {
                            "DuctType": "return",
                            "DuctLeakage": {
                                "Units": "CFM25",
                                "Value": 0,
                                "TotalOrToOutside": "to outside",
                            },
                        },
                    ],
                    "Ducts": [
                        {
                            "SystemIdentifier": {"@id": "Ducts1"},
                            "DuctType": "supply",
                            "DuctInsulationRValue": 0.0,
                        },
                        {
                            "SystemIdentifier": {"@id": "Ducts2"},
                            "DuctType": "return",
                            "DuctInsulationRValue": 0.0,
                        },
                    ],
                }
            },
            "ConditionedFloorAreaServed": ag_heated_floor_area + bg_heated_floor_area,
        }

    elif "hydronic_" in str(hvac_dist_type):
        # HydronicDistributionType choices are “radiator”, “baseboard”, “radiant floor”, “radiant ceiling”, or “water loop”.
        # However, h2k does not include sufficient information to determine which is used, so we default to "radiant floor"

        pass

    return hvac_dist_dict
