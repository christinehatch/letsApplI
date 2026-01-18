import os
from openai import OpenAI


class LLMAdapterError(Exception):
    pass


class LLMAdapter:
    """
    Phase 5.7 LLM Adapter (Shadow Mode)

    Guarantees:
    - No persistence
    - No retries that alter semantics
    - No authority or recommendations
    - Caller controls visibility and approval
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMAdapterError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)

    def generate(
        self,
        *,
        prompt: str,
        context: str,
        temperature: float = 0.0,
        max_tokens: int = 200,
    ) -> str:
        """
        Generate a non-authoritative phrasing variant.

        This method:
        - Returns raw text only
        - Makes no guarantees about usefulness
        - Raises on hard failures
        """

        try:
            response = self.client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You generate neutral, non-authoritative phrasing variants.\n"
                            "Do not add facts.\n"
                            "Do not make recommendations.\n"
                            "Do not infer intent or skill.\n"
                            "Do not evaluate correctness.\n"
                            "Return only the rewritten text."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            # Extract plain text safely
            output = response.output_text
            if not output or not output.strip():
                raise LLMAdapterError("Empty LLM response")

            return output.strip()

        except Exception as e:
            raise LLMAdapterError(str(e)) from e
