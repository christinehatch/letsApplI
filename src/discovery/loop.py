# src/discovery/loop.py
from __future__ import annotations

import time
from typing import Dict

from discovery.models import Signal
from discovery.registry import load_registry, save_registry
from discovery.store import DiscoveryStore
from discovery.signals.greenhouse import GreenhouseAdapter
from discovery.signals.lever import LeverAdapter
from discovery.signals.ashby import AshbyAdapter


ADAPTERS: Dict[str, object] = {
    "greenhouse_job_board_api": GreenhouseAdapter(),
    "lever_job_board_api": LeverAdapter(),
    "ashby_job_board_api": AshbyAdapter(),
}


# Each adapter builds job keys as "<prefix>:<board>:<id>".
BOARD_KEY = {
    "greenhouse_job_board_api": ("greenhouse", "board_token"),
    "lever_job_board_api": ("lever", "company_slug"),
    "ashby_job_board_api": ("ashby", "board_name"),
}


def board_prefix(signal: Signal) -> str:
    """Key prefix shared by every job from this signal's board, or '' if unknown."""
    prefix, config_key = BOARD_KEY.get(signal.method, ("", ""))
    board = (signal.config or {}).get(config_key) if config_key else None
    return f"{prefix}:{board}:" if prefix and board else ""


def should_poll(signal: Signal, now: float) -> bool:
    interval_s = max(1, signal.poll_interval_minutes) * 60
    return (now - signal.last_polled_at) >= interval_s


def poll_all(db_path: str) -> None:
    now = time.time()
    signals = load_registry()
    updated = []

    store = DiscoveryStore(db_path)

    for s in signals:
        if not should_poll(s, now):
            updated.append(s)
            continue

        try:
            adapter = ADAPTERS.get(s.method)
            if not adapter:
                raise ValueError(f"No adapter for method={s.method}")

            jobs = adapter.poll(s)  # metadata-only

            new_count, upd_count = store.upsert_jobs(
                incoming=jobs,
            )
            # Only a successful check can close roles; a failed one leaves them as they were.
            closed_count = store.close_missing(board_prefix(s), [j.job_uid for j in jobs])

            s2 = Signal(
                signal_id=s.signal_id,
                company=s.company,
                method=s.method,
                poll_interval_minutes=s.poll_interval_minutes,
                last_polled_at=now,
                availability="available",
                notes=f"polled_ok new={new_count} updated={upd_count} closed={closed_count}",
                config=s.config,
            )

            updated.append(s2)

        except Exception as e:
            s2 = Signal(
                signal_id=s.signal_id,
                company=s.company,
                method=s.method,
                poll_interval_minutes=s.poll_interval_minutes,
                last_polled_at=now,
                availability="unavailable",
                notes=f"poll_failed: {type(e).__name__}: {e}",
                config=s.config,
            )
            updated.append(s2)

    save_registry(updated)

    # Roles from boards no longer on the list can't be confirmed open.
    prefixes = [p for p in (board_prefix(s) for s in signals) if p]
    if prefixes:
        store.close_unchecked_boards(prefixes)