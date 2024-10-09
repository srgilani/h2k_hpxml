# Utility function to perform unit conversions, including map of unit conversions

unit_map = {
    "length": {
        "ft": {
            "m": {"scale": 0.3048, "offset": 0.0},
            "mm": {"scale": 304.8, "offset": 0.0},
            "cm": {"scale": 30.48, "offset": 0.0},
            "in": {"scale": 12.0, "offset": 0.0},
        },
        "m": {
            "ft": {"scale": 3.28084, "offset": 0.0},
            "mm": {"scale": 1000.0, "offset": 0.0},
            "cm": {"scale": 100.0, "offset": 0.0},
            "in": {"scale": 39.3701, "offset": 0.0},
        },
        "mm": {
            "ft": {"scale": 0.00328084, "offset": 0.0},
            "m": {"scale": 0.001, "offset": 0.0},
            "cm": {"scale": 0.1, "offset": 0.0},
            "in": {"scale": 0.0393701, "offset": 0.0},
        },
        "cm": {
            "ft": {"scale": 0.0328084, "offset": 0.0},
            "mm": {"scale": 10.0, "offset": 0.0},
            "m": {"scale": 0.01, "offset": 0.0},
            "in": {"scale": 0.393701, "offset": 0.0},
        },
        "in": {
            "ft": {"scale": 0.0833333, "offset": 0.0},
            "mm": {"scale": 25.4, "offset": 0.0},
            "cm": {"scale": 2.54, "offset": 0.0},
            "m": {"scale": 0.0254, "offset": 0.0},
        },
    },
    "area": {
        "in2": {
            "m2": {"scale": 0.00064516, "offset": 0.0},
            "cm2": {"scale": 6.4516, "offset": 0.0},
            "ft2": {"scale": 0.00694443888889, "offset": 0.0},
        },
        "m2": {
            "in2": {"scale": 1550.0047740100001, "offset": 0.0},
            "cm2": {"scale": 10000.0, "offset": 0.0},
            "ft2": {"scale": 10.7639111056, "offset": 0.0},
        },
        "cm2": {
            "in2": {"scale": 0.155000477401, "offset": 0.0},
            "m2": {"scale": 0.0001, "offset": 0.0},
            "ft2": {"scale": 0.00107639111056, "offset": 0.0},
        },
        "ft2": {
            "in2": {"scale": 144.0, "offset": 0.0},
            "cm2": {"scale": 929.0304, "offset": 0.0},
            "m2": {"scale": 0.09290304, "offset": 0.0},
        },
    },
    "volume": {
        "gal_imp": {
            "L": {"scale": 4.54609, "offset": 0.0},
            "ft3": {"scale": 0.160544, "offset": 0.0},
            "m3": {"scale": 0.00454609, "offset": 0.0},
            "gal_us": {"scale": 1.20095, "offset": 0.0},
        },
        "m3": {
            "gal_imp": {"scale": 219.969, "offset": 0.0},
            "ft3": {"scale": 35.31467011169671, "offset": 0.0},
            "L": {"scale": 1000.0, "offset": 0.0},
            "gal_us": {"scale": 264.172, "offset": 0.0},
        },
        "ft3": {
            "gal_imp": {"scale": 6.22884, "offset": 0.0},
            "m3": {"scale": 0.0283168, "offset": 0.0},
            "L": {"scale": 28.3168, "offset": 0.0},
            "gal_us": {"scale": 7.48052, "offset": 0.0},
        },
        "L": {
            "gal_imp": {"scale": 0.219969, "offset": 0.0},
            "ft3": {"scale": 0.0353147, "offset": 0.0},
            "m3": {"scale": 0.001, "offset": 0.0},
            "gal_us": {"scale": 0.264172, "offset": 0.0},
        },
        "gal_us": {
            "gal_imp": {"scale": 0.832674, "offset": 0.0},
            "ft3": {"scale": 0.133681, "offset": 0.0},
            "m3": {"scale": 0.00378541, "offset": 0.0},
            "L": {"scale": 3.78541, "offset": 0.0},
        },
    },
    "thermal_resistance": {
        "R": {"RSI": {"scale": 0.17611028730632272, "offset": 0.0}},
        "RSI": {"R": {"scale": 5.67826, "offset": 0.0}},
    },
    "airFlow": {
        "L/s": {"cfm": {"scale": 2.118882, "offset": 0}},
        "cfm": {"L/s": {"scale": 0.471946998, "offset": 0}},
    },
}


def convert_unit(val, unit_type, input_unit, output_unit):
    # converts units of val of unit_type from input_unit to output_unit
    conversions = unit_map.get(unit_type, {}).get(input_unit, {}).get(output_unit, {})
    if "scale" not in conversions.keys():
        return val

    if input_unit == output_unit:
        return val

    return conversions["scale"] * val + conversions["offset"]
