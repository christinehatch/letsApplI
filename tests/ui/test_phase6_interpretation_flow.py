# tests/ui/test_phase6_interpretation_flow.py

import pytest

# You may adjust imports depending on your final wiring
# from src.ui.phase6.state_machine import Phase6StateMachine
# from src.bridge_server import app


# -----------------------------
# Helpers (Minimal Mock State)
# -----------------------------

class MockPhase6State:
    def __init__(self):
        self.state = "VIEWING"
        self.hydration = {"jobId": None, "rawContent": None}
        self.interpretation = {"jobId": None, "result": None}


def transition(mock, event):
    """
    Minimal logical state transition simulator.
    Replace with reducer binding if wired to Python.
    """

    state = mock.state

    if state == "VIEWING" and event == "REQUEST_HYDRATION":
        mock.state = "CONSENT_REQUESTED_HYDRATION"

    elif state == "CONSENT_REQUESTED_HYDRATION" and event == "GRANT_HYDRATION_CONSENT":
        mock.state = "HYDRATING"

    elif state == "HYDRATING" and event == "HYDRATION_SUCCESS":
        mock.state = "HYDRATED"
        mock.hydration["jobId"] = "test_job"
        mock.hydration["rawContent"] = "raw job content"

    elif state == "HYDRATED" and event == "REQUEST_INTERPRETATION":
        mock.state = "CONSENT_REQUESTED_INTERPRETATION"

    elif state == "CONSENT_REQUESTED_INTERPRETATION" and event == "GRANT_INTERPRETATION_CONSENT":
        mock.state = "INTERPRETING"

    elif state == "INTERPRETING" and event == "INTERPRETATION_SUCCESS":
        mock.state = "INTERPRETED"
        mock.interpretation["jobId"] = "test_job"
        mock.interpretation["result"] = {"summary": "structured result"}

    elif event == "REVOKE_INTERPRETATION":
        mock.state = "HYDRATED"
        mock.interpretation = {"jobId": None, "result": None}

    elif event == "REVOKE_HYDRATION":
        mock.state = "VIEWING"
        mock.hydration = {"jobId": None, "rawContent": None}
        mock.interpretation = {"jobId": None, "result": None}

    return mock


# -----------------------------
# Test Cases
# -----------------------------


def test_cannot_interpret_without_hydration():
    mock = MockPhase6State()
    transition(mock, "REQUEST_INTERPRETATION")
    assert mock.state == "VIEWING"


def test_cannot_interpret_without_consent():
    mock = MockPhase6State()

    transition(mock, "REQUEST_HYDRATION")
    transition(mock, "GRANT_HYDRATION_CONSENT")
    transition(mock, "HYDRATION_SUCCESS")

    # Attempt direct interpretation success without consent
    transition(mock, "INTERPRETATION_SUCCESS")
    assert mock.state == "HYDRATED"


def test_full_interpretation_flow():
    mock = MockPhase6State()

    transition(mock, "REQUEST_HYDRATION")
    transition(mock, "GRANT_HYDRATION_CONSENT")
    transition(mock, "HYDRATION_SUCCESS")

    transition(mock, "REQUEST_INTERPRETATION")
    transition(mock, "GRANT_INTERPRETATION_CONSENT")
    transition(mock, "INTERPRETATION_SUCCESS")

    assert mock.state == "INTERPRETED"
    assert mock.interpretation["result"] is not None


def test_revoke_interpretation_clears_only_interpretation():
    mock = MockPhase6State()

    transition(mock, "REQUEST_HYDRATION")
    transition(mock, "GRANT_HYDRATION_CONSENT")
    transition(mock, "HYDRATION_SUCCESS")
    transition(mock, "REQUEST_INTERPRETATION")
    transition(mock, "GRANT_INTERPRETATION_CONSENT")
    transition(mock, "INTERPRETATION_SUCCESS")

    transition(mock, "REVOKE_INTERPRETATION")

    assert mock.state == "HYDRATED"
    assert mock.interpretation["result"] is None
    assert mock.hydration["rawContent"] is not None


def test_revoke_hydration_clears_everything():
    mock = MockPhase6State()

    transition(mock, "REQUEST_HYDRATION")
    transition(mock, "GRANT_HYDRATION_CONSENT")
    transition(mock, "HYDRATION_SUCCESS")
    transition(mock, "REQUEST_INTERPRETATION")
    transition(mock, "GRANT_INTERPRETATION_CONSENT")
    transition(mock, "INTERPRETATION_SUCCESS")

    transition(mock, "REVOKE_HYDRATION")

    assert mock.state == "VIEWING"
    assert mock.hydration["rawContent"] is None
    assert mock.interpretation["result"] is None
