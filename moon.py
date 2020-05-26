# coding: utf-8

# Usage:
# python moon.py --latitude 48.8638 --longitude 2.4485 --elevation 97 \
# --datetime "2020-05-11 14:00:00"

import argparse
from datetime import datetime, timedelta
import json

from skyfield.api import Topos, load, utc
from skyfield import almanac

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
COORDINATES_PRECISION = 4
DEGREE_SYMBOL = "°"
RADIAN_SYMBOL = "rad"
MOON_TOTAL_PHASE_ANGLE = 360.0
APPROXIMATIVE_MOON_REVOLUTION_DAYS = 30
NEW_MOON_IDENTIFIER = 0


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
sun, earth, moon = eph["sun"], eph["earth"], eph["moon"]

observer_location = earth + Topos(
    latitude_degrees=round(float(args.latitude), COORDINATES_PRECISION),
    longitude_degrees=round(float(args.longitude), COORDINATES_PRECISION),
    elevation_m=int(args.elevation),
)
position = observer_location.at(t)
apparent_observation = observer_location.at(t).observe(moon).apparent()


# Coordinates

ra, dec, distance = apparent_observation.radec()
alt, az, _ = apparent_observation.altaz()


# Current phase

_, sun_ecliptic_longitude, _ = observer_location.at(t).observe(sun).apparent().ecliptic_latlon()
_, moon_ecliptic_latitude, _ = apparent_observation.ecliptic_latlon()
current_phase = (
    moon_ecliptic_latitude.degrees - sun_ecliptic_longitude.degrees
) % MOON_TOTAL_PHASE_ANGLE


# Phases

observation_date = datetime.strptime(args.datetime, DATETIME_FORMAT).replace(tzinfo=utc)
phrase_start_date = observation_date - timedelta(days=APPROXIMATIVE_MOON_REVOLUTION_DAYS)
phrase_end_date = observation_date + timedelta(days=APPROXIMATIVE_MOON_REVOLUTION_DAYS)
observation_time = ts.utc(observation_date.year, observation_date.month, observation_date.day)
phrase_start_time = ts.utc(phrase_start_date.year, phrase_start_date.month, phrase_start_date.day)
phrase_end_time = ts.utc(phrase_end_date.year, phrase_end_date.month, phrase_end_date.day)

moon_phases = almanac.moon_phases(eph)

previous_phases_times, previous_phases_indentifiers = almanac.find_discrete(
    phrase_start_time, observation_time, moon_phases,
)

next_phases_times, next_phases_indentifiers = almanac.find_discrete(
    observation_time, phrase_end_time, moon_phases,
)

moon_phases = []

previous_phases = zip(reversed(previous_phases_times), reversed(previous_phases_indentifiers))
previous_new_moon_selected = False
for phase_time, phase_identifier in previous_phases:
    if previous_new_moon_selected:
        break
    if phase_identifier == NEW_MOON_IDENTIFIER:
        previous_new_moon_selected = True
    moon_phases.append(
        {"name": almanac.MOON_PHASES[phase_identifier], "datetime": phase_time.utc_datetime()}
    )

moon_phases.reverse()

next_phases = zip(next_phases_times, next_phases_indentifiers)
next_new_moon_selected = False
for phase_time, phase_identifier in next_phases:
    if next_new_moon_selected:
        break
    if phase_identifier == NEW_MOON_IDENTIFIER:
        next_new_moon_selected = True
    moon_phases.append(
        {"name": almanac.MOON_PHASES[phase_identifier], "datetime": phase_time.utc_datetime()}
    )


# JSON build

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
        "current_phase": {"deg": {"value": current_phase, "unit": DEGREE_SYMBOL},},
        "phases": moon_phases,
    },
    indent=2,
    default=default_json_converter,
    ensure_ascii=False,
)

print(dumps)
