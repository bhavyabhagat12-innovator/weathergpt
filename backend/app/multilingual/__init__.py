"""
Multilingual package exports.
"""

from app.multilingual.detector import LanguageDetector
from app.multilingual.lexicon import LEXICON, LANGUAGE_NAMES
from app.multilingual.translator import MultilingualTranslator

__all__ = ["LanguageDetector", "LEXICON", "LANGUAGE_NAMES", "MultilingualTranslator"]
