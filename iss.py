# coding: utf-8

# Usage:
# python iss.py --latitude 51.5073 --longitude -0.1276 --elevation 0.0 --horizon 10.0 \
# --start_datetime "2022-03-22 00:00:00" --end_datetime "2022-03-23 00:00:00"

# High inspired from https://github.com/redraw/groundtrack-api

# TODO: missing events, when available:
# rises (above 0°)
# gets outs of shadow
# above horizon set limit
# culmination
# below horizon set limit
# enters shadow
# sets (below 0°)

import json
import argparse
from datetime import datetime
from skyfield.api import EarthSatellite, Topos, utc
from skyfield.api import load as skyfield_load
from more_itertools import chunked
import utils.constants
from utils.json_converter import json_converter


ISS_TLE_IDENTIFIER = "ISS (ZARYA)"
ISS_TLE_LINE1 = "1 25544U 98067A   22080.68009259  .00003410  00000-0  68902-4 0  9998"
ISS_TLE_LINE2 = "2 25544  51.6437  49.9813 0004101 297.5850  44.2706 15.49480131331606"


class SatTracker:
    def __init__(self, lat, lon, elevation, horizon=10.0):
        self.eph = skyfield_load("de421.bsp")
        self.timescale = skyfield_load.timescale()
        self.horizon = horizon
        self.observer = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)
        self.satellite = EarthSatellite(ISS_TLE_LINE1, ISS_TLE_LINE2, ISS_TLE_IDENTIFIER, self.timescale)

    def next_passes(self, starts_at, ends_at, visible_only=False):
        passes = []

        # Find satellite events for observer
        times, events = self.satellite.find_events(
            self.observer, starts_at, ends_at, altitude_degrees=self.horizon
        )

        # Each pass is composed by 3 events (rise, culmination, set)
        # Start arrays on next first pass
        offset = len(events) % 3
        times = times[offset:]
        events = events[offset:]

        # Loop for each pass (3 events)
        for pass_times, pass_events in zip(chunked(times, 3), chunked(events, 3)):
            full_pass = self.serialize_pass(pass_times, pass_events)
            full_pass["visible"] = any(event["visible"] for event in full_pass.values())
            passes.append(full_pass)

        # Filter visible ones
        if visible_only:
            passes = [p for p in passes if p["visible"]]

        return passes

    def serialize_pass(self, pass_times, pass_events):
        full_pass = {}
        observer_barycenter = self.eph["earth"] + self.observer

        for time, event_type in zip(pass_times, pass_events):
            geometric_sat = (self.satellite - self.observer).at(time)
            geometric_sun = (self.eph["sun"] - observer_barycenter).at(time)

            sat_alt, sat_az, sat_d = geometric_sat.altaz()
            sun_alt, sun_az, sun_d = geometric_sun.altaz()

            is_sunlit = geometric_sat.is_sunlit(self.eph)
            event = ('rise', 'culmination', 'set')[event_type]

            is_visible = -18 <= int(sun_alt.degrees) <= -6 and bool(is_sunlit)

            full_pass[event] = {
                "alt": f"{sat_alt.degrees:.2f}",
                "az": f"{sat_az.degrees:.2f}",
                "utc_datetime": str(time.utc_datetime()),
                "utc_timestamp": int(time.utc_datetime().timestamp()),
                "is_sunlit": bool(is_sunlit),
                "visible": is_visible
            }

        return full_pass


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--latitude")
arg_parser.add_argument("--longitude")
arg_parser.add_argument("--elevation")
arg_parser.add_argument("--horizon")
arg_parser.add_argument("--start_datetime")
arg_parser.add_argument("--end_datetime")
args = arg_parser.parse_args()

ts = skyfield_load.timescale(builtin=True)
start_time = ts.utc(
    datetime.strptime(args.start_datetime, utils.constants.DATETIME_FORMAT).replace(tzinfo=utc)
)
end_time = ts.utc(
    datetime.strptime(args.end_datetime, utils.constants.DATETIME_FORMAT).replace(tzinfo=utc)
)

tracker = SatTracker(float(args.latitude), float(args.longitude), float(args.elevation), float(args.horizon))
next_passes = tracker.next_passes(starts_at=start_time, ends_at=end_time, visible_only=True)

dumps = json.dumps(next_passes, indent=2, default=json_converter)
print(dumps)
