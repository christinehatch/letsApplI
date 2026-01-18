# src/llm/adapter.py

from typing import Optional


class LLMAdapterError(Exception):
    """Raised when the LLM adapter fails in a non-recoverable way."""


class LLMAdapter:
    """
    Minimal, non-authoritative LLM adapter (Phase 5.7).

    This adapter:
    - accepts a fully-formed prompt
    - returns raw text output only
    - performs no retries
    - performs no logging
    - performs no memory writes
    - has no side effects

    It is intended for shadow-mode execution only.
    """

    def generate(
        self,
        prompt: str,
        *,
        context: str,
        temperature: float = 0.0,
    ) -> str:
        """
        Execute the prompt and return raw LLM output.

        Parameters:
            prompt (str): Fully rendered prompt text.
            context (str): Declarative generation context
                           (e.g. 'phrasing_variant').
            temperature (float): Explicitly set; defaults to 0.0.

        Returns:
            str: Raw LLM output (untrusted, unvalidated).

        Raises:
            LLMAdapterError: If the call fails.
        """
        raise NotImplementedError("LLMAdapter.generate is not implemented")

