"""
Servicio híbrido de extracción de texto usando AWS Textract y fallbacks
"""

import os
import io
import logging
from typing import Optional, Dict, Any, Tuple
from PIL import Image
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class TextractService:
    """Servicio híbrido para extracción de texto con AWS Textract y fallbacks"""
    
    def __init__(self):
        self.textract_client = None
        self.textract_available = False
        
        # Intentar inicializar Textract
        try:
            # Verificar credenciales AWS
            if self._has_aws_credentials():
                self.textract_client = boto3.client(
                    'textract',
                    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
                
                # Verificar que Textract esté disponible haciendo una llamada de prueba
                try:
                    # Crear una imagen de prueba pequeña (1x1 pixel blanco)
                    test_image = Image.new('RGB', (1, 1), color='white')
                    test_buffer = io.BytesIO()
                    test_image.save(test_buffer, format='PNG')
                    test_bytes = test_buffer.getvalue()
                    
                    # Intentar analizar la imagen de prueba
                    response = self.textract_client.detect_document_text(
                        Document={'Bytes': test_bytes}
                    )
                    
                    if response.get('DocumentMetadata'):
                        self.textract_available = True
                        logger.info("✅ AWS Textract initialized and available")
                    else:
                        logger.warning("⚠️ AWS Textract responded but no metadata - service may be limited")
                        
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                    if error_code == 'AccessDeniedException':
                        logger.warning("⚠️ AWS Textract access denied - check permissions")
                    else:
                        logger.warning(f"⚠️ AWS Textract test failed: {error_code}")
                except Exception as e:
                    logger.warning(f"⚠️ AWS Textract test failed: {e}")
                    
            else:
                logger.info("ℹ️ AWS credentials not found - Textract not available")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize AWS Textract: {e}")
    
    def _has_aws_credentials(self) -> bool:
        """Verificar si las credenciales AWS están disponibles"""
        return bool(
            os.getenv("AWS_ACCESS_KEY_ID") and 
            os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    def extract_text_from_content(self, content: bytes, content_type: str, filename: str = "") -> Tuple[str, Dict[str, Any]]:
        """
        Extraer texto usando el método más apropiado según el tipo de contenido
        
        Args:
            content: Contenido del archivo en bytes
            content_type: Tipo MIME del contenido
            filename: Nombre del archivo (opcional, para contexto)
            
        Returns:
            Tuple[str, Dict[str, Any]]: (texto_extraído, metadata)
        """
        metadata = {
            "extraction_method": "unknown",
            "content_type": content_type,
            "file_size": len(content),
            "textract_available": self.textract_available,
            "success": False,
            "error": None
        }
        
        try:
            logger.info(f"🔍 Extracting text from {content_type}, size: {len(content)} bytes")
            
            # 1. Para imágenes, intentar Textract primero
            if content_type.startswith('image/'):
                if self.textract_available:
                    text, success = self._extract_with_textract(content, content_type)
                    if success:
                        metadata.update({
                            "extraction_method": "aws_textract",
                            "success": True
                        })
                        logger.info(f"✅ Textract extraction successful: {len(text)} characters")
                        return text, metadata
                    else:
                        logger.warning("⚠️ Textract extraction failed, trying fallback...")
                
                # Fallback para imágenes: OCR básico o error
                text = self._extract_image_fallback(content, content_type)
                metadata.update({
                    "extraction_method": "image_fallback",
                    "success": len(text) > 0
                })
                return text, metadata
            
            # 2. Para PDFs, usar PyPDF2 primero (más eficiente para PDFs nativos)
            elif content_type == 'application/pdf':
                # Intentar PyPDF2 primero
                text = self._extract_pdf_fallback(content)
                if len(text.strip()) > 50:  # Si PyPDF2 extrajo suficiente texto
                    metadata.update({
                        "extraction_method": "pypdf2",
                        "success": True
                    })
                    logger.info(f"✅ PyPDF2 PDF extraction successful: {len(text)} characters")
                    return text, metadata
                else:
                    logger.info("📄 PyPDF2 extracted minimal text, trying Textract for scanned PDF...")
                    
                    # Si PyPDF2 no extrajo suficiente, intentar Textract (PDF escaneado)
                    if self.textract_available:
                        textract_text, success = self._extract_with_textract(content, content_type)
                        if success and len(textract_text.strip()) > len(text.strip()):
                            metadata.update({
                                "extraction_method": "aws_textract_fallback",
                                "success": True,
                                "note": "Used Textract after PyPDF2 extracted minimal text"
                            })
                            logger.info(f"✅ Textract fallback successful: {len(textract_text)} characters")
                            return textract_text, metadata
                        else:
                            logger.warning("⚠️ Textract also failed or didn't improve, using PyPDF2 result")
                    
                    # Usar resultado de PyPDF2 aunque sea limitado
                    metadata.update({
                        "extraction_method": "pypdf2",
                        "success": len(text) > 0,
                        "note": "Limited text extracted, may be a scanned PDF"
                    })
                return text, metadata
            
            # 3. Para documentos de Word
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                'application/msword']:
                text = self._extract_word_document(content)
                metadata.update({
                    "extraction_method": "python_docx",
                    "success": len(text) > 0
                })
                return text, metadata
            
            # 4. Para texto plano
            elif content_type.startswith('text/') or content_type == 'application/octet-stream':
                text = content.decode('utf-8', errors='ignore')
                metadata.update({
                    "extraction_method": "text_decode",
                    "success": len(text) > 0
                })
                logger.info(f"📄 Plain text extraction: {len(text)} characters")
                return text, metadata
            
            # 5. Fallback general
            else:
                logger.info(f"🔄 Using fallback extraction for content type: {content_type}")
                text = content.decode('utf-8', errors='ignore')
                metadata.update({
                    "extraction_method": "fallback_decode",
                    "success": len(text) > 0
                })
                return text, metadata
                
        except Exception as e:
            logger.error(f"❌ Error extracting text: {e}")
            metadata.update({
                "error": str(e),
                "success": False
            })
            return "", metadata
    
    def _extract_with_textract(self, content: bytes, content_type: str) -> Tuple[str, bool]:
        """Extraer texto usando AWS Textract"""
        try:
            if not self.textract_client:
                return "", False
            
            # Verificar tamaño (máximo 10MB para Textract)
            if len(content) > 10 * 1024 * 1024:
                logger.warning("⚠️ File too large for Textract (>10MB)")
                return "", False
            
            logger.info("🔄 Using AWS Textract for text extraction...")
            
            # Llamar a Textract
            if content_type == 'application/pdf':
                # Para PDFs, usar analyze_document que es más potente
                response = self.textract_client.analyze_document(
                    Document={'Bytes': content},
                    FeatureTypes=['TABLES', 'FORMS']  # Extraer también tablas y formularios
                )
            else:
                # Para imágenes, usar detect_document_text
                response = self.textract_client.detect_document_text(
                    Document={'Bytes': content}
                )
            
            # Extraer texto de la respuesta
            text_blocks = []
            
            for block in response.get('Blocks', []):
                if block.get('BlockType') == 'LINE':
                    text_blocks.append(block.get('Text', ''))
                elif block.get('BlockType') == 'WORD':
                    # Para mayor precisión, también incluir palabras individuales si no hay líneas
                    if not any(b.get('BlockType') == 'LINE' for b in response.get('Blocks', [])):
                        text_blocks.append(block.get('Text', ''))
            
            extracted_text = '\n'.join(text_blocks)
            
            if extracted_text.strip():
                logger.info(f"✅ Textract extracted {len(extracted_text)} characters")
                return extracted_text, True
            else:
                logger.warning("⚠️ Textract returned no text")
                return "", False
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'UnsupportedDocumentException':
                logger.info(f"📄 Textract doesn't support this PDF format - likely a native PDF that doesn't need OCR")
            elif error_code == 'InvalidParameterException':
                logger.warning(f"⚠️ Textract parameter error: {e}")
            elif error_code == 'ThrottlingException':
                logger.warning(f"⚠️ Textract throttling: {e}")
            else:
                logger.error(f"❌ Textract ClientError: {error_code} - {e}")
            return "", False
        except Exception as e:
            logger.error(f"❌ Textract extraction failed: {e}")
            return "", False
    
    def _extract_pdf_fallback(self, content: bytes) -> str:
        """Extraer texto de PDF usando PyPDF2"""
        try:
            import PyPDF2
            import io
            
            logger.info("🔄 Using PyPDF2 for PDF text extraction...")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            
            logger.info(f"📄 PDF has {len(pdf_reader.pages)} pages")
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    text += f"--- Página {page_num + 1} ---\n{page_text}\n\n"
                    logger.debug(f"✅ Extracted {len(page_text)} characters from page {page_num + 1}")
                except Exception as page_error:
                    logger.warning(f"⚠️ Error extracting text from page {page_num + 1}: {page_error}")
                    continue
            
            logger.info(f"✅ PyPDF2 extraction complete: {len(text)} total characters")
            return text
            
        except ImportError:
            logger.error("❌ PyPDF2 not available")
            return ""
        except Exception as e:
            logger.error(f"❌ PyPDF2 extraction failed: {e}")
            return ""
    
    def _extract_word_document(self, content: bytes) -> str:
        """Extraer texto de documento Word usando python-docx"""
        try:
            import docx
            import io
            
            logger.info("🔄 Using python-docx for Word document extraction...")
            doc = docx.Document(io.BytesIO(content))
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info(f"✅ Word extraction complete: {len(text)} characters")
            return text
            
        except ImportError:
            logger.error("❌ python-docx not available")
            return ""
        except Exception as e:
            logger.error(f"❌ Word document extraction failed: {e}")
            return ""
    
    def _extract_image_fallback(self, content: bytes, content_type: str) -> str:
        """Fallback para extracción de imágenes sin Textract"""
        # Por ahora, no implementamos OCR local ya que requeriría tesseract
        # En el futuro se podría agregar pytesseract como fallback
        logger.warning("⚠️ Image text extraction not available without Textract")
        return f"[Imagen detectada: {content_type}. Para extraer texto de imágenes, configure AWS Textract.]"
    
    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado del servicio de extracción"""
        return {
            "textract_available": self.textract_available,
            "aws_credentials": self._has_aws_credentials(),
            "supported_formats": {
                "text": ["txt", "md"],
                "pdf": ["pdf"],
                "word": ["docx", "doc"],
                "images": ["png", "jpg", "jpeg", "tiff", "bmp", "webp"]
            },
            "extraction_methods": {
                "aws_textract": "Available" if self.textract_available else "Not available",
                "pypdf2": "Available",
                "python_docx": "Available", 
                "text_decode": "Available"
            }
        }

# Instancia global del servicio
textract_service = TextractService()
