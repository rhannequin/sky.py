# coding: utf-8

import utils.constants


def azimuth_presenter(az):
    return {
        "hms": {"value": az.hstr(warn=False), "unit": None},
        "dms": {"value": az.dstr(), "unit": None},
        "deg": {"value": az._degrees, "unit": utils.constants.DEGREE_SYMBOL},
        "rad": {"value": az.radians, "unit": utils.constants.RADIAN_SYMBOL},
    }
