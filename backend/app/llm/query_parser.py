"""
Intent parsing engine for WeatherGPT.
Extracts location, role, weather variables, and time horizons from natural language queries.
"""

import re
from typing import Optional, List
from app.schemas.common import DomainRole
from app.llm.base import QueryIntent
from app.multilingual.detector import LanguageDetector

# Role trigger keywords (multilingual: English, Hindi, Marathi, Tamil, Telugu)
ROLE_KEYWORDS = {
    DomainRole.AGRICULTURE: [
        "farmer", "crop", "sowing", "harvest", "irrigation", "soil", "pesticide",
        "fertilizer", "field", "farm", "onion", "wheat", "cotton", "rice", "paddy", "grape",
        "किसान", "खेती", "फसल", "कटाई", "बुवाई", "प्याज", "खाद", "सिंचाई",
        "शेतकरी", "शेती", "पीक", "कांदा", "पेरणी", "फवारणी",
        "விவசாயி", "பயிர்", "அறுவடை", "விதைப்பு", "உரம்",
        "రైతు", "పంట", "కోత", "విత్తనం", "ఎరువు"
    ],
    DomainRole.AVIATION: [
        "flight", "pilot", "aircraft", "landing", "takeoff", "runway", "airport",
        "visibility", "ifr", "vfr", "ceiling", "turbulence", "crosswind", "shear",
        "विमान", "पायलट", "रनवे", "हवाई अड्डा", "उड़ान"
    ],
    DomainRole.MARINE: [
        "ship", "boat", "fisherman", "fishing", "marine", "sea", "ocean", "port",
        "coastal", "harbour", "harbor", "swell", "wave", "tide", "cyclone", "depression",
        "मछुआरे", "नाव", "समुद्र", "बंदरगाह", "चक्रवात", "तूफान",
        "मच्छीमार", "बंदर", "लाटा", "चक्रीवादळ",
        "மீனவர்", "கடல்", "துறைமுகம்", "புயல்",
        "మత్స్యకారులు", "సముద్రం", "నౌకాశ్రయం", "తుఫాను"
    ],
    DomainRole.DISASTER_MANAGEMENT: [
        "disaster", "evacuate", "evacuation", "flood", "warning", "red alert",
        "orange alert", "ndrf", "sdrf", "emergency", "shelter", "rescue", "hazard",
        "आपदा", "बाढ़", "चेतावनी", "रेड अलर्ट", "राहत",
        "आपत्ती", "पूर", "इशारा",
        "பேரிடர்", "வெள்ளம்", "எச்சரிக்கை",
        "విపత్తు", "వరద", "హెచ్చరిక"
    ],
    DomainRole.URBAN_PLANNING: [
        "traffic", "waterlogging", "drainage", "commute", "urban", "heat island", "metro"
    ]
}

# Weather variables keywords
VARIABLE_KEYWORDS = {
    "precipitation": [
        "rain", "raining", "rainfall", "drizzle", "shower", "downpour", "precipitation",
        "बारिश", "वर्षा", "पानी", "बूंदाबांदी", "पाऊस", "மழை", "மழைப்பொழிவு", "వర్షం", "వాన"
    ],
    "temperature": [
        "temp", "temperature", "hot", "cold", "heat", "heatwave", "warm", "chill",
        "तापमान", "गर्मी", "लू", "थंड", "வெப்பநிலை", "சூடு", "ఉష్ణోగ్రత", "ఎండ"
    ],
    "wind": [
        "wind", "gust", "breeze", "gale", "squall", "speed",
        "हवा", "आंधी", "वारा", "वादळ", "காற்று", "சூறாவளி", "గాలి"
    ],
    "soil_moisture": [
        "soil", "moisture", "ground water", "मृदा", "ओलावा", "ஈரப்பதம்", "తేమ"
    ],
    "cyclone": [
        "cyclone", "storm", "typhoon", "depression", "gale",
        "चक्रवात", "तूफान", "चक्रीवादळ", "புயல்", "తుఫాను"
    ],
    "humidity": ["humidity", "muggy", "moist", "relative humidity", "उमस", "आर्द्रता"],
    "uv": ["uv", "sun", "sunlight", "radiation"],
}

# Time horizons
TIME_KEYWORDS = {
    "historical": ["past", "history", "historical", "trend", "decade", "last year", "10 years", "monsoon onset", "इतिहास", "दशक"],
    "tomorrow": ["tomorrow", "next day", "kal", "कल", "उद्या", "நாளை", "రేపు"],
    "weekly": ["week", "7 days", "next few days", "forecast", "weekend", "सप्ताह", "आठवडा", "வாரம்"],
    "today": ["today", "aaj", "tonight", "afternoon", "evening", "morning", "आज", "இன்று", "ఈరోజు"],
    "current": ["now", "currently", "live", "right now", "present", "अभी", "आत्ता", "தற்போது", "ఇప్పుడు"]
}

# Multilingual Location Dictionary
INDIAN_CITIES_MAP = {
    "nashik": "Nashik", "नासिक": "Nashik", "नाशिक": "Nashik",
    "visakhapatnam": "Visakhapatnam", "vizag": "Visakhapatnam", "विशाखापट्टनम": "Visakhapatnam", "విశాఖపట్నం": "Visakhapatnam", "விசாகப்பட்டினம்": "Visakhapatnam",
    "nagpur": "Nagpur", "नागपुर": "Nagpur", "नागपूर": "Nagpur",
    "chennai": "Chennai", "चेन्नई": "Chennai", "சென்னை": "Chennai",
    "mumbai": "Mumbai", "मुंबई": "Mumbai", "மும்பை": "Mumbai",
    "delhi": "Delhi", "new delhi": "Delhi", "दिल्ली": "Delhi", "புது தில்லி": "Delhi", "ఢిల్లీ": "Delhi",
    "bengaluru": "Bengaluru", "bangalore": "Bengaluru", "बेंगलुरु": "Bengaluru", "பெங்களூரு": "Bengaluru", "బెంగళూరు": "Bengaluru",
    "hyderabad": "Hyderabad", "हैदराबाद": "Hyderabad", "హైదరాబాద్": "Hyderabad", "ஹைதராபாத்": "Hyderabad",
    "kolkata": "Kolkata", "कोलकाता": "Kolkata", "கொல்கத்தா": "Kolkata",
    "pune": "Pune", "पुणे": "Pune", "புனே": "Pune",
    "patna": "Patna", "पटना": "Patna",
    "kochi": "Kochi", "cochin": "Kochi", "कोच्चि": "Kochi",
    "shimla": "Shimla", "शिमला": "Shimla",
    "guwahati": "Guwahati", "गुवाहाटी": "Guwahati"
}


class RuleBasedQueryParser:
    """Robust multilingual query intent parser."""

    @classmethod
    def detect_location(cls, query: str) -> Optional[str]:
        """Return the city found in the query, or None if there isn't one."""
        clean = query.lower().strip()
        for city_key, resolved_city in INDIAN_CITIES_MAP.items():
            if city_key in clean:
                return resolved_city
        loc_match = re.search(
            r"\b(?:in|at|for|near|में|मध्ये|இல்|లో)\s+([a-zA-Z\u0900-\u0D7F\s]+?)(?:\s+(?:today|tomorrow|now|this|for|with|\?|$|आज|कल|उद्या))",
            query,
        )
        if loc_match:
            extracted = loc_match.group(1).strip()
            if len(extracted) > 2:
                return extracted.title()
        return None

    @classmethod
    def parse(cls, query: str, default_role: Optional[DomainRole] = None) -> QueryIntent:
        clean = query.lower().strip()
        detected_lang = LanguageDetector.detect_language(query)

        # 1. Detect location (supports English and Indian scripts)
        # Falls back to Nashik so the rest of the pipeline keeps working.
        # The chat endpoint should call detect_location() first and ask the
        # user for a city when it returns None.
        location = cls.detect_location(query) or "Nashik"

        # 2. Detect target variables
        detected_vars = []
        for var_name, triggers in VARIABLE_KEYWORDS.items():
            if any(t.lower() in clean for t in triggers):
                detected_vars.append(var_name)
        if not detected_vars:
            detected_vars = ["general_weather"]

        # 3. Detect time horizon
        time_horizon = "current"
        for th, triggers in TIME_KEYWORDS.items():
            if any(t.lower() in clean for t in triggers):
                time_horizon = th
                break

        # 4. Detect role
        role = default_role or DomainRole.GENERAL
        if default_role in (None, DomainRole.GENERAL):
            for r, triggers in ROLE_KEYWORDS.items():
                if any(t.lower() in clean for t in triggers):
                    role = r
                    break

        return QueryIntent(
            raw_query=query,
            location=location,
            target_variables=detected_vars,
            time_horizon=time_horizon,
            detected_role=role,
            language=detected_lang,
            confidence=0.95
        )
