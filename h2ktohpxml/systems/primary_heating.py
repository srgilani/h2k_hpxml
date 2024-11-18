import math

from ..utils import obj, h2k


# Translates data from the "Type1" heating system section of h2k
def get_primary_heating_system(h2k_dict, model_data):

    type1_heating_system = obj.get_val(h2k_dict, "HouseFile,House,HeatingCooling,Type1")

    # h2k files cannot be built without a Type 1 heating system, so we don't need to check for the presence of one
    type1_type = [x for x in list(type1_heating_system.keys()) if x != "FansAndPump"][0]

    type1_data = type1_heating_system.get(type1_type, {})

    print("type1 system type", type1_type)

    # Only one primary heating system, define its id
    model_data.set_system_id({"primary_heating": "HeatingSystem1"})

    primary_heating_dict = {}
    if type1_type == "Baseboards":
        # TODO: Remove after testing
        model_data.set_is_hvac_translated(True)
        primary_heating_dict = get_electric_resistance(
            type1_data, model_data.get_system_id("primary_heating")
        )

    return primary_heating_dict


# Translates h2k's Baseboards Type1 system
def get_electric_resistance(type1_data, primary_heating_id):

    baseboard_capacity = h2k.get_number_field(type1_data, "baseboard_capacity")
    baseboard_efficiency = h2k.get_number_field(type1_data, "baseboard_efficiency")

    # By default we assume electric resistance, overwriting with radiant if present
    # “baseboard”, “radiant floor”, or “radiant ceiling”
    elec_resistance = {
        "SystemIdentifier": {"@id": primary_heating_id},
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

    print(elec_resistance)

    # TODO: FractionHeatLoadServed is not allowed if this is a heat pump backup system
    # Also must sum to 1 across all heating systems

    return elec_resistance
