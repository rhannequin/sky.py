# coding: utf-8

# Usage:
# python dark.py --latitude 48.8638 --longitude 2.4485 --elevation 97 --date "2020-05-11"

import argparse
import datetime as dt
import json
from skyfield import almanac
from skyfield.api import Topos, load
from utils.json_converter import json_converter
import utils.constants

DATE_FORMAT = "%Y-%m-%d"


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--latitude")
arg_parser.add_argument("--longitude")
arg_parser.add_argument("--elevation")
arg_parser.add_argument("--date")
args = arg_parser.parse_args()


# Figure out local midnight
zone = dt.timezone.utc
time = dt.datetime.strptime(args.date, DATE_FORMAT)
midnight = time.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=zone)
next_midnight = midnight + dt.timedelta(days=1)

ts = load.timescale(builtin=True)
t0 = ts.utc(midnight)
t1 = ts.utc(next_midnight)
eph = load("de421.bsp")
observer_location = Topos(
    latitude_degrees=round(float(args.latitude), utils.constants.COORDINATES_PRECISION),
    longitude_degrees=round(float(args.longitude), utils.constants.COORDINATES_PRECISION),
    elevation_m=int(args.elevation),
)
f = almanac.dark_twilight_day(eph, observer_location)
times, events = almanac.find_discrete(t0, t1, f)

twilight_events = []

for t, e in zip(times, events):
    time = t.astimezone(zone)
    name = almanac.TWILIGHTS[e]
    twilight_events.append({"time": time, "name": name})

dumps = json.dumps(
    {"events": twilight_events}, indent=2, default=json_converter, ensure_ascii=False,
)

print(dumps)
