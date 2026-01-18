import os

from phase5.proposal import Proposal
from llm.adapter import LLMAdapter


FALLBACK_TEXT = "This is an example AI-generated phrasing suggestion."
TEST_SHADOW_OUTPUT = os.getenv("LLM_SHADOW_TEST_OUTPUT")

def get_mock_proposals():
    """
    Phase 5.7 — Shadow-mode proposal surfacing

    - LLM runs only when USE_LLM_SHADOW_MODE=1
    - Successful output replaces fallback text
    - Failures preserve fallback behavior
    - Output is visible ONLY as a Proposal
    """

    text = FALLBACK_TEXT

    if os.getenv("USE_LLM_SHADOW_MODE") == "1":
        try:
            # 🧪 Test-only override (cross-process safe)
            if TEST_SHADOW_OUTPUT:
                generated = TEST_SHADOW_OUTPUT
            else:
                adapter = LLMAdapter()
                generated = adapter.generate(
                    prompt=(
                        "Generate a neutral phrasing variant for an existing resume bullet. "
                        "Do not add facts. Do not make recommendations."
                    ),
                    context="phrasing_variant",
                    temperature=0.0,
                )

            if generated and generated.strip():
                text = generated.strip()

        except Exception:
            pass

    return [
        Proposal.create(
            text=text,
            context="phrasing_suggestion",
        )
    ]
