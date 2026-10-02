"""
Tests for query intent parser and entity extraction across Indian domains.
"""

import pytest
from app.schemas.common import DomainRole
from app.llm.query_parser import RuleBasedQueryParser


def test_parse_agriculture_intent_nashik():
    query = "Can I harvest onions in Nashik today or will it rain?"
    intent = RuleBasedQueryParser.parse(query)

    assert intent.location.lower() == "nashik"
    assert intent.detected_role == DomainRole.AGRICULTURE
    assert "precipitation" in intent.target_variables
    assert intent.time_horizon == "today"


def test_parse_marine_intent_visakhapatnam():
    query = "Is there a severe cyclone warning near Visakhapatnam port for fishing boats?"
    intent = RuleBasedQueryParser.parse(query)

    assert intent.location.lower() == "visakhapatnam"
    assert intent.detected_role == DomainRole.MARINE
    assert "cyclone" in intent.target_variables


def test_parse_aviation_intent_delhi():
    query = "Flight landing runway wind gusts and visibility briefing for Delhi airport"
    intent = RuleBasedQueryParser.parse(query)

    assert intent.location.lower() in ["delhi", "new delhi"]
    assert intent.detected_role == DomainRole.AVIATION
    assert "wind" in intent.target_variables


def test_parse_disaster_intent_konkan():
    query = "Disaster emergency evacuation and heavy rainfall red alert near Pune"
    intent = RuleBasedQueryParser.parse(query)

    assert intent.location.lower() == "pune"
    assert intent.detected_role == DomainRole.DISASTER_MANAGEMENT
    assert "precipitation" in intent.target_variables


def test_parse_historical_trend_intent():
    query = "How has monsoon onset rainfall trend shifted in Nashik over the past 10 years?"
    intent = RuleBasedQueryParser.parse(query)

    assert intent.location.lower() == "nashik"
    assert intent.time_horizon == "historical"
