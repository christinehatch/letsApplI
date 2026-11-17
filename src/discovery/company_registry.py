from __future__ import annotations

from typing import Iterable, List, Literal, Tuple

from discovery.models import Signal


Provider = Literal["greenhouse", "lever", "ashby", "all"]


# Curated seeds intended for discovery bootstrapping. Each company is listed
# under the job board service it actually uses (verified 2026-11-17 against
# each public API). Boards can move over time; the poll loop marks a failing
# board unavailable without failing globally.
GREENHOUSE_COMPANIES: Tuple[Tuple[str, str], ...] = (
    ("Airbnb", "airbnb"),
    ("Airtable", "airtable"),
    ("Algolia", "algolia"),
    ("Anthropic", "anthropic"),
    ("Asana", "asana"),
    ("Attentive", "attentive"),
    ("Brex", "brex"),
    ("Checkr", "checkr"),
    ("CircleCI", "circleci"),
    ("Cloudflare", "cloudflare"),
    ("Coinbase", "coinbase"),
    ("Databricks", "databricks"),
    ("Discord", "discord"),
    ("Dropbox", "dropbox"),
    ("Figma", "figma"),
    ("Flexport", "flexport"),
    ("Gusto", "gusto"),
    ("Human Interest", "humaninterest"),
    ("Instacart", "instacart"),
    ("Intercom", "intercom"),
    ("Lattice", "lattice"),
    ("LaunchDarkly", "launchdarkly"),
    ("Lyft", "lyft"),
    ("Maven Clinic", "mavenclinic"),
    ("Mercury", "mercury"),
    ("Pinterest", "pinterest"),
    ("PlanetScale", "planetscale"),
    ("Reddit", "reddit"),
    ("Robinhood", "robinhood"),
    ("Roblox", "roblox"),
    ("Samsara", "samsara"),
    ("Scale AI", "scaleai"),
    ("Stripe", "stripe"),
    ("Vercel", "vercel"),
)

ASHBY_COMPANIES: Tuple[Tuple[str, str], ...] = (
    ("1Password", "1password"),
    ("Amplitude", "amplitude"),
    ("Benchling", "benchling"),
    ("Clerk", "clerk"),
    ("Headway", "headway"),
    ("Linear", "linear"),
    ("Miro", "miro"),
    ("Notion", "notion"),
    ("OpenAI", "openai"),
    ("Patreon", "patreon"),
    ("Plaid", "plaid"),
    ("Pleo", "pleo"),
    ("PostHog", "posthog"),
    ("Ramp", "ramp"),
    ("Render", "render"),
    ("Sentry", "sentry"),
    ("Snowflake", "snowflake"),
    ("Snyk", "snyk"),
    ("Temporal", "temporal"),
    ("Webflow", "webflow"),
    ("Zapier", "zapier"),
)

# None of the seeded companies currently publish on Lever; the adapter stays
# available for companies added by hand (cli add-lever).
LEVER_COMPANIES: Tuple[Tuple[str, str], ...] = ()

# Seeded before, but no public Greenhouse, Lever, or Ashby board was found
# (most use Workday or an in-house system). Kept here so they aren't re-added
# by mistake: Canva, Confluent, Deel, DoorDash, GitHub, HashiCorp, Netflix,
# Postman, Retool, Rippling, Scribd, Segment, Sourcegraph, Uber.


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


def _ashby_signals(poll_interval_minutes: int) -> Iterable[Signal]:
    for company, board_name in ASHBY_COMPANIES:
        yield Signal(
            signal_id=f"ashby:{board_name}",
            company=company,
            method="ashby_job_board_api",
            poll_interval_minutes=poll_interval_minutes,
            config={"board_name": board_name},
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

    if provider in ("all", "ashby"):
        out.extend(_ashby_signals(poll_interval_minutes))

    # Deduplicate by signal_id while preserving order.
    seen = set()
    unique: List[Signal] = []
    for signal in out:
        if signal.signal_id in seen:
            continue
        seen.add(signal.signal_id)
        unique.append(signal)

    return unique
