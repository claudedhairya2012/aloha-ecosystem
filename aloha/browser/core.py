"""
Aloha Browser Engine — Core Coordinator
Orchestrates Fetcher, Parser, and Optimizer into a single scrape function.
"""

from .fetcher import fetch_raw_html
from .parser import parse_html_to_markdown
from .optimizer import clean_markdown, calculate_metrics


def scrape_url(url: str, timeout: int = 10) -> dict:
    """
    Main entry point for the Aloha Raw Data Browser Engine.
    Fetches a web page, strips visual bloat, and returns token-optimized Markdown.
    """
    # Step 1: Fetch Raw HTML
    fetch_result = fetch_raw_html(url, timeout=timeout)
    if fetch_result.get("status") == "error":
        return fetch_result

    # Step 2: Parse HTML to Markdown
    parse_result = parse_html_to_markdown(fetch_result["html"])

    # Step 3: Clean and Optimize Markdown
    cleaned_content = clean_markdown(parse_result["raw_markdown"])

    # Step 4: Calculate Performance Metrics
    metrics = calculate_metrics(
        original_bytes=fetch_result["original_size_bytes"],
        optimized_text=cleaned_content,
        latency_ms=fetch_result["latency_ms"]
    )

    return {
        "status": "success",
        "url": url,
        "metadata": parse_result["metadata"],
        "metrics": metrics,
        "content": cleaned_content
    }


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

    print("🌺 Running Raw Data Browser Engine Test...")
    res = scrape_url("https://example.com")
    print(f"Status  : {res['status']}")
    print(f"Savings : {res.get('metrics', {}).get('data_reduced_by_percent')}%")
