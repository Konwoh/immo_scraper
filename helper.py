from dataclasses import dataclass


def to_float(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def to_int(v, default=""):
    if v is None:
        return None
    if isinstance(v, str) and v.strip() == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None 