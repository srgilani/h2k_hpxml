# High level HPXML structure :
#     "HVAC": {
#         "HVACPlant": {
#             "PrimarySystems": {
#                 "PrimaryHeatingSystem": {...},
#                 "PrimaryCoolingSystem": {...}
#             },
#             "HeatingSystem": [...],
#             "CoolingSystem": {...},
#         },
#         "HVACControl": {...},
#         "HVACDistribution": [...],
#     },
#     "WaterHeating": {
#         "WaterHeatingSystem": [...],
#         "HotWaterDistribution": [...],
#         "WaterFixture": [...],
#     }
# Certain sections must be conditionally present
# For example, with electric baseboards, no HVACDistribution section should be present

from .primary_heating import get_primary_heating_system
from .hvac_control import get_hvac_control
from .hvac_distribution import get_hvac_distribution
from .heat_pumps import get_heat_pump


from .hot_water import get_hot_water_systems
from .hot_water_distribution import get_hot_water_distribution
from .water_fixtures import get_water_fixtures


# This function compiles translations for all HVAC and DHW sections, as there are many dependencies between these sections
def get_systems(h2k_dict, model_data):

    # Only one primary heating system, define its id
    model_data.set_system_id({"primary_heating": "HeatingSystem1"})
    model_data.set_system_id({"air_conditioner": "CoolingSystem1"})
    model_data.set_system_id({"heat_pump": "HeatPump1"})
    model_data.set_system_id({"hvac_air_distribution": "HVACAirDistribution1"})
    model_data.set_system_id(
        {"hvac_hydronic_distribution": "HVACHydronicDistribution1"}
    )
    model_data.set_system_id({"primary_dhw": "WaterHeatingSystem1"})
    model_data.set_system_id({"secondary_dhw": "WaterHeatingSystem2"})
    model_data.set_system_id({"dhw_distribution": "HotWaterDistribution1"})

    # Primary heating system as a component of the HVACPlant Section
    primary_heating_result = get_primary_heating_system(h2k_dict, model_data)

    # Primary cooling system as a component of the HVACPlant Section
    # air_conditioner_result = get_air_conditioner(h2k_dict, model_data)
    air_conditioner_result = {}

    # Heat Pumps handled here
    heat_pump_result = get_heat_pump(h2k_dict, model_data)
    # If backup type is integrated, get rid of the heating system
    # print("HEAT PUMP RESULT", heat_pump_result)

    # Always produces a complete dictionary, includes set point information.
    hvac_control_result = get_hvac_control(h2k_dict, model_data)

    # This may be an empty dictionary, e.g. for baseboards, in which case it must not be included in hvac_dict
    hvac_distribution_result = get_hvac_distribution(h2k_dict, model_data)

    primary_heating_id = model_data.get_system_id("primary_heating")
    primary_cooling_id = None
    if heat_pump_result != {}:
        primary_heating_id = model_data.get_system_id("heat_pump")
        primary_cooling_id = model_data.get_system_id("heat_pump")

    heat_pump_backup_type = model_data.get_building_detail("heat_pump_backup_type")

    hvac_dict = {
        "HVACPlant": {
            "PrimarySystems": {
                "PrimaryHeatingSystem": {"@idref": primary_heating_id},
                **(
                    {"PrimaryCoolingSystem": {"@idref": primary_cooling_id}}
                    if primary_cooling_id != None
                    else {}
                ),
            },
            **(
                {}
                if heat_pump_backup_type == "integrated"
                else {"HeatingSystem": primary_heating_result}
            ),
            **({"HeatPump": heat_pump_result} if heat_pump_result != {} else {}),
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

    hot_water_system_result = get_hot_water_systems(h2k_dict, model_data)

    hot_water_distribution_result = get_hot_water_distribution(h2k_dict, model_data)
    water_fixtures_result = get_water_fixtures(h2k_dict, model_data)

    dhw_dict = {
        "WaterHeatingSystem": hot_water_system_result,
        "HotWaterDistribution": hot_water_distribution_result,
        "WaterFixture": water_fixtures_result,
    }

    mech_vent_dict = {
        "VentilationFans": {
            "VentilationFan": {
                "SystemIdentifier": {"@id": "VentilationFan1"},
                "FanType": "heat recovery ventilator",
                "RatedFlowRate": 79.5,
                "HoursInOperation": 24,
                "UsedForWholeBuildingVentilation": "true",
                "SensibleRecoveryEfficiency": 0.75,
                "FanPower": 75.8,
            }
        }
    }

    return {
        "hvac_dict": hvac_dict,
        "dhw_dict": dhw_dict,
        "mech_vent_dict": mech_vent_dict,
    }
