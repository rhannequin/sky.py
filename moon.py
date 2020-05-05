# coding: utf-8

# Usage:
# python moon.py

from datetime import datetime
import json
import math
import ephem
from astroquery.jplhorizons import Horizons
from astropy.coordinates import Angle


def default_json_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()
    return None


def generate_property(prop):
    angle = Angle(prop.data[0], prop.unit)
    return [
        {"value": prop.data[0], "unit": prop.unit.name},
        {"value": degree_to_hms(angle), "unit": "hms"},
    ]


def degree_to_hms(degree_angle):
    h, m, s = degree_angle.hms
    return f"{math.floor(h)}h {math.floor(m)}m {math.floor(s)}s"


observer = {"lat": 48.8638, "lon": 2.4485, "elevation": 97}


target = Horizons(
    id="301",
    location=observer,
    id_type="majorbody",
    epochs={
        "start": "2020-05-05 17:00:00",  # FIXME: is it in UTC?
        "stop": "2020-05-05 17:00:01",
        "step": "1m",
    },
)

eph = target.ephemerides()

dumps = json.dumps(
    {
        "right_ascension": generate_property(eph["RA"]),
        "declination": generate_property(eph["DEC"]),  # FIXME: SI unit is DMS
        "azimuth": generate_property(eph["AZ"]),  # FIXME: SI unit is degree
        "elevation": generate_property(eph["EL"]),  # FIXME: SI unit is degree
    },
    indent=2,
    default=default_json_converter,
)

print(dumps)

moon = ephem.Moon()
obs = ephem.Observer()
obs.lat = 48.8638
obs.long = 2.4485
obs.elevation = 97
obs.pressure = 0
obs.horizon = "00:00"
obs.date = "2020/05/05 17:00:00"  # FIXME: is it in UTC?
moon.compute(obs)

print()

print("RA:", moon.ra, "(deg),", repr(moon.ra), "(rad" ")")
print("DEC:", moon.dec, "(deg),", repr(moon.dec), "(rad" ")")
print("AZ:", moon.az, "(deg),", repr(moon.az), "(rad" ")")
print("EL:", moon.alt, "(deg),", repr(moon.alt), "(rad" ")")

dumps = json.dumps(
    {
        "right_ascension": {"value": moon.ra, "unit": "rad"},
        "declination": {"value": moon.dec, "unit": "rad"},
        "azimuth": {"value": moon.az, "unit": "rad"},
        "elevation": {"value": moon.alt, "unit": "rad"},
    },
    indent=2,
    default=default_json_converter,
)

print(dumps)
