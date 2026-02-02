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

# Phase 3 Stripe-specific allowlist (intentionally narrower than general Bay Area)
STRIPE_NORCAL_TOKENS = [
    "sf",
    "san francisco",
    "san francisco, ca",
    "san jose",
    "san jose, ca",
    "sunnyvale",
    "sunnyvale, ca",
    "mountain view",
    "mountain view, ca",
    "cupertino",
    "cupertino, ca",
    "redwood city",
    "redwood city, ca",
]


def is_stripe_norcal(location: str) -> bool:
    if not location:
        return False

    loc = location.lower()
    for token in STRIPE_NORCAL_TOKENS:
        if token in loc:
            return True

    return False
