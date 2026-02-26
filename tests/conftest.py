# tests/conftest.py
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

# -------------------------------
# Phase 5.2 LLM Mock (Test Only)
# -------------------------------

from src.phase5.phase5_2.llm_adapter import Phase52LLMAdapter


@pytest.fixture(autouse=True)
def mock_phase52_llm(monkeypatch):
    """
    Automatically replaces Phase52LLMAdapter.run during tests
    so tests never call the real LLM.
    """

    def fake_run(self, raw_content):
        return {
            "schema_version": "5.2.0",
            "RoleSummary": {
                "summary_text": "Test summary",
                "evidence_span_ids": ["span_1"]
            },
            "RequirementsAnalysis": {
                "explicit_requirements": [],
                "implicit_signals": []
            },
            "CapabilityEmphasisSignals": [
                {
                    "domain_label": "Test Domain",
                    "description": "Test description",
                    "evidence_span_ids": ["span_1"]
                }
            ],
            "ProjectOpportunitySignals": [],
            "InterpretationResult": {
                "structural_notes": "Test"
            },
            "confidence": "LOW"
        }

    monkeypatch.setattr(Phase52LLMAdapter, "run", fake_run)