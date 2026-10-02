"""
Google Gemini LLM Provider for WeatherGPT.
Connects to Gemini API via async HTTP with prompt grounding, falling back to local engine if unconfigured.
"""

import json
import logging
from typing import Optional
import httpx

from app.config import settings
from app.schemas.common import DomainRole
from app.schemas.unified import UnifiedWeatherReport
from app.llm.base import BaseLLMProvider, QueryIntent
from app.llm.prompts import build_grounded_prompt
from app.llm.query_parser import RuleBasedQueryParser
from app.llm.providers.fallback import FallbackAdvisoryProvider

logger = logging.getLogger("weathergpt.gemini")


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini model provider with graceful offline fallback."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(provider_name="Google-Gemini")
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.fallback = FallbackAdvisoryProvider()
        self.model = "gemini-1.5-flash"

    async def parse_intent(self, user_query: str, default_role: Optional[DomainRole] = None) -> QueryIntent:
        # Fast local parser handles 99% of intent structures instantly
        return RuleBasedQueryParser.parse(user_query, default_role=default_role)

    async def generate_advisory(
        self,
        report: UnifiedWeatherReport,
        user_query: str,
        role: DomainRole,
        language: str = "en"
    ) -> str:
        if not self.api_key:
            logger.info("Gemini API key not configured. Using grounded local rules engine.")
            return await self.fallback.generate_advisory(report, user_query, role, language)

        prompt = build_grounded_prompt(
            role=role,
            query=user_query,
            grounded_facts=report.grounded_facts,
            active_alerts=[a.model_dump() for a in report.alerts]
        )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2, # Low temperature prevents number hallucinations
                    "maxOutputTokens": 800,
                }
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {})
                        parts = content.get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                
                logger.warning(f"Gemini API returned status {res.status_code}. Using grounded fallback.")
                return await self.fallback.generate_advisory(report, user_query, role, language)

        except Exception as e:
            logger.error(f"Gemini generation exception ({e}). Falling back to local rules engine.")
            return await self.fallback.generate_advisory(report, user_query, role, language)
