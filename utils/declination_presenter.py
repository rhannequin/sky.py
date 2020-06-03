# coding: utf-8

import utils.constants


def declination_presenter(dec):
    return {
        "hms": {"value": dec.hstr(warn=False), "unit": None},
        "dms": {"value": dec.dstr(), "unit": None},
        "deg": {"value": dec._degrees, "unit": utils.constants.DEGREE_SYMBOL},
        "rad": {"value": dec.radians, "unit": utils.constants.RADIAN_SYMBOL},
    }
