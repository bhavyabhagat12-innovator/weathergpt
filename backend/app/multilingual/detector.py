"""
Language and script detection engine for Indian multilingual queries.
Detects Hindi, Marathi, Tamil, Telugu, and English from both native script and transliteration.
"""

import re
from typing import Tuple

# Unicode Ranges
UNICODE_TAMIL = (0x0B80, 0x0BFF)
UNICODE_TELUGU = (0x0C00, 0x0C7F)
UNICODE_DEVANAGARI = (0x0900, 0x097F)

# Transliteration markers
TRANSLIT_MARKERS = {
    "hi": ["barish", "tapman", "kisan", "hawa", "aaj", "kal", "fasal", "pani", "mosam", "mausam", "kheti"],
    "mr": ["paus", "hava", "tamapan", "sheti", "kadhi", "udya", "sheti", "pik", "kanda"],
    "ta": ["mazhai", "kaatru", "veppanilai", "vivasayi", "indru", "naalai", "puyal"],
    "te": ["varsham", "gaali", "tufan", "raithu", "eeroju", "repu", "methe"]
}

MARATHI_SPECIFIC_CHARS = {"ळ", "ऱ", "ज्ञ"}
MARATHI_SPECIFIC_WORDS = ["आहे", "होईल", "का", "नाही", "शेतकरी", "कांदा", "पाऊस", "हवामान", "पीक", "उद्या"]
HINDI_SPECIFIC_WORDS = ["है", "होगी", "क्या", "नहीं", "किसान", "प्याज", "बारिश", "मौसम", "फसल", "आज"]


class LanguageDetector:
    """Detects Indian languages from input text."""

    @classmethod
    def detect_language(cls, text: str) -> str:
        """
        Returns ISO language code: 'hi', 'mr', 'ta', 'te', or 'en'.
        """
        if not text or not text.strip():
            return "en"

        clean = text.strip()

        # 1. Script checks
        has_tamil = any(UNICODE_TAMIL[0] <= ord(c) <= UNICODE_TAMIL[1] for c in clean)
        if has_tamil:
            return "ta"

        has_telugu = any(UNICODE_TELUGU[0] <= ord(c) <= UNICODE_TELUGU[1] for c in clean)
        if has_telugu:
            return "te"

        has_devanagari = any(UNICODE_DEVANAGARI[0] <= ord(c) <= UNICODE_DEVANAGARI[1] for c in clean)
        if has_devanagari:
            # Distinguish Marathi vs Hindi
            # Check Marathi specific words/characters
            if any(c in clean for c in MARATHI_SPECIFIC_CHARS):
                return "mr"
            for w in MARATHI_SPECIFIC_WORDS:
                if re.search(rf"\b{w}\b", clean):
                    return "mr"
            for w in HINDI_SPECIFIC_WORDS:
                if re.search(rf"\b{w}\b", clean):
                    return "hi"
            return "hi" # Default Devanagari to Hindi

        # 2. Transliteration / Romanized checks
        lower_clean = clean.lower()
        for lang, markers in TRANSLIT_MARKERS.items():
            if any(re.search(rf"\b{m}\b", lower_clean) for m in markers):
                return lang

        return "en"
