"""
Abstract Base Class and data models for LLM Providers in WeatherGPT.
Ensures vendor-agnostic architecture (Gemini, OpenAI, Ollama, and local rule-based engine).
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field

from app.schemas.common import DomainRole
from app.schemas.unified import UnifiedWeatherReport


class QueryIntent(BaseModel):
    """Structured interpretation of user's free-text weather query."""
    raw_query: str
    location: str
    target_variables: List[str] = Field(
        default_factory=list,
        description="e.g. ['precipitation', 'temperature', 'wind', 'soil_moisture', 'cyclone']"
    )
    time_horizon: str = Field(
        default="current",
        description="'current', 'today', 'tomorrow', 'weekly', 'historical'"
    )
    detected_role: DomainRole = DomainRole.GENERAL
    language: str = "en"
    confidence: float = 0.95


class GroundedResponse(BaseModel):
    """Conversational output strictly bound to verified measurements."""
    answer: str
    intent: QueryIntent
    role: DomainRole
    report_id: str
    grounded_facts: Dict[str, Any]
    citations: List[str]
    active_alerts: List[str] = Field(default_factory=list)
    chart_spec: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0



class BaseLLMProvider(ABC):
    """Abstract interface for pluggable LLM backends."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    async def parse_intent(self, user_query: str, default_role: Optional[DomainRole] = None) -> QueryIntent:
        """Parses free-text user query into a structured QueryIntent."""
        pass

    @abstractmethod
    async def generate_advisory(
        self,
        report: UnifiedWeatherReport,
        user_query: str,
        role: DomainRole,
        language: str = "en"
    ) -> str:
        """Generates grounded natural-language advisory using verified telemetry."""
        pass
