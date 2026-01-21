# src/discovery/cli.py
from __future__ import annotations

import argparse
import time

from discovery.models import Signal
from discovery.registry import save_registry, load_registry, upsert_signal
from discovery.loop import poll_all
from discovery.run_state import load_last_run, save_last_run
from discovery.summary import summarize_since


def cmd_init(_: argparse.Namespace) -> None:
    save_registry([])
    print("Initialized state/signal_registry.json")


def cmd_list(_: argparse.Namespace) -> None:
    signals = load_registry()
    if not signals:
        print("No signals registered.")
        return
    for s in signals:
        print(f"- {s.signal_id} company={s.company} method={s.method} availability={s.availability} last_polled_at={s.last_polled_at}")
        if s.notes:
            print(f"  notes: {s.notes}")


def cmd_add_greenhouse(args: argparse.Namespace) -> None:
    s = Signal(
        signal_id=args.signal_id,
        company=args.company,
        method="greenhouse_job_board_api",
        poll_interval_minutes=args.poll_interval_minutes,
        config={"board_token": args.board_token},
    )
    upsert_signal(s)
    print(f"Added signal {args.signal_id}")


def cmd_poll(_: argparse.Namespace) -> None:
    poll_all()
    print("Poll complete. See state/signal_registry.json and state/discovered_jobs.json")


def cmd_summary(args: argparse.Namespace) -> None:
    since = load_last_run()
    text = summarize_since(since, explain_roles=args.explain_roles)
    print(text)
    save_last_run(time.time())



def main() -> None:
    p = argparse.ArgumentParser(prog="letsApplI discovery")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("list")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("add-greenhouse")
    sp.add_argument("--signal-id", required=True)
    sp.add_argument("--company", required=True)
    sp.add_argument("--board-token", required=True)
    sp.add_argument("--poll-interval-minutes", type=int, default=360)
    sp.set_defaults(func=cmd_add_greenhouse)

    sp = sub.add_parser("poll")
    sp.set_defaults(func=cmd_poll)

    sp = sub.add_parser("summary")
    sp.add_argument(
        "--explain-roles",
        action="store_true",
        help="Show general role orientation based on job titles only (no job content read)",
    )
    sp.set_defaults(func=cmd_summary)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

