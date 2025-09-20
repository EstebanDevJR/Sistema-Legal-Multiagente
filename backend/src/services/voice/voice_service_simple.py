"""
Servicio de voz simplificado usando ElevenLabs directamente
"""

import os
import uuid
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime
from io import BytesIO
import subprocess
import tempfile

from fastapi import UploadFile

# Intentar importar pydub para conversión de audio
try:
    from pydub import AudioSegment
    from pydub.utils import which
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

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
        
        # Verificar si ffmpeg está disponible
        self.ffmpeg_available = self._check_ffmpeg_availability()
        
        # Verificar si pydub está disponible
        self.pydub_available = PYDUB_AVAILABLE
        if self.pydub_available:
            logger.info("✅ PyDub is available for audio conversion")
            # Verificar si PyDub puede funcionar sin FFmpeg
            self.pydub_webm_support = self._check_pydub_webm_support()
        else:
            logger.warning("⚠️ PyDub not available - limited audio conversion")
            self.pydub_webm_support = False
    
    def _check_ffmpeg_availability(self) -> bool:
        """Verificar si ffmpeg está disponible en el sistema"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ FFmpeg is available for audio conversion")
                return True
            else:
                logger.warning("⚠️ FFmpeg not available - audio conversion disabled")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"⚠️ FFmpeg check failed: {e}")
            return False
    
    def _check_pydub_webm_support(self) -> bool:
        """Verificar si PyDub puede procesar WebM sin FFmpeg"""
        if not self.pydub_available:
            return False
        
        try:
            # Crear un pequeño archivo WebM de prueba en memoria
            # En lugar de probar con un archivo real, asumimos que PyDub necesita FFmpeg para WebM
            logger.info("ℹ️ PyDub WebM support requires FFmpeg (not available)")
            return False
        except Exception as e:
            logger.debug(f"PyDub WebM test failed: {e}")
            return False
    
    def _convert_webm_to_wav(self, audio_content: bytes) -> bytes:
        """Convertir audio webm a wav usando ffmpeg"""
        if not self.ffmpeg_available:
            logger.warning("⚠️ FFmpeg not available, returning original audio content")
            return audio_content
            
        try:
            # Crear archivos temporales
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_file.write(audio_content)
                webm_path = webm_file.name
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name
            
            # Convertir usando ffmpeg con parámetros optimizados para speech-to-text
            cmd = [
                'ffmpeg', '-i', webm_path, 
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-ar', '16000',          # 16kHz sample rate (recomendado para STT)
                '-ac', '1',              # Mono
                '-af', 'highpass=f=200,lowpass=f=8000',  # Filtros para mejorar la voz
                '-y', wav_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Leer el archivo wav convertido
                with open(wav_path, 'rb') as f:
                    wav_content = f.read()
                
                # Limpiar archivos temporales
                os.unlink(webm_path)
                os.unlink(wav_path)
                
                logger.info(f"✅ Successfully converted webm to wav: {len(audio_content)} -> {len(wav_content)} bytes")
                return wav_content
            else:
                logger.error(f"❌ FFmpeg conversion failed: {result.stderr}")
                # Limpiar archivos temporales
                os.unlink(webm_path)
                if os.path.exists(wav_path):
                    os.unlink(wav_path)
                return audio_content
                
        except subprocess.TimeoutExpired:
            logger.error("❌ FFmpeg conversion timed out")
            return audio_content
        except Exception as e:
            logger.error(f"❌ Error converting webm to wav: {e}")
            return audio_content
    
    def _convert_webm_to_wav_pydub(self, audio_content: bytes) -> bytes:
        """Convertir audio webm a wav usando pydub (requiere FFmpeg para WebM)"""
        if not self.pydub_available:
            logger.warning("⚠️ PyDub not available, returning original audio content")
            return audio_content
        
        webm_path = None
        try:
            # Crear un archivo temporal para el audio WebM
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_file.write(audio_content)
                webm_path = webm_file.name
            
            logger.info(f"🔄 Converting WebM to WAV using PyDub...")
            
            # Verificar si PyDub puede manejar WebM (necesita FFmpeg)
            try:
                # Intentar cargar el audio usando pydub
                audio = AudioSegment.from_file(webm_path, format="webm")
                
                # Configurar para speech-to-text
                audio = audio.set_frame_rate(16000)  # 16kHz
                audio = audio.set_channels(1)        # Mono
                audio = audio.set_sample_width(2)    # 16-bit
                
                # Aplicar filtros básicos para mejorar la voz
                # Normalizar volumen
                audio = audio.normalize()
                
                # Exportar a WAV en memoria
                wav_buffer = BytesIO()
                audio.export(wav_buffer, format="wav")
                wav_content = wav_buffer.getvalue()
                
                logger.info(f"✅ Successfully converted webm to wav using PyDub: {len(audio_content)} -> {len(wav_content)} bytes")
                return wav_content
                
            except Exception as pydub_error:
                logger.warning(f"⚠️ PyDub cannot process WebM without FFmpeg: {pydub_error}")
                logger.info("🔄 Falling back to direct upload...")
                return audio_content
            
        except Exception as e:
            logger.error(f"❌ Error in PyDub conversion setup: {e}")
            return audio_content
        finally:
            # Limpiar archivo temporal de forma segura
            if webm_path and os.path.exists(webm_path):
                try:
                    os.unlink(webm_path)
                    logger.debug(f"🧹 Cleaned up temporary file: {webm_path}")
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Could not clean up temporary file {webm_path}: {cleanup_error}")
    
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
            
            content_type = None
            if isinstance(audio_file, UploadFile):
                logger.info(f"Processing UploadFile: {audio_file.filename}, content_type: {audio_file.content_type}")
                audio_content = await audio_file.read()
                content_type = audio_file.content_type
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
            
            # Verificar el formato del audio
            logger.info(f"Audio content size: {len(audio_content)} bytes")
            logger.info(f"First 20 bytes: {audio_content[:20].hex()}")
            
            # Intentar convertir webm a wav para mejor compatibilidad con ElevenLabs
            is_webm = (content_type and 'webm' in content_type.lower()) or audio_content[:4] == b'\x1a\x45\xdf\xa3'
            
            # Intentar conversión de WebM si está disponible, sino usar directo
            if is_webm:
                logger.info("🔍 WebM format detected")
                
                if self.ffmpeg_available:
                    logger.info("🔄 Converting webm to wav using FFmpeg")
                    audio_content = self._convert_webm_to_wav(audio_content)
                else:
                    logger.info("ℹ️ No FFmpeg available, sending WebM directly to ElevenLabs")
                    logger.info("📝 Note: ElevenLabs supports WebM format directly")
            
            # Usar BytesIO como en el ejemplo oficial de ElevenLabs
            audio_data = BytesIO(audio_content)
            
            logger.info(f"Transcribing with ElevenLabs Scribe v1...")
            
            # Transcribir con ElevenLabs Scribe v1 usando BytesIO
            # Resetear el puntero del BytesIO al inicio
            audio_data.seek(0)
            
            # Llamar a ElevenLabs con configuración optimizada
            try:
                transcript = self.elevenlabs_client.speech_to_text.convert(
                    file=audio_data,
                    model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
                    tag_audio_events=False,  # No necesitamos eventos de audio para consultas legales
                    diarize=False  # No necesitamos diarización para consultas individuales
                )
            except Exception as api_error:
                logger.error(f"❌ ElevenLabs API error: {api_error}")
                # Intentar con un archivo temporal si BytesIO falla
                temp_file_path = None
                try:
                    # Determinar extensión basada en el contenido
                    file_extension = '.wav' if not is_webm else '.webm'
                    
                    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
                        temp_file.write(audio_content)
                        temp_file_path = temp_file.name
                    
                    logger.info(f"🔄 Retrying with temporary file: {temp_file_path}")
                    with open(temp_file_path, 'rb') as file_handle:
                        transcript = self.elevenlabs_client.speech_to_text.convert(
                            file=file_handle,
                            model_id="scribe_v1",
                            tag_audio_events=False,
                            diarize=False
                        )
                except Exception as retry_error:
                    logger.error(f"❌ Retry with temporary file also failed: {retry_error}")
                    raise api_error  # Re-raise the original error
                finally:
                    # Limpiar archivo temporal de forma segura
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                            logger.debug(f"🧹 Cleaned up retry temp file: {temp_file_path}")
                        except Exception as cleanup_error:
                            logger.warning(f"⚠️ Could not clean up retry temp file: {cleanup_error}")
            
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
                text = transcript.text or ""
                logger.info(f"✅ Found text attribute: '{text}'")
            elif hasattr(transcript, 'transcript'):
                text = transcript.transcript or ""
                logger.info(f"✅ Found transcript attribute: '{text}'")
            elif hasattr(transcript, 'transcription'):
                text = transcript.transcription or ""
                logger.info(f"✅ Found transcription attribute: '{text}'")
            else:
                text = str(transcript)
                logger.info(f"⚠️ Using str(transcript): '{text}'")
            
            logger.info(f"📝 Final extracted text: '{text}' (length: {len(text)})")
            
            # Validar que tenemos texto útil
            if not text or len(text.strip()) == 0:
                logger.warning("⚠️ Empty text received from ElevenLabs")
                return {
                    "text": "",
                    "error": "No speech detected in audio. Please ensure you're speaking clearly and the microphone is working.",
                    "confidence": 0.0,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
            
            return {
                "text": text.strip(),
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
        # Determinar capacidades de conversión de audio
        conversion_method = "Direct upload only"
        webm_support = "Native (ElevenLabs direct)"
        
        if self.ffmpeg_available:
            conversion_method = "FFmpeg (preferred)"
            webm_support = "Full (FFmpeg conversion + direct)"
        
        return {
            "elevenlabs_enabled": self.voice_enabled,
            "ffmpeg_available": self.ffmpeg_available,
            "pydub_available": self.pydub_available,
            "plan_type": "Creator" if self.voice_enabled else "Unknown",
            "custom_voice_id": self.custom_voice_id,
            "temp_directory": self.temp_dir,
            "stt_provider": "ElevenLabs Scribe v1",
            "tts_provider": "ElevenLabs",
            "supported_audio_formats": [
                "wav", "mp3", "m4a", "ogg", "flac", "aac", "webm", "opus", "aiff"
            ],
            "supported_output_formats": ["mp3", "wav"],
            "audio_conversion": conversion_method,
            "webm_support": webm_support,
            "notes": [
                "WebM is supported natively by ElevenLabs",
                "FFmpeg conversion available for optimization" if self.ffmpeg_available else "FFmpeg not available - using direct upload",
                "System optimized for speech-to-text processing"
            ]
        }

# Instancia global
voice_service = VoiceService()