"""
Servicio de voz simplificado usando ElevenLabs directamente
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from io import BytesIO

from fastapi import UploadFile

logger = logging.getLogger(__name__)

class VoiceService:
    """Servicio de voz simplificado usando ElevenLabs"""
    
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
                logger.warning("⚠️ ElevenLabs not installed. Voice services disabled.")
            except Exception as e:
                logger.warning(f"⚠️ ElevenLabs initialization failed: {e}")
        else:
            logger.warning("⚠️ ElevenLabs API key not found. Voice services disabled.")
        
        # Tu voz personalizada
        self.custom_voice_id = "86V9x9hrQds83qf7zaGn"
        
        # Directorio temporal para archivos de audio
        self.temp_dir = "./temp_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def speech_to_text(
        self,
        audio_file: Union[UploadFile, bytes, str],
        language: str = "es"
    ) -> Dict[str, Any]:
        """Convertir audio a texto usando ElevenLabs Scribe v1 - Solución directa"""
        if not self.voice_enabled:
            return {
                "text": "",
                "error": "ElevenLabs not available for speech-to-text",
                "confidence": 0.0
            }
        
        try:
            # Obtener contenido de audio directamente
            audio_content = None
            
            if isinstance(audio_file, UploadFile):
                logger.info(f"Processing UploadFile: {audio_file.filename}, content_type: {audio_file.content_type}")
                audio_content = await audio_file.read()
                logger.info(f"Read {len(audio_content)} bytes from audio file")
            elif isinstance(audio_file, bytes):
                logger.info(f"Processing bytes: {len(audio_file)} bytes")
                audio_content = audio_file
            elif isinstance(audio_file, str):
                logger.info(f"Processing file path: {audio_file}")
                # Leer archivo desde ruta
                with open(audio_file, 'rb') as f:
                    audio_content = f.read()
                logger.info(f"Read {len(audio_content)} bytes from file path")
            
            if not audio_content:
                logger.error("No audio content available")
                raise ValueError("No audio content to process")
            
            if len(audio_content) == 0:
                logger.error("Audio content is empty")
                raise ValueError("Empty audio content")
            
            # Usar BytesIO como en el ejemplo oficial de ElevenLabs
            audio_data = BytesIO(audio_content)
            
            logger.info(f"Transcribing with ElevenLabs Scribe v1...")
            
            # Transcribir con ElevenLabs Scribe v1 usando BytesIO
            transcript = self.elevenlabs_client.speech_to_text.convert(
                file=audio_data,
                model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
                tag_audio_events=False,  # No necesitamos eventos de audio para consultas legales
                language_code="spa" if language == "es" else "eng",  # Usar código ISO correcto
                diarize=False  # No necesitamos diarización para consultas individuales
            )
            
            # La respuesta de ElevenLabs es directamente el objeto de transcripción
            logger.info(f"ElevenLabs transcript response type: {type(transcript)}")
            logger.info(f"ElevenLabs transcript response: {transcript}")
            
            # Debug: Ver todos los atributos del objeto transcript
            logger.info(f"Transcript attributes: {dir(transcript)}")
            if hasattr(transcript, '__dict__'):
                logger.info(f"Transcript dict: {transcript.__dict__}")
            
            # Extraer texto de la respuesta
            text = ""
            if hasattr(transcript, 'text'):
                text = transcript.text
                logger.info(f"Found text attribute: '{text}'")
            elif hasattr(transcript, 'transcript'):
                text = transcript.transcript
                logger.info(f"Found transcript attribute: '{text}'")
            elif hasattr(transcript, 'transcription'):
                text = transcript.transcription
                logger.info(f"Found transcription attribute: '{text}'")
            else:
                text = str(transcript)
                logger.info(f"Using str(transcript): '{text}'")
            
            logger.info(f"Final extracted text: '{text}' (length: {len(text)})")
            
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
            
            logger.info(f"Audio generated successfully: {filename}, size: {file_size} bytes")
            
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
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado del servicio de voz"""
        return {
            "elevenlabs_enabled": self.voice_enabled,
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