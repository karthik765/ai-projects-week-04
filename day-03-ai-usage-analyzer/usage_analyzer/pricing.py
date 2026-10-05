"""Illustrative local pricing profiles; not live billing data."""

PRICING_PER_MILLION_TOKENS = {
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (5.00, 15.00),
    "claude-3-5-sonnet": (3.00, 15.00),
    "gemini-1.5-flash": (0.075, 0.30),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    input_rate, output_rate = PRICING_PER_MILLION_TOKENS.get(model, (1.00, 3.00))
    return input_tokens * input_rate / 1_000_000 + output_tokens * output_rate / 1_000_000
