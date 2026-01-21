# src/discovery/location_filters.py

from __future__ import annotations


SF_BAY_AREA_TOKENS = [
    "san francisco",
    "south san francisco",
    "sf",
    "san jose",
    "santa clara",
    "sunnyvale",
    "mountain view",
    "palo alto",
    "menlo park",
    "redwood city",
    "san mateo",
    "fremont",
    "oakland",
    "berkeley",
    "emeryville",
    "hayward",
    "cupertino",
    "bay area",
]


def is_sf_bay_area(location: str) -> bool:
    if not location:
        return False

    loc = location.lower()

    for token in SF_BAY_AREA_TOKENS:
        if token in loc:
            return True

    return False

