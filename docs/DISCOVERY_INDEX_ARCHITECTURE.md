# DISCOVERY_INDEX_ARCHITECTURE

## Purpose

Define the long-term architecture for deterministic job discovery and exploration in letsA(ppl)I.

The system must:

- function without LLMs
- provide high-quality job discovery
- allow structured exploration
- use AI only for optional interpretation and insight

LLMs must not be required for core functionality.

## System Philosophy

letsA(ppl)I follows this principle:

> The system must work deterministically. LLMs are tools for the user, not the engine of the product.

Core functionality must remain available if AI services fail.

## System Layers

The discovery system consists of four layers.

Adapters  
↓  
Discovery Index  
↓  
Signal Classification  
↓  
Exploration Engine

LLM interpretation is optional and occurs only after user interaction.

## Layer 1 - Adapter Ingestion

Adapters retrieve structured job data from ATS platforms.

Supported adapters:

- Greenhouse
- Lever
- Ashby
- SmartRecruiters
- Workday

Each adapter must return:

- `job_id`
- `company`
- `title`
- `location`
- `description_html`
- `source_url`
- `discovered_at`

Adapters must attempt API access first, then fallback to board JSON extraction.

Example flow:

```text
attempt API
↓
if blocked
↓
fetch board HTML
↓
extract embedded JSON
```

## Layer 2 - Discovery Index

The discovery index stores raw job descriptions at ingestion time.

Unlike the current hydration model, discovery ingestion retrieves `description_html` immediately.

This enables deterministic indexing.

Example storage model:

```text
jobs
    id
    company
    title
    location
    description_html
    description_text
    discovered_at
```

No AI processing occurs here.

## Layer 3 - Deterministic Signal Classification

Jobs are categorized using rule-based keyword detection.

This classification produces signals like:

- AI
- DATA
- BACKEND
- PLATFORM
- INFRASTRUCTURE
- ML

Example rules:

```text
AI:
    machine learning
    deep learning
    LLM
    pytorch
    tensorflow

DATA:
    spark
    ETL
    data pipeline
    analytics

BACKEND:
    API
    microservices
    distributed systems

PLATFORM:
    internal tooling
    developer platform
    infrastructure platform
```

Classification must be:

- deterministic
- fast
- explainable

LLMs are not used.

Output:

```text
job_signals
    job_id
    signals[]
```

## Layer 4 - Company Intelligence

Company-level signals enable advanced exploration.

Example attributes:

- `company_size`
- `tech_focus`
- `cloud_stack`
- `engineering_domain`

Possible sources:

- job descriptions
- company engineering pages
- external datasets

Example derived signals:

- `cloud_stack = aws`
- `engineering_focus = infrastructure`
- `company_size = mid`

## Exploration Engine

The exploration engine combines job signals and company signals.

Example queries:

- AI infrastructure jobs
- platform teams using AWS
- mid-size companies building ML systems

Future exploration queries may include:

- companies using AWS with Glassdoor rating > 4
- remote-first ML companies
- platform teams at mid-size companies

These queries operate on the deterministic index.

## LLM Role (Optional Layer)

LLMs are invoked only when a user requests analysis.

Example actions:

- Analyze this role
- Explain key requirements
- Identify capability signals
- Suggest project opportunities

LLM output must always reference:

- `span_map`
- source evidence

LLMs do not influence discovery or ranking.

## Why This Architecture

This approach provides:

- reliability  
  Discovery works without AI.
- speed  
  Keyword indexing is extremely fast.
- transparency  
  Users see how roles are classified.
- trust  
  AI is optional and user-controlled.

## Implementation Roadmap

Development should proceed in phases.

### Phase 1 - Adapter Coverage

Implement adapters for:

- Greenhouse fallback JSON extraction
- Ashby
- SmartRecruiters
- Workday

Goal: increase discovery coverage.

### Phase 2 - Description Indexing

Modify discovery pipeline to store:

- `description_html`
- `description_text`

at ingestion time.

Hydration becomes unnecessary for most jobs.

### Phase 3 - Deterministic Signal Classifier

Implement rule-based classifier:

- AI
- DATA
- BACKEND
- PLATFORM
- INFRA

Store results in `job_signals`.

### Phase 4 - Exploration Queries

Enable exploration based on signals:

- AI roles
- platform roles
- data roles

### Phase 5 - Company Intelligence

Add company attributes:

- size
- cloud stack
- domain
- culture signals
