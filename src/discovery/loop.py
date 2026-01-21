# src/discovery/loop.py
from __future__ import annotations

import time
from typing import Dict

from discovery.models import Signal
from discovery.registry import load_registry, save_registry
from discovery.store import upsert_jobs
from discovery.signals.greenhouse import GreenhouseAdapter


ADAPTERS: Dict[str, object] = {
    "greenhouse_job_board_api": GreenhouseAdapter(),
}


def should_poll(signal: Signal, now: float) -> bool:
    interval_s = max(1, signal.poll_interval_minutes) * 60
    return (now - signal.last_polled_at) >= interval_s


def poll_all() -> None:
    now = time.time()
    signals = load_registry()
    updated = []

    for s in signals:
        if not should_poll(s, now):
            updated.append(s)
            continue

        try:
            adapter = ADAPTERS.get(s.method)
            if not adapter:
                raise ValueError(f"No adapter for method={s.method}")

            jobs = adapter.poll(s)  # metadata-only
            new_count, upd_count, stale_count = upsert_jobs(
                incoming=jobs,
                now=now,
                mark_stale_for_signal_id=s.signal_id,
            )

            s2 = Signal(
                signal_id=s.signal_id,
                company=s.company,
                method=s.method,
                poll_interval_minutes=s.poll_interval_minutes,
                last_polled_at=now,
                availability="available",
                notes=f"polled_ok new={new_count} updated={upd_count} stale={stale_count}",
                config=s.config,
            )
            updated.append(s2)

        except Exception as e:
            # No spoofing, no bypassing. Mark unavailable and move on.
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

