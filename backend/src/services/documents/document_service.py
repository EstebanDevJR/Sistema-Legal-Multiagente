import os
import uuid
import boto3
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class S3DocumentService:
    """Servicio completo para manejo de documentos con AWS S3"""
    
    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET_NAME", "legal-agent-docs")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.documents_db = {}  # En producción usar una base de datos real
        
        # Configurar cliente S3
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region
            )
            self._ensure_bucket_exists()
            logger.info(f"✅ S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.warning("⚠️ AWS credentials not found. S3 functionality disabled.")
            self.s3_client = None
        except Exception as e:
            logger.error(f"❌ Error initializing S3 client: {e}")
            self.s3_client = None
    
    def _ensure_bucket_exists(self):
        """Asegurar que el bucket S3 existe"""
        if not self.s3_client:
            return
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket no existe, crearlo
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    logger.info(f"✅ Created S3 bucket: {self.bucket_name}")
                except ClientError as create_error:
                    logger.error(f"❌ Error creating bucket: {create_error}")
    
    async def upload_document(
        self,
        file: UploadFile,
        user_id: str,
        document_type: str = "legal_document"
    ) -> Dict[str, Any]:
        """
        Subir documento a S3 y registrar metadata
        
        Args:
            file: Archivo subido
            user_id: ID del usuario
            document_type: Tipo de documento
            
        Returns:
            Información del documento subido
        """
        if not self.s3_client:
            # Fallback: guardar localmente si S3 no está disponible
            return await self._save_local_fallback(file, user_id, document_type)
        
        try:
            # Generar ID único para el documento
            doc_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Generar key S3
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
            s3_key = f"documents/{user_id}/{doc_id}.{file_extension}"
            
            # Leer contenido del archivo
            content = await file.read()
            
            # Metadata del documento
            metadata = {
                'user_id': user_id,
                'document_type': document_type,
                'original_filename': file.filename,
                'upload_timestamp': timestamp,
                'file_size': str(len(content)),
                'content_type': file.content_type or 'application/octet-stream'
            }
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                Metadata=metadata,
                ContentType=file.content_type or 'application/octet-stream'
            )
            
            # Generar URL presignada (válida por 1 hora)
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=3600
            )
            
            # Guardar información en "base de datos" local
            document_info = {
                'id': doc_id,
                'user_id': user_id,
                'filename': file.filename,
                'document_type': document_type,
                'file_size': len(content),
                'content_type': file.content_type,
                's3_key': s3_key,
                's3_url': presigned_url,
                'upload_timestamp': timestamp,
                'status': 'uploaded'
            }
            
            # Almacenar en memoria (en producción usar DB)
            if user_id not in self.documents_db:
                self.documents_db[user_id] = []
            self.documents_db[user_id].append(document_info)
            
            logger.info(f"✅ Document uploaded: {doc_id} for user {user_id}")
            # Procesar documento para el vector store
            await self._process_document_for_vectorstore(document_info, content)
            
            return document_info
            
        except Exception as e:
            logger.error(f"❌ Error uploading document: {e}")
            # Fallback a almacenamiento local
            return await self._save_local_fallback(file, user_id, document_type)
    
    async def _save_local_fallback(
        self,
        file: UploadFile,
        user_id: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Fallback para guardar documentos localmente"""
        try:
            doc_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Crear directorio local si no existe
            local_dir = f"./uploads/{user_id}"
            os.makedirs(local_dir, exist_ok=True)
            
            # Guardar archivo localmente
            file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
            local_path = f"{local_dir}/{doc_id}.{file_extension}"
            
            content = await file.read()
            async with aiofiles.open(local_path, 'wb') as f:
                await f.write(content)
            
            document_info = {
                'id': doc_id,
                'user_id': user_id,
                'filename': file.filename,
                'document_type': document_type,
                'file_size': len(content),
                'content_type': file.content_type,
                'local_path': local_path,
                's3_url': None,
                'upload_timestamp': timestamp,
                'status': 'local_storage'
            }
            
            if user_id not in self.documents_db:
                self.documents_db[user_id] = []
            self.documents_db[user_id].append(document_info)
            
            logger.info(f"📁 Document saved locally: {doc_id}")
            
            # Procesar documento para el vector store
            await self._process_document_for_vectorstore(document_info, content)
            
            return document_info
            
        except Exception as e:
            logger.error(f"❌ Error in local fallback: {e}")
            raise
    
    async def _process_document_for_vectorstore(self, document_info: Dict[str, Any], content: bytes):
        """
        Procesar documento para agregarlo al vector store
        """
        try:
            # Importar aquí para evitar dependencias circulares
            from ..legal.rag.vector_manager import VectorManager
            
            # Crear instancia del vector manager
            vector_manager = VectorManager()
            
            # Extraer texto del contenido
            logger.info(f"🔄 Extracting text from document {document_info['id']} (type: {document_info.get('content_type', 'unknown')})")
            text_content = self._extract_text_from_content(content, document_info.get('content_type', ''))
            logger.info(f"📝 Extracted text length: {len(text_content) if text_content else 0} characters")
            
            if text_content:
                # Agregar al vector store
                success = await vector_manager.add_document_to_vectorstore(
                    document_id=document_info['id'],
                    content=text_content,
                    filename=document_info['filename'],
                    user_id=document_info['user_id']
                )
                
                if success:
                    logger.info(f"✅ Document {document_info['id']} processed for vector store")
                else:
                    logger.warning(f"⚠️ Failed to process document {document_info['id']} for vector store")
            else:
                logger.warning(f"⚠️ No text content extracted from document {document_info['id']}")
                
        except Exception as e:
            logger.error(f"❌ Error processing document for vector store: {e}")
    
    def _extract_text_from_content(self, content: bytes, content_type: str) -> str:
        """
        Extraer texto del contenido del archivo
        """
        try:
            logger.info(f"🔍 Extracting text from content type: {content_type}, size: {len(content)} bytes")
            
            # Para archivos de texto simple
            if content_type.startswith('text/') or content_type == 'application/octet-stream':
                text = content.decode('utf-8', errors='ignore')
                logger.info(f"📄 Extracted text from plain text file: {len(text)} characters")
                return text
            
            # Para PDFs (requiere PyPDF2 o similar)
            elif content_type == 'application/pdf':
                try:
                    import PyPDF2
                    import io
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
                except ImportError:
                    logger.warning("PyPDF2 not available, cannot extract text from PDF")
                    return ""
            
            # Para documentos de Word (requiere python-docx)
            elif content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                'application/msword']:
                try:
                    import docx
                    import io
                    doc = docx.Document(io.BytesIO(content))
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    logger.warning("python-docx not available, cannot extract text from Word document")
                    return ""
            
            # Fallback: intentar decodificar como texto
            else:
                logger.info(f"🔄 Using fallback text extraction for content type: {content_type}")
                text = content.decode('utf-8', errors='ignore')
                logger.info(f"📄 Fallback extraction result: {len(text)} characters")
                return text
                
        except Exception as e:
            logger.error(f"❌ Error extracting text from content: {e}")
            return ""
    
    def get_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        """Obtener documentos del usuario"""
        return self.documents_db.get(user_id, [])
    
    def get_document_by_id(self, user_id: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Obtener documento específico por ID"""
        user_docs = self.get_user_documents(user_id)
        return next((doc for doc in user_docs if doc['id'] == doc_id), None)
    
    async def download_document(self, user_id: str, doc_id: str) -> Optional[bytes]:
        """Descargar contenido del documento"""
        document = self.get_document_by_id(user_id, doc_id)
        if not document:
            return None
        
        try:
            if self.s3_client and document.get('s3_key'):
                # Descargar de S3
                response = self.s3_client.get_object(
                    Bucket=self.bucket_name,
                    Key=document['s3_key']
                )
                return response['Body'].read()
            elif document.get('local_path'):
                # Leer archivo local
                async with aiofiles.open(document['local_path'], 'rb') as f:
                    return await f.read()
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error downloading document {doc_id}: {e}")
            return None
    
    async def delete_document(self, user_id: str, doc_id: str) -> bool:
        """Eliminar documento"""
        document = self.get_document_by_id(user_id, doc_id)
        if not document:
            return False
        
        try:
            # Eliminar de S3 si existe
            if self.s3_client and document.get('s3_key'):
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=document['s3_key']
                )
            
            # Eliminar archivo local si existe
            if document.get('local_path') and os.path.exists(document['local_path']):
                os.remove(document['local_path'])
            
            # Remover de la "base de datos"
            if user_id in self.documents_db:
                self.documents_db[user_id] = [
                    doc for doc in self.documents_db[user_id] 
                    if doc['id'] != doc_id
                ]
            
            logger.info(f"🗑️ Document deleted: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting document {doc_id}: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de almacenamiento"""
        total_docs = sum(len(docs) for docs in self.documents_db.values())
        total_users = len(self.documents_db)
        
        return {
            "total_documents": total_docs,
            "total_users": total_users,
            "s3_enabled": self.s3_client is not None,
            "bucket_name": self.bucket_name if self.s3_client else None,
            "storage_mode": "s3" if self.s3_client else "local"
        }

# Instancia global
document_service = S3DocumentService()
