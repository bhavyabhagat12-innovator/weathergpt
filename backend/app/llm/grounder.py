"""
Conversational Grounding Engine for WeatherGPT.
Connects query understanding, data ingestion, strict RAG grounding, and citation generation.
"""

import time
import logging
from typing import Optional

from app.schemas.common import DomainRole
from app.data_ingestion.service import WeatherIntelligenceDataService
from app.llm.base import QueryIntent, GroundedResponse
from app.llm.factory import get_llm_provider
from app.multilingual.translator import MultilingualTranslator
from app.climate.analyzer import ClimateAnalyzer

logger = logging.getLogger("weathergpt.grounder")


class WeatherGPTGroundingEngine:
    """End-to-end conversational weather reasoning engine."""

    def __init__(self):
        self.data_service = WeatherIntelligenceDataService()
        self.llm = get_llm_provider()
        self.climate_analyzer = ClimateAnalyzer()

    async def process_query(
        self,
        query: str,
        role_override: Optional[DomainRole] = None,
        language: str = "en"
    ) -> GroundedResponse:
        start_time = time.perf_counter()

        # 1. Parse free-text user query into structured intent (detects location, role, language)
        intent = await self.llm.parse_intent(query, default_role=role_override)
        active_role = role_override or intent.detected_role
        target_lang = language if language != "en" else intent.language

        # 2. Fetch ground-truth telemetry via Data Ingestion Layer
        is_historical = (intent.time_horizon == "historical")
        report = await self.data_service.get_unified_report(
            query=intent.location,
            role=active_role,
            include_climate=is_historical
        )

        # 3. Generate grounded advisory via LLM / Rules Engine
        advisory_text = await self.llm.generate_advisory(
            report=report,
            user_query=query,
            role=active_role,
            language=target_lang
        )

        # 4. Localize advisory if non-English target language requested
        if target_lang != "en":
            advisory_text = await MultilingualTranslator.translate_advisory(
                advisory_text,
                target_lang=target_lang,
                role=active_role,
                report=report
            )

        # 5. Generate historical chart specification if requested
        chart_spec = None
        if is_historical:
            try:
                chart = await self.climate_analyzer.generate_monsoon_trend_chart(intent.location, years=7)
                chart_spec = chart.model_dump(mode="json")
            except Exception as e:
                logger.warning(f"Failed to generate historical chart spec: {e}")

        latency = (time.perf_counter() - start_time) * 1000

        # 6. Format active alert headlines
        alert_headlines = [f"[{a.severity.value.upper()}] {a.headline}" for a in report.alerts]

        return GroundedResponse(
            answer=advisory_text,
            intent=intent,
            role=active_role,
            report_id=report.report_id,
            grounded_facts=report.grounded_facts,
            citations=report.citations,
            active_alerts=alert_headlines,
            chart_spec=chart_spec,
            latency_ms=round(latency, 2)
        )

