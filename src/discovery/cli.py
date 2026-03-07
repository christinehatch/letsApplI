# src/discovery/cli.py
from __future__ import annotations

import argparse


from discovery.models import Signal
from discovery.registry import save_registry, load_registry, upsert_signal
from discovery.loop import poll_all
from discovery.run_state import load_last_run, save_last_run
from discovery.summary import summarize_since
from discovery.company_registry import seeded_signals
from state import DB_PATH

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

def cmd_add_lever(args: argparse.Namespace) -> None:
    s = Signal(
        signal_id=args.signal_id,
        company=args.company,
        method="lever_job_board_api",
        poll_interval_minutes=args.poll_interval_minutes,
        config={"company_slug": args.company_slug},
    )
    upsert_signal(s)
    print(f"Added signal {args.signal_id}")


def cmd_poll(_: argparse.Namespace) -> None:
    poll_all(DB_PATH)
    print("Poll complete. Discovery results stored in SQL database.")

def cmd_summary(args: argparse.Namespace) -> None:
    since = load_last_run()
    text = summarize_since(since)
    print(text)
    from datetime import datetime, timezone
    save_last_run(datetime.now(timezone.utc).isoformat())


def cmd_seed_registry(args: argparse.Namespace) -> None:
    seeds = seeded_signals(
        provider=args.provider,
        poll_interval_minutes=args.poll_interval_minutes,
    )

    if args.replace:
        save_registry(seeds)
        print(
            f"Seeded registry with {len(seeds)} signals "
            f"(provider={args.provider}, replace=True)."
        )
        return

    for signal in seeds:
        upsert_signal(signal)

    print(
        f"Upserted {len(seeds)} seeded signals "
        f"(provider={args.provider}, replace=False)."
    )


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

    sp = sub.add_parser("add-lever")
    sp.add_argument("--signal-id", required=True)
    sp.add_argument("--company", required=True)
    sp.add_argument("--company-slug", required=True)
    sp.add_argument("--poll-interval-minutes", type=int, default=360)
    sp.set_defaults(func=cmd_add_lever)

    sp = sub.add_parser("poll")
    sp.set_defaults(func=cmd_poll)

    sp = sub.add_parser("summary")

    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("seed-registry")
    sp.add_argument(
        "--provider",
        choices=["all", "greenhouse", "lever"],
        default="all",
    )
    sp.add_argument("--poll-interval-minutes", type=int, default=360)
    sp.add_argument("--replace", action="store_true")
    sp.set_defaults(func=cmd_seed_registry)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
