# src/discovery/registry.py
from __future__ import annotations

import json
import os
from typing import List, Dict, Any, Optional
from discovery.models import Signal


DEFAULT_REGISTRY_PATH = os.path.join("state", "signal_registry.json")


def load_registry(path: str = DEFAULT_REGISTRY_PATH) -> List[Signal]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    signals = data.get("signals", [])
    return [Signal(**s) for s in signals]


def save_registry(signals: List[Signal], path: str = DEFAULT_REGISTRY_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"signals": [s.to_dict() for s in signals]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def upsert_signal(new_signal: Signal, path: str = DEFAULT_REGISTRY_PATH) -> None:
    signals = load_registry(path)
    out: List[Signal] = []
    replaced = False
    for s in signals:
        if s.signal_id == new_signal.signal_id:
            out.append(new_signal)
            replaced = True
        else:
            out.append(s)
    if not replaced:
        out.append(new_signal)
    save_registry(out, path)

