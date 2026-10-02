"""
OpenAI & Ollama (Local Llama) LLM Provider for WeatherGPT.
Connects via standard OpenAI-compatible completions format.
"""

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

logger = logging.getLogger("weathergpt.openai_ollama")


class OpenAIOllamaProvider(BaseLLMProvider):
    """OpenAI and local Ollama provider."""

    def __init__(self, is_ollama: bool = False):
        name = "Ollama-Local-LLM" if is_ollama else "OpenAI-GPT"
        super().__init__(provider_name=name)
        self.is_ollama = is_ollama
        self.fallback = FallbackAdvisoryProvider()
        
        if is_ollama:
            self.base_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/v1"
            self.api_key = "ollama"
            self.model = "llama3:latest"
        else:
            self.base_url = "https://api.openai.com/v1"
            self.api_key = settings.OPENAI_API_KEY
            self.model = "gpt-4o-mini"

    async def parse_intent(self, user_query: str, default_role: Optional[DomainRole] = None) -> QueryIntent:
        return RuleBasedQueryParser.parse(user_query, default_role=default_role)

    async def generate_advisory(
        self,
        report: UnifiedWeatherReport,
        user_query: str,
        role: DomainRole,
        language: str = "en"
    ) -> str:
        if not self.is_ollama and not self.api_key:
            return await self.fallback.generate_advisory(report, user_query, role, language)

        prompt = build_grounded_prompt(
            role=role,
            query=user_query,
            grounded_facts=report.grounded_facts,
            active_alerts=[a.model_dump() for a in report.alerts]
        )

        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are WeatherGPT, an authoritative weather advisory assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }

            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0].get("message", {}).get("content", "")
                
                logger.warning(f"{self.provider_name} call failed with status {res.status_code}. Using fallback.")
                return await self.fallback.generate_advisory(report, user_query, role, language)

        except Exception as e:
            logger.error(f"{self.provider_name} exception ({e}). Using fallback.")
            return await self.fallback.generate_advisory(report, user_query, role, language)
