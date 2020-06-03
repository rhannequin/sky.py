# coding: utf-8

import utils.constants


def right_ascension_presenter(ra):
    return {
        "hms": {"value": ra.hstr(), "unit": None},
        "dms": {"value": ra.dstr(warn=False), "unit": None},
        "deg": {"value": ra._degrees, "unit": utils.constants.DEGREE_SYMBOL},
        "rad": {"value": ra.radians, "unit": utils.constants.RADIAN_SYMBOL},
    }
