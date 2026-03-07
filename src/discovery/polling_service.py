from __future__ import annotations

import time
from typing import Callable, Optional

from discovery.loop import poll_all


def run_polling_service(
    db_path: str,
    *,
    cycle_sleep_seconds: float = 60.0,
    max_cycles: Optional[int] = None,
    poll_fn: Callable[[str], None] = poll_all,
    sleep_fn: Callable[[float], None] = time.sleep,
    log_fn: Callable[[str], None] = print,
) -> None:
    """
    Continuous discovery polling loop.

    Guarantees:
    - Uses existing discovery polling implementation.
    - Keeps running even if one cycle raises.
    - Sleeps between cycles.
    """

    cycle = 0
    log_fn(
        "[discovery.polling_service] start "
        f"cycle_sleep_seconds={cycle_sleep_seconds} max_cycles={max_cycles}"
    )

    while True:
        cycle += 1
        started_at = time.time()
        log_fn(f"[discovery.polling_service] cycle={cycle} started")

        try:
            poll_fn(db_path)
            elapsed = time.time() - started_at
            log_fn(
                "[discovery.polling_service] "
                f"cycle={cycle} completed elapsed_s={elapsed:.2f}"
            )
        except Exception as exc:
            elapsed = time.time() - started_at
            log_fn(
                "[discovery.polling_service] "
                f"cycle={cycle} failed elapsed_s={elapsed:.2f} "
                f"error={type(exc).__name__}: {exc}"
            )

        if max_cycles is not None and cycle >= max_cycles:
            log_fn(
                "[discovery.polling_service] "
                f"stopping after max_cycles={max_cycles}"
            )
            return

        if cycle_sleep_seconds > 0:
            sleep_fn(cycle_sleep_seconds)
