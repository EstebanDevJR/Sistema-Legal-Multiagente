"""
API REST para servicios de voz (Speech-to-Text y Text-to-Speech)
"""

import os
import time
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Request
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, Optional
import re

from ...services.voice.voice_service_simple import voice_service
from ...core.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Services"])

@router.post("/speech-to-text")
async def speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form("es")
) -> Dict[str, Any]:
    """
    Convertir audio a texto usando OpenAI Whisper
    
    - **audio_file**: Archivo de audio (WAV, MP3, M4A, etc.)
    - **language**: Idioma del audio (por defecto: español)
    """
    try:
        # Validar archivo
        if not audio_file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo de audio requerido"
            )
        
        # Validar tipo de archivo
        allowed_types = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg", "audio/flac"]
        if audio_file.content_type not in allowed_types:
            # También permitir por extensión
            allowed_extensions = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac"]
            if not any(audio_file.filename.lower().endswith(ext) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de archivo no soportado. Use: WAV, MP3, M4A, OGG, FLAC"
                )
        
        # Procesar audio
        result = await voice_service.speech_to_text(audio_file, language)
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en transcripción: {result['error']}"
            )
        
        return {
            "transcription": result,
            "ready_for_query": bool(result.get("text", "").strip()),
            "suggested_next_step": "Envía el texto a /rag/query para obtener respuesta legal"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in speech-to-text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el procesamiento de audio"
        )

@router.post("/text-to-speech")
async def text_to_speech(
    request: Request,
    text: str = Form(...),
    voice_style: str = Form("legal"),
    output_format: str = Form("mp3")
) -> Dict[str, Any]:
    """
    Convertir texto a audio usando ElevenLabs
    
    - **text**: Texto a sintetizar
    - **voice_style**: Estilo de voz (legal, formal, casual)
    - **output_format**: Formato de salida (mp3, wav)
    """
    try:
        # Validaciones
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Texto requerido para síntesis"
            )
        
        if len(text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Texto demasiado largo (máximo 5000 caracteres)"
            )
        
        if voice_style not in ["legal", "formal", "casual"]:
            voice_style = "legal"
        
        if output_format not in ["mp3", "wav"]:
            output_format = "mp3"
        
        # Generar audio
        result = await voice_service.text_to_speech(text, voice_style, output_format)
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en síntesis: {result['error']}"
            )
        
        # Generate dynamic URL based on request host
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        return {
            "audio_info": result,
            "download_url": f"{base_url}/voice/download/{result['audio_id']}",
            "message": "Audio generado exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in text-to-speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en la síntesis de voz"
        )

@router.post("/smart-text-to-speech")
async def smart_text_to_speech(
    request: Request,
    text: str = Form(...),
    auto_detect_style: bool = Form(True),
    output_format: str = Form("mp3")
) -> Dict[str, Any]:
    """
    Síntesis de voz inteligente con detección automática de estilo (Plan Creator)
    
    - **text**: Texto a sintetizar
    - **auto_detect_style**: Detectar automáticamente el mejor estilo de voz
    - **output_format**: Formato de salida (mp3, wav)
    
    Funcionalidades avanzadas:
    - Detección automática del contexto legal
    - Optimización de voz basada en contenido
    - Configuración adaptativa de parámetros
    - Máxima calidad de audio
    """
    try:
        # Validaciones
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Texto requerido para síntesis"
            )
        
        if len(text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Texto demasiado largo (máximo 5000 caracteres)"
            )
        
        if output_format not in ["mp3", "wav"]:
            output_format = "mp3"
        
        # Generar audio con IA inteligente
        result = await voice_service.smart_text_to_speech(
            text=text,
            auto_detect_style=auto_detect_style,
            output_format=output_format
        )
        
        if result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en síntesis inteligente: {result['error']}"
            )
        
        # Generate dynamic URL based on request host
        base_url = f"{request.url.scheme}://{request.url.netloc}"
        
        return {
            "audio_info": result,
            "download_url": f"{base_url}/voice/download/{result['audio_id']}",
            "message": "Audio generado con IA inteligente (Plan Creator)",
            "optimization_details": {
                "detected_style": result.get("detected_style"),
                "smart_features_used": result.get("creator_features_used", [])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in smart text-to-speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en la síntesis inteligente"
        )

import re

_AUDIO_ID_RE = re.compile(r"^[a-f0-9\-]{8,}$", re.IGNORECASE)

@router.options("/download/{audio_id}")
async def download_audio_options(audio_id: str):
    """Handle CORS preflight requests for audio download"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
    )

@router.get("/download/{audio_id}")
async def download_audio(audio_id: str):
    """
    Descargar archivo de audio generado
    """
    try:
        # Validar ID de audio para evitar path traversal
        if not _AUDIO_ID_RE.match(audio_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de audio inválido"
            )
        # Buscar archivo en directorio temporal
        temp_dir = voice_service.temp_dir
        
        # Buscar archivo con el ID
        for filename in os.listdir(temp_dir):
            if audio_id in filename:
                file_path = os.path.join(temp_dir, filename)
                
                # Determinar tipo de contenido
                if filename.endswith('.mp3'):
                    media_type = "audio/mpeg"
                elif filename.endswith('.wav'):
                    media_type = "audio/wav"
                else:
                    media_type = "audio/mpeg"
                
                return FileResponse(
                    path=file_path,
                    media_type=media_type,
                    filename=filename,
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "GET, OPTIONS",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization",
                        "Cache-Control": "public, max-age=3600"
                    }
                )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de audio no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al descargar audio"
        )

@router.post("/voice-query")
async def process_voice_query(
    request: Request,
    audio_file: UploadFile = File(...),
    voice_response_style: str = Form("legal"),
    language: str = Form("es"),
    response_mode: str = Form("text"),
    document_ids: str = Form("")
) -> Dict[str, Any]:
    """
    Procesar consulta legal completa por voz: Audio -> Texto -> Respuesta Legal -> Audio
    
    - **audio_file**: Archivo de audio con la consulta
    - **voice_response_style**: Estilo para la respuesta de voz
    - **language**: Idioma del audio
    """
    try:
        # Log información básica sin datos sensibles
        logger.info("🎤 Voice query received")
        logger.info(f"  - content_type: {audio_file.content_type}")
        logger.info(f"  - voice_response_style: {voice_response_style}")
        logger.info(f"  - language: {language}")
        
        # Read the audio file content to check if it's empty
        audio_content = await audio_file.read()
        logger.info(f"  - audio_content size: {len(audio_content)} bytes")
        
        if len(audio_content) == 0:
            logger.error("❌ Audio file is empty!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo de audio está vacío"
            )
        
        # 1. Convertir audio a texto - Pass the content directly instead of the file object
        logger.info("🔄 Starting speech-to-text conversion...")
        stt_result = await voice_service.speech_to_text(audio_content, language)
        
        logger.info("📝 STT result received")
        logger.info(f"  - text_length: {len(stt_result.get('text', ''))}")
        logger.info(f"  - has_error: {bool(stt_result.get('error'))}")
        logger.info(f"  - confidence: {stt_result.get('confidence', 'None')}")
        
        if stt_result.get("error") or not stt_result.get("text", "").strip():
            logger.error(f"❌ STT failed: {stt_result.get('error', 'No text returned')}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo transcribir el audio correctamente"
            )
        
        transcribed_text = stt_result["text"]
        
        # 2. Procesar consulta legal
        logger.info("⚖️ Processing legal query...")
        
        # Parse document IDs if provided
        document_ids_list = []
        if document_ids:
            try:
                document_ids_list = document_ids.split(",") if document_ids else []
                logger.info(f"📄 Document IDs provided: {document_ids_list}")
            except Exception as e:
                logger.warning(f"⚠️ Error parsing document IDs: {e}")
        
        legal_response = await rag_service.process_legal_query(
            question=transcribed_text,
            user_id="voice_user",
            document_ids=document_ids_list
        )
        
        # 3. Generar respuesta de audio solo si se solicita
        audio_url = None
        if response_mode == "audio":
            logger.info("🔊 Generating audio response...")
            tts_result = await voice_service.text_to_speech(
                text=legal_response["answer"],
                voice_style=voice_response_style,
                output_format="mp3"
            )
            logger.info(f"TTS result: {tts_result}")
            # Generate dynamic URL based on request host
            base_url = f"{request.url.scheme}://{request.url.netloc}"
            audio_url = f"{base_url}/voice/download/{tts_result['audio_id']}" if not tts_result.get("error") else None
            logger.info(f"Generated audio URL: {audio_url}")
        else:
            logger.info("📝 Text-only response mode")
        
        # Return in the format expected by the frontend (LegalQueryResponse)
        return {
            "id": f"voice_query_{int(time.time())}",
            "response": legal_response["answer"],
            "confidence": legal_response.get("confidence", 0.8),
            "area": legal_response.get("category", "general"),
            "sources": legal_response.get("sources", []),
            "relatedQuestions": legal_response.get("suggestions", []),
            "audioUrl": audio_url,
            "metadata": {
                "processingTime": 0,  # Will be calculated by frontend
                "sourceCount": len(legal_response.get("sources", [])),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "transcription": stt_result.get("text", ""),
                "voiceProcessing": response_mode == "audio"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in voice query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando consulta por voz"
        )

@router.get("/voices")
async def get_available_voices() -> Dict[str, Any]:
    """
    Obtener lista de voces disponibles y configuraciones
    """
    try:
        return await voice_service.get_available_voices()
        
    except Exception as e:
        logger.error(f"❌ Error getting voices: {e}")
        return {
            "voices": [],
            "error": str(e),
            "configured_styles": ["legal", "formal", "casual"]
        }

@router.get("/status")
async def get_voice_status() -> Dict[str, Any]:
    """
    Obtener estado del servicio de voz
    """
    try:
        return voice_service.get_service_status()
        
    except Exception as e:
        logger.error(f"❌ Error getting voice status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@router.get("/health")
async def voice_health_check() -> Dict[str, str]:
    """
    Health check para servicios de voz
    """
    try:
        status = voice_service.get_service_status()
        
        if status["elevenlabs_enabled"] or status["whisper_enabled"]:
            return {"status": "healthy", "message": "Voice services operational"}
        else:
            return {"status": "limited", "message": "Voice services have limited functionality"}
            
    except Exception as e:
        logger.error(f"❌ Voice health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}
