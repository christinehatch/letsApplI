from src.phase5.phase5_2.span_indexer import build_spans, format_span_prompt


def test_build_spans_uses_paragraph_boundaries():
    spans = build_spans("Paragraph A\n\nParagraph B\n\nParagraph C")

    assert [s["span_id"] for s in spans] == ["span_1", "span_2", "span_3"]
    assert [s["text"] for s in spans] == ["Paragraph A", "Paragraph B", "Paragraph C"]


def test_build_spans_splits_long_paragraphs_under_400_chars():
    sentence = "This is a sentence with enough text to support deterministic splitting."
    long_paragraph = " ".join([sentence] * 20)

    spans = build_spans(long_paragraph)

    assert len(spans) > 1
    assert all(len(s["text"]) <= 400 for s in spans)
    assert spans[0]["span_id"] == "span_1"
    assert spans[-1]["span_id"] == f"span_{len(spans)}"


def test_format_span_prompt_renders_span_index_section():
    prompt = format_span_prompt(
        [
            {"span_id": "span_1", "text": "First"},
            {"span_id": "span_2", "text": "Second"},
        ]
    )

    assert "Span Index" in prompt
    assert "span_1:" in prompt
    assert "First" in prompt
    assert "span_2:" in prompt
    assert "Second" in prompt
