"""
Chat API routes for WeatherGPT.
Provides conversational message processing, session tracking, and streaming responses.
"""

from typing import Optional, List, Dict
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.schemas.common import DomainRole
from app.llm.base import GroundedResponse
from app.llm.grounder import WeatherGPTGroundingEngine

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])
grounder = WeatherGPTGroundingEngine()

# Lightweight in-memory session history store
SESSION_HISTORIES: Dict[str, List[Dict[str, str]]] = {}


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's weather query in natural language")
    session_id: Optional[str] = Field(default="default-session", description="Conversation session ID")
    role: Optional[DomainRole] = Field(default=None, description="Optional role override (e.g. agriculture, aviation)")
    language: str = Field(default="en", description="Language code (en, hi, mr, ta, te)")


@router.post("/message", response_model=GroundedResponse)
async def send_chat_message(request: ChatMessageRequest):
    """
    Primary conversational endpoint.
    Parses intent -> Ingests verified weather data -> Generates role-grounded response.
    """
    try:
        response = await grounder.process_query(
            query=request.message,
            role_override=request.role,
            language=request.language
        )

        # Update session history
        if request.session_id not in SESSION_HISTORIES:
            SESSION_HISTORIES[request.session_id] = []
        SESSION_HISTORIES[request.session_id].append({"role": "user", "content": request.message})
        SESSION_HISTORIES[request.session_id].append({"role": "assistant", "content": response.answer})

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversational reasoning failed: {str(e)}")


@router.post("/stream")
async def stream_chat_message(request: ChatMessageRequest):
    """
    Streaming endpoint returning Server-Sent Events (SSE) for low-bandwidth / mobile responsiveness.
    """
    try:
        response = await grounder.process_query(
            query=request.message,
            role_override=request.role,
            language=request.language
        )

        async def event_generator():
            # First send metadata event (intent, facts, citations)
            metadata_event = {
                "type": "metadata",
                "intent": response.intent.model_dump(),
                "role": response.role.value,
                "citations": response.citations,
                "grounded_facts": response.grounded_facts,
                "active_alerts": response.active_alerts,
                "report_id": response.report_id
            }
            yield f"data: {json.dumps(metadata_event)}\n\n"

            # Stream words with slight typing delay for responsive UX
            words = response.answer.split(" ")
            for w in words:
                chunk = {"type": "token", "content": w + " "}
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.015)

            # Completion event
            done_event = {"type": "done", "latency_ms": response.latency_ms}
            yield f"data: {json.dumps(done_event)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")


@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Returns conversation history for the session."""
    return {"session_id": session_id, "messages": SESSION_HISTORIES.get(session_id, [])}
