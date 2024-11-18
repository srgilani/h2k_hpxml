import math

from ..utils import obj, h2k


# Translates data from the "Type1" heating system section of h2k
def get_primary_heating_system(h2k_dict, model_data):

    type1_heating_system = obj.get_val(h2k_dict, "HouseFile,House,HeatingCooling,Type1")

    # h2k files cannot be built without a Type 1 heating system, so we don't need to check for the presence of one
    type1_type = [x for x in list(type1_heating_system.keys()) if x != "FansAndPump"][0]

    type1_data = type1_heating_system.get(type1_type, {})

    print("type1 system type", type1_type)

    primary_heating_dict = {}
    if type1_type == "Baseboards":
        # TODO: Remove is_hvac_translated flag after testing
        model_data.set_is_hvac_translated(True)
        primary_heating_dict = get_electric_resistance(type1_data, model_data)

    elif type1_type == "Furnace":
        # model_data.set_is_hvac_translated(True)
        primary_heating_dict = get_furnace(type1_data, model_data)

    return primary_heating_dict


# Translates h2k's Baseboards Type1 system
def get_electric_resistance(type1_data, model_data):

    baseboard_capacity = h2k.get_number_field(type1_data, "baseboard_capacity")
    baseboard_efficiency = h2k.get_number_field(type1_data, "baseboard_efficiency")

    # By default we assume electric resistance, overwriting with radiant if present
    # “baseboard”, “radiant floor”, or “radiant ceiling”
    elec_resistance = {
        "SystemIdentifier": {"@id": model_data.get_system_id("primary_heating")},
        "HeatingSystemType": {
            "ElectricResistance": {"ElectricDistribution": "baseboard"}
        },
        "HeatingSystemFuel": "electricity",
        "HeatingCapacity": baseboard_capacity,
        "AnnualHeatingEfficiency": {
            "Units": "Percent",  # Only unit type allowed here. Note actual value must be a fraction
            "Value": baseboard_efficiency,
        },
        "FractionHeatLoadServed": 1,  # Hardcoded for now
    }

    print("BASEBOARD: ", elec_resistance)

    # TODO: FractionHeatLoadServed is not allowed if this is a heat pump backup system
    # Also must sum to 1 across all heating systems

    return elec_resistance


def get_furnace(type1_data, model_data):
    # Currently, this portion of the HPXML doesn't have an analog for the "Equipment type" field

    furnace_capacity = h2k.get_number_field(type1_data, "furnace_capacity")

    furnace_efficiency = h2k.get_number_field(type1_data, "furnace_efficiency")

    # TODO: The documentation makes it look like the Units can be set to "Percent", but this throws an error when simulating
    # Currently hardcoded to AFUE
    is_steady_state = obj.get_val(type1_data, "Specifications,@isSteadyState")

    furnace_sizing_factor = h2k.get_number_field(type1_data, "furnace_sizing_factor")
    is_auto_sized = (
        "Calculated" == obj.get_val(type1_data, "Specifications,OutputCapacity,English")
        or furnace_capacity == 0
    )

    furnace_pilot_light = h2k.get_number_field(type1_data, "furnace_pilot_light")

    furnace_fuel_type = h2k.get_selection_field(type1_data, "furnace_fuel_type")

    # TODO: confirm desired behaviour around auto-sizing
    furnace_dict = {
        "SystemIdentifier": {"@id": model_data.get_system_id("primary_heating")},
        "DistributionSystem": {"@idref": model_data.get_system_id("hvac_distribution")},
        "HeatingSystemType": {
            "Furnace": None
        },  # potential to add pilot light info later
        "HeatingSystemFuel": furnace_fuel_type,
        **({} if is_auto_sized else {"HeatingCapacity": furnace_capacity}),
        "AnnualHeatingEfficiency": {
            "Units": (
                "AFUE"  # "Percent" if is_steady_state == "true" else "AFUE"
            ),  # "AFUE" / "Percent"
            "Value": furnace_efficiency,
        },
        "FractionHeatLoadServed": 1,
        **(
            {"extension": {"HeatingAutosizingFactor": furnace_sizing_factor}}
            if is_auto_sized
            else {}
        ),
    }

    # TODO: FractionHeatLoadServed is not allowed if this is a heat pump backup system
    # Also must sum to 1 across all heating systems

    # Add pilot light if present
    if furnace_pilot_light > 0:
        furnace_dict["HeatingSystemType"] = {
            "Furnace": {
                "PilotLight": "true",
                "extension": {"PilotLightBtuh": furnace_pilot_light},
            }
        }

    print("FURNACE: ", furnace_dict)

    # No h2k representation for "gravity" distribution type
    # Might need to update this based on logic around system types
    model_data.set_hvac_distribution_type("air_regular velocity")

    return furnace_dict
