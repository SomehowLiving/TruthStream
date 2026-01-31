"""
Anthropic Claude client for fact-checking analysis.
"""
import json
import re
from typing import Any

from anthropic import AsyncAnthropic

from src.config import get_settings
from src.services.ai.llm_provider import LLMProvider


def _extract_json(text: str) -> str:
    """Extract JSON from markdown code blocks if present."""
    if "```json" in text:
        match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    if "```" in text:
        match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
    return text.strip()


class AnthropicClient(LLMProvider):
    """Anthropic Claude client for fact-checking."""

    def __init__(self) -> None:
        api_key = get_settings().anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def analyze_content(self, text: str) -> dict[str, Any]:
        """
        Extract factual claims, sentiment, bias, manipulation from text.
        Returns dict with provider="anthropic".
        """
        prompt = """Extract factual claims, sentiment, bias_indicators, manipulation_techniques, confidence_score, summary from the following content.
Return JSON only. No markdown, no explanation.
Keys: claims (list of strings), sentiment (string), bias_indicators (list), manipulation_techniques (list), confidence_score (float 0-1), summary (string)

Content:
"""
        prompt += text[:4000]

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = message.content[0].text
            raw = _extract_json(content)
            result = json.loads(raw)
            result["provider"] = "anthropic"
            return result
        except json.JSONDecodeError as e:
            return {
                "provider": "anthropic",
                "claims": ["Parse error"],
                "sentiment": "unknown",
                "bias_indicators": [],
                "manipulation_techniques": [],
                "confidence_score": 0.5,
                "summary": f"JSON parse failed: {e}",
            }
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e

    async def synthesize(
        self,
        ai_analysis: dict[str, Any],
        web_results: list[dict[str, Any]],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Synthesize AI analysis + web results into verdict.
        Returns dict with verdict, confidence, explanation, toma_transparency, toma_alignment.
        """
        prompt = f"""Synthesize this fact-check evidence into a verdict.

AI Analysis: {ai_analysis}
Web Verification: {web_results}
File Metadata: {metadata}

Determine:
1. verdict: One of [verified, partially_false, out_of_context, manipulated, unverified]
2. confidence: 0.0 to 1.0
3. explanation: Why this verdict
4. toma_transparency: 0-100 (how clear are the sources?)
5. toma_alignment: 0-100 (how neutral/biased?)

Return JSON only. Keys: verdict, confidence, explanation, toma_transparency, toma_alignment"""

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )
            content = message.content[0].text
            raw = _extract_json(content)
            result = json.loads(raw)
            result["provider"] = "anthropic"
            return result
        except json.JSONDecodeError:
            return {
                "provider": "anthropic",
                "verdict": "unverified",
                "confidence": 0.0,
                "explanation": "Synthesis parse failed",
                "toma_transparency": 50,
                "toma_alignment": 50,
            }
        except Exception as e:
            raise RuntimeError(f"Anthropic synthesis error: {e}") from e
