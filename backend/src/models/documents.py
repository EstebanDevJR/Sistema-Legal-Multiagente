from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentResponse(BaseModel):
    """Response with document information compatible with the frontend"""
    id: str
    filename: str
    original_name: str
    file_type: str
    file_size: int
    upload_date: str
    status: str  # "processing", "ready", "error", "completed", "draft", "review"
    page_count: Optional[int] = None
    content_preview: Optional[str] = None
    content_length: Optional[int] = None
    description: Optional[str] = None
    
    # Additional fields for frontend compatibility
    name: Optional[str] = None  # Nombre amigable del documento
    type: Optional[str] = None  # Tipo de documento (ej: "Contrato Laboral")
    category: Optional[str] = None  # Categoría (ej: "Laboral", "Societario", "Tributario")
    size: Optional[str] = None  # Tamaño en formato legible (ej: "245 KB")
    createdAt: Optional[str] = None  # Fecha de creación en formato frontend
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_123e4567-e89b-12d3-a456-426614174000",
                "filename": "contrato_123.pdf",
                "original_name": "contrato_servicios.pdf",
                "file_type": ".pdf",
                "file_size": 1024000,
                "upload_date": "2024-01-15T10:30:00",
                "status": "ready",
                "page_count": 5,
                "content_preview": "CONTRATO DE PRESTACIÓN DE SERVICIOS...",
                "content_length": 2500,
                "description": "Contrato de servicios de desarrollo web",
                "name": "Contrato de Trabajo - Juan Pérez",
                "type": "Contrato Laboral",
                "category": "Laboral",
                "size": "1024 KB",
                "createdAt": "2024-01-15"
            }
        }

class DocumentListResponse(BaseModel):
    """Response with list of user documents"""
    documents: List[DocumentResponse]
    total_count: int
    total_size_mb: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "doc_123",
                        "filename": "contrato_123.pdf",
                        "original_name": "contrato_servicios.pdf",
                        "file_type": ".pdf",
                        "file_size": 1024000,
                        "upload_date": "2024-01-15T10:30:00",
                        "status": "ready",
                        "page_count": 5,
                        "content_preview": "CONTRATO DE PRESTACIÓN...",
                        "content_length": 2500,
                        "name": "Contrato de Trabajo - Juan Pérez",
                        "type": "Contrato Laboral",
                        "category": "Laboral",
                        "size": "1024 KB",
                        "createdAt": "2024-01-15"
                    }
                ],
                "total_count": 1,
                "total_size_mb": 1.0
            }
        }

class DocumentUploadRequest(BaseModel):
    """Template for additional data when uploading documents"""
    description: Optional[str] = None
    category: Optional[str] = None  # "contrato", "ley", "reglamento", "otro"
    name: Optional[str] = None  # Nombre amigable del documento
    type: Optional[str] = None  # Tipo de documento
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Contrato de servicios de desarrollo web",
                "category": "contrato",
                "name": "Contrato de Trabajo - Juan Pérez",
                "type": "Contrato Laboral"
            }
        }

class SupportedFormat(BaseModel):
    """Information about supported file formats"""
    extension: str
    description: str
    max_size_mb: float
    features: List[str]
    
class SupportedFormatsResponse(BaseModel):
    """Response with supported formats"""
    supported_formats: List[SupportedFormat]
    limitations: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "supported_formats": [
                    {
                        "extension": ".pdf",
                        "description": "Documentos PDF - Contratos, leyes, documentos legales",
                        "max_size_mb": 10.0,
                        "features": ["Extracción de texto", "Conteo de páginas", "Análisis de contenido"]
                    }
                ],
                "limitations": {
                    "max_file_size_mb": 10.0,
                    "max_files_per_user": "Ilimitado",
                    "retention_policy": "Los archivos se mantienen mientras la cuenta esté activa"
                }
            }
        } 