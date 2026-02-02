from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Optional, Tuple


# ---------------------------------------------------------------------------
# Canonical archetype set (v0)
# ---------------------------------------------------------------------------

ARCHETYPES_V0: Tuple[str, ...] = (
    "SOFTWARE_ENGINEER",
    "SOFTWARE_ENGINEER_EARLY",
    "ML_ENGINEER",
    "AI_ML_RESEARCHER",
    "DATA_SCIENTIST",
    "PRODUCT_MANAGER",
    "PRODUCT_PROGRAM_MANAGER",
    "TECHNICAL_PROGRAM_MANAGER",
    "AI_SOLUTIONS_ARCHITECT",
    "SOLUTIONS_ENGINEER",
    "DEVREL_COMMUNICATOR",
    "ENGINEERING_MANAGER",
    "UX_PRODUCT_DESIGNER",
    "UX_RESEARCHER",
    "ANALYST_COMMENTATOR",
    "SALES_ACCOUNT",
    "UNKNOWN",
)


# ---------------------------------------------------------------------------
# Public return object
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArchetypeMatch:
    """
    Result of deterministic archetype matching from title-only input.

    This object provides *orientation*, not interpretation.
    It is safe to compute before job hydration.
    """

    archetype: str
    label: str
    orientation_lines: Tuple[str, ...]
    matched_rule_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def normalize_title(title: str) -> str:
    """
    Normalize a raw job title for deterministic matching.

    Rules:
    - lower-case
    - replace common separators with spaces
    - collapse whitespace
    - do NOT inspect job content
    """
    t = title.strip().lower()
    t = re.sub(r"[/,_\-]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# ---------------------------------------------------------------------------
# Rule definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArchetypeRule:
    """
    One ordered deterministic matching rule.
    First matching rule wins.
    """
    rule_id: str
    pattern: re.Pattern
    archetype: str
    label: str
    orientation_lines: Tuple[str, ...]


def _c(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


# ---------------------------------------------------------------------------
# Orientation text (what we say *without* reading the job)
# ---------------------------------------------------------------------------

_ORIENTATION: dict[str, Tuple[str, Tuple[str, ...]]] = {
    "AI_SOLUTIONS_ARCHITECT": (
        "AI Solutions Architect",
        (
            "Customer-facing technical role, often sales-adjacent or advisory.",
            "Translates product capabilities into architectures and use cases.",
            "Typically emphasizes communication, demos, and stakeholder alignment.",
        ),
    ),
    "SOLUTIONS_ENGINEER": (
        "Solutions Engineer",
        (
            "Customer-facing technical role supporting adoption and integration.",
            "Often involves demos, prototyping, and troubleshooting.",
            "Success measured by customer clarity and outcomes.",
        ),
    ),
    "ML_ENGINEER": (
        "Machine Learning Engineer",
        (
            "Applies ML models in production systems.",
            "More engineering and reliability than research novelty.",
            "Success measured by performance and stability.",
        ),
    ),
    "AI_ML_RESEARCHER": (
        "AI / ML Researcher",
        (
            "Research-focused role exploring new models or methods.",
            "Often involves experimentation or publication.",
            "Success measured by insight and novelty.",
        ),
    ),
    "SOFTWARE_ENGINEER_EARLY": (
        "Software Engineer (Early Career)",
        (
            "Entry-level or internship engineering role.",
            "Emphasis on learning, execution, and mentorship.",
            "Interview bar may still be high despite junior scope.",
        ),
    ),
    "SOFTWARE_ENGINEER": (
        "Software Engineer",
        (
            "Builds and maintains production software systems.",
            "Scope varies widely by team and product area.",
            "Success measured by shipping and reliability.",
        ),
    ),
    "DATA_SCIENTIST": (
        "Data Scientist",
        (
            "Analyzes data to inform decisions and strategy.",
            "Often communication-heavy with metrics and experiments.",
            "May emphasize analytics over modeling.",
        ),
    ),
    "PRODUCT_PROGRAM_MANAGER": (
        "Product Program Manager",
        (
            "Execution-focused role managing timelines and delivery.",
            "Coordinates across teams and dependencies.",
            "Success measured by predictable execution.",
        ),
    ),
    "TECHNICAL_PROGRAM_MANAGER": (
        "Technical Program Manager",
        (
            "Coordinates complex technical initiatives.",
            "Requires system understanding but limited coding ownership.",
            "Success measured by removing blockers.",
        ),
    ),
    "PRODUCT_MANAGER": (
        "Product Manager",
        (
            "Owns product direction and prioritization.",
            "Heavy stakeholder communication.",
            "Success measured by product outcomes.",
        ),
    ),
    "DEVREL_COMMUNICATOR": (
        "Developer Relations / Technical Communicator",
        (
            "Explains technical concepts to developer audiences.",
            "Includes writing, talks, and educational content.",
            "Success measured by understanding and adoption.",
        ),
    ),
    "ENGINEERING_MANAGER": (
        "Engineering Manager",
        (
            "Leads engineering teams and delivery.",
            "Focus on people, planning, and execution.",
            "Success measured by team outcomes.",
        ),
    ),
    "UX_PRODUCT_DESIGNER": (
        "UX / Product Designer",
        (
            "Designs user experiences and product flows.",
            "Highly collaborative with product and engineering.",
            "Success measured by usability and clarity.",
        ),
    ),
    "UX_RESEARCHER": (
        "UX Researcher",
        (
            "Studies user behavior to inform product decisions.",
            "Methods-driven qualitative and quantitative work.",
            "Success measured by insight quality.",
        ),
    ),
    "ANALYST_COMMENTATOR": (
        "Analyst / Commentator",
        (
            "Analyzes topics and communicates insight to an audience.",
            "Often writing or opinion-driven.",
            "Success measured by clarity and influence.",
        ),
    ),
    "SALES_ACCOUNT": (
        "Sales / Account Role",
        (
            "Revenue-focused customer relationship role.",
            "Often quota-driven.",
            "Success measured by pipeline and closed deals.",
        ),
    ),
    "UNKNOWN": (
        "Unknown",
        (
            "This title does not match a known archetype.",
            "Click the listing to explore the role directly.",
        ),
    ),
}


# ---------------------------------------------------------------------------
# Ordered matching rules (v0)
# ---------------------------------------------------------------------------

RULES_V0: Tuple[ArchetypeRule, ...] = (
    ArchetypeRule(
        "ai_solutions_architect_explicit",
        _c(r"\b(ai|ml)\s+solutions\s+architect\b"),
        "AI_SOLUTIONS_ARCHITECT",
        *_ORIENTATION["AI_SOLUTIONS_ARCHITECT"],
    ),
    ArchetypeRule(
        "solutions_architect",
        _c(r"\bsolutions\s+architect\b"),
        "AI_SOLUTIONS_ARCHITECT",
        *_ORIENTATION["AI_SOLUTIONS_ARCHITECT"],
    ),
    ArchetypeRule(
        "sales_engineer",
        _c(r"\b(sales|pre[-\s]?sales|field)\s+engineer\b"),
        "SOLUTIONS_ENGINEER",
        *_ORIENTATION["SOLUTIONS_ENGINEER"],
    ),
    ArchetypeRule(
        "solutions_engineer",
        _c(r"\bsolutions\s+engineer\b"),
        "SOLUTIONS_ENGINEER",
        *_ORIENTATION["SOLUTIONS_ENGINEER"],
    ),
    ArchetypeRule(
        "ml_engineer",
        _c(r"\b(machine\s+learning|ml)\s+engineer\b"),
        "ML_ENGINEER",
        *_ORIENTATION["ML_ENGINEER"],
    ),
    ArchetypeRule(
        "ai_engineer",
        _c(r"\bai\s+engineer\b"),
        "ML_ENGINEER",
        *_ORIENTATION["ML_ENGINEER"],
    ),
    ArchetypeRule(
        "researcher",
        _c(r"\b(research\s+scientist|ai\s+researcher|ml\s+researcher|research\s+engineer)\b"),
        "AI_ML_RESEARCHER",
        *_ORIENTATION["AI_ML_RESEARCHER"],
    ),
    ArchetypeRule(
        "early_career_engineer",
        _c(r"\b(new\s+grad|graduate|intern)\b.*\bengineer\b"),
        "SOFTWARE_ENGINEER_EARLY",
        *_ORIENTATION["SOFTWARE_ENGINEER_EARLY"],
    ),
    ArchetypeRule(
        "software_engineer",
        _c(r"\bsoftware\s+engineer\b"),
        "SOFTWARE_ENGINEER",
        *_ORIENTATION["SOFTWARE_ENGINEER"],
    ),
    ArchetypeRule(
        "engineering_specialty",
        _c(r"\b(backend|frontend|full\s*stack|platform|infrastructure|cloud|systems)\s+engineer\b"),
        "SOFTWARE_ENGINEER",
        *_ORIENTATION["SOFTWARE_ENGINEER"],
    ),
    ArchetypeRule(
        "data_scientist",
        _c(r"\bdata\s+scientist\b"),
        "DATA_SCIENTIST",
        *_ORIENTATION["DATA_SCIENTIST"],
    ),
    ArchetypeRule(
        "product_program_manager",
        _c(r"\bproduct\s+program\s+manager\b"),
        "PRODUCT_PROGRAM_MANAGER",
        *_ORIENTATION["PRODUCT_PROGRAM_MANAGER"],
    ),
    ArchetypeRule(
        "technical_program_manager",
        _c(r"\b(technical\s+program\s+manager|tpm)\b"),
        "TECHNICAL_PROGRAM_MANAGER",
        *_ORIENTATION["TECHNICAL_PROGRAM_MANAGER"],
    ),
    ArchetypeRule(
        "product_manager",
        _c(r"\b(product\s+manager|\bpm\b)\b"),
        "PRODUCT_MANAGER",
        *_ORIENTATION["PRODUCT_MANAGER"],
    ),
    ArchetypeRule(
        "devrel",
        _c(r"\b(developer\s+advocate|developer\s+relations|devrel|technical\s+writer)\b"),
        "DEVREL_COMMUNICATOR",
        *_ORIENTATION["DEVREL_COMMUNICATOR"],
    ),
    ArchetypeRule(
        "designer",
        _c(r"\b(ux|product|ui)\s+designer\b"),
        "UX_PRODUCT_DESIGNER",
        *_ORIENTATION["UX_PRODUCT_DESIGNER"],
    ),
    ArchetypeRule(
        "ux_researcher",
        _c(r"\bux\s+researcher\b"),
        "UX_RESEARCHER",
        *_ORIENTATION["UX_RESEARCHER"],
    ),
    ArchetypeRule(
        "engineering_manager",
        _c(r"\bengineering\s+manager\b"),
        "ENGINEERING_MANAGER",
        *_ORIENTATION["ENGINEERING_MANAGER"],
    ),
    ArchetypeRule(
        "analyst_commentator",
        _c(r"\b(analyst|columnist|commentator|editorial)\b"),
        "ANALYST_COMMENTATOR",
        *_ORIENTATION["ANALYST_COMMENTATOR"],
    ),
    ArchetypeRule(
        "sales_account",
        _c(r"\b(account\s+executive|sales\s+manager|business\s+development|bdr|sdr)\b"),
        "SALES_ACCOUNT",
        *_ORIENTATION["SALES_ACCOUNT"],
    ),
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match_archetype(title: str, *, include_debug: bool = False) -> ArchetypeMatch:
    """
    Deterministically map a job title to a role archetype.

    Title-only input. No job content is read.
    """
    t = normalize_title(title)

    for rule in RULES_V0:
        if rule.pattern.search(t):
            return ArchetypeMatch(
                archetype=rule.archetype,
                label=rule.label,
                orientation_lines=rule.orientation_lines,
                matched_rule_id=rule.rule_id if include_debug else None,
            )

    label, lines = _ORIENTATION["UNKNOWN"]
    return ArchetypeMatch(
        archetype="UNKNOWN",
        label=label,
        orientation_lines=lines,
        matched_rule_id="no_match" if include_debug else None,
    )


# ---------------------------------------------------------------------------
# Safety check
# ---------------------------------------------------------------------------

def _assert_archetypes_are_known() -> None:
    allowed = set(ARCHETYPES_V0)
    for rule in RULES_V0:
        assert rule.archetype in allowed, f"Unknown archetype: {rule.archetype}"


_assert_archetypes_are_known()


