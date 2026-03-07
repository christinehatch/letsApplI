from __future__ import annotations

from typing import Iterable, List, Literal, Tuple

from discovery.models import Signal


Provider = Literal["greenhouse", "lever", "all"]


# Curated seeds intended for discovery bootstrapping.
# Some endpoints may become unavailable over time; poll loop availability
# handling will mark those signals as unavailable without failing globally.
GREENHOUSE_COMPANIES: Tuple[Tuple[str, str], ...] = (
    ("Stripe", "stripe"),
    ("OpenAI", "openai"),
    ("Notion", "notion"),
    ("Databricks", "databricks"),
    ("Discord", "discord"),
    ("Uber", "uber"),
    ("Reddit", "reddit"),
    ("Lyft", "lyft"),
    ("GitHub", "github"),
    ("Airbnb", "airbnb"),
    ("Coinbase", "coinbase"),
    ("Figma", "figma"),
    ("Canva", "canva"),
    ("Asana", "asana"),
    ("Miro", "miro"),
    ("Dropbox", "dropbox"),
    ("Robinhood", "robinhood"),
    ("Retool", "retool"),
    ("Brex", "brex"),
    ("Snowflake", "snowflake"),
    ("Cloudflare", "cloudflare"),
    ("Amplitude", "amplitude"),
    ("Plaid", "plaid"),
    ("Rippling", "rippling"),
    ("Gusto", "gusto"),
    ("Samsara", "samsara"),
    ("Doordash", "doordash"),
    ("Instacart", "instacart"),
    ("Pinterest", "pinterest"),
    ("Airtable", "airtable"),
    ("Postman", "postman"),
    ("Linear", "linear"),
    ("Vercel", "vercel"),
    ("Sourcegraph", "sourcegraph"),
    ("Benchling", "benchling"),
)

LEVER_COMPANIES: Tuple[Tuple[str, str], ...] = (
    ("Plaid", "plaid"),
    ("Rippling", "rippling"),
    ("Scale AI", "scaleai"),
    ("Flexport", "flexport"),
    ("Figma", "figma"),
    ("Coinbase", "coinbase"),
    ("Segment", "segment"),
    ("PostHog", "posthog"),
    ("Netflix", "netflix"),
    ("Anthropic", "anthropic"),
    ("Roblox", "roblox"),
    ("Sentry", "sentry"),
    ("HashiCorp", "hashicorp"),
    ("PlanetScale", "planetscale"),
    ("Render", "render"),
    ("Clerk", "clerk"),
    ("Temporal", "temporal"),
    ("Snyk", "snyk"),
    ("Algolia", "algolia"),
    ("CircleCI", "circleci"),
    ("Airtable", "airtable"),
    ("Zapier", "zapier"),
    ("1Password", "1password"),
    ("LaunchDarkly", "launchdarkly"),
    ("Intercom", "intercom"),
    ("Webflow", "webflow"),
    ("Attentive", "attentive"),
    ("Ramp", "ramp"),
    ("Deel", "deel"),
    ("Checkr", "checkr"),
    ("Scribd", "scribd"),
    ("Lattice", "lattice"),
    ("Confluent", "confluent"),
    ("Maven Clinic", "maven"),
    ("Patreon", "patreon"),
    ("Headway", "headway"),
    ("Notion", "notion"),
    ("Pleo", "pleo"),
    ("Mercury", "mercury"),
    ("Human Interest", "humaninterest"),
)


def _greenhouse_signals(poll_interval_minutes: int) -> Iterable[Signal]:
    for company, board_token in GREENHOUSE_COMPANIES:
        yield Signal(
            signal_id=f"greenhouse:{board_token}",
            company=company,
            method="greenhouse_job_board_api",
            poll_interval_minutes=poll_interval_minutes,
            config={"board_token": board_token},
        )


def _lever_signals(poll_interval_minutes: int) -> Iterable[Signal]:
    for company, company_slug in LEVER_COMPANIES:
        yield Signal(
            signal_id=f"lever:{company_slug}",
            company=company,
            method="lever_job_board_api",
            poll_interval_minutes=poll_interval_minutes,
            config={"company_slug": company_slug},
        )


def seeded_signals(
    *,
    provider: Provider = "all",
    poll_interval_minutes: int = 360,
) -> List[Signal]:
    out: List[Signal] = []

    if provider in ("all", "greenhouse"):
        out.extend(_greenhouse_signals(poll_interval_minutes))

    if provider in ("all", "lever"):
        out.extend(_lever_signals(poll_interval_minutes))

    # Deduplicate by signal_id while preserving order.
    seen = set()
    unique: List[Signal] = []
    for signal in out:
        if signal.signal_id in seen:
            continue
        seen.add(signal.signal_id)
        unique.append(signal)

    return unique
