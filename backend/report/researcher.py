"""
Async researcher that enriches high-priority BGP recommendations with
web-searched guidance, official form links, and timeline information.

One Claude call (with web_search tool) is made per high-priority
recommendation; all calls run concurrently via asyncio.gather.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TypedDict

import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"


class ResearchLink(TypedDict):
    title: str
    url: str
    description: str


class EnrichedRecommendation(TypedDict):
    priority: str
    title: str
    detail: str
    links: list[ResearchLink]
    guidance: str
    timeline: str | None
    researched: bool


async def research_recommendations(
    recommendations: list[dict],
    context: dict,
) -> list[EnrichedRecommendation]:
    """
    Enrich each high-priority recommendation with web-searched guidance.
    Medium/low recommendations are passed through unchanged.
    All high-priority calls run concurrently.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set — skipping recommendation research")
        return [_pass_through(r) for r in recommendations]

    client = anthropic.AsyncAnthropic(api_key=api_key)

    tasks = [
        _research_one(rec, context, client) if rec.get("priority") == "high"
        else _pass_through_async(rec)
        for rec in recommendations
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    enriched: list[EnrichedRecommendation] = []
    for rec, result in zip(recommendations, results):
        if isinstance(result, Exception):
            logger.warning("Research failed for '%s': %s", rec.get("title"), result)
            enriched.append(_pass_through(rec))
        else:
            enriched.append(result)
    return enriched


async def _research_one(
    rec: dict,
    context: dict,
    client: anthropic.AsyncAnthropic,
) -> EnrichedRecommendation:
    """Single Claude + web_search call for one recommendation."""
    prompt = _build_prompt(rec, context)

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=2048,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract the final text block (after all tool calls resolve)
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text = block.text

        parsed = _parse_response(final_text)
        logger.info("Researched '%s': %d links found", rec.get("title"), len(parsed.get("links", [])))

        return EnrichedRecommendation(
            priority=rec["priority"],
            title=rec["title"],
            detail=rec["detail"],
            links=parsed.get("links", []),
            guidance=parsed.get("guidance", ""),
            timeline=parsed.get("timeline"),
            researched=True,
        )

    except Exception as e:
        logger.warning("Research call failed for '%s': %s", rec.get("title"), e)
        return _pass_through(rec)


def _build_prompt(rec: dict, context: dict) -> str:
    lpa = context.get("developer", {}).get("lpa") or "the relevant Local Planning Authority"
    location = context.get("location_hint") or "England"
    notes = context.get("notes") or ""

    return f"""You are a UK planning advisor helping a developer navigate Biodiversity Net Gain requirements.

RECOMMENDATION TO RESEARCH:
Title: {rec['title']}
Detail: {rec['detail']}

PROJECT CONTEXT:
- Development type: Access road
- Location: {location}
- Local Planning Authority: {lpa}
- Additional notes: {notes}

Use web search to find:
1. The specific official UK government form, service page, or application process for this requirement (prefer gov.uk links)
2. The most current guidance (2023–2025) from Natural England, the Environment Agency, or relevant authority
3. Any practical timeline information (statutory response periods, deadlines)

Respond ONLY with a JSON object — no markdown, no preamble:
{{
  "links": [
    {{"title": "...", "url": "https://...", "description": "One sentence on what this link provides"}}
  ],
  "guidance": "2–3 sentences of practical, specific advice for this exact situation. Be concrete about next steps.",
  "timeline": "e.g. Allow 28 statutory days for Natural England response, or null if not applicable"
}}

Include 1–3 links maximum. Only include URLs you have confirmed exist via search."""


def _parse_response(text: str) -> dict:
    """Extract JSON from Claude's final response text."""
    text = text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find a JSON object within the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return {"links": [], "guidance": text[:500] if text else "", "timeline": None}


async def _pass_through_async(rec: dict) -> EnrichedRecommendation:
    return _pass_through(rec)


def _pass_through(rec: dict) -> EnrichedRecommendation:
    """Return a recommendation unchanged, marked as not researched."""
    return EnrichedRecommendation(
        priority=rec["priority"],
        title=rec["title"],
        detail=rec["detail"],
        links=[],
        guidance="",
        timeline=None,
        researched=False,
    )
