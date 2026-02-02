import os

from phase5.proposal import Proposal


FALLBACK_TEXT = "This is an example AI-generated phrasing suggestion."


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
            from llm.adapter import LLMAdapter
            adapter = LLMAdapter()
            # 🧪 Test-only override (cross-process safe)
            test_override = os.getenv("LLM_SHADOW_TEST_OUTPUT")

            if test_override:
                generated = test_override
            else:
                source_text = (
                    "Implemented a small Python project using data structures."
                )

                prompt = (
                    "Rewrite the following resume bullet using neutral, non-authoritative language.\n\n"
                    f"Original text:\n{source_text}\n\n"
                    "Constraints:\n"
                    "- Do not add facts\n"
                    "- Do not infer skill level or seniority\n"
                    "- Do not recommend actions\n"
                    "- Return only the rewritten text"
                )

                adapter = LLMAdapter()
                generated = adapter.generate(
                    prompt=prompt,
                    context="phrasing_variant",
                    temperature=0.0,
                )


            # 🔑 Phase 5.7 liveness gate
            if generated and generated.strip():
                text = generated.strip()

        except Exception as e:
            # Shadow-mode failures must never affect behavior
            pass

    return [
        Proposal.create(
            text=text,
            context="phrasing_suggestion",
        )
    ]
