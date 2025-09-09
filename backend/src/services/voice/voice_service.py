"""
Servicio de voz simplificado y compatible con ElevenLabs
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from io import BytesIO

import openai
from fastapi import UploadFile
import aiofiles
import subprocess

logger = logging.getLogger(__name__)

class VoiceService:
    """Servicio de voz compatible con todas las versiones de ElevenLabs"""
    
    def __init__(self):
        # Configuración ElevenLabs
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_client = None
        self.voice_enabled = False
        
        if self.elevenlabs_api_key:
            try:
                from elevenlabs.client import ElevenLabs
                self.elevenlabs_client = ElevenLabs(api_key=self.elevenlabs_api_key)
                self.voice_enabled = True
                logger.info("✅ ElevenLabs client initialized")
            except ImportError:
                logger.warning("⚠️ ElevenLabs not installed. Voice synthesis disabled.")
            except Exception as e:
                logger.warning(f"⚠️ ElevenLabs initialization failed: {e}")
        else:
            logger.warning("⚠️ ElevenLabs API key not found. Voice synthesis disabled.")
        
        # Configuración para Speech-to-Text (usando ElevenLabs)
        self.stt_enabled = self.voice_enabled  # Usar ElevenLabs para STT también
        if self.stt_enabled:
            logger.info("✅ ElevenLabs Scribe v1 enabled for STT")
        else:
            logger.warning("⚠️ ElevenLabs not available. Speech-to-text disabled.")
        
        # Tu voz personalizada
        self.custom_voice_id = "86V9x9hrQds83qf7zaGn"
        
        # Directorio temporal para archivos de audio
        self.temp_dir = "./temp_audio"
        try:
            os.makedirs(self.temp_dir, exist_ok=True)
            logger.info(f"✅ Temp directory created/verified: {self.temp_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create temp directory: {e}")
            self.temp_dir = "/tmp"  # Fallback to system temp
    
    async def speech_to_text(
        self,
        audio_file: Union[UploadFile, bytes, str],
        language: str = "es"
    ) -> Dict[str, Any]:
        """Convertir audio a texto usando ElevenLabs Scribe v1 (STT)"""
        if not self.voice_enabled:
            return {
                "text": "",
                "error": "Speech-to-text not available",
                "confidence": 0.0
            }
        
        try:
            # Preparar archivo temporal
            temp_file_path = None
            
            if isinstance(audio_file, UploadFile):
                logger.info(f"Processing UploadFile: {audio_file.filename}, content_type: {audio_file.content_type}")
                content = await audio_file.read()
                logger.info(f"Read {len(content)} bytes from audio file")
                temp_file_path = await self._save_temp_audio(content, audio_file.filename)
                logger.info(f"_save_temp_audio returned: {temp_file_path}")
            elif isinstance(audio_file, bytes):
                logger.info(f"Processing bytes: {len(audio_file)} bytes")
                temp_file_path = await self._save_temp_audio(audio_file, "audio.wav")
                logger.info(f"_save_temp_audio returned: {temp_file_path}")
            elif isinstance(audio_file, str):
                logger.info(f"Processing file path: {audio_file}")
                temp_file_path = audio_file
                logger.info(f"Using provided file path: {temp_file_path}")
            
            if not temp_file_path:
                logger.error("temp_file_path is None")
                raise ValueError("Invalid audio file format")
            
            logger.info(f"Temp file path: {temp_file_path}")
            
            # Verificar que el archivo existe y tiene contenido
            if not os.path.exists(temp_file_path):
                logger.error(f"Temp file does not exist: {temp_file_path}")
                raise ValueError("Temp file not created")
            
            file_size = os.path.getsize(temp_file_path)
            logger.info(f"Temp file size: {file_size} bytes")
            
            if file_size == 0:
                logger.error("Temp file is empty")
                raise ValueError("Empty audio file")
            
            # Transcribir con ElevenLabs Scribe v1
            with open(temp_file_path, 'rb') as audio:
                transcript = self.elevenlabs_client.speech_to_text.convert(
                    file=audio,
                    model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
                    tag_audio_events=False,  # No necesitamos eventos de audio para consultas legales
                    language_code="spa" if language == "es" else "eng",  # Usar código ISO correcto
                    diarize=False  # No necesitamos diarización para consultas individuales
                )
            
            # Limpiar archivo temporal
            if isinstance(audio_file, (UploadFile, bytes)):
                await self._cleanup_temp_files([temp_file_path])
            
            # La respuesta de ElevenLabs es directamente el objeto de transcripción
            # Según el ejemplo oficial, transcript es el objeto completo
            logger.info(f"ElevenLabs transcript response type: {type(transcript)}")
            logger.info(f"ElevenLabs transcript response: {transcript}")
            
            text = getattr(transcript, 'text', '') if hasattr(transcript, 'text') else str(transcript)
            
            return {
                "text": text,
                "language": getattr(transcript, 'language_code', language) if hasattr(transcript, 'language_code') else language,
                "confidence": 0.9,  # ElevenLabs no proporciona confidence score
                "words": getattr(transcript, 'words', []) if hasattr(transcript, 'words') else [],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in speech-to-text: {e}")
            return {
                "text": "",
                "error": str(e),
                "confidence": 0.0
            }
    
    async def text_to_speech(
        self,
        text: str,
        voice_style: str = "legal",
        output_format: str = "mp3"
    ) -> Dict[str, Any]:
        """Convertir texto a audio usando ElevenLabs (TTS)"""
        if not self.voice_enabled:
            return {
                "audio_url": None,
                "error": "Text-to-speech not available",
                "duration": 0
            }
        
        try:
            # Configuración de voz optimizada para tu voz personalizada
            voice_settings = {
                "stability": 0.85,
                "similarity_boost": 0.90,
                "style": 0.0,
                "use_speaker_boost": True
            }
            
            # Generar audio usando la API más simple
            audio_generator = self.elevenlabs_client.text_to_speech.convert(
                voice_id=self.custom_voice_id,
                text=text,
                voice_settings=voice_settings,
                model_id="eleven_multilingual_v2"
            )
            
            # Guardar archivo temporal
            audio_id = str(uuid.uuid4())
            filename = f"legal_response_{audio_id}.{output_format}"
            file_path = os.path.join(self.temp_dir, filename)
            
            # Guardar audio
            with open(file_path, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            # Obtener información del archivo
            file_size = os.path.getsize(file_path)
            
            return {
                "audio_id": audio_id,
                "audio_path": file_path,
                "filename": filename,
                "duration": 0,  # Placeholder
                "file_size": file_size,
                "voice_style": voice_style,
                "format": output_format,
                "timestamp": datetime.now().isoformat(),
                "text_length": len(text),
                "voice_id_used": self.custom_voice_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error in text-to-speech: {e}")
            return {
                "audio_url": None,
                "error": str(e),
                "duration": 0
            }
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Obtener información de tu voz personalizada"""
        if not self.voice_enabled:
            return {"voices": [], "error": "ElevenLabs not available"}
        
        try:
            return {
                "voices": [
                    {
                        "voice_id": self.custom_voice_id,
                        "name": "Tu Voz Personalizada (Creator)",
                        "category": "custom",
                        "description": "Voz personalizada optimizada para contenido legal"
                    }
                ],
                "total_count": 1,
                "configured_styles": ["legal", "professional", "custom"],
                "plan_type": "Creator"
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting voices: {e}")
            return {"voices": [], "error": str(e)}
    
    async def _save_temp_audio(self, content: bytes, filename: str) -> str:
        """Guardar audio temporal"""
        try:
            file_id = str(uuid.uuid4())
            extension = filename.split('.')[-1] if '.' in filename else 'wav'
            temp_path = os.path.join(self.temp_dir, f"temp_{file_id}.{extension}")
            
            logger.info(f"Saving temp audio: {filename} -> {temp_path} ({len(content)} bytes)")
            logger.info(f"Temp directory: {self.temp_dir}")
            logger.info(f"Directory exists: {os.path.exists(self.temp_dir)}")
            
            # Crear directorio si no existe
            os.makedirs(self.temp_dir, exist_ok=True)
            
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(content)
            
            # Verificar que se guardó correctamente
            if os.path.exists(temp_path):
                saved_size = os.path.getsize(temp_path)
                logger.info(f"Temp file saved successfully: {saved_size} bytes")
                return temp_path
            else:
                logger.error(f"Failed to save temp file: {temp_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error in _save_temp_audio: {e}")
            return None
    
    async def _cleanup_temp_files(self, file_paths: list):
        """Limpiar archivos temporales"""
        for file_path in file_paths:
            try:
                if file_path and os.path.exists(file_path) and self.temp_dir in file_path:
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"⚠️ Could not remove temp file {file_path}: {e}")
    
    async def process_voice_query(
        self,
        audio_file: UploadFile,
        voice_response_style: str = "legal"
    ) -> Dict[str, Any]:
        """Procesar consulta de voz completa: STT -> Procesamiento -> TTS"""
        try:
            # 1. Convertir audio a texto
            stt_result = await self.speech_to_text(audio_file)
            
            if stt_result.get("error"):
                return {
                    "transcription": stt_result,
                    "audio_response": None,
                    "error": "Failed to transcribe audio"
                }
            
            transcribed_text = stt_result["text"]
            
            return {
                "transcription": stt_result,
                "query_text": transcribed_text,
                "ready_for_processing": True,
                "voice_style": voice_response_style
            }
            
        except Exception as e:
            logger.error(f"❌ Error in voice query processing: {e}")
            return {
                "transcription": None,
                "audio_response": None,
                "error": str(e)
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado del servicio de voz"""
        return {
            "elevenlabs_enabled": self.voice_enabled,
            "stt_enabled": self.stt_enabled,
            "plan_type": "Creator" if self.voice_enabled else "Unknown",
            "custom_voice_id": self.custom_voice_id,
            "temp_directory": self.temp_dir,
            "stt_provider": "ElevenLabs Scribe v1",
            "tts_provider": "ElevenLabs",
            "supported_audio_formats": [
                "wav", "mp3", "m4a", "ogg", "flac", "aac", "webm", "opus", "aiff"
            ],
            "supported_output_formats": ["mp3", "wav"]
        }

# Instancia global
voice_service = VoiceService()
