from datetime import datetime


def json_converter(obj):
    if isinstance(obj, datetime):
        return obj.__str__()
    return None
