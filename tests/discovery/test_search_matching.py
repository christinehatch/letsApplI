"""
Feed search matching (src/discovery/search_query.py + JobsRepo).

Each case here was broken before: synonyms narrowed results ("ai" → 0 jobs),
short terms matched inside words ("pm" → "Development"), the keyword box
ignored company names, and location aliases (SF, NYC) didn't exist.
"""

import re
import sqlite3
import tempfile

import pytest

from discovery.search_query import location_patterns, role_term_patterns
from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo

JOBS = [
    # key, company, title, location_raw, location_norm
    ("j1", "Datadog", "AI Research Engineer", "New York, New York, USA", None),
    ("j2", "Stripe", "Machine Learning Engineer, Payments", "San Francisco, CA", None),
    ("j3", "Reddit", "Senior ML Engineer", "Remote - United States", None),
    ("j4", "Plaid", "Artificial Intelligence Product Lead", "SF, NYC", None),
    ("j5", "Datadog", "Corporate Development Lead", "Paris, France", None),
    ("j6", "Datadog", "Manager I, Engineering - APM SDK", "Lisbon, Portugal", None),
    ("j7", "Notion", "Senior Product Manager", "New York, NY", None),
    ("j8", "Asana", "Group PM, Workflows", "Remote - SF Bay Area", None),
    ("j9", "Aiven", "Maintenance Coordinator", "Helsinki", None),
    ("j10", "Vercel", "Senior Front-End Engineer", "Remote", "remote"),
    ("j11", "GitHub", "Software Developer", "Bay Area", "san_francisco_bay_area"),
    ("j12", "Stripe", "Recruiter", "Dublin", None),
    ("j13", "Lattice", "Account Executive", "Los Angeles, CA", None),
    ("j14", "Retool", "Sales Lead", "Lake Tahoe", None),
    ("j15", "Datadog", "Senior Manager, Product Management", "Boston", None),
    ("j16", "Stripe", "Product Marketing Manager", "Boston", None),
]


@pytest.fixture
def repo():
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executemany(
        """
        INSERT INTO jobs (provider, external_id, provider_job_key, company, title,
                          location_raw, location_norm, url, discovered_at)
        VALUES ('greenhouse', ?, ?, ?, ?, ?, ?, 'https://example.com', '2026-01-01T00:00:00Z')
        """,
        [(k, k, c, t, lr, ln) for k, c, t, lr, ln in JOBS],
    )
    conn.commit()
    yield JobsRepo(conn)
    conn.close()


def ids(repo, **filters):
    jobs, total = repo.list_discovery_feed_jobs(page_size=100, **filters)
    assert total == len(jobs)
    return {j["job_id"] for j in jobs}


# ------------------------------------------------------------
# Keyword search
# ------------------------------------------------------------

def test_ai_matches_abbreviation_and_spelled_out_but_not_inside_words(repo):
    assert ids(repo, role="ai") == {"j1", "j4"}  # not Aiven, not Maintenance


def test_spelled_out_synonym_matches_the_abbreviation_too(repo):
    assert ids(repo, role="artificial intelligence") == {"j1", "j4"}


@pytest.mark.parametrize("query", ["ml", "machine learning", "ML"])
def test_ml_and_machine_learning_are_equivalent(repo, query):
    assert ids(repo, role=query) == {"j2", "j3"}


def test_synonyms_widen_multi_word_searches(repo):
    assert ids(repo, role="ml engineer") == {"j2", "j3"}


def test_pm_matches_product_manager_not_development_or_apm(repo):
    assert ids(repo, role="pm") == {"j7", "j8", "j15"}


def test_product_manager_excludes_product_marketing_manager(repo):
    assert ids(repo, role="product manager") == {"j7", "j8", "j15"}


def test_terms_match_at_word_start(repo):
    # "engineer" matches "Engineering" and "Engineer", nothing mid-word.
    assert ids(repo, role="engineer") == {"j1", "j2", "j3", "j6", "j10"}


def test_hyphenated_and_spaced_phrases_match_each_other(repo):
    assert ids(repo, role="front end") == {"j10"}
    assert ids(repo, role="frontend") == {"j10"}


def test_keyword_search_includes_company_names(repo):
    assert ids(repo, role="stripe") == {"j2", "j12", "j16"}


def test_keyword_and_company_combine(repo):
    assert ids(repo, role="stripe recruiter") == {"j12"}


def test_title_matches_rank_above_company_matches(repo):
    jobs, _ = repo.list_discovery_feed_jobs(role="datadog ai")
    assert jobs[0]["job_id"] == "j1"


# ------------------------------------------------------------
# Location
# ------------------------------------------------------------

@pytest.mark.parametrize("query", ["sf", "SF", "san francisco", "bay area"])
def test_san_francisco_aliases_are_equivalent(repo, query):
    assert ids(repo, location=query) == {"j2", "j4", "j8", "j11"}


@pytest.mark.parametrize("query", ["nyc", "new york"])
def test_new_york_aliases_are_equivalent(repo, query):
    assert ids(repo, location=query) == {"j1", "j4", "j7"}


def test_short_location_alias_needs_a_whole_word(repo):
    assert ids(repo, location="la") == {"j13"}  # not "Lake Tahoe"


def test_location_matches_normalized_location(repo):
    assert "j11" in ids(repo, location="san francisco")


def test_remote_still_matches(repo):
    assert ids(repo, location="remote") == {"j3", "j8", "j10"}


# ------------------------------------------------------------
# Parser
# ------------------------------------------------------------

def test_parser_returns_one_group_per_term():
    assert len(role_term_patterns("senior machine learning engineer")) == 3
    assert role_term_patterns("") == []
    assert role_term_patterns("   ") == []
    assert role_term_patterns(None) == []


def test_parser_dedupes_repeated_terms():
    assert len(role_term_patterns("ml machine learning")) == 1


def test_parser_escapes_regex_characters():
    [pattern] = role_term_patterns("c++")
    assert re.search(pattern, "Senior C++ Engineer", re.IGNORECASE)
    assert len(location_patterns("new york (hybrid)")) == 2  # "new york" is one alias group
