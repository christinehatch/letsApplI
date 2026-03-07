from discovery.models import Signal
from discovery import loop
from discovery.polling_service import run_polling_service


class _FakeAdapter:
    def __init__(self):
        self.calls = []

    def poll(self, signal):
        self.calls.append(signal.signal_id)
        return []


class _FakeStore:
    def __init__(self, db_path):
        self.db_path = db_path

    def upsert_jobs(self, incoming):
        return (len(incoming), 0)


def test_poll_all_respects_signal_poll_interval(monkeypatch):
    adapter = _FakeAdapter()

    due_signal = Signal(
        signal_id="due",
        company="DueCo",
        method="greenhouse_job_board_api",
        poll_interval_minutes=10,
        last_polled_at=0,
        config={"board_token": "due"},
    )
    not_due_signal = Signal(
        signal_id="not-due",
        company="LaterCo",
        method="greenhouse_job_board_api",
        poll_interval_minutes=10,
        last_polled_at=1000,
        config={"board_token": "later"},
    )

    saved = {}

    monkeypatch.setattr(loop, "ADAPTERS", {"greenhouse_job_board_api": adapter})
    monkeypatch.setattr(loop, "DiscoveryStore", _FakeStore)
    monkeypatch.setattr(loop, "load_registry", lambda: [due_signal, not_due_signal])
    monkeypatch.setattr(loop.time, "time", lambda: 1200)
    monkeypatch.setattr(loop, "save_registry", lambda signals: saved.setdefault("signals", signals))

    loop.poll_all("/tmp/test.sqlite")

    assert adapter.calls == ["due"]
    assert len(saved["signals"]) == 2
    assert saved["signals"][1].signal_id == "not-due"
    assert saved["signals"][1].last_polled_at == 1000


def test_polling_service_continues_after_cycle_failure():
    logs = []
    calls = []

    def fake_poll(_db_path):
        calls.append("poll")
        if len(calls) == 1:
            raise RuntimeError("boom")

    run_polling_service(
        "/tmp/test.sqlite",
        cycle_sleep_seconds=0,
        max_cycles=2,
        poll_fn=fake_poll,
        sleep_fn=lambda _seconds: None,
        log_fn=logs.append,
    )

    assert len(calls) == 2
    assert any("failed" in line and "boom" in line for line in logs)
    assert any("completed" in line for line in logs)
