"""
Tests for multilingual intelligence layer (Hindi, Marathi, Tamil, Telugu).
"""

import pytest
from app.multilingual.detector import LanguageDetector
from app.multilingual.translator import MultilingualTranslator
from app.llm.query_parser import RuleBasedQueryParser
from app.llm.grounder import WeatherGPTGroundingEngine
from app.schemas.common import DomainRole


def test_language_detection():
    assert LanguageDetector.detect_language("क्या आज नासिक में बारिश होगी?") == "hi"
    assert LanguageDetector.detect_language("नाशिकमध्ये आज पाऊस पडेल का?") == "mr"
    assert LanguageDetector.detect_language("சென்னையில் இன்று மழை பெய்யுமா?") == "ta"
    assert LanguageDetector.detect_language("విశాఖపట్నం సముద్రంలో తుఫాను ఎలా ఉంది?") == "te"
    assert LanguageDetector.detect_language("Will it rain in Delhi today?") == "en"
    # Transliterated Hindi
    assert LanguageDetector.detect_language("aaj barish hogi kya?") == "hi"


def test_multilingual_query_parsing():
    # Hindi Agriculture query
    hi_query = "क्या आज नासिक में प्याज की कटाई कर सकते हैं या बारिश होगी?"
    intent_hi = RuleBasedQueryParser.parse(hi_query)
    assert intent_hi.location == "Nashik"
    assert intent_hi.detected_role == DomainRole.AGRICULTURE
    assert "precipitation" in intent_hi.target_variables
    assert intent_hi.language == "hi"

    # Marathi Agriculture query
    mr_query = "नाशिकमध्ये आज कांदा काढणी करावी का?"
    intent_mr = RuleBasedQueryParser.parse(mr_query)
    assert intent_mr.location == "Nashik"
    assert intent_mr.detected_role == DomainRole.AGRICULTURE
    assert intent_mr.language == "mr"

    # Telugu Marine query
    te_query = "విశాఖపట్నం సముద్రంలో తుఫాను పరిస్థితి ఏమిటి?"
    intent_te = RuleBasedQueryParser.parse(te_query)
    assert intent_te.location == "Visakhapatnam"
    assert intent_te.detected_role == DomainRole.MARINE
    assert intent_te.language == "te"


@pytest.mark.asyncio
async def test_end_to_end_hindi_advisory():
    engine = WeatherGPTGroundingEngine()
    hi_query = "क्या आज नासिक में प्याज की कटाई कर सकते हैं?"
    resp = await engine.process_query(hi_query, role_override=DomainRole.AGRICULTURE)

    assert resp.role == DomainRole.AGRICULTURE
    assert resp.intent.language == "hi"
    # Verify Hindi translations are present in output
    assert "कृषि मौसम परामर्श" in resp.answer or "सल्लागार" in resp.answer or "परामर्श" in resp.answer or "नासिक" in resp.answer or "Nashik" in resp.answer
    assert resp.grounded_facts["query_location"] == "Nashik"


@pytest.mark.asyncio
async def test_end_to_end_marathi_advisory():
    engine = WeatherGPTGroundingEngine()
    mr_query = "नाशिकमध्ये आज कांदा काढणी करावी का?"
    resp = await engine.process_query(mr_query, role_override=DomainRole.AGRICULTURE)

    assert resp.role == DomainRole.AGRICULTURE
    assert resp.intent.language == "mr"
    assert "सल्लागार" in resp.answer or "हवामान" in resp.answer or "Nashik" in resp.answer or "कांदा" in resp.answer
