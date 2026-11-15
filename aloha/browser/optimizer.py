"""
Aloha Browser Engine — Optimizer
Cleans raw Markdown, calculates LLM token metrics, and computes bandwidth savings.
"""

import re


def clean_markdown(raw_markdown: str) -> str:
    """Removes excessive whitespace and blank lines from parsed Markdown."""
    if not raw_markdown:
        return ""
    # Replace 3 or more consecutive newlines with 2 newlines
    cleaned = re.sub(r'\n{3,}', '\n\n', raw_markdown)
    return cleaned.strip()


def estimate_llm_tokens(text: str) -> int:
    """Fast approximation of LLM token consumption (~1.3 tokens per word)."""
    words = text.split()
    return int(len(words) * 1.3)


def calculate_metrics(original_bytes: int, optimized_text: str, latency_ms: float) -> dict:
    """Calculates performance gains and compression statistics."""
    optimized_bytes = len(optimized_text.encode('utf-8'))
    orig_kb = original_bytes / 1024
    opt_kb = optimized_bytes / 1024

    if orig_kb > 0:
        savings = round((1 - (opt_kb / orig_kb)) * 100, 2)
    else:
        savings = 0.0

    return {
        "original_size_kb": round(orig_kb, 2),
        "aloha_size_kb": round(opt_kb, 2),
        "data_reduced_by_percent": max(savings, 0.0),
        "estimated_tokens": estimate_llm_tokens(optimized_text),
        "latency_ms": round(latency_ms, 2)
    }


if __name__ == "__main__":
    sample_text = "This is a test sentence for token calculation."
    print("🌺 Tokens:", estimate_llm_tokens(sample_text))
    print("🌺 Metrics:", calculate_metrics(50000, sample_text, 120.5))
