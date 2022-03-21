# SkyPy

A few Python scripts to request space-oriented data.

## Overview

- [ISS next visible path](#iss-next-visible-path) `iss.py`
- [JPL Horizons basic real-time information](#jpl-horizons-basic-real-time-information) `horizons.py`
- [Moon ephemeris](#moon-ephemeris) `moon.py`
- [When is it getting dark?](#when-is-it-getting-dark) `dark.py`
- [α Ursae Minoris data](#%CE%B1-ursae-minoris-data) `polaris.py`

## ISS next visible path

### Usage

```sh
$ python iss.py --latitude YY.YYY --longitude XX.XXX --elevation ZZ.Z --horizon WW.W --start_time "YYYY-MM-DD hh:mm:ss" --end_time "YYYY-MM-DD hh:mm:ss"
```

- `latitude`: angle in degrees between `-90` and `90`
- `longitude`: angle in degrees between `-90` and `90`
- `elevation`: distance in meters from sea level
- `horizon`: horizon's angle in degrees between `-90` and `90`
- `start_time`: time to start monitoring events in `YYYY-MM-DD hh:mm:ss`
- `end_time`: time to stop monitoring events in `YYYY-MM-DD hh:mm:ss`

## JPL Horizons basic real-time information

### Usage

See [Horizons](https://ssd.jpl.nasa.gov/?horizons_doc) documentation for target and location ids.

```sh
$ python horizons.py --target 599 --target-type majorbody --location 500 --time "2020-05-06 17:00:00"
```

- `target`: body's ID to observe
- `target-type`: body's type
- `location`: location's ID
- `time`: datetime of ephemeris

## Moon ephemeris

### Usage

```sh
$ python moon.py --latitude 48.8638 --longitude 2.4485 --elevation 97 --datetime "2020-05-11 14:00:00"
```

- `latitude`: angle in degrees between `-90` and `90`
- `longitude`: angle in degrees between `-90` and `90`
- `elevation`: distance in meters from sea level
- `datetime`: datetime of ephemeris in UTC

## When is it getting dark?

### Usage

```sh
$ python dark.py --latitude 48.8638 --longitude 2.4485 --elevation 97 --date "2020-05-11"
```

- `latitude`: angle in degrees between `-90` and `90`
- `longitude`: angle in degrees between `-90` and `90`
- `elevation`: distance in meters from sea level
- `datetime`: date of observation

## α Ursae Minoris data

### Usage

```sh
$ python polaris.py --latitude 48.8638 --longitude 2.4485 --elevation 97 --datetime "2020-05-11 14:00:00"
```

- `latitude`: angle in degrees between `-90` and `90`
- `longitude`: angle in degrees between `-90` and `90`
- `elevation`: distance in meters from sea level
- `datetime`: datetime of observation in UTC
