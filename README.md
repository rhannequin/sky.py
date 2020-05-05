# SkyPy

A few Python scripts to request space-oriented data.

## ISS next visible path

### Usage

```sh
$ python iss.py --latitude YY.YYY --longitude XX.XXX \
--elevation ZZ --pressure B --horizon mm:ss --step 60
```

- `latitude`: angle in degrees between `-90` and `90`
- `longitude`: angle in degrees between `-90` and `90`
- `elevation`: distance in meters from sea level
- `pressure`: atmospheric pressure in mBar
- `horizon`: horizon's angle in minutes and seconds of arc
- `step`: time in seconds between each event during the pass

## JPL Horizons basic real-time information

### Usage

See [Horizons](https://ssd.jpl.nasa.gov/?horizons_doc)'s documentation for target and location ids.

```sh
$ python horizons.py --target 599 --target-type majorbody \
--location 500 --time "2020-05-06 17:00:00"
```

- `target`: body's ID to observe
- `target-type`: body's type
- `location`: location's ID
- `time`: datetime of ephemeris
