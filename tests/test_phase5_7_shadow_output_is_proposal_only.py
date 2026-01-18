import os

from .cli_helpers import run_cli

def test_shadow_mode_llm_output_is_visible_only_as_proposal():
    """
    Invariant (Phase 5.7):

    When shadow-mode LLM execution is enabled,
    AI output may be surfaced ONLY as a Proposal.

    It must:
    - appear in `proposals` output
    - be clearly labeled as AI-generated
    - NOT be applied automatically
    - NOT write any files
    - NOT change behavior without human approval
    """

    # Enable shadow mode
    os.environ["USE_LLM_SHADOW_MODE"] = "1"

    # Run proposals listing
    out, err = run_cli(["proposals"])

    # Sanity: CLI ran
    assert err == ""

    # Proposal list should exist
    assert "--- AI Proposals (optional) ---" in out

    # Proposal should be labeled and pending
    assert "phrasing_suggestion" in out
    assert "(pending)" in out

    # Must NOT show applied output
    assert "Applied Output" not in out
    assert "✓ Applied" not in out

    # Must NOT imply authority or recommendation
    forbidden_phrases = [
        "you should",
        "recommended",
        "we suggest",
        "best option",
        "apply this",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in out.lower()

