from astroquery.jplhorizons import Horizons

obj = Horizons(
    id="599",
    location="500",
    id_type="majorbody",
    epochs={"start": "2020-05-05 17:00", "stop": "2020-05-05 17:01", "step": "1h"},
)

eph = obj.ephemerides(quantities="19,20,22")

print(obj.uri)
print()

print(eph)
print()

print(eph.columns)
print()

print(eph["r"].data[0])
print(eph["delta"].data[0])
print(eph["vel_sun"].data[0])


# Kushiro
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
