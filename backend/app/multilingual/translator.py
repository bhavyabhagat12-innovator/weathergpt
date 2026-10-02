"""
Multilingual Translation Engine for WeatherGPT.
Supports Hindi, Marathi, Tamil, Telugu, and English.
Uses LLM contextual translation when online, and local dictionary rules engine when offline.
"""

import logging
from typing import Optional
import httpx

from app.config import settings
from app.schemas.common import DomainRole
from app.schemas.unified import UnifiedWeatherReport
from app.multilingual.lexicon import LEXICON, LANGUAGE_NAMES

logger = logging.getLogger("weathergpt.multilingual.translator")


class MultilingualTranslator:
    """Translates weather queries and advisories into Indian languages."""

    @classmethod
    async def translate_advisory(
        cls,
        text: str,
        target_lang: str,
        role: DomainRole = DomainRole.GENERAL,
        report: Optional[UnifiedWeatherReport] = None
    ) -> str:
        """
        Translates an advisory into target language (hi, mr, ta, te).
        Preserves numbers, locations, and safety directives.
        """
        if target_lang == "en" or not target_lang:
            return text

        # 1. If Gemini API key is configured, use contextual LLM translation
        if settings.GEMINI_API_KEY:
            try:
                translated = await cls._translate_via_gemini(text, target_lang)
                if translated:
                    return translated
            except Exception as e:
                logger.warning(f"LLM translation failed ({e}). Falling back to local lexicon translator.")

        # 2. Local Lexicon & Template Translation Fallback
        return cls._translate_via_lexicon(text, target_lang, role, report)

    @classmethod
    async def _translate_via_gemini(cls, text: str, target_lang: str) -> Optional[str]:
        target_name = LANGUAGE_NAMES.get(target_lang, target_lang)
        prompt = (
            f"Translate the following Indian weather advisory accurately into {target_name}. "
            f"PRESERVE all numbers, units (°C, km/h, mm, m³/m³), and proper nouns (e.g. city names). "
            f"Do not add any extra commentary.\n\n"
            f"TEXT TO TRANSLATE:\n{text}"
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800}
        }

        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        return None

    @classmethod
    def _translate_via_lexicon(
        cls,
        text: str,
        target_lang: str,
        role: DomainRole,
        report: Optional[UnifiedWeatherReport] = None
    ) -> str:
        """Translates terms and structures using the pre-compiled Indian meteorological lexicon."""
        if target_lang not in ["hi", "mr", "ta", "te"]:
            return text

        translated = text

        # Replace role headers
        role_key_map = {
            DomainRole.AGRICULTURE: "agro_advisory_title",
            DomainRole.AVIATION: "aviation_advisory_title",
            DomainRole.MARINE: "marine_advisory_title",
            DomainRole.DISASTER_MANAGEMENT: "disaster_advisory_title",
            DomainRole.GENERAL: "general_advisory_title",
        }
        title_key = role_key_map.get(role, "general_advisory_title")
        en_title = LEXICON[title_key]["en"]
        tgt_title = LEXICON[title_key].get(target_lang, en_title)
        translated = translated.replace(en_title, tgt_title)

        # Replace labels
        replacements = [
            ("Current Status", LEXICON["current_status"].get(target_lang, "Current Status")),
            ("Humidity", LEXICON["humidity"].get(target_lang, "Humidity")),
            ("Condition", LEXICON["condition"].get(target_lang, "Condition")),
            ("Wind Speed", LEXICON["wind"].get(target_lang, "Wind Speed")),
            ("Mandatory Directive", LEXICON["mandatory_directive"].get(target_lang, "Mandatory Directive")),
            ("Postpone harvesting and sensitive field operations", LEXICON["harvest_postpone"].get(target_lang, "Postpone harvesting")),
            ("DO NOT SPRAY pesticides/fertilizers", LEXICON["spray_avoid"].get(target_lang, "DO NOT SPRAY")),
            ("All fishing vessels must immediately return to port", LEXICON["fishermen_warning"].get(target_lang, "Fishermen return to port")),
        ]

        for en_word, tgt_word in replacements:
            translated = translated.replace(en_word, tgt_word)

        return translated
