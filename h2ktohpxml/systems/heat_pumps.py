import math

from ..utils import obj, h2k


# Translates heat pump data from the "Type2" heating system section of h2k
# TODO: all backup types are defined as "integrated", need to add support for "separate"
def get_heat_pump(h2k_dict, model_data):

    type2_heating_system = obj.get_val(h2k_dict, "HouseFile,House,HeatingCooling,Type2")

    # h2k files cannot be built without a Type 1 heating system, so we don't need to check for the presence of one
    type2_type = [
        x for x in list(type2_heating_system.keys()) if x != "@shadingInF280Cooling"
    ]

    type2_type = "None" if len(type2_type) == 0 else type2_type[0]

    # print("type2_type", type2_type)
    type2_data = type2_heating_system.get(type2_type, {})

    # Get common specs
    hp_heating_eff = h2k.get_number_field(type2_data, "heat_pump_heating_efficiency")
    hp_cooling_eff = h2k.get_number_field(type2_data, "heat_pump_cooling_efficiency")
    hp_capacity = h2k.get_number_field(type2_data, "heat_pump_capacity")

    is_heating_cop = (
        obj.get_val(type2_data, "Specifications,HeatingEfficiency,@isCop") == "true"
    )
    is_cooling_cop = (
        obj.get_val(type2_data, "Specifications,CoolingEfficiency,@isCop") == "true"
    )

    if is_heating_cop:
        hp_heating_cop = hp_heating_eff
    else:
        hp_heating_cop = hp_heating_eff * (1 / 3.412)

    if is_cooling_cop:
        hp_cooling_eer = hp_cooling_eff * 3.412
    else:
        # TODO: in v11.13, we can use the raw value here because they moved from SEER to EER
        hp_cooling_eer = -0.02 * (hp_cooling_eff**2) + 1.12 * hp_cooling_eff

    # Get backup system details
    heat_pump_backup_type = model_data.get_building_detail(
        "heat_pump_backup_type"
    )  # "separate" or "integrated"
    heat_pump_backup_system = model_data.get_building_detail("heat_pump_backup_system")
    heat_pump_backup_fuel = model_data.get_building_detail("heat_pump_backup_fuel")
    heat_pump_backup_efficiency = model_data.get_building_detail(
        "heat_pump_backup_efficiency"
    )
    heat_pump_backup_eff_unit = model_data.get_building_detail(
        "heat_pump_backup_eff_unit"
    )
    heat_pump_backup_autosized = model_data.get_building_detail(
        "heat_pump_backup_autosized"
    )
    heat_pump_backup_capacity = model_data.get_building_detail(
        "heat_pump_backup_capacity"
    )
    heat_pump_backup_system_id = model_data.get_building_detail(
        "heat_pump_backup_system_id"
    )

    # Get switchover information
    switchover_type = h2k.get_selection_field(type2_data, "heat_pump_switchover_type")
    switchover_temp = -7.6  # -22C
    if switchover_type == "restricted":
        switchover_temp = h2k.get_number_field(type2_data, "heat_pump_switchover_temp")
    elif switchover_type == "unrestricted":
        switchover_temp = -40  # -40C, placeholder value to prevent switchover
    elif switchover_type == "balance":
        # Use default behaviour depending on different heat pump types (until comparison testing between the two engines)
        pass

    heat_pump_dict = {}
    if type2_type == "AirHeatPump":
        # Default backup logic for central ASHP
        # If neither CompressorLockoutTemperature nor BackupHeatingSwitchoverTemperature provided,
        # CompressorLockoutTemperature defaults to 25F if fossil fuel backup
        # otherwise -20F if CompressorType is “variable speed” otherwise 0F.

        # Default backup logic for mini split ASHP
        # If neither CompressorLockoutTemperature nor BackupHeatingSwitchoverTemperature provided,
        # CompressorLockoutTemperature defaults to 25F if fossil fuel backup otherwise -20F.

        # Default backup logic for packaged terminal ASHP
        # If neither CompressorLockoutTemperature nor BackupHeatingSwitchoverTemperature provided,
        # CompressorLockoutTemperature defaults to 25F if fossil fuel backup otherwise 0F.

        print("ASHP DETECTED")

    elif type2_type == "WaterHeatPump":
        print("WSHP DETECTED")

    elif type2_type == "GroundHeatPump":
        print("GSHP DETECTED")
        # print(type2_data)

        # TODO: Check if we ever need more logic around distribution system splitting
        # TODO: separate back-up needs switchover temperature information "BackupHeatingSwitchoverTemperature"

        # A separate backup is used if the primary heating system type is a baseboard, boiler, stove, or fireplace, integrated if furnace.
        heat_pump_dict = {
            "SystemIdentifier": {"@id": model_data.get_system_id("heat_pump")},
            "DistributionSystem": {
                "@idref": model_data.get_system_id("hvac_air_distribution")
            },
            "HeatPumpType": "ground-to-air",
            "HeatPumpFuel": "electricity",
            # "HeatingCapacity": hp_capacity,  # TODO: autosized
            # "CoolingCapacity": hp_capacity,  # TODO: autosized
            "CoolingSensibleHeatFraction": 0.76,  # TODO: tie to file
            **(
                {
                    "BackupType": "separate",
                    "BackupSystem": {"@idref": heat_pump_backup_system_id},
                }
                if heat_pump_backup_type == "separate"
                else {}
            ),
            **(
                {
                    "BackupType": "integrated",
                    "BackupSystemFuel": heat_pump_backup_fuel,
                    "BackupAnnualHeatingEfficiency": {
                        "Units": heat_pump_backup_eff_unit,
                        "Value": heat_pump_backup_efficiency,
                    },
                    **(
                        {}
                        if heat_pump_backup_autosized
                        else {"BackupHeatingCapacity": heat_pump_backup_capacity}
                    ),
                    **(
                        {}
                        if switchover_type == "balance"
                        else {"BackupHeatingSwitchoverTemperature": switchover_temp}
                    ),
                }
                if heat_pump_backup_type == "integrated"
                else {}
            ),
            "FractionHeatLoadServed": 1,
            "FractionCoolLoadServed": 1,
            "AnnualCoolingEfficiency": {
                "Units": "EER",  # only option
                "Value": round(hp_cooling_eer, 2),
            },
            "AnnualHeatingEfficiency": {
                "Units": "COP",  # only option
                "Value": round(hp_heating_cop, 2),
            },
            # extension
        }

        model_data.set_ac_hp_distribution_type("air_regular velocity")

    # print("NO HEAT PUMP")

    return heat_pump_dict
