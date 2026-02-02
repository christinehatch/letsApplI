# Phase 5.1 — PR Test Checklist  
**Consent-Scoped Reading**

**Applies To:** Any PR touching Phase 5.1 code  
**Blocking:** YES — all items must be satisfied before merge

---

## 🔐 Consent Enforcement

- [ ] No code path allows job content access without a valid consent payload
- [ ] Consent scope is checked for exact equality: `read_job_posting`
- [ ] Phase 5.1 aborts immediately if consent is missing, invalid, or malformed
- [ ] Consent revocation halts execution immediately
- [ ] No content remains visible or accessible after consent revocation

---

## 📖 Reading Boundary

- [ ] No job content exists in memory before Phase 5.1 activation
- [ ] No parsing, inspection, tokenization, or preprocessing occurs pre-consent
- [ ] Exactly **one** fetch occurs per read
- [ ] Fetch target is limited to the primary job posting surface explicitly requested by the user
- [ ] No linked pages, PDFs, expandable sections, or external assets are fetched
- [ ] Unavailable or blocked sources terminate Phase 5.1 without retries

---

## 🪞 Representation Integrity

- [ ] Displayed content matches source content byte-for-byte
- [ ] No reordering, cleanup, summarization, or omission occurs
- [ ] No UI highlights, emphasis, or prioritization is introduced
- [ ] Partial or truncated content is explicitly labeled as incomplete

---

## 🧠 Persistence & Memory

- [ ] Raw job content is not persisted beyond the active user session
- [ ] No debug logs contain job content
- [ ] No caches, replay buffers, or background stores retain content
- [ ] No summaries, tags, embeddings, or inferred attributes are stored

---

## 🧭 Truthfulness

- [ ] System language accurately reflects what was read (or not read)
- [ ] The system never implies interpretation, evaluation, or understanding
- [ ] Reading is explicitly framed as non-interpretive

---

## 🚧 Phase Boundaries

- [ ] Phase 5.1 does **not** trigger Phase 5.2 or later phases
- [ ] No downstream artifacts are precomputed or previewed
- [ ] No interpretation logic is reachable from Phase 5.1 code paths

---

## ✅ Final Gate

- [ ] All Phase 5.1 invariant tests pass in CI
- [ ] No invariant tests were weakened, skipped, or removed
- [ ] Any changes touching Phase 5.1 include updated or validated tests

**If any box above is unchecked, the PR must not merge.**

