"""
API REST para manejo de documentos
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Dict, Any, List, Optional
import io
import os
import re

from ...services.documents.document_service import document_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Management"])

_SAFE_FILENAME_RE = re.compile(r"^[\w,\s,\-\.]+$")

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form("anonymous"),
    document_type: str = Form("legal_document"),
    description: str = Form("")
) -> Dict[str, Any]:
    """
    Subir documento a AWS S3 o almacenamiento local
    
    - **file**: Archivo a subir
    - **user_id**: ID del usuario (por defecto: anonymous)
    - **document_type**: Tipo de documento
    - **description**: Descripción opcional del documento
    """
    try:
        # Validaciones
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Archivo requerido"
            )
        # Evitar path traversal y nombres peligrosos
        if not _SAFE_FILENAME_RE.match(os.path.basename(file.filename)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo inválido"
            )
        
        # Validar tamaño (máximo 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Archivo demasiado grande (máximo 10MB)"
            )
        
        # Restaurar el archivo para el servicio
        await file.seek(0)
        
        # Validar tipo de contenido básico
        allowed_mime_prefixes = ("text/", "application/pdf", "image/png", "image/jpeg")
        if file.content_type and not file.content_type.startswith(allowed_mime_prefixes):
            # Permitir por extensión conocida si no hay content_type confiable
            allowed_ext = [".txt", ".md", ".pdf", ".png", ".jpg", ".jpeg"]
            if not any(file.filename.lower().endswith(ext) for ext in allowed_ext):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de archivo no soportado"
                )

        # Subir documento
        logger.info("📄 Uploading document")
        logger.info(f"  - user_id: {user_id}")
        logger.info(f"  - document_type: {document_type}")
        result = await document_service.upload_document(
            file=file,
            user_id=user_id,
            document_type=document_type
        )
        logger.info("📄 Document upload completed")
        logger.info(f"  - document_id: {result.get('id', 'No ID')}")
        
        # Agregar descripción si se proporcionó
        if description:
            result["description"] = description
        
        return {
            "success": True,
            "document": result,
            "message": "Documento subido exitosamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al subir documento"
        )

@router.get("/test-search/{user_id}")
async def test_document_search(user_id: str, query: str = "test") -> Dict[str, Any]:
    """
    Endpoint de prueba para verificar que los documentos se están indexando correctamente
    """
    try:
        from ...services.legal.rag.vector_manager import VectorManager
        
        vector_manager = VectorManager()
        
        # Obtener documentos del usuario
        user_docs = document_service.get_user_documents(user_id)
        document_ids = [doc['id'] for doc in user_docs]
        
        # Buscar en vector store
        context, sources = vector_manager.search_vectorstore(
            question=query,
            category="general",
            document_ids=document_ids
        )
        
        return {
            "success": True,
            "query": query,
            "user_documents": len(user_docs),
            "document_ids": document_ids,
            "search_results": {
                "context_length": len(context),
                "sources_count": len(sources),
                "sources": sources
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in test search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda de prueba: {str(e)}"
        )

@router.get("/debug/{user_id}")
async def debug_user_documents(user_id: str) -> Dict[str, Any]:
    """
    Endpoint de debug para verificar documentos del usuario
    """
    try:
        # Obtener documentos del usuario
        user_docs = document_service.get_user_documents(user_id)
        
        # Verificar vector store
        from ...services.legal.rag.vector_manager import VectorManager
        vector_manager = VectorManager()
        
        # Hacer una búsqueda simple para ver si hay documentos
        context, sources = vector_manager.search_vectorstore(
            question="test",
            category="general"
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "user_documents": {
                "count": len(user_docs),
                "documents": user_docs
            },
            "vector_store": {
                "context_length": len(context),
                "sources_count": len(sources),
                "sources": sources[:3]  # Solo primeros 3
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in debug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en debug: {str(e)}"
        )

@router.post("/test-document-query/{user_id}")
async def test_document_query(user_id: str, query: str = "resumen del documento") -> Dict[str, Any]:
    """
    Endpoint específico para probar consultas sobre documentos específicos
    """
    try:
        # Obtener documentos del usuario
        user_docs = document_service.get_user_documents(user_id)
        document_ids = [doc['id'] for doc in user_docs]
        
        logger.info(f"🔍 Testing document query for user {user_id}")
        logger.info(f"📄 User has {len(user_docs)} documents: {document_ids}")
        
        if not document_ids:
            return {
                "success": False,
                "error": "No documents found for user",
                "user_documents": [],
                "document_ids": [],
                "query": query
            }
        
        # Probar búsqueda con documentos específicos
        from ...services.legal.rag.vector_manager import VectorManager
        vector_manager = VectorManager()
        
        # Búsqueda general (sin filtro)
        logger.info("🔍 Testing general search (no document filter)")
        general_context, general_sources = vector_manager.search_vectorstore(
            question=query,
            category="general"
        )
        
        # Búsqueda específica (con filtro de documentos)
        logger.info(f"🔍 Testing specific document search with IDs: {document_ids}")
        specific_context, specific_sources = vector_manager.search_vectorstore(
            question=query,
            category="general",
            document_ids=document_ids
        )
        
        # Probar con el servicio RAG completo
        from ...core.rag_service import rag_service
        logger.info("🔍 Testing full RAG service with document IDs")
        rag_result = await rag_service.process_legal_query(
            question=query,
            user_id=user_id,
            document_ids=document_ids
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "query": query,
            "user_documents": {
                "count": len(user_docs),
                "document_ids": document_ids,
                "documents": user_docs
            },
            "search_comparison": {
                "general_search": {
                    "context_length": len(general_context),
                    "sources_count": len(general_sources),
                    "context_preview": general_context[:200] + "..." if len(general_context) > 200 else general_context,
                    "sources": general_sources[:2]
                },
                "specific_search": {
                    "context_length": len(specific_context),
                    "sources_count": len(specific_sources),
                    "context_preview": specific_context[:200] + "..." if len(specific_context) > 200 else specific_context,
                    "sources": specific_sources[:2]
                }
            },
            "rag_service_result": {
                "answer_preview": rag_result["answer"][:200] + "..." if len(rag_result["answer"]) > 200 else rag_result["answer"],
                "confidence": rag_result["confidence"],
                "sources_count": len(rag_result.get("sources", [])),
                "sources": rag_result.get("sources", [])[:2]
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error in test document query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en test document query: {str(e)}"
        )

@router.get("/user/{user_id}")
async def get_user_documents(user_id: str) -> Dict[str, Any]:
    """
    Obtener todos los documentos de un usuario
    """
    try:
        documents = document_service.get_user_documents(user_id)
        
        return {
            "user_id": user_id,
            "documents": documents,
            "total_documents": len(documents),
            "total_size": sum(doc.get("file_size", 0) for doc in documents)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting user documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener documentos del usuario"
        )

@router.get("/download/{user_id}/{doc_id}")
async def download_document(user_id: str, doc_id: str):
    """
    Descargar documento específico
    """
    try:
        # Obtener información del documento
        document = document_service.get_document_by_id(user_id, doc_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Descargar contenido
        content = await document_service.download_document(user_id, doc_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contenido del documento no disponible"
            )
        
        # Determinar tipo de contenido
        content_type = document.get("content_type", "application/octet-stream")
        filename = document.get("filename", f"document_{doc_id}")
        
        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error downloading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al descargar documento"
        )

@router.delete("/delete/{user_id}/{doc_id}")
async def delete_document(user_id: str, doc_id: str) -> Dict[str, Any]:
    """
    Eliminar documento específico
    """
    try:
        success = await document_service.delete_document(user_id, doc_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return {
            "success": True,
            "message": "Documento eliminado exitosamente",
            "doc_id": doc_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar documento"
        )

@router.get("/info/{user_id}/{doc_id}")
async def get_document_info(user_id: str, doc_id: str) -> Dict[str, Any]:
    """
    Obtener información detallada de un documento
    """
    try:
        document = document_service.get_document_by_id(user_id, doc_id)
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return {
            "document": document,
            "access_info": {
                "can_download": True,
                "can_delete": True,
                "storage_location": "s3" if document.get("s3_key") else "local"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting document info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener información del documento"
        )

@router.get("/stats")
async def get_storage_stats() -> Dict[str, Any]:
    """
    Obtener estadísticas del sistema de almacenamiento
    """
    try:
        return document_service.get_storage_stats()
        
    except Exception as e:
        logger.error(f"❌ Error getting storage stats: {e}")
        return {
            "error": str(e),
            "total_documents": 0,
            "total_users": 0
        }

@router.get("/health")
async def documents_health_check() -> Dict[str, str]:
    """
    Health check para el servicio de documentos
    """
    try:
        stats = document_service.get_storage_stats()
        
        if stats.get("s3_enabled"):
            return {"status": "healthy", "message": "Document service operational with S3"}
        else:
            return {"status": "limited", "message": "Document service operational with local storage"}
            
    except Exception as e:
        logger.error(f"❌ Documents health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}

@router.post("/bulk-upload")
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    user_id: str = Form("anonymous"),
    document_type: str = Form("legal_document")
) -> Dict[str, Any]:
    """
    Subir múltiples documentos de una vez
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Máximo 10 archivos por carga"
            )
        
        results = []
        errors = []
        
        for file in files:
            try:
                if file.filename:
                    result = await document_service.upload_document(
                        file=file,
                        user_id=user_id,
                        document_type=document_type
                    )
                    results.append(result)
                else:
                    errors.append({"filename": "unknown", "error": "Archivo sin nombre"})
            except Exception as e:
                errors.append({"filename": file.filename, "error": str(e)})
        
        return {
            "success": len(results) > 0,
            "uploaded_documents": results,
            "total_uploaded": len(results),
            "errors": errors,
            "total_errors": len(errors)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in bulk upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en carga masiva de documentos"
        )
