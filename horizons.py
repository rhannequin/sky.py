# coding: utf-8

# Usage:
# python horizons.py --target 599 --target-type majorbody --location 500 \
# --time "2020-05-05 17:00:00"

import argparse
from datetime import datetime, timedelta
import json
import math
from astroquery.jplhorizons import Horizons


AU_IN_M = 149597870700
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_STEP = "1m"


def default_json_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()
    return None


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--target")
arg_parser.add_argument("--target-type")
arg_parser.add_argument("--location")
arg_parser.add_argument("--time")
args = arg_parser.parse_args()

start_time = datetime.strptime(args.time, DATETIME_FORMAT)
end_time_str = (start_time + timedelta(0, 1)).strftime(DATETIME_FORMAT)

target = Horizons(
    id=args.target,
    location=args.location,
    id_type=args.target_type,
    epochs={"start": args.time, "stop": end_time_str, "step": DEFAULT_STEP,},
)

eph = target.ephemerides(quantities="19,20,22")


dumps = json.dumps(
    {
        "distance_from_the_sun": {"value": math.floor(eph["r"].data[0] * AU_IN_M), "unit": "m"},
        "distance_from_location": {
            "value": math.floor(eph["delta"].data[0] * AU_IN_M),
            "unit": "m",
        },
        "velocity_with_respect_to_the_sun": {
            "value": math.floor(eph["vel_sun"].data[0] * 1000),
            "unit": "m / s",
        },
    },
    indent=2,
    default=default_json_converter,
)

print(dumps)


# https://ssd.jpl.nasa.gov/horizons_batch.cgi?
# batch=1 &
# TABLE_TYPE=OBSERVER &
# QUANTITIES='19,20,22' &
# COMMAND="599" &
# SOLAR_ELONG="0,180" &
# LHA_CUTOFF=0 &
# CSV_FORMAT=YES &
# CAL_FORMAT=BOTH & -- > CAL
# ANG_FORMAT=DEG &  -- > HMS
# APPARENT=AIRLESS &
# REF_SYSTEM=J2000 &
# EXTRA_PREC=NO &
# CENTER='500' &
# START_TIME="2020-05-05+17:00" &
# STOP_TIME="2020-05-05+17:01" &
# STEP_SIZE="1h" &
# SKIP_DAYLT=NO
