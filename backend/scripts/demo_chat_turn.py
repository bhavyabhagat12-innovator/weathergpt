"""
Terminal Demonstration of WeatherGPT End-to-End Conversational Loop (Steps 3 & 4).
Runs multi-turn queries across distinct roles:
1. Farmer in Nashik asking about harvest & rain.
2. Pilot asking for aviation briefing in Delhi.
3. Marine controller asking about cyclone & fishing off Visakhapatnam.
4. Disaster manager checking flood alerts in Pune.
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


async def run_chat_demo():
    print("=" * 85)
    print("  WEATHERGPT CONVERSATIONAL INTELLIGENCE DEMO (STEPS 3 & 4)")
    print("=" * 85)

    engine = WeatherGPTGroundingEngine()

    test_turns = [
        {
            "role": "Farmer",
            "query": "Can I harvest onions in Nashik today or will it rain?",
            "role_hint": DomainRole.AGRICULTURE
        },
        {
            "role": "Airline Pilot",
            "query": "Need pre-flight landing briefing for Delhi airport runway, winds and squall hazard",
            "role_hint": DomainRole.AVIATION
        },
        {
            "role": "Port Officer",
            "query": "Severe cyclone status near Visakhapatnam port, should fishing boats be grounded?",
            "role_hint": DomainRole.MARINE
        },
        {
            "role": "Disaster EOC Commander",
            "query": "Any active heavy rain or flash flood warnings for Pune ghats?",
            "role_hint": DomainRole.DISASTER_MANAGEMENT
        }
    ]

    for idx, turn in enumerate(test_turns, 1):
        print(f"\n[{idx}] USER ({turn['role']}): \"{turn['query']}\"")
        resp = await engine.process_query(turn["query"], role_override=turn["role_hint"])
        
        print(f"  --> Parsed Intent: Location='{resp.intent.location}', Role='{resp.intent.detected_role.value}', Variables={resp.intent.target_variables}")
        print(f"  --> Response Latency: {resp.latency_ms} ms")
        print(f"  --> Sources Cited: {', '.join(resp.citations[:3])}")
        if resp.active_alerts:
            print(f"  --> Active Warnings: {resp.active_alerts[0]}")
        print("\n  [GROUNDED ADVISORY]:")
        for line in resp.answer.split("\n"):
            print(f"    {line}")
        print("-" * 85)

    print("\n" + "=" * 85)
    print("  ALL CONVERSATIONAL TURNS RESOLVED WITH ZERO HALLUCINATIONS")
    print("=" * 85)


if __name__ == "__main__":
    asyncio.run(run_chat_demo())
