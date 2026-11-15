"""
Aloha Browser Engine — Fetcher
Handles network requests with custom stealth headers and latency metrics.
"""

import urllib.request
import urllib.error
import time


def fetch_raw_html(url: str, timeout: int = 10) -> dict:
    """
    Fetches raw HTML from a target URL with latency and size tracking.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (AlohaBot/2.0; AI Native Browser Engine; +https://aloha.net)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    req = urllib.request.Request(url, headers=headers)
    start_time = time.time()

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw_bytes = response.read()
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000

            return {
                "status": "success",
                "url": url,
                "html": raw_bytes.decode('utf-8', errors='ignore'),
                "original_size_bytes": len(raw_bytes),
                "latency_ms": latency_ms
            }

    except urllib.error.URLError as e:
        return {
            "status": "error",
            "url": url,
            "error_message": f"Network Error: {str(e.reason)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "url": url,
            "error_message": f"Unexpected Error: {str(e)}"
        }


if __name__ == "__main__":
    print("🌺 Testing Fetcher...")
    res = fetch_raw_html("https://example.com")
    print(f"Status: {res['status']}, Latency: {res.get('latency_ms', 0):.2f}ms")
