"""
API REST para consultas legales RAG
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
import time

from ...models.rag import QueryRequest, QueryResponse, QuerySuggestionsResponse, QueryExamplesResponse
from ...core.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["Legal RAG"])

@router.post("/query", response_model=QueryResponse)
async def process_legal_query(request: QueryRequest) -> QueryResponse:
    """
    Procesar consulta legal usando el sistema RAG multiagente
    
    - **query**: Pregunta legal del usuario
    - **method**: Método de consulta (text, voice, document)
    - **area**: Área legal específica (opcional)
    - **userId**: ID del usuario (opcional)
    - **documentIds**: IDs de documentos a usar (opcional)
    - **use_uploaded_docs**: Si usar documentos subidos por el usuario
    """
    try:
        logger.info(f"🔍 Received query request: {request}")
        logger.info(f"🔍 Query: {request.query}")
        logger.info(f"🔍 Document IDs: {request.documentIds}")
        logger.info(f"🔍 Session ID: {request.sessionId}")
        
        if not request.query or len(request.query.strip()) < 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La pregunta debe tener al menos 4 caracteres"
            )
        
        start_time = time.time()
        # Procesar consulta
        result = await rag_service.process_legal_query(
            question=request.query.strip(),  # Usar el campo 'query' del request
            user_id=request.userId or "anonymous",  # Usar userId si está disponible
            use_uploaded_docs=request.use_uploaded_docs,
            session_id=request.sessionId,  # Usar sessionId directamente
            document_ids=request.documentIds  # Usar documentIds directamente
        )
        
        # Convertir a modelo de respuesta
        return QueryResponse(
            id=f"query_{int(time.time())}",  # Generar ID único
            response=result["answer"],  # Usar 'answer' del servicio como 'response'
            confidence=result["confidence"],
            area=result.get("category", "general"),  # Usar 'category' como 'area'
            sources=result.get("sources", []),
            relatedQuestions=result.get("suggestions", []),  # Usar 'suggestions' como 'relatedQuestions'
            audioUrl=None,  # Por ahora sin audio
            metadata={
                "processingTime": int((time.time() - start_time) * 1000),
                "sourceCount": len(result.get("sources", [])),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing legal query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la consulta"
        )

@router.get("/suggestions", response_model=QuerySuggestionsResponse)
async def get_query_suggestions() -> QuerySuggestionsResponse:
    """
    Obtener sugerencias de consultas legales organizadas por categoría
    """
    try:
        suggestions_data = rag_service.get_query_suggestions()
        
        return QuerySuggestionsResponse(
            suggestions=suggestions_data["suggestions"],
            total_categories=suggestions_data["total_categories"],
            message=suggestions_data["message"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener sugerencias"
        )

@router.get("/examples", response_model=QueryExamplesResponse)
async def get_query_examples() -> QueryExamplesResponse:
    """
    Obtener ejemplos de consultas para testing y demostración
    """
    try:
        examples_data = rag_service.get_query_examples()
        
        return QueryExamplesResponse(
            examples=examples_data["examples"],
            total_examples=examples_data["total_examples"],
            usage=examples_data["usage"],
            note=examples_data.get("note")
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting examples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener ejemplos"
        )

@router.get("/status")
async def get_rag_status() -> Dict[str, Any]:
    """
    Obtener estado del sistema RAG y sus componentes
    """
    try:
        return rag_service.get_system_status()
        
    except Exception as e:
        logger.error(f"❌ Error getting RAG status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "components": {}
        }

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check básico para el sistema RAG
    """
    try:
        # Verificar componentes críticos
        status = rag_service.get_system_status()
        
        if status["status"] == "operational":
            return {"status": "healthy", "message": "RAG system operational"}
        else:
            return {"status": "degraded", "message": "Some components have issues"}
            
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}

@router.get("/debug/memory/{session_id}")
async def debug_memory(session_id: str) -> Dict[str, Any]:
    """
    DEBUG: Obtener información de memoria para una sesión (solo sistema de agentes)
    """
    try:
        from ...agent.legal_agents import legal_agent_system
        
        # Obtener información del sistema de memoria de agentes
        agent_context = legal_agent_system.memory_service.get_conversation_context(session_id)
        agent_summary = legal_agent_system.get_conversation_summary(session_id)
        
        # Obtener cache de conversaciones directamente
        conversation_cache = legal_agent_system.memory_service.conversation_cache.get(session_id, [])
        
        return {
            "session_id": session_id,
            "memory_system": "legal_agents_only",
            "agent_context_length": len(agent_context),
            "agent_context": agent_context,
            "agent_summary": agent_summary,
            "conversation_cache": conversation_cache[-5:] if conversation_cache else [],  # últimos 5 intercambios
            "total_exchanges": len(conversation_cache)
        }
    except Exception as e:
        logger.error(f"❌ Debug memory failed: {e}")
        return {"error": str(e)}

@router.delete("/debug/memory/{session_id}")
async def clear_session_memory(session_id: str) -> Dict[str, Any]:
    """
    DEBUG: Limpiar memoria de una sesión específica
    """
    try:
        from ...agent.legal_agents import legal_agent_system
        
        success = legal_agent_system.clear_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "cleared": success,
            "message": f"Memoria de sesión {session_id} {'limpiada' if success else 'no encontrada'}"
        }
    except Exception as e:
        logger.error(f"❌ Clear memory failed: {e}")
        return {"error": str(e)}
