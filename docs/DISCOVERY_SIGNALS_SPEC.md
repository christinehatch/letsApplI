# Discovery Signals Specification
*(Phase 4.5 — Design Document)*

## Purpose

This document defines how letsA(ppl)I discovers job opportunities **without scraping gated content, executing JavaScript, or impersonating users**.

Discovery is intentionally separated from interpretation, ranking, or application.

The goal is to remove cognitive labor from users **without adopting hostile automation**.

---

## Core Principle

> **Discovery ≠ Understanding**

Discovery answers:
- “Does a job exist?”
- “Did something change?”

Discovery does **not** answer:
- “Is this a good fit?”
- “What should the user do?”
- “What does this role require?”

---

## Discovery vs Hydration Model

Jobs exist in two explicit states:

### 🟡 Discovered
- Identified via public, machine-readable signals
- Contains metadata only
- Fully automated and deterministic

### 🔵 Hydrated
- Requires explicit user action
- Full description fetched *only if permitted*
- Enables Phase 5 alignment and proposals

No job may transition from Discovered → Hydrated without user consent.

---

## Supported Discovery Signals

### 1. Sitemap & Index Monitoring (Primary)

**Description**  
Many enterprises publish sitemap files that enumerate public URLs for indexing.

These files are intentionally exposed to automated systems (e.g., search engines).

**Inputs**
- `sitemap.xml`
- sitemap index files
- robots-referenced indexes

**Extracted Fields**
- Job URL
- Job ID (if present)
- Last modified date (if present)

**Explicitly Not Extracted**
- Job descriptions
- Requirements
- Role evaluations

**Failure Behavior**
- If blocked or absent → mark source as unavailable
- No retries with altered headers

> _Gemini influence_: Uses “index auditing” instead of page scraping.  
> _Your constraint_: Read-only, deterministic, no JS execution.

---

### 2. Public Search API Side-Channels (Secondary)

**Description**  
Some companies expose JSON job search APIs to power their own internal search experiences.

These APIs often return structured metadata without rendering heavy UI layers.

**Allowed Behavior**
- Standard GET/POST requests
- No spoofed headers
- No authentication bypass

**Extracted Fields**
- Job ID
- Title
- Team / Department (if provided)
- Location (if provided)

**Explicitly Forbidden**
- Pulling full descriptions automatically
- Following private or undocumented endpoints

**Failure Behavior**
- If blocked → mark source as “Limited Availability”
- Do not degrade into scraping

> _Gemini influence_: “Side-channel APIs”  
> _Your constraint_: No interpretation, no fallback to scraping

---

### 3. Aggregator-of-Aggregators (Tertiary)

**Description**  
Large companies intentionally mirror job postings on platforms that support indexing.

letsA(ppl)I may use these sources **for discovery only**.

**Examples**
- LinkedIn RSS feeds
- Google Jobs structured results
- Greenhouse / Lever public feeds

**Verification Step**
- Perform a HEAD request to the official job URL
- Confirm 200 OK (existence only)

**Explicitly Forbidden**
- Parsing gated job pages
- Extracting proprietary content

> _Gemini influence_: Proxy discovery via aggregators  
> _Your constraint_: Company site remains source of truth, but not scraped

---

## Output: Discovery Signal Record

```json
{
  "company": "Adobe",
  "job_id": "R164245",
  "title": "Data Engineer",
  "url": "...",
  "discovered_at": "2026-01-18T00:00:00Z",
  "source_type": "sitemap",
  "hydrated": false
}

