# Phase 5.1 — Test Implementation Guide

**Concrete Stack Mapping**

---

## Reference Stack: Python

### Recommended Tools

* **pytest** — unit + integration tests
* **unittest.mock / pytest-mock** — fetch & consent mocking
* **requests / httpx mock adapters** — network interception
* **tempfile / tmp_path** — persistence inspection

---

## Example: Consent Guard (INV-5.1-CONSENT-001)

```python
def test_no_read_without_consent(reader):
    reader.consent = None

    with pytest.raises(NotAuthorizedError):
        reader.read()

    assert reader.fetch_call_count == 0
```

---

## Example: Fetch Scope Enforcement (INV-5.1-READ-002)

```python
def test_single_surface_fetch(mock_fetch, reader_with_consent):
    reader_with_consent.read()

    assert mock_fetch.call_count == 1
    assert mock_fetch.called_with_primary_job_url_only()
```

---

## Example: No Persistence (INV-5.1-PERSIST-001)

```python
def test_no_raw_content_persisted(tmp_path, reader_with_consent):
    reader_with_consent.read()
    reader_with_consent.teardown()

    assert not any(tmp_path.iterdir())
```

---

## Representation Integrity (INV-5.1-REP-001)

```python
def test_no_content_transformation(fixture_job_text, reader_with_consent):
    rendered = reader_with_consent.read()

    assert rendered == fixture_job_text
```

---

## Truthfulness Assertions (INV-5.1-TRUTH-001)

```python
def test_truthful_status_messages(reader_with_consent):
    reader_with_consent.read()

    status = reader_with_consent.status()
    assert "analyzed" not in status
    assert "interpreted" not in status
```

---

## Mapping to TypeScript (High Level)

* **Jest / Vitest** → unit tests
* **MSW / fetch mocks** → enforce single-surface fetch
* **Playwright** → UI salience + consent revocation tests
* **Object.freeze()** → guard against mutation / transformation

## Mapping to Swift (High Level)

* **XCTest** → unit + integration
* **URLProtocol mocks** → network enforcement
* **SwiftUI snapshot tests** → ensure no UI emphasis
* **Ephemeral in-memory stores** → persistence checks

---

## CI Requirements

* All invariant tests must run on every PR
* Any failure blocks merge
* Invariant tests are **design tests**, not feature tests

