from src.phase5.phase5_2.llm_adapter import Phase52LLMAdapter


def test_build_user_prompt_includes_span_index_section():
    raw_content = "Paragraph A\n\nParagraph B"
    prompt = Phase52LLMAdapter._build_user_prompt(raw_content)

    assert "Span Index" in prompt
    assert "span_1:" in prompt
    assert "span_2:" in prompt
    assert "Use these span IDs when referencing evidence." in prompt
    assert f"Job Content:\n{raw_content}" in prompt
