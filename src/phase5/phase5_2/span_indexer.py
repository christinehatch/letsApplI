import re


MAX_SPAN_CHARS = 400


def _split_paragraphs(raw_content: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_content) if p.strip()]
    if paragraphs:
        return paragraphs
    stripped = raw_content.strip()
    return [stripped] if stripped else []


def _split_sentences(text: str) -> list[str]:
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    return parts if parts else [text.strip()]


def _chunk_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    sentences = _split_sentences(text)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(sentence), max_chars):
                chunks.append(sentence[i : i + max_chars].strip())
            continue

        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = sentence

    if current:
        chunks.append(current)

    return [c for c in chunks if c]


def build_spans(raw_content: str) -> list[dict]:
    paragraphs = _split_paragraphs(raw_content)

    span_texts: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= MAX_SPAN_CHARS:
            span_texts.append(paragraph)
        else:
            span_texts.extend(_chunk_text(paragraph, MAX_SPAN_CHARS))

    if not span_texts:
        fallback = raw_content.strip() or "[empty]"
        span_texts = [fallback[:MAX_SPAN_CHARS]]

    spans = []
    for i, text in enumerate(span_texts, start=1):
        spans.append({"span_id": f"span_{i}", "text": text})

    return spans


def format_span_prompt(spans: list[dict]) -> str:
    lines = ["Span Index", ""]
    for span in spans:
        lines.append(f"{span['span_id']}:")
        lines.append(span["text"])
        lines.append("")

    return "\n".join(lines).strip()
