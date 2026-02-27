# PHASE4_5_PROVIDER_AGNOSTIC_LOCK.md

## Phase 4.5 — Provider-Agnostic Metadata Discovery Lock

---

## Status

Phase 4.5 is formally locked.

Discovery is provider-agnostic, metadata-only, and persistence-neutral.

No adapter may expand scope beyond this boundary.

---

## Scope of Phase 4.5

Phase 4.5 is responsible only for:

- Polling external job board APIs
- Extracting metadata-only job information
- Producing `DiscoveredJob` artifacts
- Persisting via `DiscoveryStore`
- Updating signal availability and poll state

Phase 4.5 does **not**:

- Hydrate job content
- Interpret job content
- Rank jobs
- Filter jobs
- Normalize semantics
- Evaluate fit
- Modify resume
- Predict match quality
- Generate summaries
- Mutate downstream artifacts

Discovery is ingestion only.

---

## Architectural Guarantees

The following guarantees are enforced by code and tests.

---

## 1. Provider-Agnostic Persistence

All providers persist into the same `jobs` table.

There are:

- No provider-specific columns
- No provider-conditional SQL branches
- No schema forks
- No adapter-specific persistence logic

The database schema remains neutral.

---

## 2. Deterministic UID Format

Each discovered job must have:

```
provider_job_key = "<provider>:<namespace>:<external_id>"
```

Store derives:

```
provider = provider_job_key.split(":")[0]
```

Invariant:

```
provider == provider_job_key prefix
```

Enforced by test: `test_provider_matches_job_uid_prefix`

---

## 3. Metadata-Only Enforcement

Adapters may extract only metadata.

Disallowed content fields include:

- description
- content
- requirements
- responsibilities
- qualifications
- job_description
- body
- text (when used as content)
- html

`assert_metadata_only` is enforced during `DiscoveredJob` construction.

Invariant: No banned meta keys may enter SQL.

---

## 4. Timestamp Ownership Boundary

Adapters must:

```
first_seen_at = 0.0
last_seen_at = 0.0
```

Adapters do not generate ISO timestamps.

`DiscoveryStore` owns:

- discovered_at (UTC ISO)
- persistence timestamps

Invariant: `posted_at` remains NULL for all discovery rows.

---

## 5. Idempotent Upsert

Uniqueness is enforced by:

```
UNIQUE(provider_job_key)
```

Polling repeatedly must:

- Not duplicate rows
- Increment update count
- Preserve row identity

Invariant: No duplicate `provider_job_key` rows may exist.

---

## 6. Signal Isolation

Each signal:

- Polls independently
- Updates its own availability
- Does not mutate other signals
- Does not cascade behavior

Provider failure does not affect other providers.

---

## 7. Adapter Symmetry

All adapters must:

- Implement `SignalAdapter.poll`
- Accept `Signal`
- Return `List[DiscoveredJob]`
- Avoid persistence logic
- Avoid timestamp logic
- Avoid filtering
- Avoid ranking

Adapters are pure extraction layers.

---

## Supported Providers (At Lock Time)

- Greenhouse (`greenhouse_job_board_api`)
- Lever (`lever_job_board_api`)

Additional providers must conform to this document.

---

## What This Lock Does Not Guarantee

Phase 4.5 does not guarantee:

- Completeness of third-party APIs
- Pagination support
- External API uptime
- Content stability
- Location normalization
- Job de-duplication across providers

These are outside the Phase 4.5 boundary.

---

## Change Policy

Any modification to:

- DiscoveredJob schema
- jobs table schema
- Adapter behavior
- Timestamp handling
- UID structure

Requires:

1. Update to this document
2. Update to invariant tests
3. Explicit lock revision

No silent drift is permitted.

---

## Architectural Outcome

Discovery is now:

- Multi-provider
- Metadata-only
- Deterministic
- Idempotent
- Persistence-neutral
- Explicitly bounded

Phase 4.5 is complete and locked.
