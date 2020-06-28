from skyfield.api import load
from skyfield.searchlib import find_maxima

ts = load.timescale(builtin=True)
planets = load("de421.bsp")

earth, sun, venus = planets["earth"], planets["sun"], planets["venus"]

venus_elongation_degrees.rough_period = 1.0

t1 = ts.utc(2018)
t2 = ts.utc(2023)
t, values = find_maxima(t1, t2, venus_elongation_degrees)

def venus_elongation_degrees(time):
    e = earth.at(time)
    s = e.observe(sun).apparent()
    v = e.observe(venus).apparent()
    return s.separation_from(v).degrees
