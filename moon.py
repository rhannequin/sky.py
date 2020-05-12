# coding: utf-8

# Usage:
# python moon.py --latitude 48.8638 --longitude 2.4485 --elevation 97 \
# --datetime "2020-05-11 14:00:00"

import argparse
from datetime import datetime
import json

# import math
# from astroquery.jplhorizons import Horizons
# from astropy.coordinates import Angle
from skyfield.api import Topos, load, utc

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
COORDINATES_PRECISION = 4
DEGREE_SYMBOL = "°"
RADIAN_SYMBOL = "rad"


def default_json_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()
    return None


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--latitude")
arg_parser.add_argument("--longitude")
arg_parser.add_argument("--elevation")
arg_parser.add_argument("--datetime")
args = arg_parser.parse_args()

ts = load.timescale(builtin=True)
obersation_time = datetime.strptime(args.datetime, DATETIME_FORMAT).replace(tzinfo=utc)
t = ts.utc(obersation_time)

eph = load("de421.bsp")
earth, moon = eph["earth"], eph["moon"]

observer_location = earth + Topos(
    latitude_degrees=round(float(args.latitude), COORDINATES_PRECISION),
    longitude_degrees=round(float(args.longitude), COORDINATES_PRECISION),
    elevation_m=int(args.elevation),
)
apparent_observation = observer_location.at(t).observe(moon).apparent()
ra, dec, distance = apparent_observation.radec()
alt, az, _ = apparent_observation.altaz()

dumps = json.dumps(
    {
        "right_ascension": {
            "hms": {"value": ra.hstr(), "unit": None},
            "dms": {"value": ra.dstr(warn=False), "unit": None},
            "deg": {"value": ra._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": ra.radians, "unit": RADIAN_SYMBOL},
        },
        "declination": {
            "hms": {"value": dec.hstr(warn=False), "unit": None},
            "dms": {"value": dec.dstr(), "unit": None},
            "deg": {"value": dec._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": dec.radians, "unit": RADIAN_SYMBOL},
        },
        "elevation": {
            "hms": {"value": alt.hstr(warn=False), "unit": None},
            "dms": {"value": alt.dstr(), "unit": None},
            "deg": {"value": alt._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": alt.radians, "unit": RADIAN_SYMBOL},
        },
        "azimuth": {
            "hms": {"value": az.hstr(warn=False), "unit": None},
            "dms": {"value": az.dstr(), "unit": None},
            "deg": {"value": az._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": az.radians, "unit": RADIAN_SYMBOL},
        },
        "distance": {
            "au": {"value": distance.au, "unit": "au"},
            "m": {"value": distance.m, "unit": "m"},
        },
    },
    indent=2,
    default=default_json_converter,
    ensure_ascii=False,
)

print(dumps)


# def generate_hms_property(prop):
#     angle = Angle(prop.data[0], prop.unit)
#     return {
#         "original": {"value": prop.data[0], "unit": prop.unit.name},
#         "si": {"value": degree_to_hms(angle), "unit": "hms"},
#     }


# def generate_dms_property(prop):
#     angle = Angle(prop.data[0], prop.unit)
#     return {
#         "original": {"value": prop.data[0], "unit": prop.unit.name},
#         "si": {"value": degree_to_dms(angle), "unit": "dms"},
#     }


# def generate_deg_property(prop):
#     return {
#         "si": {"value": prop.data[0], "unit": prop.unit.name},
#     }


# def degree_to_hms(degree_angle):
#     h, m, s = degree_angle.hms
#     return f"{math.floor(h)}h {math.floor(m)}m {math.floor(s)}s"


# def degree_to_dms(degree_angle):
#     d, m, s = degree_angle.dms
#     return f"{math.floor(d)}° {math.floor(m)}' {math.floor(s)}\""


# observer = {"lat": 0, "lon": 0, "elevation": 0}


# target = Horizons(
#     id="301",
#     location=observer,
#     id_type="majorbody",
#     epochs={
#         "start": "2020-05-11 14:00:00",  # UTC timezone
#         "stop": "2020-05-11 14:00:01",
#         "step": "1m",
#     },
# )

# eph = target.ephemerides()

# dumps = json.dumps(
#     {
#         "right_ascension": generate_hms_property(eph["RA"]),
#         "declination": generate_dms_property(eph["DEC"]),
#         "azimuth": generate_deg_property(eph["AZ"]),
#         "elevation": generate_deg_property(eph["EL"]),
#     },
#     indent=2,
#     default=default_json_converter,
#     ensure_ascii=False,
# )

# print(dumps)
