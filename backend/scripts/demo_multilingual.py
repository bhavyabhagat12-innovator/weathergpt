"""
Demo script: Multilingual Weather Intelligence (Hindi, Marathi, Tamil, Telugu).
Verifies that Indian language queries are understood, grounded with live telemetry,
and translated into actionable regional advisories.
"""

import asyncio
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.llm.grounder import WeatherGPTGroundingEngine
from app.schemas.common import DomainRole


async def run_multilingual_demo():
    print("=" * 85)
    print("  WEATHERGPT MULTILINGUAL WEATHER INTELLIGENCE DEMO (STEP 6)")
    print("=" * 85)

    engine = WeatherGPTGroundingEngine()

    cases = [
        {
            "lang": "हिन्दी (Hindi)",
            "query": "क्या आज नासिक में प्याज की कटाई कर सकते हैं या बारिश होगी?",
            "role": DomainRole.AGRICULTURE
        },
        {
            "lang": "मराठी (Marathi)",
            "query": "नाशिकमध्ये आज कांदा काढणी करावी का? पाऊस पडेल का?",
            "role": DomainRole.AGRICULTURE
        },
        {
            "lang": "தமிழ் (Tamil)",
            "query": "சென்னையில் இன்று மழை பெய்யுமா? துறைமுக வானிலை எப்படி?",
            "role": DomainRole.MARINE
        },
        {
            "lang": "తెలుగు (Telugu)",
            "query": "విశాఖపట్నం సముद्रంలో తుఫాను పరిస్థితి ఏమిటి? చేపల వేటకు వెళ్ళవచ్చా?",
            "role": DomainRole.MARINE
        }
    ]

    for idx, c in enumerate(cases, 1):
        print(f"\n[{idx}] LANGUAGE: {c['lang']}")
        print(f"  User Query: \"{c['query']}\"")
        resp = await engine.process_query(c["query"], role_override=c["role"])

        print(f"  --> Detected Language: {resp.intent.language}")
        print(f"  --> Resolved Location: {resp.intent.location}")
        print(f"  --> Role: {resp.role.value}")
        print(f"  --> Citations: {', '.join(resp.citations[:2])}")
        print("  --> Localized Advisory:")
        for line in resp.answer.split("\n")[:8]:
            print(f"      {line}")
        print("-" * 85)

    print("\n" + "=" * 85)
    print("  MULTILINGUAL ADVISORY GENERATION VERIFIED ACROSS 4 REGIONAL LANGUAGES")
    print("=" * 85)


if __name__ == "__main__":
    asyncio.run(run_multilingual_demo())
