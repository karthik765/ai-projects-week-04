import re


_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)


def clean_json_text(text: str) -> tuple[str, list[str]]:
    """Apply only deterministic, low-risk formatting repairs."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("model output must be a non-empty string")
    cleaned = text.strip()
    repairs: list[str] = []
    match = _FENCE.search(cleaned)
    if match:
        cleaned = match.group(1).strip()
        repairs.append("removed Markdown code fence")
    without_trailing = _remove_trailing_commas(cleaned)
    if without_trailing != cleaned:
        cleaned = without_trailing
        repairs.append("removed trailing comma")
    return cleaned, repairs


def _remove_trailing_commas(text: str) -> str:
    """Remove commas before a closing token while preserving quoted strings."""
    output: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == '"' and not escaped:
            in_string = not in_string
        if char == "," and not in_string:
            lookahead = index + 1
            while lookahead < len(text) and text[lookahead].isspace():
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in "}]":
                index += 1
                escaped = False
                continue
        output.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
        index += 1
    return "".join(output)
