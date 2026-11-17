"""Ashby job board adapter and the verified seed list (no network)."""

import pytest

from discovery.company_registry import (
    ASHBY_COMPANIES,
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES,
    seeded_signals,
)
from discovery.loop import ADAPTERS
from discovery.models import Signal
from discovery.signals.ashby import AshbyAdapter

SIGNAL = Signal(
    signal_id="ashby:linear",
    company="Linear",
    method="ashby_job_board_api",
    config={"board_name": "linear"},
)

PAYLOAD = {
    "apiVersion": "1",
    "jobs": [
        {
            "id": "a1",
            "title": "Product Engineer",
            "location": "San Francisco",
            "secondaryLocations": [{"location": "New York"}, {"location": "San Francisco"}],
            "isRemote": True,
            "isListed": True,
            "jobUrl": "https://jobs.ashbyhq.com/linear/a1",
            "applyUrl": "https://jobs.ashbyhq.com/linear/a1/application",
            "publishedAt": "2026-11-10T00:00:00Z",
            "department": "Engineering",
            "team": "Product",
            "workplaceType": "Hybrid",
            "employmentType": "FullTime",
            "descriptionHtml": "<p>MUST NOT BE STORED</p>",
            "descriptionPlain": "MUST NOT BE STORED",
        },
        {"id": "a2", "title": "Hidden Role", "isListed": False, "jobUrl": "https://x"},
        {"id": "", "title": "No id"},
        {
            "id": "a3",
            "title": "Support Engineer",
            "location": "Remote - US",
            "isRemote": True,
            "jobUrl": "",
            "applyUrl": "https://jobs.ashbyhq.com/linear/a3/application",
        },
    ],
}


def parse():
    return AshbyAdapter().parse(SIGNAL, "linear", PAYLOAD)


def test_parses_listed_jobs_only():
    assert [j.external_job_id for j in parse()] == ["a1", "a3"]


def test_job_fields_and_unique_key():
    job = parse()[0]
    assert job.job_uid == "ashby:linear:a1"
    assert job.company == "Linear"
    assert job.title == "Product Engineer"
    assert job.url == "https://jobs.ashbyhq.com/linear/a1"
    assert job.source_signal_id == "ashby:linear"


def test_locations_combine_secondary_and_remote_without_duplicates():
    assert parse()[0].location == "San Francisco; New York; Remote"
    assert parse()[1].location == "Remote - US"  # already says remote


def test_falls_back_to_apply_url():
    assert parse()[1].url == "https://jobs.ashbyhq.com/linear/a3/application"


def test_metadata_only_no_description():
    job = parse()[0]
    assert "MUST NOT BE STORED" not in str(job.raw_meta)
    assert job.raw_meta == {
        "department": "Engineering",
        "team": "Product",
        "workplace_type": "Hybrid",
        "employment_type": "FullTime",
        "published_at": "2026-11-10T00:00:00Z",
    }


def test_missing_board_name_is_an_error():
    bad = Signal(signal_id="ashby:x", company="X", method="ashby_job_board_api", config={})
    with pytest.raises(ValueError):
        AshbyAdapter().poll(bad)


def test_poll_loop_knows_every_seeded_method():
    for signal in seeded_signals():
        assert signal.method in ADAPTERS


def test_seed_list_has_no_company_on_two_providers():
    names = [c for c, _ in GREENHOUSE_COMPANIES + ASHBY_COMPANIES + LEVER_COMPANIES]
    assert len(names) == len(set(names))


def test_known_moves_are_on_the_right_provider():
    gh = dict(GREENHOUSE_COMPANIES)
    ashby = dict(ASHBY_COMPANIES)
    assert gh["Anthropic"] == "anthropic"
    assert gh["Scale AI"] == "scaleai"
    assert ashby["OpenAI"] == "openai"
    assert ashby["Notion"] == "notion"
    assert ashby["Linear"] == "linear"
