# High level HPXML structure for HVAC portion:
# {
#     "HVACPlant": {
#         "PrimarySystems": {
#             "PrimaryHeatingSystem": {...},
#             "PrimaryCoolingSystem": {...}
#         },
#         "HeatingSystem": {...},
#         "CoolingSystem": {...},
#     },
#     "HVACControl": {...},
#     "HVACDistribution": {...},
# }
# Certain sections must be conditionally present
# For example, with electric baseboards, no HVACDistribution section should be present

from .primary_heating import get_primary_heating_system
from .hvac_control import get_hvac_control
from .hvac_distribution import get_hvac_distribution


# This function compiles translations for all HVAC and DHW sections, as there are many dependencies between these sections
def get_systems(h2k_dict, model_data):

    # Only one primary heating system, define its id
    model_data.set_system_id({"primary_heating": "HeatingSystem1"})
    model_data.set_system_id({"air_conditioner": "CoolingSystem1"})
    model_data.set_system_id({"hvac_distribution": "HVACDistribution1"})

    # Primary heating system as a component of the HVACPlant Section
    primary_heating_result = get_primary_heating_system(h2k_dict, model_data)

    # Primary cooling system as a component of the HVACPlant Section
    # air_conditioner_result = get_air_conditioner(h2k_dict, model_data)
    air_conditioner_result = {}

    # Always produces a complete dictionary, includes set point information.
    hvac_control_result = get_hvac_control(h2k_dict, model_data)

    # This may be an empty dictionary, e.g. for baseboards, in which case it must not be included in hvac_dict
    hvac_distribution_result = get_hvac_distribution(h2k_dict, model_data)

    print("DISTRIBUTION: ", hvac_distribution_result)

    hvac_dict = {
        "HVACPlant": {
            "PrimarySystems": {
                "PrimaryHeatingSystem": {
                    "@idref": model_data.get_system_id("primary_heating")
                }
            },
            "HeatingSystem": primary_heating_result,
            **(
                {"CoolingSystem": air_conditioner_result}
                if air_conditioner_result != {}
                else {}
            ),
        },
        "HVACControl": hvac_control_result,
        **(
            {"HVACDistribution": hvac_distribution_result}
            if hvac_distribution_result != {}
            else {}
        ),
    }

    return {"hvac_dict": hvac_dict, "dhw_dict": {}}
