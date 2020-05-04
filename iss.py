# coding: utf-8

# Usage:
# python iss.py --latitude 48.8638 --longitude 2.4485 --elevation 97 \
# --pressure 0 --horizon 00:00 --step 60

import argparse
import datetime
import json
import math
import ephem

AU_IN_KM = 149597871
MAXIMUM_VISIBLE_MAGNITUDE = -0.5


def default_json_converter(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    return None

# Credits to Liam Kennedy
# https://stackoverflow.com/questions/19759501/calculating-the-phase-angle-\
# between-the-sun-iss-and-an-observer-on-the-earth


def get_magnitude(light_source, target):
    a = light_source.earth_distance * AU_IN_KM - ephem.earth_radius
    b = target.range / 1000
    angle_c = ephem.separation(
        (target.az, target.alt), (light_source.az, light_source.alt))
    c = math.sqrt(math.pow(a, 2) + math.pow(b, 2) -
                  2 * a * b * math.cos(angle_c))
    angle_a = math.acos(
        (math.pow(b, 2) + math.pow(c, 2) - math.pow(a, 2)) / (2 * b * c))
    return -1.3 - 15 + 5 * math.log10(target.range / 1000) - 2.5 * math.log10(
        math.sin(angle_a)+((math.pi-angle_a)*math.cos(angle_a)))


def generate_event(event_time, target, light_source):
    obs.date = event_time
    light_source.compute(obs)
    target.compute(obs)
    return {
        "hour": event_time,
        "altitude": target.alt,
        "azimuth": target.az,
        "magnitude": get_magnitude(light_source, target),
        "distance_from_earth": target.range / 1000,
        "eclipsed": target.eclipsed,
        "sun_altitude": light_source.alt
    }


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--latitude')
arg_parser.add_argument('--longitude')
arg_parser.add_argument('--elevation')
arg_parser.add_argument('--pressure')
arg_parser.add_argument('--horizon')
arg_parser.add_argument('--step')
args = arg_parser.parse_args()

iss = ephem.readtle(
    "ISS",
    "1 25544U 98067A   20124.51596176  .00016717  00000-0  10270-3 0  9040",
    "2 25544  51.6426 209.5696 0001578 232.9055 127.1951 15.49338516 25086"
)

sun = ephem.Sun()
obs = ephem.Observer()
obs.lat = args.latitude
obs.long = args.longitude
obs.elevation = int(args.elevation)
obs.pressure = int(args.pressure)
obs.horizon = args.horizon

rendered_next_visible = False

# As long as we don't have a visible pass
while not rendered_next_visible:

    obs.date = obs.date.datetime()
    # We get the next pass from the current date
    rise_time, _, maximum_altitude_time, _, set_time, _ = obs.next_pass(iss)

    # We set the current date at the pass' maximum altitude time
    # to ensure we check if the pass is visible from the middle of the event
    obs.date = maximum_altitude_time.datetime()
    iss.compute(obs)
    sun.compute(obs)
    mag = get_magnitude(sun, iss)

    # We check if the pass is visible or not: ISS eclipsed or magnitude not high
    # enough

    # FIXME: this is not good because sometimes the ISS enters or leaves Earth's
    # shadow before or after being at its maximum altitude.
    # For instance: https://heavens-above.com/passdetails.aspx?lat=48.8638\
    # &lng=2.4485&alt=97&tz=UCT&satid=25544&mjd=58974.0759329665

    if iss.eclipsed or mag > MAXIMUM_VISIBLE_MAGNITUDE:
        # The pass is not visible, we set the current date to right after the
        # pass is finished to get a new one from the loop
        obs.date = set_time.datetime()
        continue

    # This pass is visible, let's get all the information

    rendered_next_visible = True

    times = []
    # We set the current time to the very first beginning of the pass
    current_time = rise_time.datetime()

    # Loop from the very beginning to the very last moment of the event
    while current_time < set_time.datetime():
        times.append(current_time)
        current_time = current_time + datetime.timedelta(0, int(args.step))

    events_list = []

    # For every intervalle of time from the start to the end of the event,
    # get ISS information
    for time in times:
        event = generate_event(time, iss, sun)
        events_list.append(event)

    dumps = json.dumps({
        'longitude': obs.long,
        'latitude': obs.lat,
        'elevation': obs.elevation,
        'pressure': obs.pressure,
        'main_events': {
            'rise': generate_event(rise_time.datetime(), iss, sun),
            # PAS BON À VÉRIFIER
            'maximum': generate_event(
                maximum_altitude_time.datetime(), iss, sun),
            'set': generate_event(set_time.datetime(), iss, sun)
        },
        'events': events_list
    }, indent=2, default=default_json_converter)

    print(dumps)

# Sun altitude -14:46:57.4 => Degrees minutes seconds
# Sun altitude -0.2580050528049469 => radians
