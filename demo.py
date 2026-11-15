"""
🌺 ALOHA ECOSYSTEM — MVP END-TO-END DEMO
Runs Module 1 (Agent Identity Passport) and Module 2 (Raw Data Browser Engine).
"""

import json
import time

from aloha.identity import (
    create_agent_passport,
    validate_agent_id,
    print_passport_summary
)
from aloha.browser import scrape_url


def main():
    print("\n" + "=" * 60)
    print(" 🌺 WELCOME TO THE ALOHA ECOSYSTEM DEMO")
    print("=" * 60 + "\n")

    # STEP 1: INITIALIZE BOT IDENTITY
    print("▶ STEP 1: Registering AI Agent on the Aloha Network...")
    time.sleep(1)

    passport = create_agent_passport(
        agent_name="AlohaExplorer_v1",
        agent_class="101",
        capability="001",
        operator="Founder"
    )

    print_passport_summary(passport)

    bot_id = passport["aloha_id"]
    is_valid = validate_agent_id(bot_id)
    print(f"\n[Security Check] Verifying ID '{bot_id}'...")
    print(f"Status: {'✅ VERIFIED & AUTHENTIC' if is_valid else '❌ INVALID'}\n")

    if not is_valid:
        print("❌ Authentication failed.")
        return

    # STEP 2: EXECUTE RAW DATA BROWSER
    target_url = "https://example.com"
    print(f"▶ STEP 2: Agent {bot_id} requesting raw web payload from: {target_url}\n")
    time.sleep(1)

    result = scrape_url(target_url)

    if result.get("status") == "success":
        metrics = result.get("metrics", {})
        print("=" * 60)
        print(" 🚀 BROWSER ENGINE RESULTS")
        print("=" * 60)
        print(f" Original Size : {metrics.get('original_size_kb')} KB")
        print(f" Aloha Size    : {metrics.get('aloha_size_kb')} KB")
        print(f" Reduced By    : {metrics.get('data_reduced_by_percent')}%")
        print(f" Est. Tokens   : {metrics.get('estimated_tokens')} tokens")
        print(f" Latency       : {metrics.get('latency_ms')} ms")

        print("\n" + "-" * 60)
        print(" EXTRACTED MARKDOWN CONTENT FOR LLM:")
        print("-" * 60)
        print(result.get("content", ""))
        print("-" * 60)
        print("\n🎉 SUCCESS: Agent authenticated & raw data fetched successfully!")
    else:
        print(f"❌ Scrape failed: {result.get('error_message')}")


if __name__ == "__main__":
    main()
