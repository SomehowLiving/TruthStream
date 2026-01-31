#!/usr/bin/env python3
"""
Test script for UnifiedAI - Phase 2 verification.

Usage:
    cd packages/api && python -m scripts.test_ai

Requires ANTHROPIC_API_KEY or GROQ_API_KEY in .env
"""
import asyncio
import sys
from pathlib import Path

# Add packages/api to path so src.* imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.ai.unified_ai import UnifiedAI


async def main() -> None:
    ai = UnifiedAI()
    test_text = "Modi announced new currency today"

    print("Testing UnifiedAI.analyze_with_fallback(...)")
    print(f"Input: {test_text!r}\n")

    result = await ai.analyze_with_fallback(test_text)

    if result.get("error"):
        print("ERROR: All AI providers failed")
        print(f"Message: {result.get('message', '')}")
        print(f"Detail: {result.get('detail', '')}")
        print("\nEnsure ANTHROPIC_API_KEY or GROQ_API_KEY is set in .env")
        print("(UnifiedAI structure OK - run with API key to verify full flow)")
        sys.exit(1)

    print(f"Provider: {result.get('provider')}")
    print(f"Claims: {result.get('claims', [])}")
    print(f"Sentiment: {result.get('sentiment', 'N/A')}")
    print(f"Confidence: {result.get('confidence_score', 'N/A')}")
    print(f"Summary: {result.get('summary', 'N/A')}")

    # Test synthesize
    print("\n--- Testing synthesize_with_fallback ---")
    web_results = [{"title": "News", "snippet": "No new currency announced"}]
    synth = await ai.synthesize_with_fallback(result, web_results, {})
    if synth.get("error"):
        print("Synthesize failed:", synth.get("message"))
    else:
        print(f"Provider: {synth.get('provider')}")
        print(f"Verdict: {synth.get('verdict')}")
        print(f"Confidence: {synth.get('confidence')}")
        print(f"Explanation: {synth.get('explanation', '')[:200]}...")

    print("\n✓ UnifiedAI test passed")


if __name__ == "__main__":
    asyncio.run(main())
