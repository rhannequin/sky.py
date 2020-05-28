# coding: utf-8

# Usage:
# python moon.py --latitude 48.8638 --longitude 2.4485 --elevation 97 \
# --datetime "2020-05-11 14:00:00"

import argparse
from datetime import datetime, timedelta
import json
from skyfield.api import Topos, load, utc
from skyfield import almanac
from utils.json_converter import json_converter

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
COORDINATES_PRECISION = 4
DEGREE_SYMBOL = "°"
RADIAN_SYMBOL = "rad"
MOON_TOTAL_PHASE_ANGLE = 360.0
APPROXIMATIVE_MOON_REVOLUTION_DAYS = 30
NEW_MOON_IDENTIFIER = 0


def detailled_coordinates(right_ascension, declination, elevation, azimuth, distance):
    return {
        "right_ascension": {
            "hms": {"value": right_ascension.hstr(), "unit": None},
            "dms": {"value": right_ascension.dstr(warn=False), "unit": None},
            "deg": {"value": right_ascension._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": right_ascension.radians, "unit": RADIAN_SYMBOL},
        },
        "declination": {
            "hms": {"value": declination.hstr(warn=False), "unit": None},
            "dms": {"value": declination.dstr(), "unit": None},
            "deg": {"value": declination._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": declination.radians, "unit": RADIAN_SYMBOL},
        },
        "elevation": {
            "hms": {"value": elevation.hstr(warn=False), "unit": None},
            "dms": {"value": elevation.dstr(), "unit": None},
            "deg": {"value": elevation._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": elevation.radians, "unit": RADIAN_SYMBOL},
        },
        "azimuth": {
            "hms": {"value": azimuth.hstr(warn=False), "unit": None},
            "dms": {"value": azimuth.dstr(), "unit": None},
            "deg": {"value": azimuth._degrees, "unit": DEGREE_SYMBOL},
            "rad": {"value": azimuth.radians, "unit": RADIAN_SYMBOL},
        },
        "distance": {
            "au": {"value": distance.au, "unit": "au"},
            "m": {"value": distance.m, "unit": "m"},
        },
    }


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--latitude")
arg_parser.add_argument("--longitude")
arg_parser.add_argument("--elevation")
arg_parser.add_argument("--datetime")
args = arg_parser.parse_args()

timescale = load.timescale(builtin=True)
observation_datetime = datetime.strptime(args.datetime, DATETIME_FORMAT).replace(tzinfo=utc)
observation_time = timescale.utc(observation_datetime)

eph = load("de421.bsp")
sun, earth, moon = eph["sun"], eph["earth"], eph["moon"]

observer_topos = Topos(
    latitude_degrees=round(float(args.latitude), COORDINATES_PRECISION),
    longitude_degrees=round(float(args.longitude), COORDINATES_PRECISION),
    elevation_m=int(args.elevation),
)
observer_location = earth + observer_topos
position = observer_location.at(observation_time)
apparent_observation = observer_location.at(observation_time).observe(moon).apparent()


# Coordinates

ra, dec, dist = apparent_observation.radec()
alt, az, _ = apparent_observation.altaz()


# Current phase

_, sun_ecliptic_longitude, _ = (
    observer_location.at(observation_time).observe(sun).apparent().ecliptic_latlon()
)
_, moon_ecliptic_latitude, _ = apparent_observation.ecliptic_latlon()
current_phase = (
    moon_ecliptic_latitude.degrees - sun_ecliptic_longitude.degrees
) % MOON_TOTAL_PHASE_ANGLE


# Phases

phrase_start_date = observation_datetime - timedelta(days=APPROXIMATIVE_MOON_REVOLUTION_DAYS)
phrase_end_date = observation_datetime + timedelta(days=APPROXIMATIVE_MOON_REVOLUTION_DAYS)
phrase_start_time = timescale.utc(
    phrase_start_date.year, phrase_start_date.month, phrase_start_date.day
)
phrase_end_time = timescale.utc(phrase_end_date.year, phrase_end_date.month, phrase_end_date.day)

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


# Rising and setting

next_day = observation_datetime + timedelta(days=1)
next_day_time = timescale.utc(next_day)
rs_almanac = almanac.risings_and_settings(eph, moon, observer_topos)
rs_times, rs_moments = almanac.find_discrete(observation_time, next_day_time, rs_almanac)


# JSON build

data = detailled_coordinates(ra, dec, alt, az, dist)

for rs_time, rs_moment in zip(rs_times, rs_moments):
    rs_apparent = observer_location.at(rs_time).observe(moon).apparent()
    rs_ra, rs_dec, rs_dist = rs_apparent.radec()
    rs_alt, rs_az, _ = rs_apparent.altaz()
    rs_coordinates = detailled_coordinates(rs_ra, rs_dec, rs_alt, rs_az, rs_dist)
    moment_name = "rises" if rs_moment else "sets"
    data[moment_name] = {**rs_coordinates, "datetime": rs_time.utc_datetime()}

data["current_phase"] = current_phase
data["phases"] = moon_phases


dumps = json.dumps(data, indent=2, default=json_converter, ensure_ascii=False,)

print(dumps)
