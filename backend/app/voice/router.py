"""
Voice API routes for transcription and speech synthesis.
"""

from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

from app.voice.service import VoiceService

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])


class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize into speech")
    language: str = Field(default="en", description="Target language (hi, mr, ta, te, en)")


@router.post("/synthesize")
async def synthesize_speech(req: SynthesisRequest):
    """
    Returns synthesis configuration and normalized audio stream instructions
    for client-side zero-bandwidth Web Speech API rendering.
    """
    try:
        return VoiceService.get_speech_synthesis_config(req.text, language=req.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis configuration failed: {str(e)}")


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language_hint: Optional[str] = Form("hi")
):
    """
    Transcribes uploaded user voice recording (WAV, MP3, WebM) into text query.
    """
    try:
        content = await file.read()
        return await VoiceService.transcribe_audio(content, file.filename or "audio.wav", language_hint=language_hint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
