from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from fastapi import UploadFile

class QueryRequest(BaseModel):
    """Request for legal consultation"""
    query: str  # Cambiado de 'question' a 'query' para coincidir con el frontend
    method: Optional[str] = "text"  # Agregado para coincidir con el frontend
    area: Optional[str] = ""  # Cambiado de 'context' a 'area' para coincidir con el frontend
    userId: Optional[str] = None 
    sessionId: Optional[str] = None  # ID de la sesión para mantener contexto
    documentIds: Optional[List[str]] = []  # Cambiado de list a List[str] para mejor tipado
    use_uploaded_docs: Optional[bool] = True
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cómo constituyo una SAS en Colombia?",
                "method": "text",
                "area": "empresa",
                "userId": "user123",
                "sessionId": "session_123",
                "documentIds": [],
                "use_uploaded_docs": True
            }
        }
    )

class ChatMessage(BaseModel):
    """Chat message for the frontend"""
    id: str
    content: str
    sender: str  # "user" o "assistant"
    timestamp: str
    type: Optional[str] = "text"  # "text", "document", "legal-advice"
    fileName: Optional[str] = None
    fileUrl: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat request with optional archive"""
    message: str
    file: Optional[UploadFile] = None
    use_uploaded_docs: Optional[bool] = True

class ChatResponse(BaseModel):
    """Chat response for the frontend"""
    message: ChatMessage
    suggestions: Optional[List[str]] = []
    confidence: Optional[float] = 0.0
    sources: Optional[List[Dict[str, Any]]] = []

class StreamingChatResponse(BaseModel):
    """Streaming response for chat"""
    content: str
    is_complete: bool = False
    message_id: str
    confidence: Optional[float] = None

class QueryResponse(BaseModel):
    """Legal query response - updated to match frontend LegalQueryResponse"""
    id: str  # Agregado para coincidir con el frontend
    response: str  # Cambiado de 'answer' a 'response' para coincidir con el frontend
    confidence: float
    area: str  # Cambiado de 'category' a 'area' para coincidir con el frontend
    sources: List[Dict[str, Any]] = []
    relatedQuestions: List[str] = []  # Cambiado de 'suggestions' a 'relatedQuestions' para coincidir con el frontend
    audioUrl: Optional[str] = None  # Agregado para coincidir con el frontend
    metadata: Dict[str, Any] = {  # Agregado para coincidir con el frontend
        "processingTime": 0,
        "sourceCount": 0,
        "timestamp": ""
    }
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "query_123",
                "response": "Para constituir una SAS en Colombia necesitas...",
                "confidence": 0.9,
                "area": "Constitución de Empresa",
                "sources": [
                    {
                        "title": "Código de Comercio",
                        "content": "Artículo 2...",
                        "relevance": 0.95
                    }
                ],
                "relatedQuestions": ["¿Qué documentos necesito?", "¿Cuánto cuesta?"],
                "audioUrl": None,
                "metadata": {
                    "processingTime": 1500,
                    "sourceCount": 3,
                    "timestamp": "2024-01-01T12:00:00Z"
                }
            }
        }
    )

class QuerySuggestion(BaseModel):
    """Suggestion for consultation"""
    category: str
    question: str
    description: str

class QuerySuggestionsResponse(BaseModel):
    """Response with suggested queries"""
    suggestions: List[QuerySuggestion]
    total_categories: int
    message: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "suggestions": [
                    {
                        "category": "🏪 Constitución de Empresa",
                        "queries": [
                            "¿Cómo constituyo una SAS en Colombia?",
                            "¿Qué diferencias hay entre SAS y Ltda?"
                        ]
                    }
                ],
                "total_categories": 5,
                "message": "Consultas comunes para PyMEs colombianas"
            }
        }
    )

class QueryExample(BaseModel):
    """Query example"""
    question: str
    expected_topics: List[str]
    complexity: str
    requires_documents: bool

class QueryExamplesResponse(BaseModel):
    """Answer with sample queries"""
    examples: List[QueryExample]
    total_examples: int
    usage: str
    note: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "examples": [
                    {
                        "question": "¿Cómo constituyo una SAS en Colombia?",
                        "expected_topics": ["Cámara de Comercio", "Documentos requeridos"],
                        "complexity": "Media",
                        "requires_documents": False
                    }
                ],
                "total_examples": 3,
                "usage": "Usa estos ejemplos para probar el endpoint /rag/query",
                "note": "Algunos ejemplos requieren documentos subidos"
            }
        }
    )

class ChatHistoryResponse(BaseModel):
    """Reply with chat history"""
    messages: List[ChatMessage]
    total_messages: int
    user_id: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "messages": [
                    {
                        "id": "1",
                        "content": "¿Cómo constituyo una SAS?",
                        "sender": "user",
                        "timestamp": "2024-01-15T10:00:00Z",
                        "type": "text"
                    }
                ],
                "total_messages": 1,
                "user_id": "user123"
            }
        }
    ) 

