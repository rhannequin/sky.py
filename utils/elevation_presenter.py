# coding: utf-8

import utils.constants


def elevation_presenter(el):
    return {
        "hms": {"value": el.hstr(warn=False), "unit": None},
        "dms": {"value": el.dstr(), "unit": None},
        "deg": {"value": el._degrees, "unit": utils.constants.DEGREE_SYMBOL},
        "rad": {"value": el.radians, "unit": utils.constants.RADIAN_SYMBOL},
    }
